import asyncio
import logging
from configparser import ConfigParser

from src.colorlogs import ColoredLevelFormatter
from src.utils import App

# Configure logging
logging.getLogger().setLevel(logging.INFO)
formatter = ColoredLevelFormatter("%(levelname)s: %(message)s")
console = logging.StreamHandler()
console.setFormatter(ColoredLevelFormatter("%(levelname)s: %(message)s"))
logger = logging.getLogger()
logger.addHandler(console)

def read_urls_from_file(filename):
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

def main():
    adlist_urls = read_urls_from_file("adlist.ini")
    whitelist_urls = read_urls_from_file("whitelist.ini")
    adlist_name = "DNS-Filters"
    app = App(adlist_name, adlist_urls, whitelist_urls)
    # await app.delete()  # Leave script
    asyncio.run(app.run())

if __name__ == "__main__":
    main()
