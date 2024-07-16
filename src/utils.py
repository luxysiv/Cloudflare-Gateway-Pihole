import re
import hashlib

def split_domain_list(domains, chunk_size):
    for i in range(0, len(domains), chunk_size):
        yield domains[i:i + chunk_size]

def safe_sort_key(list_item):
    match = re.search(r'\d+', list_item["name"])
    return int(match.group()) if match else float('inf')

def hash_list(list_items):
    hash_object = hashlib.sha256()
    for item in sorted(list_items):
        hash_object.update(item.encode('utf-8'))
    return hash_object.hexdigest()
