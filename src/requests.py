import os
import sys
import json
import gzip
import zlib
import time
import random
import http.client
import urllib.parse
from functools import wraps
from src import (
    info, silent_error, error, 
    RATE_LIMIT_INTERVAL, CF_IDENTIFIER, CF_API_TOKEN
)

class RequestException(Exception):
    pass

class Session:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {CF_API_TOKEN}",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate"
        }
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway"

    def _decode_response(self, response):
        content_encoding = response.getheader('Content-Encoding', '')
        response_body = response.read()
        
        if content_encoding == 'gzip':
            response_body = gzip.decompress(response_body).decode('utf-8')
        elif content_encoding == 'deflate':
            response_body = zlib.decompress(response_body).decode('utf-8')
        else:
            response_body = response_body.decode('utf-8')
        
        return response_body

    def _request(self, method, endpoint, data=None):
        url = self.base_url + endpoint
        parsed_url = urllib.parse.urlparse(url)
        connection = http.client.HTTPSConnection(parsed_url.netloc)
        
        body = None
        if data:
            body = json.dumps(data)
        
        connection.request(method, parsed_url.path + ('?' + parsed_url.query if parsed_url.query else ''), body, self.headers)
        response = connection.getresponse()
        
        response_body = self._decode_response(response)
        
        if response.status >= 400:
            if response.status == 400:
                error(f"Request failed: {response.status} {response.reason}, Body: {response_body} for url: {url}")
            raise RequestException(f"Request failed: {response.status} {response.reason}, Body: {response_body} for url: {url}")
        
        return response_body

    def get(self, endpoint):
        return self._request("GET", endpoint)

    def post(self, endpoint, json=None):
        return self._request("POST", endpoint, json)

    def patch(self, endpoint, json=None):
        return self._request("PATCH", endpoint, json)

    def delete(self, endpoint):
        return self._request("DELETE", endpoint)

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
    'retry': retry_if_exception_type((RequestException, )),
    'after': lambda retry_state: silent_error(
        f"Retrying ({retry_state['attempt_number']}): {retry_state['outcome']}"
    ),
    'before_sleep': lambda retry_state: silent_error(
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
    
session = Session()
