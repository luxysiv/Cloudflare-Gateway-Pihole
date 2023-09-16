import asyncio
import logging
import uvloop
from configparser import ConfigParser

from src.colorlogs import ColoredLevelFormatter
from src.utils import App

logging.getLogger().setLevel(logging.INFO)
formatter = ColoredLevelFormatter("%(levelname)s: %(message)s")
console = logging.StreamHandler()
console.setFormatter(ColoredLevelFormatter("%(levelname)s: %(message)s"))
logger = logging.getLogger()
logger.addHandler(console)


def read_lists():
    adlist_urls = []
    config = ConfigParser()
    
    try:
        config.read("lists.ini")
        for section in config.sections():
            for key in config.options(section):

                if not key.startswith("#"):
                    adlist_urls.append(config.get(section, key))
    except Exception:
        with open("lists.ini", "r") as file:
            adlist_urls = [
                url.strip() for url in file if not url.startswith("#") and url.strip()
            ]

    return adlist_urls


def white_lists():
    whitelist_urls = []
    config = ConfigParser()
    
    try:
        config.read("whitelists.ini")
        for section in config.sections():
            for key in config.options(section):

                if not key.startswith("#"):
                    whitelist_urls.append(config.get(section, key))
    except Exception:
        with open("whitelists.ini", "r") as file:
            whitelist_urls = [
                url.strip() for url in file if not url.startswith("#") and url.strip()
            ]

    return whitelist_urls

async def main():
    adlist_urls = read_lists()
    whitelist_urls = white_lists()
    adlist_name = "DNS-Filters"
    app = App(adlist_name, adlist_urls, whitelist_urls)
    success = False  
    for _ in range(3):
        try:
            # await app.delete()  # Leave script
            await app.run()
            success = True
            break  
        except Exception:
            await asyncio.sleep(60)
    return 0 if success else 1


if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())
