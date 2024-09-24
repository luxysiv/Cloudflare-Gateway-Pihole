import ssl
import gzip
import json
import time
import random
import socket
import http.client
from io import BytesIO
from functools import wraps
from typing import Optional, Tuple
from src import info, silent_error, error, CF_IDENTIFIER, CF_API_TOKEN


def cloudflare_gateway_request(
    method: str, 
    endpoint: str, 
    body: Optional[str] = None, 
    timeout: int = 10
) -> Tuple[int, dict]:
    """
    Makes a request to the Cloudflare gateway API and returns the status and response data.
    
    Args:
        method: HTTP method (GET, POST, etc.).
        endpoint: API endpoint.
        body: Request payload as a JSON string.
        timeout: Timeout for the request.
    
    Returns:
        Tuple containing response status code and JSON-decoded response data.
    
    Raises:
        RuntimeError: On failure to complete the request or process the response.
    """
    
    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection("api.cloudflare.com", context=context, timeout=timeout)
    url = f"/client/v4/accounts/{CF_IDENTIFIER}/gateway{endpoint}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip"
    }

    try:
        conn.request(method, url, body, headers)
        response = conn.getresponse()
        data = response.read()

        try:
            # Decompress GZIP response data
            data = gzip.GzipFile(fileobj=BytesIO(data)).read()
        except OSError as e:
            raise RuntimeError(f"Error during gzip decompression: {e}")

        if response.status >= 400:
            error_message = (
                f"Request failed: {response.status} {response.reason}, "
                f"Body: {data.decode('utf-8', errors='ignore')} "
                f"for URL: https://api.cloudflare.com{url}"
            )
            raise RuntimeError(error_message)

        # Return status and parsed JSON data
        return response.status, json.loads(data.decode('utf-8'))

    except (http.client.HTTPException, ssl.SSLError, socket.timeout, OSError) as e:
        raise RuntimeError(f"Network error occurred: {e}")
    except json.JSONDecodeError:
        raise RuntimeError("Failed to decode JSON response")
    finally:
        conn.close()


def retry(func):
    """
    Decorator that retries the wrapped function up to 5 times with exponential backoff
    in case of an exception.
    
    Args:
        func: Function to wrap.
    
    Returns:
        The result of the wrapped function or raises the exception if all attempts fail.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        attempt_number = 0
        while True:
            attempt_number += 1
            try:
                return func(*args, **kwargs)
            except Exception as e:
                silent_error(f"Attempt {attempt_number} failed with {e}. Retrying...")

                if attempt_number >= 5:
                    raise

                # Exponential backoff with randomness
                wait_time = min(1 * (2 ** random.uniform(0, attempt_number - 1)), 10)
                silent_error(f"Sleeping for {wait_time:.2f} seconds before retrying...")
                time.sleep(wait_time)

    return wrapper


def rate_limited_request(func):
    """
    Decorator that ensures the wrapped function is called no more than once per second.
    
    Args:
        func: Function to wrap.
    
    Returns:
        The result of the wrapped function after enforcing rate limits.
    """
    last_call_time = [0]

    @wraps(func)
    def wrapper(*args, **kwargs):
        current_time = time.time()
        elapsed_time = current_time - last_call_time[0]
        wait_time = 1 - elapsed_time
        
        if wait_time > 0:
            time.sleep(wait_time)
        
        last_call_time[0] = time.time()
        return func(*args, **kwargs)

    return wrapper
