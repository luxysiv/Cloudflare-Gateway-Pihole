import asyncio
import logging
import re

from libs import aiohttp
from src import cloudflare

replace_pattern = re.compile(
    r"(^([0-9.]+|[0-9a-fA-F:.]+)\s+|^(\|\||@@\|\||\*\.|\*))"
)
domain_pattern = re.compile(
    r"^([a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)*"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?$"
)
ip_pattern = re.compile(
    r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
)

class App:
    def __init__(
        self, adlist_name: str, adlist_urls: list[str], whitelist_urls: list[str]
    ):
        self.adlist_name = adlist_name
        self.adlist_urls = adlist_urls
        self.whitelist_urls = whitelist_urls
        self.name_prefix = f"[AdBlock-{adlist_name}]"

    async def run(self):
        async with aiohttp.ClientSession() as session:
            all_urls = self.adlist_urls + self.whitelist_urls
            download_tasks = [
                self.download_file(session, url) for url in all_urls
            ]
            results = await asyncio.gather(*download_tasks)
            block_content = "".join(results[:len(self.adlist_urls)])
            white_content = "".join(results[len(self.adlist_urls):])
                        
        domains = self.convert_to_domain_list(block_content, white_content)
        
        # check if number of domains exceeds the limit
        if len(domains) == 0:
            logging.warning("No domains found in the adlist file. Exiting script.")
            return 
        
        # stop script if the number of final domains exceeds the limit
        if len(domains) > 300000:
            logging.warning("The number of final domains exceeds the limit. Exiting script.")
            return

        # check if the list is already in Cloudflare
        cf_lists = await cloudflare.get_lists(self.name_prefix)

        logging.info(f"Number of lists in Cloudflare: {len(cf_lists)}")

        # compare the lists size
        if len(domains) == sum([l["count"] for l in cf_lists]):
            logging.warning("Lists are the same size, checking policy")
            cf_policies = await cloudflare.get_firewall_policies(self.name_prefix)

            if len(cf_policies) == 0:
                logging.info("No firewall policy found, creating new policy")
                cf_policies = await cloudflare.create_gateway_policy(
                    f"{self.name_prefix} Block Ads", [l["id"] for l in cf_lists]
                )
            else:
                logging.warning("Firewall policy already exists, exiting script")
                return

            return 

        # Delete existing policy created by script
        policy_prefix = f"{self.name_prefix} Block Ads"
        deleted_policies = await cloudflare.delete_gateway_policy(policy_prefix)
        logging.info(f"Deleted {deleted_policies} gateway policies")

        # Delete old lists on Cloudflare 
        delete_list_tasks = []
        for l in cf_lists:
            logging.info(f"Deleting list {l['name']} - ID:{l['id']} ")
            delete_list_tasks.append(cloudflare.delete_list(l["name"], l["id"]))
        await asyncio.gather(*delete_list_tasks)

        # Start creating new lists and firewall policy concurrently
        create_list_tasks = []
        for i, chunk in enumerate(self.chunk_list(domains, 1000)):
            list_name = f"{self.name_prefix} {i + 1}"
            logging.info(f"Creating list {list_name}")
            create_list_tasks.append(cloudflare.create_list(list_name, chunk))
    
        cf_lists = await asyncio.gather(*create_list_tasks)

        cf_policies = await cloudflare.get_firewall_policies(self.name_prefix)
        logging.info(f"Number of policies in Cloudflare: {len(cf_policies)}")

        # setup the gateway policy
        if len(cf_policies) == 0:
            logging.info("Creating firewall policy")
            cf_policies = await cloudflare.create_gateway_policy(
                policy_prefix, [l["id"] for l in cf_lists]
            )
        elif len(cf_policies) != 1:
            logging.error("More than one firewall policy found")
            raise Exception("More than one firewall policy found")
        else:
            logging.info("Updating firewall policy")
            await cloudflare.update_gateway_policy(
                f"{self.name_prefix} Block Ads",
                cf_policies[0]["id"],
                [l["id"] for l in cf_lists],
            )

        logging.info("Done")

    async def download_file(self, session: aiohttp.ClientSession, url: str):
        async with session.get(url) as response:
            text = await response.text("utf-8")
            logging.info(f"Downloaded file from {url} File size: {len(text)}")
            return text

    def convert_to_domain_list(self, block_content: str, white_content: str):
        # Process the downloaded content to extract domains
        white_domains = set()
        block_domains = set()
        filters_subdomains = set()

        # Process white content 
        for line in white_content.splitlines():
            white_domain = self.convert_domains(line)
            if white_domain:
                white_domains.add(white_domain)

        logging.info(f"Number of white domains: {len(white_domains)}")

        # Process block content 
        for line in block_content.splitlines():
            block_domain = self.convert_domains(line)
            if block_domain:
                parts = block_domain.split(".")
                is_subdomain = False
                for i in range(len(parts) - 1, 0, -1):
                    subdomain = ".".join(parts[i:])
                    if subdomain in filters_subdomains:
                        is_subdomain = True
                        break
                if not is_subdomain:
                    block_domains.add(block_domain)
                    filters_subdomains.add(block_domain)

        logging.info(f"Number of block domains: {len(block_domains)}")

        final_domains = sorted(list(block_domains - white_domains))

        logging.info(f"Number of final domains: {len(final_domains)}")

        return final_domains

    def convert_domains(self, line: str):
        # Convert a line into a valid domain name
        if line.startswith(("#", "!", "/")) or line == "":
            return None

        linex = line.lower().strip().split("#")[0].split("^")[0].replace("\r", "")
        domain = replace_pattern.sub("", linex, count=1)
        try:
            domain = domain.encode("idna").decode("utf-8", "replace")
            if domain_pattern.match(domain) and not ip_pattern.match(domain):
                return domain
        except Exception:
            pass
        return None

    def chunk_list(self, _list: list[str], n: int):
        for i in range(0, len(_list), n):
            yield _list[i : i + n]

    async def delete(self):
        # Delete gateway policy
        policy_prefix = f"{self.name_prefix} Block Ads"
        deleted_policies = await cloudflare.delete_gateway_policy(policy_prefix)
        logging.info(f"Deleted {deleted_policies} gateway policies")

        # Delete lists
        cf_lists = await cloudflare.get_lists(self.name_prefix)
        delete_list_tasks = []
        for l in cf_lists:
            logging.info(f"Deleting list {l['name']} - ID:{l['id']} ")
            delete_list_tasks.append(cloudflare.delete_list(l["name"], l["id"]))
        await asyncio.gather(*delete_list_tasks)
        logging.info("Deletion completed")
