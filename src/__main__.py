import re
import argparse
from src import (
    info, error, silent_error,
    utils, domains, cloudflare, 
    PREFIX, MAX_LISTS, MAX_LIST_SIZE,
)

class CloudflareManager:
    def __init__(self, prefix, max_lists, max_list_size):
        self.prefix = prefix
        self.max_lists = max_lists
        self.max_list_size = max_list_size
        self.adlist_name = f"[{self.prefix}]"
        self.policy_name = f"[{self.prefix}] Block Ads"

    def update_domain_lists(self):
        domain_converter = domains.DomainConverter()
        domain_list = domain_converter.process_urls()
        total_domains = len(domain_list)

        if total_domains == 0:
            silent_error("No domain")
            return

        if total_domains > (self.max_list_size * self.max_lists):
            error(f"The domains list has more than {self.max_list_size * self.max_lists} lines")

        total_required_lists = total_domains // self.max_list_size
        existing_lists = cloudflare.get_current_lists()
        existing_policies = cloudflare.get_current_policies()
        existing_lists.sort(key=utils.safe_sort_key)

        info(f"Total lists on Cloudflare: {len(existing_lists)}")
        total_domains_on_cloudflare = sum([l['count'] for l in existing_lists]) if existing_lists else 0
        info(f"Total domains on Cloudflare: {total_domains_on_cloudflare}")

        prefixed_lists = [
            list_item for list_item in existing_lists if self.prefix in list_item["name"]
        ]

        if total_domains == sum([l['count'] for l in prefixed_lists]):
            silent_error("Same size, skipping")
            return

        if total_required_lists > self.max_lists - (len(existing_lists) - len(prefixed_lists)):
            error(
                f"The number of lists required ({total_required_lists}) is greater than the maximum allowed "
                f"({self.max_lists - (len(existing_lists) - len(prefixed_lists))})"
            )

        chunked_domain_lists = utils.split_domain_list(domain_list, self.max_list_size)
        info(f"Total chunked lists generated: {len(chunked_domain_lists)}")

        used_list_ids = []
        excess_list_ids = []
        existing_indices = [
            int(re.search(r'\d+', list_item["name"]).group())
            for list_item in prefixed_lists
        ]
        missing_indices = utils.get_missing_indices(existing_indices, len(chunked_domain_lists))

        for list_item in prefixed_lists:
            list_index = int(re.search(r'\d+', list_item["name"]).group())
            if list_index - 1 < len(chunked_domain_lists):
                current_list_items = cloudflare.get_list_items(list_item["id"], self.max_list_size)
                current_list_values = [item["value"] for item in current_list_items]
                new_list_values = chunked_domain_lists[list_index - 1]

                if utils.hash_list(new_list_values) == utils.hash_list(current_list_values):
                    info(f"No changes detected for list {list_item['name']}, skipping update")
                else:
                    info(f"Updating list {list_item['name']}")
                    list_items_array = [{"value": domain} for domain in new_list_values]

                    payload = {
                        "append": list_items_array,
                        "remove": current_list_values,
                    }

                    cloudflare.patch_list(list_item["id"], payload)
                used_list_ids.append(list_item["id"])
            else:
                info(f"Marking list {list_item['name']} for deletion")
                excess_list_ids.append(list_item["id"])

        for index in missing_indices:
            if index - 1 < len(chunked_domain_lists):
                formatted_counter = f"{index:03d}"
                info(f"Creating list {self.adlist_name} - {formatted_counter}")

                payload = utils.create_list_payload(
                    f"{self.adlist_name} - {formatted_counter}", chunked_domain_lists[index - 1]
                )

                created_list = cloudflare.create_list(payload)
                used_list_ids.append(created_list["id"])

        policy_id = next(
            (policy["id"] for policy in existing_policies if policy["name"] == self.policy_name), 
            None
        )
        policy_payload = utils.create_policy_json(self.policy_name, used_list_ids)

        if not policy_id:
            info(f"Creating policy {self.policy_name}")
            cloudflare.create_policy(policy_payload)
        else:
            info(f"Updating policy {self.policy_name}")
            cloudflare.update_policy(policy_id, policy_payload)

        for list_id in excess_list_ids:
            list_to_delete = next(
                list_item for list_item in existing_lists if list_item["id"] == list_id
            )
            info(f"Deleting list {list_to_delete['name']}")
            cloudflare.delete_list(list_id)

    def remove_all_resources(self):
        existing_lists = cloudflare.get_current_lists()
        existing_policies = cloudflare.get_current_policies()
        existing_lists.sort(key=utils.safe_sort_key)

        policy_id = next(
            (policy["id"] for policy in existing_policies if policy["name"] == self.policy_name), 
            None
        )
        if policy_id:
            info(f"Deleting policy {self.policy_name}")
            cloudflare.delete_policy(policy_id)

        list_ids_to_delete = [
            list_item['id'] for list_item in existing_lists if self.adlist_name in list_item["name"]
        ]
        for list_id in list_ids_to_delete:
            list_to_delete = next(
                list_item for list_item in existing_lists if list_item["id"] == list_id
            )
            info(f"Deleting list {list_to_delete['name']}")
            cloudflare.delete_list(list_id)

def main():
    parser = argparse.ArgumentParser(description="Cloudflare Manager Script")
    parser.add_argument("action", choices=["run", "leave"], help="Choose action: run or leave")
    args = parser.parse_args()    
    cloudflare_manager = CloudflareManager(PREFIX, MAX_LISTS, MAX_LIST_SIZE)
    
    if args.action == "run":
        cloudflare_manager.update_domain_lists()
    elif args.action == "leave":
        cloudflare_manager.remove_all_resources()
    else:
        error("Invalid action. Please choose either 'run' or 'leave'.")

if __name__ == "__main__":
    main()
