import re
from src import ids_pattern, info, error, silent_error
from concurrent.futures import ThreadPoolExecutor
from src.domains import DomainConverter
from src.cloudflare import (
    get_lists, get_rules, create_list, update_list, create_rule, 
    update_rule, delete_list, delete_rule, get_list_items
)

class CloudflareManager:
    def __init__(self, prefix):
        self.list_name = f"[{prefix}]"
        self.rule_name = f"[{prefix}] Block Ads"

    def update_resources(self):
        domains_to_block = DomainConverter().process_urls()
        if len(domains_to_block) > 300000:
            error("The domains list exceeds Cloudflare Gateway's free limit of 300,000 domains.")
        
        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)

        # Mapping list_id to current domains in that list
        list_id_to_domains = {}
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(get_list_items, lst["id"]): lst["id"] for lst in current_lists}
            for future in futures:
                lst_id = futures[future]
                items = future.result()
                list_id_to_domains[lst_id] = set(items)

        # Mapping domain to its current list_id
        domain_to_list_id = {domain: lst_id for lst_id, domains in list_id_to_domains.items() for domain in domains}

        # Exit if no change 
        if set(domains_to_block) == set(domain_to_list_id.keys()):
            silent_error(f"Nothing to change")
            return
        
        # Calculate remaining domains 
        remaining_domains = set(domains_to_block) - set(domain_to_list_id.keys())

        # Create a dictionary for list names to keep track of missing indexes
        list_name_to_id = {lst["name"]: lst["id"] for lst in current_lists}
        existing_indexes = sorted([int(name.split('-')[-1]) for name in list_name_to_id.keys()])

        # Determine the missing indexes
        all_indexes = set(range(1, max(existing_indexes + [(len(domains_to_block) + 999) // 1000]) + 1))
        missing_indexes = sorted(all_indexes - set(existing_indexes))

        # Process current lists and fill them with remaining domains
        new_list_ids = []
        for i in sorted(existing_indexes + missing_indexes):
            list_name = f"{self.list_name} - {i:03d}"
            if list_name in list_name_to_id:
                list_id = list_name_to_id[list_name]
                current_values = list_id_to_domains[list_id]
                remove_items = current_values - set(domains_to_block)
                chunk = current_values - remove_items

                new_items = []
                if len(chunk) < 1000:
                    needed_items = 1000 - len(chunk)
                    new_items = list(remaining_domains)[:needed_items]
                    chunk.update(new_items)
                    remaining_domains.difference_update(new_items)

                if remove_items or new_items:
                    update_list(list_id, remove_items, new_items)
                    info(f"Updated list: {list_name}")
                
                new_list_ids.append(list_id)
            else:
                # Create new lists for remaining domains
                if remaining_domains:
                    needed_items = min(1000, len(remaining_domains))
                    new_items = list(remaining_domains)[:needed_items]
                    remaining_domains.difference_update(new_items)
                    lst = create_list(list_name, new_items)
                    info(f"Created list: {lst['name']}")
                    new_list_ids.append(lst["id"])

        # Update the rule with the new list IDs
        cgp_rule = next((rule for rule in current_rules if rule["name"] == self.rule_name), None)
        cgp_list_ids = extract_list_ids(cgp_rule)

        if cgp_rule:
            if set(new_list_ids) != cgp_list_ids:
                update_rule(self.rule_name, cgp_rule["id"], new_list_ids)
                info(f"Updated rule {cgp_rule['name']}")
        else:
            rule = create_rule(self.rule_name, new_list_ids)
            info(f"Created rule {rule['name']}")
            

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
