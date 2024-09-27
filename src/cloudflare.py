import json
from src.requests import *


@rate_limited_request
@retry
def create_list(name, domains):
    """
    Creates a list of domains in Cloudflare.

    Args:
        name: Name of the list.
        domains: List of domains to add.

    Returns:
        The created list result.
    """
    endpoint = "/lists"
    data = {
        "name": name,
        "description": "Ads & Tracking Domains",
        "type": "DOMAIN",
        "items": [{"value": domain} for domain in domains]
    }
    status, response = cloudflare_gateway_request("POST", endpoint, body=json.dumps(data))
    return response["result"]


@rate_limited_request
@retry
def update_list(list_id, remove_items, append_items):
    """
    Updates an existing list by removing and appending items.

    Args:
        list_id: The ID of the list to update.
        remove_items: List of domains to remove.
        append_items: List of domains to add.

    Returns:
        The updated list result.
    """
    endpoint = f"/lists/{list_id}"    
    data = {
        "remove": [domain for domain in remove_items],
        "append": [{"value": domain} for domain in append_items]
    }    
    status, response = cloudflare_gateway_request("PATCH", endpoint, body=json.dumps(data))
    return response["result"]


@retry
def create_rule(rule_name, list_ids):
    """
    Creates a new blocking rule using the provided lists.

    Args:
        rule_name: The name of the rule.
        list_ids: List of list IDs to associate with the rule.

    Returns:
        The created rule result.
    """
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


@retry
def update_rule(rule_name, rule_id, list_ids):
    """
    Updates an existing rule.

    Args:
        rule_name: The updated rule name.
        rule_id: The ID of the rule to update.
        list_ids: List of list IDs to associate with the rule.

    Returns:
        The updated rule result.
    """
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


@retry
def get_lists(prefix_name):
    """
    Retrieves all lists whose name starts with the provided prefix.

    Args:
        prefix_name: The prefix to filter list names.

    Returns:
        A list of matching lists.
    """
    status, response = cloudflare_gateway_request("GET", "/lists")
    lists = response["result"] or []
    return [l for l in lists if l["name"].startswith(prefix_name)]


@retry
def get_rules(rule_name_prefix):
    """
    Retrieves all rules whose name starts with the provided prefix.

    Args:
        rule_name_prefix: The prefix to filter rule names.

    Returns:
        A list of matching rules.
    """
    status, response = cloudflare_gateway_request("GET", "/rules")
    rules = response["result"] or []
    return [r for r in rules if r["name"].startswith(rule_name_prefix)]


@rate_limited_request
@retry
def delete_list(list_id):
    """
    Deletes a list by its ID.

    Args:
        list_id: The ID of the list to delete.

    Returns:
        The result of the deletion.
    """
    endpoint = f"/lists/{list_id}"
    status, response = cloudflare_gateway_request("DELETE", endpoint)
    return response["result"]


@retry
def delete_rule(rule_id):
    """
    Deletes a rule by its ID.

    Args:
        rule_id: The ID of the rule to delete.

    Returns:
        The result of the deletion.
    """
    endpoint = f"/rules/{rule_id}"
    status, response = cloudflare_gateway_request("DELETE", endpoint)
    return response["result"]


@retry
def get_list_items(list_id):
    """
    Retrieves items from a list by its ID.

    Args:
        list_id: The ID of the list to retrieve items from.

    Returns:
        A list of item values.
    """
    endpoint = f"/lists/{list_id}/items?limit=1000"
    status, response = cloudflare_gateway_request("GET", endpoint)
    items = response["result"] or []
    return [i["value"] for i in items]
