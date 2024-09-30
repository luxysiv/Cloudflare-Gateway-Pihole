import os
import http.client
from src.requests import retry
from urllib.parse import urlparse, urljoin
from configparser import ConfigParser
from src import info, convert, silent_error

class DomainConverter:
    def __init__(self):
        """
        Initializes the DomainConverter with file mappings for adlist and whitelist URLs.
        """
        self.env_file_map = {
            "ADLIST_URLS": "./lists/adlist.ini",
            "WHITELIST_URLS": "./lists/whitelist.ini",
            "DYNAMIC_BLACKLIST": "./lists/dynamic_blacklist.txt",
            "DYNAMIC_WHITELIST": "./lists/dynamic_whitelist.txt"
        }
        self.adlist_urls = self.read_urls("ADLIST_URLS")
        self.whitelist_urls = self.read_urls("WHITELIST_URLS")

    def read_urls_from_file(self, filename: str) -> list[str]:
        """
        Reads URLs from a configuration file or plain text file.

        Args:
            filename (str): Path to the file containing URLs.

        Returns:
            list[str]: List of URLs read from the file.
        """
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
    
    def read_urls_from_env(self, env_var: str) -> list[str]:
        """
        Reads URLs from an environment variable.

        Args:
            env_var (str): The environment variable name.

        Returns:
            list[str]: List of URLs obtained from the environment variable.
        """
        urls = os.getenv(env_var, "")
        return [
            url.strip() for url in urls.split() if url.strip()
        ]

    def read_urls(self, env_var: str) -> list[str]:
        """
        Reads URLs from a configuration file and an environment variable.

        Args:
            env_var (str): The environment variable name.

        Returns:
            list[str]: Combined list of URLs from file and environment variable.
        """
        file_path = self.env_file_map[env_var]
        urls = self.read_urls_from_file(file_path)
        urls += self.read_urls_from_env(env_var)
        return urls

    @retry
    def download_file(self, url: str) -> str:
        """
        Downloads the content of the given URL.

        Args:
            url (str): The URL to download.

        Returns:
            str: The content of the downloaded file or an empty string on failure.
        """
        parsed_url = urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.netloc) if parsed_url.scheme == "https" else http.client.HTTPConnection(parsed_url.netloc)
    
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
    
        conn.request("GET", parsed_url.path, headers=headers)
        response = conn.getresponse()
    
        # Check if the URL returns 404 and handle it without retrying
        if response.status == 404:
            silent_error(f"URL {url} returned 404. Skipping...")
            return "" 
        
        # Handle HTTP redirects
        while response.status in (301, 302, 303, 307, 308):
            location = response.getheader('Location')
            if not location:
                break
        
            if not urlparse(location).netloc:
                location = urljoin(url, location)
        
            url = location
            parsed_url = urlparse(url)
            conn = http.client.HTTPSConnection(parsed_url.netloc) if parsed_url.scheme == "https" else http.client.HTTPConnection(parsed_url.netloc)
            conn.request("GET", parsed_url.path, headers=headers)
            response = conn.getresponse()
    
        if response.status != 200:
            silent_error(f"Failed to download file from {url}, status code: {response.status}")
            conn.close()
            return ""
    
        data = response.read().decode('utf-8')
        conn.close()
        info(f"Downloaded file from {url} File size: {len(data)}")
        return data
        
    def process_urls(self) -> list[str]:
        """
        Processes the adlist and whitelist URLs to obtain final domain list.

        Returns:
            list[str]: The final list of domains after processing.
        """
        block_content = ""
        white_content = ""
        
        # Download content from adlist and whitelist URLs
        for url in self.adlist_urls:
            block_content += self.download_file(url)
        for url in self.whitelist_urls:
            white_content += self.download_file(url)
        
        # Read dynamic blacklist and whitelist from environment variables or files
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
        
        domains = convert.convert_to_domain_list(block_content, white_content)
        return domains
