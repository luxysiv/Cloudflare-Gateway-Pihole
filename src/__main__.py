import re
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
        if total_lines == 0:
            silent_error("No domain")
            return
        if total_lines > self.max_list_size * self.max_lists:
            error(f"The domains list has more than {self.max_list_size * self.max_lists} lines")
            return

        total_lists = total_lines // self.max_list_size
        if total_lines % self.max_list_size != 0:
            total_lists += 1

        current_lists = cloudflare.get_current_lists() or {"result": []}
        current_lists_result = current_lists.get("result")
        
        if current_lists_result is None:
            current_lists_result = []

        info(f"Total lists on Cloudflare: {len(current_lists_result)}")
        total_domains = sum([l['count'] for l in current_lists_result]) if current_lists_result else 0
        info(f"Total domains on Cloudflare: {total_domains}")
        
        current_policies = cloudflare.get_current_policies() or {"result": []}
        current_policies_result = current_policies.get("result")
        
        if current_policies_result is None:
            current_policies_result = []

        current_lists_count = 0
        current_lists_count_without_prefix = 0

        if current_lists_result:
            current_lists_result.sort(key=utils.safe_sort_key)
            current_lists_count = len(
                [list_item for list_item in current_lists_result if self.prefix in list_item["name"]]
            )
            current_lists_count_without_prefix = len(
                [list_item for list_item in current_lists_result if self.prefix not in list_item["name"]]
            )
            if total_lines == sum([l['count'] for l in current_lists_result]):
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
        missing_indices = []

        if current_lists_count > 0:
            used_list_ids, excess_list_ids, missing_indices = utils.update_lists(current_lists, chunked_lists, self.adlist_name)

        if missing_indices or not used_list_ids:
            used_list_ids += utils.create_lists(chunked_lists, missing_indices, self.adlist_name)
        
        if not used_list_ids:
            used_list_ids = utils.create_lists(chunked_lists, range(1, total_lists + 1), self.adlist_name)

        utils.update_or_create_policy(current_policies, used_list_ids, self.policy_name)

        if excess_list_ids:
            utils.delete_excess_lists(current_lists, excess_list_ids)

    def leave(self):
        current_lists = cloudflare.get_current_lists() or {"result": []}
        current_lists_result = current_lists.get("result")
        
        if current_lists_result is None:
            current_lists_result = []
        
        current_policies = cloudflare.get_current_policies() or {"result": []}
        current_policies_result = current_policies.get("result")
        
        if current_policies_result is None:
            current_policies_result = []

        utils.delete_policy(current_policies, self.policy_name)
        utils.delete_lists(current_lists, self.adlist_name)

if __name__ == "__main__":
    cloudflare_manager = CloudflareManager(PREFIX, MAX_LISTS, MAX_LIST_SIZE)
    cloudflare_manager.run()
    # cloudflare_manager.leave() # Uncomment if you want to leave script
