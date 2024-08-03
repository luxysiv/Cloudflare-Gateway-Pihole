import argparse
from concurrent.futures import ThreadPoolExecutor
from src.domains import DomainConverter
from src.cloudflare import (
    get_lists, get_rules, create_list, update_list, create_rule, 
    update_rule, delete_list, delete_rule, get_list_items
)
from src import utils, info, error, PREFIX

class CloudflareManager:
    def __init__(self, prefix):
        self.list_name = f"[{prefix}]"
        self.rule_name = f"[{prefix}] Block Ads"

    def fetch_list_items(self, lst_id):
        return lst_id, set(get_list_items(lst_id))

    def update_resources(self):
        domains_to_block = DomainConverter().process_urls()
        if len(domains_to_block) > 300000:
            error("The domains list exceeds Cloudflare Gateway's free limit of 300,000 domains.")
        
        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)

        # Mapping list_id to current domains in that list
        list_id_to_domains = {}
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.fetch_list_items, lst["id"]): lst["id"] for lst in current_lists}
            for future in futures:
                lst_id, items = future.result()
                list_id_to_domains[lst_id] = items

        # Mapping domain to its current list_id
        domain_to_list_id = {domain: lst_id for lst_id, domains in list_id_to_domains.items() for domain in domains}

        # Calculate remaining domains 
        remaining_domains = set(domains_to_block) - set(domain_to_list_id.keys())

        # Create a dictionary for list names to keep track of missing indexes
        list_name_to_id = {lst["name"]: lst["id"] for lst in current_lists}
        existing_indexes = sorted([int(name.split('-')[-1]) for name in list_name_to_id.keys()])

        # Calculate the number of groups needed for remaining domains
        num_groups = (len(remaining_domains) + 999) // 1000  # Round up to ensure full coverage

        # Determine the missing indexes
        all_indexes = set(range(1, max(existing_indexes + [num_groups]) + 1))
        missing_indexes = sorted(all_indexes - set(existing_indexes))

        # Process current lists and fill them with remaining domains
        new_list_ids = []
        for i in existing_indexes + missing_indexes:
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
        cgp_list_ids = utils.extract_list_ids(cgp_rule)

        if cgp_rule:
            if set(new_list_ids) != cgp_list_ids:
                update_rule(self.rule_name, cgp_rule["id"], new_list_ids)
                info(f"Updated rule {cgp_rule['name']}")
        else:
            rule = create_rule(self.rule_name, new_list_ids)
            info(f"Created rule {rule['name']}")

        # Delete excess lists that are no longer needed
        excess_lists = [lst for lst in current_lists if lst["id"] not in new_list_ids]
        for lst in excess_lists:
            delete_list(lst["id"])
            info(f"Deleted excess list: {lst['name']}")

    def delete_resources(self):
        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)
        current_lists.sort(key=utils.safe_sort_key)

        # Delete rules with the name rule_name
        for rule in current_rules:
            delete_rule(rule["id"])
            info(f"Deleted rule: {rule['name']}")

        # Delete lists with names that include prefix
        for lst in current_lists:
            delete_list(lst["id"])
            info(f"Deleted list: {lst['name']}")

def main():
    parser = argparse.ArgumentParser(description="Cloudflare Manager Script")
    parser.add_argument("action", choices=["run", "leave"], help="Choose action: run or leave")
    args = parser.parse_args()    
    cloudflare_manager = CloudflareManager(PREFIX)
    
    if args.action == "run":
        cloudflare_manager.update_resources()
    elif args.action == "leave":
        cloudflare_manager.delete_resources()
    else:
        error("Invalid action. Please choose either 'run' or 'leave'.")

if __name__ == "__main__":
    main()
