import re
from src import ids_pattern

def split_domain_list(domains, chunk_size):
    for i in range(0, len(domains), chunk_size):
        yield domains[i:i + chunk_size]

def safe_sort_key(list_item):
    match = re.search(r'\d+', list_item["name"])
    return int(match.group()) if match else float('inf')

def extract_list_ids(rule):
        if not rule or not rule.get('traffic'):
            return set()
        return set(ids_pattern.findall(rule['traffic']))
