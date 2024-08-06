import os
import argparse
from concurrent.futures import ThreadPoolExecutor
from src.domains import DomainConverter
from src.cloudflare import (
    get_lists, get_rules, create_list, update_list, create_rule, 
    update_rule, delete_list, delete_rule, get_list_items
)
from src import utils, info, error, silent_error, PREFIX

class CloudflareManager:
    def __init__(self, prefix):
        self.list_name = f"[{prefix}]"
        self.rule_name = f"[{prefix}] Block Ads"

    def update_resources(self, advanced=False):
        domains_to_block = DomainConverter().process_urls()
        if len(domains_to_block) > 300000:
            error("The domains list exceeds Cloudflare Gateway's free limit of 300,000 domains.")
        
        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)
        used_list_ids = []

        if advanced:
            list_id_to_domains = {}
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(get_list_items, lst["id"]): lst["id"] for lst in current_lists}
                for future in futures:
                    lst_id = futures[future]
                    items = future.result()
                    list_id_to_domains[lst_id] = set(items)

            domain_to_list_id = {domain: lst_id for lst_id, domains in list_id_to_domains.items() for domain in domains}

            remaining_domains = set(domains_to_block) - set(domain_to_list_id.keys())
            list_name_to_id = {lst["name"]: lst["id"] for lst in current_lists}
            existing_indexes = sorted([int(name.split('-')[-1]) for name in list_name_to_id.keys()])

            all_indexes = set(range(1, max(existing_indexes + [(len(domains_to_block) + 999) // 1000]) + 1))
            missing_indexes = sorted(all_indexes - set(existing_indexes))

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
                    
                    used_list_ids.append(list_id)
                else:
                    if remaining_domains:
                        needed_items = min(1000, len(remaining_domains))
                        new_items = list(remaining_domains)[:needed_items]
                        remaining_domains.difference_update(new_items)
                        lst = create_list(list_name, new_items)
                        info(f"Created list: {lst['name']}")
                        used_list_ids.append(lst["id"])
        else:
            chunked_domains = list(utils.split_domain_list(domains_to_block, 1000))

            for index, chunk in enumerate(chunked_domains, start=1):
                list_name = f"{self.list_name} - {index:03d}"
                
                cgp_list = next((lst for lst in current_lists if lst["name"] == list_name), None)

                if cgp_list:
                    current_values = get_list_items(cgp_list["id"])
                    remove_items = set(current_values) - set(chunk)
                    append_items = set(chunk) - set(current_values)

                    if not remove_items and not append_items:
                        silent_error(f"Skipping list update: {cgp_list['name']}")
                    else:
                        update_list(cgp_list["id"], remove_items, append_items)
                        info(f"Updated list: {cgp_list['name']}")
                    used_list_ids.append(cgp_list["id"])
                else:
                    lst = create_list(list_name, chunk)
                    info(f"Created list: {lst['name']}")
                    used_list_ids.append(lst["id"])

        cgp_rule = next((rule for rule in current_rules if rule["name"] == self.rule_name), None)
        cgp_list_ids = utils.extract_list_ids(cgp_rule)

        if cgp_rule:
            if set(used_list_ids) != cgp_list_ids:
                update_rule(self.rule_name, cgp_rule["id"], used_list_ids)
                info(f"Updated rule {cgp_rule['name']}")
        else:
            rule = create_rule(self.rule_name, used_list_ids)
            info(f"Created rule {rule['name']}")

        if not advanced:
            excess_lists = [lst for lst in current_lists if lst["id"] not in used_list_ids]
            for lst in excess_lists:
                delete_list(lst["id"])
                info(f"Deleted excess list: {lst['name']}")
    
    def delete_resources(self):
        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)
        current_lists.sort(key=utils.safe_sort_key)

        for rule in current_rules:
            delete_rule(rule["id"])
            info(f"Deleted rule: {rule['name']}")

        for lst in current_lists:
            delete_list(lst["id"])
            info(f"Deleted list: {lst['name']}")

def main():
    parser = argparse.ArgumentParser(description="Cloudflare Manager Script")
    parser.add_argument("action", choices=["run", "leave"], help="Choose action: run or leave")
    args = parser.parse_args()
    
    cloudflare_manager = CloudflareManager(PREFIX)
    
    if args.action == "run":
        mode = os.getenv('MODE', 'NORMAL')
        advanced = mode == 'ADVANCED'
        cloudflare_manager.update_resources(advanced)
    elif args.action == "leave":
        cloudflare_manager.delete_resources()
    else:
        error("Invalid action. Please choose either 'run' or 'leave'.")

if __name__ == "__main__":
    main()
