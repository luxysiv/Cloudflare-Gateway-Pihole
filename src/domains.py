import os
import requests
from configparser import ConfigParser
from src import (
    info,
    convert
)

class DomainConverter:
    def __init__(self):
        self.env_file_map = {
            "ADLIST_URLS": "./lists/adlist.ini",
            "WHITELIST_URLS": "./lists/whitelist.ini"
        }
        self.adlist_urls = self.read_urls("ADLIST_URLS")
        self.whitelist_urls = self.read_urls("WHITELIST_URLS")

    def read_urls_from_file(self, filename):
        urls = []
        try:
            config = ConfigParser()
            config.read(filename)
            for section in config.sections():
                for key in config.options(section):
                    if not key.startswith("#"):
                        urls.append(config.get(section, key))
        except Exception:
            with open(filename, "r") as file:
                urls = [
                    url.strip() for url in file if not url.startswith("#") and url.strip()
                ]
        return urls
    
    def read_urls_from_env(self, env_var):
        urls = os.getenv(env_var, "")
        return [
            url.strip() for url in urls.split() if url.strip()
        ]

    def read_urls(self, env_var):
        file_path = self.env_file_map[env_var]
        urls = self.read_urls_from_file(file_path)
        urls += self.read_urls_from_env(env_var)
        return urls

    def download_file(self, url):
        r = requests.get(url, allow_redirects=True)
        info(f"Downloaded file from {url} File size: {len(r.content)}")
        return r.text
        
    def process_urls(self):
        block_content = ""
        white_content = ""
        for url in self.adlist_urls:
            block_content += self.download_file(url)
        for url in self.whitelist_urls:
            white_content += self.download_file(url)
            
        with open("./lists/dynamic_blacklist.txt", "r") as black_file:
            blacklist_content = black_file.read()
            block_content += blacklist_content
        
        with open("./lists/dynamic_whitelist.txt", "r") as white_file:
            whitelist_content = white_file.read()
            white_content += whitelist_content
        
        domains = convert.convert_to_domain_list(block_content, white_content)
        return domains
