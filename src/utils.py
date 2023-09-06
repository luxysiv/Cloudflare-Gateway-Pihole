import logging
import requests

from typing import List, Set
from src import cloudflare

class App:
    def __init__(self, adlist_name: str, adlist_urls: List[str],whitelist_urls: List[str]):
        self.adlist_name = adlist_name
        self.adlist_urls = adlist_urls
        self.whitelist_urls = whitelist_urls
        self.name_prefix = f"[AdBlock-{adlist_name}]"

    def run(self):
        file_content = ""
        white_content = ""
        for url in self.adlist_urls:
            file_content += self.download_file(url) 
        for url in self.whitelist_urls:
            white_content += self.download_file(url)
        white_domains = self.whitelist_handing(white_content)
        domains = self.convert_to_domain_list(file_content, white_domains)
        
        # check if the list is already in Cloudflare
        cf_lists = cloudflare.get_lists(self.name_prefix)

        logging.info(f"Number of lists in Cloudflare: {len(cf_lists)}")

        # compare the lists size
        if len(domains) == sum([l["count"] for l in cf_lists]):
            logging.warning("Lists are the same size, skipping")
            return

        # Delete existing policy created by script
        policy_prefix = f"{self.name_prefix} Block Ads"
        deleted_policies = cloudflare.delete_gateway_policy(policy_prefix)
        logging.info(f"Deleted {deleted_policies} gateway policies")

        # delete the lists
        for l in cf_lists:
            logging.info(f"Deleting list {l['name']} - ID:{l['id']} ")
            cloudflare.delete_list(l["name"], l["id"])

        cf_lists = []

        # chunk the domains into lists of 1000 and create them
        for chunk in self.chunk_list(domains, 1000):
            list_name = f"{self.name_prefix} {len(cf_lists) + 1}"
            logging.info(f"Creating list {list_name}")
            _list = cloudflare.create_list(list_name, chunk)
            cf_lists.append(_list)

        # get the gateway policies
        cf_policies = cloudflare.get_firewall_policies(self.name_prefix)

        logging.info(f"Number of policies in Cloudflare: {len(cf_policies)}")

        # setup the gateway policy
        if len(cf_policies) == 0:
            logging.info("Creating firewall policy")
            cf_policies = cloudflare.create_gateway_policy(
                f"{self.name_prefix} Block Ads", [l["id"] for l in cf_lists]
            )

        elif len(cf_policies) != 1:
            logging.error("More than one firewall policy found")
            raise Exception("More than one firewall policy found")

        else:
            logging.info("Updating firewall policy")
            cloudflare.update_gateway_policy(
                f"{self.name_prefix} Block Ads", cf_policies[0]["id"], [l["id"] for l in cf_lists]
            )

        logging.info("Done")
        
    def download_file(self, url: str):
        logging.info(f"Downloading file from {url}")
        r = requests.get(url, allow_redirects=True)
        logging.info(f"File size: {len(r.content)}")
        return r.content.decode("utf-8")

    def convert_to_domain_list(self, file_content: str, white_domains: Set[str]):
        
        # check if the file is a hosts file or a list of domain
        is_hosts_file = False
        for ip in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
            if ip in file_content:
                is_hosts_file = True
                break
    
        domains = set()
    
        for line in file_content.splitlines():
            
            # Fix StevenBlack hosts
            skip_lines = [
                "0.0.0.0 0.0.0.0",
                "127.0.0.1 localhost",
                "127.0.0.1 localhost.localdomain",
                "127.0.0.1 local"
            ]
            if line in skip_lines:
                continue
              
              
            # skip comments and empty lines
            if line.startswith("#") or line == "":
                continue

            if is_hosts_file:
                # remove the ip address and the trailing newline
                parts = line.split()
                if len(parts) < 2:
                    continue
                domain = parts[1].rstrip()
                # skip the localhost entry
                if domain == "localhost":
                    continue
            else:
                domain = line.rstrip()

            domains.add(domain.encode('idna').decode())
    
        # remove duplicate line
        logging.info(f"Number of block domains: {len(domains)}")

        # white domains 
        domains = sorted(list(domains - white_domains))
        logging.info(f"Number of final domains: {len(domains)}")
    
        return domains
        
    def whitelist_handing(self, white_content:str):
        white_domains = set()
        for line in white_content.splitlines():
            if line.startswith("#") or line == "":
                continue
            white_domain = line.rstrip()

            white_domains.add(white_domain.encode('idna').decode())

        logging.info(f"Number of white domains: {len(white_domains)}")

        return white_domains

    def chunk_list(self, _list: List[str], n: int):
        for i in range(0, len(_list), n):
            yield _list[i : i + n]

    def delete(self):
        # Delete gateway policy
        policy_prefix = f"{self.name_prefix} Block Ads"
        deleted_policies = cloudflare.delete_gateway_policy(policy_prefix)
        logging.info(f"Deleted {deleted_policies} gateway policies")

        # Delete lists
        cf_lists = cloudflare.get_lists(self.name_prefix)
        for l in cf_lists:
            logging.info(f"Deleting list {l['name']} - ID:{l['id']} ")
            cloudflare.delete_list(l["name"], l["id"])

        logging.info("Deletion completed")
