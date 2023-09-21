import asyncio
import logging
from configparser import ConfigParser

from src.colorlogs import ColoredLevelFormatter
from src.utils import App

logging.getLogger().setLevel(logging.INFO)
formatter = ColoredLevelFormatter("%(levelname)s: %(message)s")
console = logging.StreamHandler()
console.setFormatter(ColoredLevelFormatter("%(levelname)s: %(message)s"))
logger = logging.getLogger()
logger.addHandler(console)


def ad_list():
    adlist_urls = []
    config = ConfigParser()
    
    try:
        config.read("adlist.ini")
        for section in config.sections():
            for key in config.options(section):

                if not key.startswith("#"):
                    adlist_urls.append(config.get(section, key))
    except Exception:
        with open("adlist.ini", "r") as file:
            adlist_urls = [url.strip() for url in file if not url.startswith("#") and url.strip()]

    return adlist_urls


def white_list():
    whitelist_urls = []
    config = ConfigParser()
    
    try:
        config.read("whitelist.ini")
        for section in config.sections():
            for key in config.options(section):

                if not key.startswith("#"):
                    whitelist_urls.append(config.get(section, key))
    except Exception:
        with open("whitelist.ini", "r") as file:
            whitelist_urls = [url.strip() for url in file if not url.startswith("#") and url.strip()]

    return whitelist_urls

async def main():
    adlist_urls = ad_list()
    whitelist_urls = white_list()
    adlist_name = "DNS-Filters"
    app = App(adlist_name, adlist_urls, whitelist_urls)
    # await app.delete()  # Leave script
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
