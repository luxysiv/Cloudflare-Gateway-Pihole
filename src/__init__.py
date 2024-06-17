import os
import re
import time
import random
import requests
from sys import exit
from loguru import logger
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CF_API_TOKEN = os.getenv("CF_API_TOKEN") or os.environ.get("CF_API_TOKEN")
CF_IDENTIFIER = os.getenv("CF_IDENTIFIER") or os.environ.get("CF_IDENTIFIER")
if not CF_API_TOKEN or not CF_IDENTIFIER:
    raise Exception("Missing Cloudflare credentials")

# Constants
PREFIX = "AdBlock-DNS-Filters"
MAX_LIST_SIZE = 1000
MAX_LISTS = 300
RATE_LIMIT_INTERVAL = 1.0

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

# Configure session
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip, deflate" 
})

BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway"

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

# Logging functions
def error(message):
    logger.error(message)
    exit(1)

def silent_error(message):
    logger.warning(message)

def info(message):
    logger.info(message)
