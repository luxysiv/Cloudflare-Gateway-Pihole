import json
from src.requests import (
    cloudflare_gateway_request, retry, rate_limited_request, retry_config
)


@retry(**retry_config)
@rate_limited_request
def create_list(name, domains):
    endpoint = "/lists"
    data = {
        "name": name,
        "description": "Ads & Tracking Domains",
        "type": "DOMAIN",
        "items": [{"value": domain} for domain in domains]
    }
    status, response = cloudflare_gateway_request("POST", endpoint, body=json.dumps(data))
    return response["result"]

@retry(**retry_config)
@rate_limited_request
def update_list(list_id, remove_items, append_items):
    endpoint = f"/lists/{list_id}"    
    data = {
        "remove": [domain for domain in remove_items],
        "append": [{"value": domain} for domain in append_items]
    }    
    status, response = cloudflare_gateway_request("PATCH", endpoint, body=json.dumps(data))
    return response["result"]

@retry(**retry_config)
def create_rule(rule_name, list_ids):
    endpoint = "/rules"
    data = {
        "name": rule_name,
        "description": "Block Ads & Tracking",
        "action": "block",
        "traffic": " or ".join(f'any(dns.domains[*] in ${lst})' for lst in list_ids),
        "enabled": True,
    }
    status, response = cloudflare_gateway_request("POST", endpoint, body=json.dumps(data))
    return response["result"]

@retry(**retry_config)
def update_rule(rule_name, rule_id, list_ids):
    endpoint = f"/rules/{rule_id}"
    data = {
        "name": rule_name,
        "description": "Block Ads & Tracking",
        "action": "block",
        "traffic": " or ".join(f'any(dns.domains[*] in ${lst})' for lst in list_ids),
        "enabled": True,
    }
    status, response = cloudflare_gateway_request("PUT", endpoint, body=json.dumps(data))
    return response["result"]

@retry(**retry_config)
def get_lists(prefix_name):
    status, response = cloudflare_gateway_request("GET", "/lists")
    lists = response["result"] or []
    return [l for l in lists if l["name"].startswith(prefix_name)]

@retry(**retry_config)
def get_rules(rule_name_prefix):
    status, response = cloudflare_gateway_request("GET", "/rules")
    rules = response["result"] or []
    return [r for r in rules if r["name"].startswith(rule_name_prefix)]

@retry(**retry_config)
@rate_limited_request
def delete_list(list_id):
    endpoint = f"/lists/{list_id}"
    status, response = cloudflare_gateway_request("DELETE", endpoint)
    return response["result"]

@retry(**retry_config)
def delete_rule(rule_id):
    endpoint = f"/rules/{rule_id}"
    status, response = cloudflare_gateway_request("DELETE", endpoint)
    return response["result"]

@retry(**retry_config)
def get_list_items(list_id):
    endpoint = f"/lists/{list_id}/items?limit=1000"
    status, response = cloudflare_gateway_request("GET", endpoint)
    items = response["result"] or []
    return [i["value"] for i in items]
