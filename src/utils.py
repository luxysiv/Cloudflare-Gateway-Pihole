import re
import hashlib

def split_domain_list(domain_list, list_size):
    return [
        domain_list[i : i + list_size]
        for i in range(0, len(domain_list), list_size)
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

def hash_list(list_items):
    hash_object = hashlib.sha256()
    for item in sorted(list_items):
        hash_object.update(item.encode('utf-8'))
    return hash_object.hexdigest()
