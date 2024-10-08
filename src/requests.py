import ssl
import gzip
import json
import time
import random
import socket
import urllib.request
import urllib.parse
import urllib.error
import http.client
import zlib
from io import BytesIO
from functools import wraps
from typing import Optional, Tuple
from src import info, silent_error, error, CF_IDENTIFIER, CF_API_TOKEN

# Custom exception to handle HTTP-related issues
class HTTPException(Exception):
    pass

# Custom exception to handle HTTP 429 (Too Many Requests) errors
class RateLimitException(HTTPException):
    pass

# Custom exceptions for urllib to handle specific errors similar to http.client
class URLLibHTTPException(HTTPException):
    pass

class URLLibTimeoutException(URLLibHTTPException, socket.timeout):
    pass

class URLLibSSLError(URLLibHTTPException, ssl.SSLError):
    pass

# Map `urllib` errors to custom exceptions
URLLIB_ERROR_MAP = {
    urllib.error.HTTPError: URLLibHTTPException,
    urllib.error.URLError: URLLibTimeoutException,
    ssl.SSLError: URLLibSSLError,
    socket.timeout: URLLibTimeoutException,
}

# Helper function to handle different content encodings in the response
def handle_response_content(data: bytes, encoding: Optional[str]) -> bytes:
    if encoding in [None, 'identity']:
        return data
    elif encoding == 'gzip':
        buf = BytesIO(data)
        with gzip.GzipFile(fileobj=buf) as f:
            return f.read()
    elif encoding == 'deflate':
        return zlib.decompress(data)
    else:
        raise ValueError(f"Unsupported Content-Encoding: {encoding}")

# Main function to send HTTP requests to Cloudflare's API using various HTTP methods
def cloudflare_gateway_request(
        method: str,
        endpoint: str,
        body: Optional[str] = None,
        headers: Optional[dict] = None,
        timeout: int = 10
    ) -> Tuple[int, dict]:
    context = ssl.create_default_context()  # Create a default SSL context
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway{endpoint}"
    
    # Default headers for all requests
    default_headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate"
    }
    
    # Allow custom headers to be added or updated
    if headers:
        default_headers.update(headers)

    # Use `urllib` for basic methods like GET, POST, and PUT
    if method.upper() in ["GET", "POST", "PUT"]:
        data = body.encode('utf-8') if body else None
        req = urllib.request.Request(url, headers=default_headers, method=method.upper(), data=data)
        
        # Retry logic for 429 errors
        while True:
            try:
                # Send request and read the response
                with urllib.request.urlopen(req, context=context, timeout=timeout) as response:
                    status = response.status
                    content_encoding = response.getheader('Content-Encoding')
                    data = handle_response_content(response.read(), content_encoding)
                    break  # Exit loop on success
            except urllib.error.HTTPError as e:
                # Capture the HTTP status code and body from the error
                status = e.code
                data = e.read()  # Read the error response body
                error_message = (
                    f"Request failed: {status} {e.reason}, "
                    f"Body: {data.decode('utf-8', errors='ignore')} "
                    f"for URL: {url}"
                )

                # Raise the appropriate exception based on status code
                if status == 429:
                    silent_error(error_message)
                    raise RateLimitException(error_message)
                elif status in [400, 403, 404]:
                    error(error_message)  # Log error for these status codes
                    raise URLLibHTTPException(error_message)
                else:
                    silent_error(error_message)
                    raise URLLibHTTPException(error_message)
            except (urllib.error.URLError, ssl.SSLError, socket.timeout) as e:
                error_message = f"Network error occurred: {e}, URL: {url}, Body: {body}"
                silent_error(error_message)
                raise URLLibHTTPException(error_message)
    else:
        # Use `http.client` for more complex methods like PATCH and DELETE
        parsed_url = urllib.parse.urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.hostname, context=context, timeout=timeout)
        
        try:
            conn.request(method, parsed_url.path, body, default_headers)  # Send HTTP request
            response = conn.getresponse()
            status = response.status
            content_encoding = response.getheader('Content-Encoding')
            data = handle_response_content(response.read(), content_encoding)

            # Handle HTTP errors and parse the JSON response
            if status >= 400:
                error_message = (
                    f"Request failed: {status} {response.reason}, "
                    f"Body: {data.decode('utf-8', errors='ignore')} "
                    f"for URL: {url}"
                )
                if status == 429:
                    silent_error(error_message)
                    raise RateLimitException(error_message)
                elif status in [400, 403, 404]:
                    error(error_message)
                else:
                    silent_error(error_message)
                raise HTTPException(error_message)

        except (http.client.HTTPException, ssl.SSLError, socket.timeout, OSError) as e:
            error_message = f"Network error occurred: {e}, URL: {url}, Body: {body}"
            silent_error(error_message)
            raise HTTPException(error_message)
        finally:
            conn.close()

    return status, json.loads(data.decode('utf-8'))

# Retry conditions and logic configurations
def wait_random_exponential(attempt_number, multiplier=1, max_wait=10):
    return min(multiplier * (2 ** random.uniform(0, attempt_number - 1)), max_wait)

def retry_if_exception_type(exceptions):
    return lambda e: isinstance(e, exceptions)

# Decorator to implement retry logic with configurable conditions
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
                    if stop and stop(e, attempt_number):
                        raise
                    if before_sleep:
                        before_sleep({'attempt_number': attempt_number})
                    wait_time = wait(attempt_number) if wait else 1
                    time.sleep(wait_time)
        return wrapper
    return decorator

# Custom stop condition to handle different exception types
def custom_stop_condition(exception, attempt_number):
    if isinstance(exception, RateLimitException):
        return False  # Continue retrying for rate-limit errors (unlimited retries)
    return attempt_number >= 5  # Stop after 5 attempts for other exceptions

# Retry configuration dictionary
retry_config = {
    'stop': custom_stop_condition,
    'wait': lambda attempt_number: wait_random_exponential(
        attempt_number, multiplier=1, max_wait=10
    ),
    'retry': retry_if_exception_type((HTTPException,)),
    'before_sleep': lambda retry_state: info(
        f"Sleeping before next retry ({retry_state['attempt_number']})"
    )
}

# Simple rate-limiter class to control request frequency
class RateLimiter:
    def __init__(self, interval: float = 1):
        self.interval = interval
        self.timestamp = time.time()

    def wait_for_next_request(self):
        now = time.time()
        elapsed = now - self.timestamp
        sleep_time = max(0, self.interval - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)
        self.timestamp = time.time()

# Decorator to apply rate-limiting logic to functions
def rate_limited_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        rate_limiter = RateLimiter()
        rate_limiter.wait_for_next_request()
        return func(*args, **kwargs)
    return wrapper
