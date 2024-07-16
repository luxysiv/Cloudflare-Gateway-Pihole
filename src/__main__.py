import argparse
from src.domains import DomainConverter
from src.cloudflare import (
    get_lists, get_rules, create_list, update_list, create_rule, 
    update_rule, delete_list, delete_rule, get_list_items
)
from src import utils, info, silent_error,PREFIX

class CloudflareManager:
    def __init__(self, prefix_name):
        self.prefix_name = f"[{prefix_name}]"
        self.rule_name = f"[{prefix_name}] Block Ads"

    def update_resources(self):
        domains_to_block = DomainConverter().process_urls()
        current_lists = get_lists(self.prefix_name)
        current_rules = get_rules(self.rule_name)

        chunked_domains = list(utils.split_domain_list(domains_to_block, 1000))
        list_ids = []

        for index, chunk in enumerate(chunked_domains, start=1):
            list_name = f"{self.prefix_name} - {index:03d}"
            
            existing_list = next((lst for lst in current_lists if lst["name"] == list_name), None)

            if existing_list:
                current_items = get_list_items(existing_list["id"])
                current_values = {item["value"] for item in current_items}

                if utils.hash_list(current_values) == utils.hash_list(chunk):
                    silent_error(f"Skipping list update: {list_name}")
                else:
                    remove_items = list(current_values - set(chunk))
                    append_items = list(set(chunk) - current_values)
                    update_list(existing_list["id"], remove_items, append_items)
                    info(f"Updated list: {list_name}")
                list_ids.append(existing_list["id"])
            else:
                list_id = create_list(list_name, chunk)
                info(f"Created list: {list_name}")
                list_ids.append(list_id)

        rule_exists = next((rule for rule in current_rules if rule["name"] == self.rule_name), None)

        if rule_exists:
            rule_id = rule_exists["id"]
            info(f"Rule '{self.rule_name}' already exists. Updating...")
            update_rule(self.rule_name, rule_id, list_ids)
        else:
            info(f"Rule '{self.rule_name}' does not exist. Creating...")
            create_rule(self.rule_name, list_ids)

        info(f"Updated rule: {self.rule_name}")

        # Delete excess lists
        excess_lists = [lst for lst in current_lists if lst["id"] not in list_ids]
        for lst in excess_lists:
            delete_list(lst["id"])
            info(f"Deleted excess list: {lst['name']}")

    def delete_resources(self):
        current_lists = get_lists(self.prefix_name)
        current_rules = get_rules(self.rule_name)
        current_lists.sort(key=utils.safe_sort_key)
        

        info(f"Deleting rule '{self.rule_name}' and associated lists.")

        # Delete rules with the name rule_name
        for rule in current_rules:
            delete_rule(rule["id"])
            info(f"Deleted rule: {rule['name']}")

        # Delete lists with names that include prefix_name
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
