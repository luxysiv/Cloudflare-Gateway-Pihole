import json
from http.client import HTTPException
from src import info
from src.requests import rate_limited_request, cloudflare_gateway_request, retry_config, retry


@retry(**retry_config)
def get_current_lists():
    status, response = cloudflare_gateway_request("GET", "/lists")
    return response["result"] or []

@retry(**retry_config)
def get_current_policies():
    status, response = cloudflare_gateway_request("GET", "/rules")
    return response["result"] or []

@retry(**retry_config)
def get_list_items(list_id):
    status, response = cloudflare_gateway_request("GET", f"/lists/{list_id}/items?limit=1000")
    return response["result"] or []

@retry(**retry_config)
@rate_limited_request
def patch_list(list_id, payload):
    body = json.dumps(payload)
    status, response = cloudflare_gateway_request("PATCH", f"/lists/{list_id}", body)
    return response["result"] or []

@retry(**retry_config)
@rate_limited_request
def create_list(payload):
    body = json.dumps(payload)
    status, response = cloudflare_gateway_request("POST", "/lists", body)
    return response ["result"] or []

@retry(**retry_config)
def create_policy(json_data):
    body = json.dumps(json_data)
    status, response = cloudflare_gateway_request("POST", "/rules", body)
    return response

@retry(**retry_config)
def update_policy(policy_id, json_data):
    body = json.dumps(json_data)
    status, response = cloudflare_gateway_request("PUT", f"/rules/{policy_id}", body)
    return response

@retry(**retry_config)
@rate_limited_request
def delete_list(list_id):
    status, response = cloudflare_gateway_request("DELETE", f"/lists/{list_id}")
    return response

@retry(**retry_config)
def delete_policy(policy_id):
    status, response = cloudflare_gateway_request("DELETE", f"/rules/{policy_id}")
    return response
