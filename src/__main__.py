import argparse
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

    def update_resources(self):
        domains_to_block = set(DomainConverter().process_urls())
        if len(domains_to_block) > 300000:
            error("The domains list exceeds Cloudflare Gateway's free limit of 300,000 domains.")
            return

        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)

        list_name_to_id = {lst["name"]: lst["id"] for lst in current_lists}
        current_domains = {lst["id"]: set(get_list_items(lst["id"])) for lst in current_lists}
        
        # Collect all domains currently in the lists
        all_current_domains = set(domain for domains in current_domains.values() for domain in domains)

        # Determine domains to add and to remove
        domains_to_add = domains_to_block - all_current_domains
        domains_to_remove = all_current_domains - domains_to_block

        # If there are no changes needed, skip further processing
        if not domains_to_add and not domains_to_remove:
            info("No changes in domains list, skipping updates.")
            return

        # Distribute domains to add across lists
        list_size = 1000
        num_new_lists = (len(domains_to_add) + list_size - 1) // list_size  # Ceiling division
        new_lists = [
            (f"{self.list_name} - {i+1:03d}", list(domains_to_add)[i*list_size:(i+1)*list_size])
            for i in range(num_new_lists)
        ]

        # Update existing lists or create new ones
        updated_list_ids = []
        for list_name, new_domains in new_lists:
            if list_name in list_name_to_id:
                list_id = list_name_to_id[list_name]
                update_list(list_id, [], new_domains)
                info(f"Updated list: {list_name}")
            else:
                lst = create_list(list_name, new_domains)
                list_id = lst["id"]
                info(f"Created list: {list_name}")
            updated_list_ids.append(list_id)

        # Delete excess lists
        excess_lists = [lst for lst in current_lists if lst["id"] not in updated_list_ids]
        for lst in excess_lists:
            delete_list(lst["id"])
            info(f"Deleted excess list: {lst['name']}")

        # Update or create rule
        cgp_rule = next((rule for rule in current_rules if rule["name"] == self.rule_name), None)
        if cgp_rule:
            update_rule(self.rule_name, cgp_rule["id"], updated_list_ids)
            info(f"Updated rule {cgp_rule['name']}")
        else:
            rule = create_rule(self.rule_name, updated_list_ids)
            info(f"Created rule {rule['name']}")

    def delete_resources(self):
        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)

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
        cloudflare_manager.update_resources()
    elif args.action == "leave":
        cloudflare_manager.delete_resources()
    else:
        error("Invalid action. Please choose either 'run' or 'leave'.")

if __name__ == "__main__":
    main()
