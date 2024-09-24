import argparse
from src.domains import DomainConverter
from src.cloudflare import (
    get_lists, get_rules, create_list, update_list, create_rule, 
    update_rule, delete_list, delete_rule, get_list_items
)
from src import utils, info, error, silent_error, PREFIX

class CloudflareManager:
    """
    Manages Cloudflare resources such as lists and rules for blocking domains.
    """
    def __init__(self, prefix):
        """
        Initializes CloudflareManager with a given prefix.

        Args:
            prefix (str): The prefix used for naming lists and rules.
        """
        self.list_name = f"[{prefix}]"
        self.rule_name = f"[{prefix}] Block Ads"

    def update_resources(self):
        """
        Updates or creates Cloudflare lists and rules for blocking domains.
        If the domain list exceeds the free limit (300,000 domains), an error is raised.
        """
        # Convert URLs into domains to block
        domains_to_block = DomainConverter().process_urls()
        if len(domains_to_block) > 300000:
            error("The domains list exceeds Cloudflare Gateway's free limit of 300,000 domains.")
        
        # Fetch existing lists and rules from Cloudflare
        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)

        # Chunk domains into 1000-size lists to stay within Cloudflare limits
        chunked_domains = list(utils.split_domain_list(domains_to_block, 1000))
        list_ids = []

        for index, chunk in enumerate(chunked_domains, start=1):
            list_name = f"{self.list_name} - {index:03d}"
            # Find existing list with the same name
            cgp_list = next((lst for lst in current_lists if lst["name"] == list_name), None)

            if cgp_list:
                # Get current items in the list and compute changes
                current_values = get_list_items(cgp_list["id"])
                remove_items = set(current_values) - set(chunk)
                append_items = set(chunk) - set(current_values)

                # Update the list only if there are changes
                if not remove_items and not append_items:
                    silent_error(f"Skipping list update: {cgp_list['name']}")
                else:
                    update_list(cgp_list["id"], remove_items, append_items)
                    info(f"Updated list: {cgp_list['name']}")
                list_ids.append(cgp_list["id"])
            else:
                # Create new list if it doesn't exist
                lst = create_list(list_name, chunk)
                info(f"Created list: {lst['name']}")
                list_ids.append(lst["id"])

        # Manage the rule that blocks traffic based on the lists
        cgp_rule = next((rule for rule in current_rules if rule["name"] == self.rule_name), None)
        cgp_list_ids = utils.extract_list_ids(cgp_rule)

        if cgp_rule:
            # Update rule only if list IDs have changed
            if set(list_ids) == cgp_list_ids:
                silent_error(f"Skipping rule update as list IDs are unchanged: {cgp_rule['name']}")
            else:
                update_rule(self.rule_name, cgp_rule["id"], list_ids)
                info(f"Updated rule {cgp_rule['name']}")
        else:
            # Create a new rule if none exists
            rule = create_rule(self.rule_name, list_ids)
            info(f"Created rule {rule['name']}")

        # Delete excess lists that are no longer needed
        excess_lists = [lst for lst in current_lists if lst["id"] not in list_ids]
        for lst in excess_lists:
            delete_list(lst["id"])
            info(f"Deleted excess list: {lst['name']}")

    def delete_resources(self):
        """
        Deletes all Cloudflare lists and rules that match the current prefix.
        """
        # Fetch current lists and rules
        current_lists = get_lists(self.list_name)
        current_rules = get_rules(self.rule_name)
        current_lists.sort(key=utils.safe_sort_key)

        # Delete rules
        for rule in current_rules:
            delete_rule(rule["id"])
            info(f"Deleted rule: {rule['name']}")

        # Delete lists
        for lst in current_lists:
            delete_list(lst["id"])
            info(f"Deleted list: {lst['name']}")

def main():
    """
    Main function to handle command-line arguments and execute actions.
    """
    parser = argparse.ArgumentParser(description="Cloudflare Manager Script")
    parser.add_argument("action", choices=["run", "leave"], help="Choose action: run or leave")
    args = parser.parse_args()

    # Initialize Cloudflare manager with the given prefix
    cloudflare_manager = CloudflareManager(PREFIX)

    # Perform action based on user input
    if args.action == "run":
        cloudflare_manager.update_resources()
    elif args.action == "leave":
        cloudflare_manager.delete_resources()
    else:
        error("Invalid action. Please choose either 'run' or 'leave'.")

if __name__ == "__main__":
    main()
