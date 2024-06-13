import random
from tenacity import (
    retry,
    stop_never,
    wait_random_exponential,
    retry_if_exception_type
)
from requests.exceptions import RequestException, HTTPError
from src import (
    info,
    session,
    BASE_URL,
    MAX_LIST_SIZE
)

retry_config = {
    'stop': stop_never,
    'wait': wait_random_exponential(multiplier=1, max=10),
    'retry': retry_if_exception_type((HTTPError, RequestException)),
    'after': lambda retry_state: info(
        f"Retrying ({retry_state.attempt_number}): {retry_state.outcome.exception()}"
    ),
    'before_sleep': lambda retry_state: info(
        f"Sleeping before next retry ({retry_state.attempt_number})"
    )
}

@retry(**retry_config)
def get_current_lists():
    response = session.get(f"{BASE_URL}/lists")
    response.raise_for_status()
    return response.json()

@retry(**retry_config)
def get_current_policies():
    response = session.get(f"{BASE_URL}/rules")
    response.raise_for_status()
    return response.json()

@retry(**retry_config)
def get_list_items(list_id):
    response = session.get(f"{BASE_URL}/lists/{list_id}/items?limit={MAX_LIST_SIZE}")
    response.raise_for_status()
    return response.json()

@retry(**retry_config)
def patch_list(list_id, payload):
    response = session.patch(f"{BASE_URL}/lists/{list_id}", json=payload)
    response.raise_for_status()
    return response.json()

@retry(**retry_config)
def create_list(payload):
    response = session.post(f"{BASE_URL}/lists", json=payload)
    response.raise_for_status()
    return response.json()

@retry(**retry_config)
def create_policy(json_data):
    response = session.post(f"{BASE_URL}/rules", json=json_data)
    response.raise_for_status()
    return response.json()

@retry(**retry_config)
def update_policy(policy_id, json_data):
    response = session.put(f"{BASE_URL}/rules/{policy_id}", json=json_data)
    response.raise_for_status()
    return response.json()

@retry(**retry_config)
def delete_list(list_id):
    response = session.delete(f"{BASE_URL}/lists/{list_id}")
    response.raise_for_status()
    return response.json()

@retry(**retry_config)
def delete_policy(policy_id):
    response = session.delete(f"{BASE_URL}/rules/{policy_id}")
    response.raise_for_status()
    return response.json()
