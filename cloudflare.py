import requests
import os
import dotenv

from typing import List
from dotenv import load_dotenv

load_dotenv()

CF_API_TOKEN = os.getenv("CF_API_TOKEN") or os.environ.get("CF_API_TOKEN")
CF_IDENTIFIER = os.getenv("CF_IDENTIFIER") or os.environ.get("CF_IDENTIFIER")

if not CF_API_TOKEN or not CF_IDENTIFIER:
    raise Exception("Missing Cloudflare credentials")

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {CF_API_TOKEN}"})


def get_lists(name_prefix: str):
    r = session.get(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/lists",
    )

    if r.status_code != 200:
        raise Exception("Failed to get Cloudflare lists")

    lists = r.json()["result"] or []

    return [l for l in lists if l["name"].startswith(name_prefix)]


def create_list(name: str, domains: List[str]):
    r = session.post(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/lists",
        json={
            "name": name,
            "description": "Created by script.",
            "type": "DOMAIN",
            "items": [*map(lambda d: {"value": d}, domains)],
        },
    )

    if r.status_code != 200:
        raise Exception("Failed to create Cloudflare list")

    return r.json()["result"]


def delete_list(name: str, list_id: str):
    r = session.delete(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/lists/{list_id}",
    )

    if r.status_code != 200:
        raise Exception("Failed to delete Cloudflare list")

    return r.json()["result"]


def get_firewall_policies(name_prefix: str):
    r = session.get(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules",
    )

    if r.status_code != 200:
        raise Exception("Failed to get Cloudflare firewall policies")
    lists = r.json()["result"] or []
    return [l for l in lists if l["name"].startswith(name_prefix)]


def create_gateway_policy(name: str, list_ids: List[str]):
    r = session.post(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules",
        json={
            "name": name,
            "description": "Created by script.",
            "action": "block",
            "enabled": True,
            "filters": ["dns"],
            "traffic": "or".join([f"any(dns.domains[*] in ${l})" for l in list_ids]),
            "rule_settings": {
                "block_page_enabled": False,
            },
        },
    )

    if r.status_code != 200:
        raise Exception("Failed to create Cloudflare firewall policy")
    return r.json()["result"]


def update_gateway_policy(name: str, policy_id: str, list_ids: List[str]):
    r = session.put(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules/{policy_id}",
        json={
            "name": name,
            "action": "block",
            "enabled": True,
            "traffic": "or".join([f"any(dns.domains[*] in ${l})" for l in list_ids]),
        },
    )

    if r.status_code != 200:
        raise Exception("Failed to update Cloudflare firewall policy")
    return r.json()["result"]
def delete_gateway_policy(policy_name_prefix: str):
    
    r = session.get(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules",
    )

    if r.status_code != 200:
        raise Exception("Failed to get Cloudflare firewall policies")

    policies = r.json()["result"] or []
    policy_to_delete = next((p for p in policies if p["name"].startswith(policy_name_prefix)), None)

    if not policy_to_delete:
        return 0

    policy_id = policy_to_delete["id"]

    r = session.delete(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules/{policy_id}",
    )

    if r.status_code != 200:
        raise Exception("Failed to delete Cloudflare gateway firewall policy")
    return 1
