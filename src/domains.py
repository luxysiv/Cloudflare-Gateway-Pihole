import requests
from configparser import ConfigParser
from src import (
    info,
    convert
)

class DomainConverter:
    def __init__(self):
        self.adlist_urls = self.read_urls_from_file("./lists/adlist.ini")
        self.whitelist_urls = self.read_urls_from_file("./lists/whitelist.ini")
    
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
                urls = [url.strip() for url in file if not url.startswith("#") and url.strip()]
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
