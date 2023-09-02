import logging
import requests

from typing import List
from src import cloudflare
from src.utils import App
from configparser import ConfigParser
from src.colorlogs import ColoredLevelFormatter

logging.getLogger().setLevel(logging.INFO)
formatter = ColoredLevelFormatter("%(levelname)s: %(message)s")
console = logging.StreamHandler()
console.setFormatter(ColoredLevelFormatter("%(levelname)s: %(message)s"))
logger = logging.getLogger()
logger.addHandler(console)

if __name__ == "__main__":
    config = ConfigParser()
    config.read("lists.ini")
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    adlist_urls = []
    for section in config.sections():
            for key in config.options(section):
                adlist_urls.append(config.get(section, key))
    adlist_name = "ManhDuong"
    app = App(adlist_name, adlist_urls)
    #app.delete() # Leave script 
    app.run()     # Use script 
