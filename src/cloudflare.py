import time
from src import (
    error,
    session,
    silent_error,
    BASE_URL,
    MAX_LIST_SIZE
)

MAX_RETRY = 3

def get_current_lists():
    for _ in range(MAX_RETRY):
        try:
            response = session.get(f"{BASE_URL}/lists")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get current lists. Error: {e}")
        time.sleep(1)
    error("Failed to get current lists after retries")

def get_current_policies():
    for _ in range(MAX_RETRY):
        try:
            response = session.get(f"{BASE_URL}/rules")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get current policies. Error: {e}")
        time.sleep(1)  
    error("Failed to get current policies after retries")

def get_list_items(list_id):
    for _ in range(MAX_RETRY):
        try:
            response = session.get(f"{BASE_URL}/lists/{list_id}/items?limit={MAX_LIST_SIZE}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get list items. Error: {e}")
        time.sleep(1)  
    error("Failed to get list items after retries")

def patch_list(list_id, payload):
    for _ in range(MAX_RETRY):
        try:
            response = session.patch(f"{BASE_URL}/lists/{list_id}",json=payload)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get patch list. Error: {e}")
        time.sleep(1)  
    error("Failed to get patch list after retries")

def create_list(payload):
    for _ in range(MAX_RETRY):
        try:
            response = session.post(f"{BASE_URL}/lists",json=payload)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get create list. Error: {e}")
        time.sleep(1)  
    error("Failed to get create list after retries")

def create_policy(json_data):
    for _ in range(MAX_RETRY):
        try:
            response = session.post(f"{BASE_URL}/rules",json=json_data)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get create policy. Error: {e}")
        time.sleep(1)  
    error("Failed to get create policy after retries")

def update_policy(policy_id, json_data):
    for _ in range(MAX_RETRY):
        try:
            response = session.put(f"{BASE_URL}/rules/{policy_id}",json=json_data)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get update policy. Error: {e}")
        time.sleep(1)  
    error("Failed to get update policy after retries")

def delete_list(list_id):
    for _ in range(MAX_RETRY):
        try:
            response = session.delete(f"{BASE_URL}/lists/{list_id}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get delete list. Error: {e}")
        time.sleep(1)  
    error("Failed to get delete list after retries")

def delete_policy(policy_id):
    for _ in range(MAX_RETRY):
        try:
            response = session.delete(f"{BASE_URL}/rules/{policy_id}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            silent_error(f"Failed to get delete policy. Error: {e}")
        time.sleep(1)  
    error("Failed to get delete policy after retries")
