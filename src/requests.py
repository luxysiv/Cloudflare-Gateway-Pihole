import ssl
import gzip
import json
import time
import random
import http.client
import socket
import urllib.parse
import zlib
from io import BytesIO
from functools import wraps
from typing import Optional, Tuple
from src import info, silent_error, error, RATE_LIMIT_INTERVAL, CF_IDENTIFIER, CF_API_TOKEN

class HTTPException(Exception):
    pass

def cloudflare_gateway_request(method: str, endpoint: str, body: Optional[str] = None, timeout: int = 10) -> Tuple[int, dict]:
    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection("api.cloudflare.com", context=context, timeout=timeout)

    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate"
    }

    url = f"/client/v4/accounts/{CF_IDENTIFIER}/gateway{endpoint}"
    full_url = f"https://api.cloudflare.com{url}"

    try:
        conn.request(method, url, body, headers)
        response = conn.getresponse()
        data = response.read()
        status = response.status

        content_encoding = response.getheader('Content-Encoding')
        if content_encoding == 'gzip':
            buf = BytesIO(data)
            with gzip.GzipFile(fileobj=buf) as f:
                data = f.read()
        elif content_encoding == 'deflate':
            data = zlib.decompress(data)

        if status >= 400:
            error_message = f"Request failed: {status} {response.reason}, Body: {data.decode('utf-8', errors='ignore')} for url: {full_url}"
            if status in [400, 403, 404]:
                error(error_message)
            else:
                silent_error(error_message)
            raise HTTPException(error_message)

        return status, json.loads(data.decode('utf-8'))

    except (http.client.HTTPException, ssl.SSLError, socket.timeout, OSError) as e:
        error_message = f"Network error occurred: {e}"
        info(error_message)
        raise HTTPException(error_message)
    except json.JSONDecodeError:
        error_message = "Failed to decode JSON response"
        info(error_message)
        raise HTTPException(error_message)
    finally:
        conn.close()

def stop_never(attempt_number):
    return False

def wait_random_exponential(attempt_number, multiplier=1, max_wait=10):
    return min(multiplier * (2 ** random.uniform(0, attempt_number - 1)), max_wait)

def retry_if_exception_type(exceptions):
    return lambda e: isinstance(e, exceptions)

def retry(stop=None, wait=None, retry=None, after=None, before_sleep=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt_number = 0
            while True:
                try:
                    attempt_number += 1
                    return func(*args, **kwargs)
                except Exception as e:
                    if retry and not retry(e):
                        raise
                    if after:
                        after({'attempt_number': attempt_number, 'outcome': e})
                    if stop and stop(attempt_number):
                        raise
                    if before_sleep:
                        before_sleep({'attempt_number': attempt_number})
                    wait_time = wait(attempt_number) if wait else 1
                    time.sleep(wait_time)
        return wrapper
    return decorator

retry_config = {
    'stop': stop_never,
    'wait': lambda attempt_number: wait_random_exponential(
        attempt_number, multiplier=1, max_wait=10
    ),
    'retry': retry_if_exception_type((HTTPException,)),
    'before_sleep': lambda retry_state: info(
        f"Sleeping before next retry ({retry_state['attempt_number']})"
    )
}

class RateLimiter:
    def __init__(self, interval):
        self.interval = interval
        self.timestamp = time.time()

    def wait_for_next_request(self):
        now = time.time()
        elapsed = now - self.timestamp
        sleep_time = max(0, self.interval - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)
        self.timestamp = time.time()

rate_limiter = RateLimiter(RATE_LIMIT_INTERVAL)

def rate_limited_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        rate_limiter.wait_for_next_request()
        return func(*args, **kwargs)
    return wrapper
