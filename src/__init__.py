import os
import re
import gzip
import json
import time
import random
import http.client
from sys import exit
from io import BytesIO
from functools import wraps
from src.colorlog import logger
from http.client import HTTPException

# Read .env variables 
def dot_env(file_path=".env"):
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    value = re.sub(r'^["\'<]*(.*?)["\'>]*$', r'\1', value)
                    env_vars[key] = value
    return env_vars

env_vars = dot_env()

# Load environment or .env variables
CF_API_TOKEN = os.getenv("CF_API_TOKEN") or env_vars.get("CF_API_TOKEN")
CF_IDENTIFIER = os.getenv("CF_IDENTIFIER") or env_vars.get("CF_IDENTIFIER")
if not CF_API_TOKEN or not CF_IDENTIFIER:
    raise Exception("Missing Cloudflare credentials")

# Constants
MAX_LISTS = 300
MAX_LIST_SIZE = 1000
RATE_LIMIT_INTERVAL = 1.0
PREFIX = "AdBlock-DNS-Filters"

# Compile regex patterns
replace_pattern = re.compile(
    r"(^([0-9.]+|[0-9a-fA-F:.]+)\s+|^(\|\||@@\|\||\*\.|\*))"
)
domain_pattern = re.compile(
    r"^([a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)*"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?$"
)
ip_pattern = re.compile(
    r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
)

# Logging functions
def error(message):
    logger.error(message)
    exit(1)

def silent_error(message):
    logger.warning(message)

def info(message):
    logger.info(message)
    
# Configure connection
def perform_request(method, endpoint, body=None):
    conn = http.client.HTTPSConnection("api.cloudflare.com")
    
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate"
    }
    
    url = f"/client/v4/accounts/{CF_IDENTIFIER}/gateway" + endpoint
    full_url = f"https://api.cloudflare.com" + url
    conn.request(method, url, body, headers)
    response = conn.getresponse()
    data = response.read()
    status = response.status

    if status >= 400:
        error_message = ""
        if status == 400:
            error_message = f"400 Client Error: Bad Request for url: {full_url}"
        elif status == 401:
            error_message = f"401 Client Error: Unauthorized for url: {full_url}"
        elif status == 403:
            error_message = f"403 Client Error: Forbidden for url: {full_url}"
        elif status == 404:
            error_message = f"404 Client Error: Not Found for url: {full_url}"
        elif status == 429:
            error_message = f"429 Client Error: Too Many Requests for url: {full_url}"
        elif status >= 500:
            error_message = f"{status} Server Error for url: {full_url}"
        else:
            error_message = f"HTTP request failed with status {status} for url: {full_url}"

        info(error_message)
        raise HTTPException(error_message)

    if response.getheader('Content-Encoding') == 'gzip':
        buf = BytesIO(data)
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()

    return response.status, json.loads(data.decode('utf-8'))

# Retry decorator
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

# Retry utility functions
def stop_never(attempt_number):
    return False

def wait_random_exponential(attempt_number, multiplier=1, max_wait=10):
    return min(multiplier * (2 ** random.uniform(0, attempt_number - 1)), max_wait)

def retry_if_exception_type(exceptions):
    return lambda e: isinstance(e, exceptions)

retry_config = {
    'stop': stop_never,
    'wait': lambda attempt_number: wait_random_exponential(
        attempt_number, multiplier=1, max_wait=10
    ),
    'retry': retry_if_exception_type((HTTPException,)),
    'after': lambda retry_state: info(
        f"Retrying ({retry_state['attempt_number']}): {retry_state['outcome']}"
    ),
    'before_sleep': lambda retry_state: info(
        f"Sleeping before next retry ({retry_state['attempt_number']})"
    )
}

# Rate limiter
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

# Function to limit requests
def rate_limited_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        rate_limiter.wait_for_next_request()
        return func(*args, **kwargs)
    return wrapper
