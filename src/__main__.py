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

    def run(self):
        converter = domains.DomainConverter()
        domain_list = converter.process_urls()
        total_lines = len(domain_list)

        if (total_lines == 0):
            silent_error("No domain")
            return

        if total_lines > (self.max_list_size * self.max_lists):
            error(f"The domains list has more than {self.max_list_size * self.max_lists} lines")
            return

        total_lists = total_lines // self.max_list_size
        current_lists = cloudflare.get_current_lists()["result"] or []
        current_policies = cloudflare.get_current_policies()["result"] or []
        current_lists.sort(key=utils.safe_sort_key)

        info(f"Total lists on Cloudflare: {len(current_lists)}")
        total_domains = sum([l['count'] for l in current_lists]) if current_lists else 0
        info(f"Total domains on Cloudflare: {total_domains}")

        current_lists_with_prefix = [
            list_item for list_item in current_lists if self.prefix in list_item["name"]
        ]
        current_lists_count = len(current_lists_with_prefix)
        current_lists_count_without_prefix = len(current_lists) - current_lists_count

        if total_lines == sum([l['count'] for l in current_lists_with_prefix]):
            silent_error("Same size, skipping")
            return

        if total_lists > self.max_lists - current_lists_count_without_prefix:
            error(
                f"The number of lists required ({total_lists}) is greater than the maximum allowed "
                f"({self.max_lists - current_lists_count_without_prefix})"
            )
            return

        chunked_lists = utils.split_domain_list(domain_list)
        info(f"Total chunked lists generated: {len(chunked_lists)}")

        used_list_ids = []
        excess_list_ids = []
        existing_indices = [
            int(re.search(r'\d+', list_item["name"]).group())
            for list_item in current_lists_with_prefix
            if f"{self.adlist_name}" in list_item["name"]
        ]
        total_lists = len(chunked_lists)
        missing_indices = utils.get_missing_indices(existing_indices, total_lists)

        for list_item in current_lists_with_prefix:
            list_index = int(re.search(r'\d+', list_item["name"]).group())
            if list_index in existing_indices and list_index - 1 < len(chunked_lists):
                list_items = cloudflare.get_list_items(list_item["id"])["result"] or []
                list_items_values = [
                    item["value"] for item in list_items
                ]
                new_list_items = chunked_lists[list_index - 1]

                if utils.hash_list(new_list_items) == utils.hash_list(list_items_values):
                    info(f"No changes detected for list {list_item['name']}, skipping update")
                    used_list_ids.append(list_item["id"])
                else:
                    info(f"Updating list {list_item['name']}")
                    list_items_array = [{"value": domain} for domain in new_list_items]

                    payload = {
                        "append": list_items_array,
                        "remove": list_items_values,
                    }

                    cloudflare.patch_list(list_item["id"], payload)
                    used_list_ids.append(list_item["id"])
            else:
                info(f"Marking list {list_item['name']} for deletion")
                excess_list_ids.append(list_item["id"])

        for index in missing_indices:
            if index - 1 < len(chunked_lists):
                formatted_counter = f"{index:03d}"
                info(f"Creating list {self.adlist_name} - {formatted_counter}")

                payload = utils.create_list_payload(
                    f"{self.adlist_name} - {formatted_counter}", chunked_lists[index - 1]
                )

                created_list = cloudflare.create_list(payload)["result"] or []
                if created_list:
                    used_list_ids.append(created_list["id"])

        policy_id = None
        for policy_item in current_policies:
            if policy_item["name"] == self.policy_name:
                policy_id = policy_item["id"]

        json_data = utils.create_policy_json(
            self.policy_name, used_list_ids
        )

        if not policy_id or policy_id == "null":
            info(f"Creating policy {self.policy_name}")
            cloudflare.create_policy(json_data)
        else:
            info(f"Updating policy {self.policy_name}")
            cloudflare.update_policy(policy_id, json_data)

        if excess_list_ids:
            for list_item in current_lists:
                if list_item["id"] in excess_list_ids:
                    info(f"Deleting list {list_item['name']}")
                    cloudflare.delete_list(list_item["id"])

    def leave(self):
        current_lists = cloudflare.get_current_lists()["result"] or []
        current_policies = cloudflare.get_current_policies()["result"] or []
        current_lists.sort(key=utils.safe_sort_key)
        policy_id = None
        list_ids_to_delete = []

        for policy_item in current_policies:
            if policy_item["name"] == self.policy_name:
                policy_id = policy_item["id"]

        if policy_id:
            info(f"Deleting policy {self.policy_name}")
            cloudflare.delete_policy(policy_id)

        for list_item in current_lists:
            if f"{self.adlist_name}" in list_item["name"]:
                list_ids_to_delete.append(list_item['id'])

        for list_id in list_ids_to_delete:
            list_to_delete = next(
                list_item for list_item in current_lists if list_item["id"] == list_id
            )
            if list_to_delete:
                info(f"Deleting list {list_to_delete['name']}")
                cloudflare.delete_list(list_id)

def main():
    parser = argparse.ArgumentParser(description="Cloudflare Manager Script")
    parser.add_argument("action", choices=["run", "leave"], help="Choose action: run or leave")
    args = parser.parse_args()    
    cloudflare_manager = CloudflareManager(PREFIX, MAX_LISTS, MAX_LIST_SIZE)
    if args.action == "run":
        cloudflare_manager.run()
    elif args.action == "leave":
        cloudflare_manager.leave()
    else:
        error("Invalid action. Please choose either 'python -m src run' or 'python -m src leave'.")

if __name__ == "__main__":
    main()
