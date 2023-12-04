import asyncio
import aiohttp

from loguru import logger
from configparser import ConfigParser

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

async def download_file(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        text = await response.text("utf-8")
        logger.info(f"Downloaded file from {url} File size: {len(text)}")
        return text

def chunk_list(_list: list[str], n: int):
    for i in range(0, len(_list), n):     
        yield _list[i : i + n]
