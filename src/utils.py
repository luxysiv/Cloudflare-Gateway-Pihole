import re
import time
from src import (
    info,
    cloudflare,
    silent_error,
    MAX_LIST_SIZE,
    RATE_LIMIT_INTERVAL
)

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

rate_limiter = RateLimiter(interval=RATE_LIMIT_INTERVAL)

def split_domain_list(domain_list):
    return [
        domain_list[i : i + MAX_LIST_SIZE]
        for i in range(0, len(domain_list), MAX_LIST_SIZE)
    ]

def create_list_payload(name, chunk_list):
    return {
        "name": name,
        "description": "Ads & Tracking Domains",
        "type": "DOMAIN",
        "items": [{"value": domain} for domain in chunk_list],
    }

def create_policy_json(name, used_list_ids):
    return {
        "name": name,
        "description": "Block Ads & Tracking",
        "action": "block",
        "enabled": True,
        "traffic": "or".join([
            f"any(dns.domains[*] in ${list_id})" 
                for list_id in used_list_ids
        ]),
        "rule_settings": {
            "block_page_enabled": False,
        },
        "filters": ["dns"],
    }

def get_missing_indices(existing_indices, total_lists):
    all_indices = set(range(1, total_lists + 1))
    missing_indices = list(all_indices - set(existing_indices))
    missing_indices.sort()
    return missing_indices

def safe_sort_key(list_item):
    match = re.search(r'\d+', list_item["name"])
    return int(match.group()) if match else float('inf')

def update_lists(current_lists, chunked_lists, adlist_name):
    used_list_ids = []
    excess_list_ids = []

    existing_indices = [
        int(re.search(r'\d+', list_item["name"]).group())
        for list_item in current_lists.get("result", [])
        if f"{adlist_name}" in list_item["name"]
    ]

    total_lists = len(chunked_lists)
    missing_indices = get_missing_indices(existing_indices, total_lists)

    for list_item in current_lists.get("result", []):
        if f"{adlist_name}" in list_item["name"]:
            list_index = int(re.search(r'\d+', list_item["name"]).group())
            if list_index in existing_indices and list_index - 1 < len(chunked_lists):
                info(f"Checking list {list_item['name']} for updates")

                list_items = cloudflare.get_list_items(list_item["id"])
                list_items_values = [
                    item["value"] for item in list_items.get("result", []) if item["value"] is not None
                ]
                new_list_items = chunked_lists[list_index - 1]

                if set(list_items_values) != set(new_list_items):
                    info(f"Updating list {list_item['name']}")
                    list_items_array = [{"value": domain} for domain in new_list_items]

                    payload = {
                        "append": list_items_array,
                        "remove": list_items_values,
                    }

                    cloudflare.patch_list(list_item["id"], payload)
                    used_list_ids.append(list_item["id"])
                    rate_limiter.wait_for_next_request()
                else:
                    info(f"No changes detected for list {list_item['name']}, skipping update")
                    used_list_ids.append(list_item["id"])
                continue 

            info(f"Marking list {list_item['name']} for deletion")
            excess_list_ids.append(list_item["id"])

    return used_list_ids, excess_list_ids, missing_indices

def create_lists(chunked_lists, missing_indices, adlist_name):
    used_list_ids = []

    for index in missing_indices:
        if index - 1 < len(chunked_lists):
            formatted_counter = f"{index:03d}"
            info(f"Creating list {adlist_name} - {formatted_counter}")

            payload = create_list_payload(
                f"{adlist_name} - {formatted_counter}", chunked_lists[index - 1]
            )

            created_list = cloudflare.create_list(payload)
            if created_list:
                used_list_ids.append(created_list.get("result", {}).get("id"))

            rate_limiter.wait_for_next_request()

    return used_list_ids

def update_or_create_policy(current_policies, used_list_ids, policy_name):
    policy_id = None

    for policy_item in current_policies.get("result", []):
        if policy_item["name"] == policy_name:
            policy_id = policy_item["id"]

    json_data = create_policy_json(
        policy_name, used_list_ids
    )

    if not policy_id or policy_id == "null":
        info(f"Creating policy {policy_name}")
        cloudflare.create_policy(json_data)
    else:
        info(f"Updating policy {policy_name}")
        cloudflare.update_policy(policy_id, json_data)
    rate_limiter.wait_for_next_request()

def delete_excess_lists(current_lists, excess_list_ids):
    info("Deleting lists...")
    for list_item in current_lists.get("result", []):
        if list_item["id"] in excess_list_ids:
            info(f"Deleting list {list_item['name']}")
            cloudflare.delete_list(list_item["id"])
            rate_limiter.wait_for_next_request()

def delete_policy(current_policies, policy_name):
    policy_id = None
    for policy_item in current_policies.get("result", []):
        if policy_item["name"] == policy_name:
            policy_id = policy_item["id"]

    if policy_id:
        info(f"Deleting policy {policy_name}")
        cloudflare.delete_policy(policy_id)
        rate_limiter.wait_for_next_request()

def delete_lists(current_lists, adlist_name):
    list_ids_to_delete = []
    if current_lists.get("result"):
        current_lists["result"].sort(key=lambda x: int(x["name"].split("-")[-1].strip()))

        for list_item in current_lists["result"]:
            if f"{adlist_name}" in list_item["name"]:
                list_ids_to_delete.append(list_item['id'])

        for list_id in list_ids_to_delete:
            list_to_delete = next(
                (list_item for list_item in current_lists["result"] if list_item["id"] == list_id), None
            )
            if list_to_delete:
                info(f"Deleting list {list_to_delete['name']}")
                cloudflare.delete_list(list_id)
                rate_limiter.wait_for_next_request()
    else:
        silent_error("No lists to delete")
