import json
from http.client import HTTPException
from src import info
from src.requests import rate_limited_request, cloudflare_gateway_request, retry_config, retry


@retry(**retry_config)
def get_current_lists():
    status, data = cloudflare_gateway_request("GET", "/lists")
    return data

@retry(**retry_config)
def get_current_policies():
    status, data = cloudflare_gateway_request("GET", "/rules")
    return data

@retry(**retry_config)
def get_list_items(list_id):
    status, data = cloudflare_gateway_request("GET", f"/lists/{list_id}/items?limit=1000")
    return data

@retry(**retry_config)
@rate_limited_request
def patch_list(list_id, payload):
    body = json.dumps(payload)
    status, data = cloudflare_gateway_request("PATCH", f"/lists/{list_id}", body)
    return data

@retry(**retry_config)
@rate_limited_request
def create_list(payload):
    body = json.dumps(payload)
    status, data = cloudflare_gateway_request("POST", "/lists", body)
    return data

@retry(**retry_config)
def create_policy(json_data):
    body = json.dumps(json_data)
    status, data = cloudflare_gateway_request("POST", "/rules", body)
    return data

@retry(**retry_config)
def update_policy(policy_id, json_data):
    body = json.dumps(json_data)
    status, data = cloudflare_gateway_request("PUT", f"/rules/{policy_id}", body)
    return data

@retry(**retry_config)
@rate_limited_request
def delete_list(list_id):
    status, data = cloudflare_gateway_request("DELETE", f"/lists/{list_id}")
    return data

@retry(**retry_config)
def delete_policy(policy_id):
    status, data = cloudflare_gateway_request("DELETE", f"/rules/{policy_id}")
    return data