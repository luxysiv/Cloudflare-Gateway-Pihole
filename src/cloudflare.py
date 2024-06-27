import json
from src import MAX_LIST_SIZE
from src.requests import session, retry, retry_config, rate_limited_request

@retry(**retry_config)
def get_current_lists():
    response = session.get(f"/lists")
    return json.loads(response)

@retry(**retry_config)
def get_current_policies():
    response = session.get(f"/rules")
    return json.loads(response)

@retry(**retry_config)
def get_list_items(list_id):
    response = session.get(f"/lists/{list_id}/items?limit={MAX_LIST_SIZE}")
    return json.loads(response)

@retry(**retry_config)
@rate_limited_request
def patch_list(list_id, payload):
    response = session.patch(f"/lists/{list_id}", json=payload)
    return json.loads(response)

@retry(**retry_config)
@rate_limited_request
def create_list(payload):
    response = session.post(f"/lists", json=payload)
    return json.loads(response)

@retry(**retry_config)
def create_policy(json_data):
    response = session.post(f"/rules", json=json_data)
    return json.loads(response)

@retry(**retry_config)
def update_policy(policy_id, json_data):
    response = session.patch(f"/rules/{policy_id}", json=json_data)
    return json.loads(response)

@retry(**retry_config)
@rate_limited_request
def delete_list(list_id):
    response = session.delete(f"/lists/{list_id}")
    return json.loads(response)

@retry(**retry_config)
def delete_policy(policy_id):
    response = session.delete(f"/rules/{policy_id}")
    return json.loads(response)
