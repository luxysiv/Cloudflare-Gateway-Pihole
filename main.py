import logging
import requests

from typing import List
from src import cloudflare
from src.utils import App
from src.colorlogs import ColoredLevelFormatter

logging.getLogger().setLevel(logging.INFO)
formatter = ColoredLevelFormatter("%(levelname)s: %(message)s")
console = logging.StreamHandler()
console.setFormatter(ColoredLevelFormatter("%(levelname)s: %(message)s"))
logger = logging.getLogger()
logger.addHandler(console)

if __name__ == "__main__":
    adlist_urls = []
    with open("lists.ini", "r") as file:
        adlist_urls = [url.strip() for url in file if url.strip()]
    adlist_name = "ManhDuong"
    app = App(adlist_name, adlist_urls)
    #app.delete() # Leave script 
    app.run()     # Use script 
