import argparse
from src.domains import DomainConverter
from src import utils, info, silent_error, error, PREFIX
from src.cloudflare import (
    create_list, update_list, create_rule, 
    update_rule, delete_list, delete_rule
)


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

        # Mapping list_id to current domains in that list
        list_id_to_domains = {}
        for lst in current_lists:
            items = utils.get_list_items_cached(self.cache, lst["id"])
            list_id_to_domains[lst["id"]] = set(items)

        # Mapping domain to its current list_id
        domain_to_list_id = {domain: lst_id for lst_id, domains in list_id_to_domains.items() for domain in domains}

        # Calculate remaining domains 
        remaining_domains = set(domains_to_block) - set(domain_to_list_id.keys())

        # Create a dictionary for list names to keep track of missing indexes
        list_name_to_id = {lst["name"]: lst["id"] for lst in current_lists}
        existing_indexes = sorted([int(name.split('-')[-1]) for name in list_name_to_id.keys()])

        # Determine the needed indexes
        all_indexes = set(range(1, max(existing_indexes + [(len(domains_to_block) + 999) // 1000]) + 1))
        
        # Process current lists and fill them with remaining domains
        new_list_ids = []
        for i in all_indexes:
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
                    info(
                        f"Updated list: {list_name} "
                        f"| Added {len(new_items)} domains,"
                        f"Removed {len(remove_items)} domains "
                        f"| Total domains in list: {len(chunk)}"
                    )
                    self.cache["mapping"][list_id] = list(chunk)
                else:
                    silent_error(
                        f"Skipped update list: {list_name} "
                        f"| Total domains in list: {len(chunk)}"
                    )
                
                new_list_ids.append(list_id)
            else:
                # Create new lists for remaining domains
                if remaining_domains:
                    needed_items = min(1000, len(remaining_domains))
                    new_items = list(remaining_domains)[:needed_items]
                    remaining_domains.difference_update(new_items)
                    lst = create_list(list_name, new_items)
                    info(f"Created list: {lst['name']} with {len(new_items)} domains")
                    self.cache["lists"].append(lst)
                    self.cache["mapping"][lst["id"]] = new_items
                    new_list_ids.append(lst["id"])

        # Update the rule with the new list IDs
        cgp_rule = next((rule for rule in current_rules if rule["name"] == self.rule_name), None)
        cgp_list_ids = utils.extract_list_ids(cgp_rule)

        if cgp_rule:
            if set(new_list_ids) != cgp_list_ids:
                updated_rule = update_rule(self.rule_name, cgp_rule["id"], new_list_ids)
                info(f"Updated rule {updated_rule['name']}")
                self.cache["rules"] = [updated_rule]
            else:
                silent_error(f"Skipping rule update as list IDs are unchanged: {cgp_rule['name']}")
        else:
            rule = create_rule(self.rule_name, new_list_ids)
            info(f"Created rule {rule['name']}")
            self.cache["rules"].append(rule)
        
        utils.save_cache(self.cache)


    def delete_resources(self):
        current_lists = utils.get_current_lists(self.cache, self.list_name)
        current_rules = utils.get_current_rules(self.cache, self.rule_name)
        current_lists.sort(key=utils.safe_sort_key)

        # Delete rules with the name rule_name
        for rule in current_rules:
            delete_rule(rule["id"])
            info(f"Deleted rule: {rule['name']}")

            # Clear the rules cache after deletion
            self.cache["rules"] = []
            utils.save_cache(self.cache)

        # Delete lists with names that include prefix
        for lst in current_lists:
            delete_list(lst["id"])
            info(f"Deleted list: {lst['name']}")

            # Remove the deleted list from the cache
            self.cache["lists"] = [item for item in self.cache["lists"] if item["id"] != lst["id"]]

            # Remove the mapping for the deleted list from the cache
            if lst["id"] in self.cache["mapping"]:
                del self.cache["mapping"][lst["id"]]

            # Save updated cache
            utils.save_cache(self.cache)


def main():
    parser = argparse.ArgumentParser(description="Cloudflare Manager Script")
    parser.add_argument("action", choices=["run", "leave"], help="Choose action: run or leave")
    args = parser.parse_args()    
    cloudflare_manager = CloudflareManager(PREFIX)
    
    if args.action == "run":
        cloudflare_manager.update_resources()
        if utils.is_running_in_github_actions():
            utils.delete_cache()
    elif args.action == "leave":
        cloudflare_manager.delete_resources()
    else:
        error("Invalid action. Please choose either 'run' or 'leave'.")

if __name__ == "__main__":
    main()
