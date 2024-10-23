import os
import argparse
from src.domains import DomainConverter
from src.cloudflare import (
    create_list, update_list, create_rule, 
    update_rule, delete_list, delete_rule
)
from src import utils, info, error, silent_error, PREFIX

class CloudflareManager:
    def __init__(self, prefix):
        self.list_name = f"[{prefix}]"
        self.rule_name = f"[{prefix}] Block Ads"
        self.cache = utils.load_cache()

    def update_resources(self):
        domains_to_block = DomainConverter().process_urls()
        if len(domains_to_block) > 300000:
            error("The domains list exceeds Cloudflare Gateway's free limit of 300,000 domains.")
        
        current_lists = utils.get_current_lists(self.cache, self.list_name)
        current_rules = utils.get_current_rules(self.cache, self.rule_name)

        chunked_domains = list(utils.split_domain_list(domains_to_block, 1000))
        list_ids = []

        for index, chunk in enumerate(chunked_domains, start=1):
            list_name = f"{self.list_name} - {index:03d}"
            
            cgp_list = next((lst for lst in current_lists if lst["name"] == list_name), None)

            if cgp_list:
                current_values = utils.get_list_items_cached(self.cache, cgp_list["id"])
                remove_items = set(current_values) - set(chunk)
                append_items = set(chunk) - set(current_values)

                if not remove_items and not append_items:
                    silent_error(f"Skipping list update: {cgp_list['name']}")
                else:
                    update_list(cgp_list["id"], remove_items, append_items)
                    info(f"Updated list: {cgp_list['name']}")
                list_ids.append(cgp_list["id"])
            
                self.cache["mapping"][cgp_list["id"]] = chunk
            else:
                lst = create_list(list_name, chunk)
                info(f"Created list: {lst['name']}")
                list_ids.append(lst["id"])

                self.cache["lists"].append(lst)
                self.cache["mapping"][lst["id"]] = chunk

        utils.save_cache(self.cache)

        # Extract existing list IDs from current_rules for comparison
        cgp_rule = next((rule for rule in current_rules if rule["name"] == self.rule_name), None)
        cgp_list_ids = utils.extract_list_ids(cgp_rule)

        if cgp_rule:
            if set(list_ids) == cgp_list_ids:
                silent_error(f"Skipping rule update as list IDs are unchanged: {cgp_rule['name']}")
            else:
                rule = update_rule(self.rule_name, cgp_rule["id"], list_ids)
                info(f"Updated rule {cgp_rule['name']}")
                self.cache["rules"] = [rule]
        else:
            rule = create_rule(self.rule_name, list_ids)
            info(f"Created rule {rule['name']}")
            self.cache["rules"].append(rule)

        # Delete excess lists
        excess_lists = [lst for lst in current_lists if lst["id"] not in list_ids]
        for lst in excess_lists:
            delete_list(lst["id"])
            info(f"Deleted excess list: {lst['name']}")
            self.cache["lists"] = [item for item in self.cache["lists"] if item["id"] != lst["id"]]
            if lst["id"] in self.cache["mapping"]:
                del self.cache["mapping"][lst["id"]]

        utils.save_cache(self.cache)

    def delete_resources(self):
        current_lists = utils.get_current_lists(self.cache, self.list_name)
        current_rules = utils.get_current_rules(self.cache, self.rule_name)
        current_lists.sort(key=utils.safe_sort_key)

        # Delete rules with the name rule_name
        for rule in current_rules:
            delete_rule(rule["id"])
            info(f"Deleted rule: {rule['name']}")

        # Delete lists with names that include prefix
        for lst in current_lists:
            delete_list(lst["id"])
            info(f"Deleted list: {lst['name']}")
            self.cache["lists"] = [item for item in self.cache["lists"] if item["id"] != lst["id"]]
            if lst["id"] in self.cache["mapping"]:
                del self.cache["mapping"][lst["id"]]
            self.cache["rules"] = []
            utils.save_cache(self.cache)

def is_running_in_github_actions():
    return os.getenv('GITHUB_ACTIONS') == 'true'

def main():
    parser = argparse.ArgumentParser(description="Cloudflare Manager Script")
    parser.add_argument("action", choices=["run", "leave"], help="Choose action: run or leave")
    args = parser.parse_args()    
    cloudflare_manager = CloudflareManager(PREFIX)
    
    if args.action == "run":
        cloudflare_manager.update_resources()
        if is_running_in_github_actions():
            utils.delete_cache()
    elif args.action == "leave":
        cloudflare_manager.delete_resources()
    else:
        error("Invalid action. Please choose either 'run' or 'leave'.")

if __name__ == "__main__":
    main()
