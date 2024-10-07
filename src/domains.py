import os
import http.client
from urllib.parse import urlparse, urljoin
from configparser import ConfigParser
from src import info, convert, silent_error, error
from src.requests import retry, retry_config, RateLimitException, HTTPException

# Define the DomainConverter class for processing URL lists
class DomainConverter:
    def __init__(self):
        # Map of environment variables to file paths
        self.env_file_map = {
            "ADLIST_URLS": "./lists/adlist.ini",
            "WHITELIST_URLS": "./lists/whitelist.ini",
            "DYNAMIC_BLACKLIST": "./lists/dynamic_blacklist.txt",
            "DYNAMIC_WHITELIST": "./lists/dynamic_whitelist.txt"
        }
        # Read adlist and whitelist URLs from environment and files
        self.adlist_urls = self.read_urls("ADLIST_URLS")
        self.whitelist_urls = self.read_urls("WHITELIST_URLS")

    def read_urls_from_file(self, filename):
        urls = []
        try:
            # Try reading as an INI file
            config = ConfigParser()
            config.read(filename)
            for section in config.sections():
                for key in config.options(section):
                    if not key.startswith("#"):
                        urls.append(config.get(section, key))
        except Exception:
            # Fallback to read as a plain text file
            with open(filename, "r") as file:
                urls = [
                    url.strip() for url in file if not url.startswith("#") and url.strip()
                ]
        return urls
    
    def read_urls_from_env(self, env_var):
        urls = os.getenv(env_var, "")
        return [url.strip() for url in urls.split() if url.strip()]

    def read_urls(self, env_var):
        file_path = self.env_file_map[env_var]
        urls = self.read_urls_from_file(file_path)
        urls += self.read_urls_from_env(env_var)
        return urls

    @retry(**retry_config)
    def download_file(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(parsed_url.netloc)
        else:
            conn = http.client.HTTPConnection(parsed_url.netloc)
    
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
    
        conn.request("GET", parsed_url.path, headers=headers)
        response = conn.getresponse()
    
        # Handle redirection responses
        while response.status in (301, 302, 303, 307, 308):
            location = response.getheader('Location')
            if not location:
                break
            # Construct new absolute URL if relative path is returned
            if not urlparse(location).netloc:
                location = urljoin(url, location)
        
            url = location
            parsed_url = urlparse(url)
        
            # Create new connection based on the new URL scheme
            if parsed_url.scheme == "https":
                conn = http.client.HTTPSConnection(parsed_url.netloc)
            else:
                conn = http.client.HTTPConnection(parsed_url.netloc)
        
            conn.request("GET", parsed_url.path, headers=headers)
            response = conn.getresponse()
    
        # Raise error for non-200 status codes
        if response.status != 200:
            error_message = f"Failed to download file from {url}, status code: {response.status}"
            silent_error(error_message)
            conn.close()
            if response.status == 429:
                raise RateLimitException(error_message)
            else:
                raise HTTPException(error_message)

        # Read response data and close the connection
        data = response.read().decode('utf-8')
        conn.close()
        info(f"Downloaded file from {url}. File size: {len(data)}")
        return data

    def process_urls(self):
        block_content = ""
        white_content = ""
        for url in self.adlist_urls:
            block_content += self.download_file(url)
        for url in self.whitelist_urls:
            white_content += self.download_file(url)
        
        # Read additional dynamic lists
        dynamic_blacklist = os.getenv("DYNAMIC_BLACKLIST", "")
        dynamic_whitelist = os.getenv("DYNAMIC_WHITELIST", "")
        
        if dynamic_blacklist:
            block_content += dynamic_blacklist
        else:
            with open(self.env_file_map["DYNAMIC_BLACKLIST"], "r") as black_file:
                block_content += black_file.read()
        
        if dynamic_whitelist:
            white_content += dynamic_whitelist
        else:
            with open(self.env_file_map["DYNAMIC_WHITELIST"], "r") as white_file:
                white_content += white_file.read()
        
        # Convert the collected content into a domain list
        domains = convert.convert_to_domain_list(block_content, white_content)
        return domains
