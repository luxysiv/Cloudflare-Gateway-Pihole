import functools
import aiohttp

from src import CF_API_TOKEN, CF_IDENTIFIER

def aiohttp_session(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
        ) as session:
            kwargs["session"] = session
            return await func(*args, **kwargs)

    return wrapper


@aiohttp_session
async def get_lists(name_prefix: str, session: aiohttp.ClientSession):
    async with session.get(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/lists",
    ) as resp:
        if resp.status != 200:
            raise Exception("Failed to get Cloudflare lists")

        lists = (await resp.json())["result"] or []
        return [l for l in lists if l["name"].startswith(name_prefix)]


@aiohttp_session
async def create_list(name: str, domains: list[str], session: aiohttp.ClientSession):
    async with session.post(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/lists",
        json={
            "name": name,
            "description": "Ads & Tracking Domains",
            "type": "DOMAIN",
            "items": [{"value": domain} for domain in domains],
        },
    ) as resp:
        if resp.status != 200:
            raise Exception("Failed to create Cloudflare list")

        return (await resp.json())["result"]


@aiohttp_session
async def delete_list(name: str, list_id: str, session: aiohttp.ClientSession):
    async with session.delete(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/lists/{list_id}",
    ) as resp:
        if resp.status != 200:
            raise Exception("Failed to delete Cloudflare list")

        return (await resp.json())["result"]


@aiohttp_session
async def get_firewall_policies(name_prefix: str, session: aiohttp.ClientSession):
    async with session.get(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules",
    ) as resp:
        if resp.status != 200:
            raise Exception("Failed to get Cloudflare firewall policies")

        policies = (await resp.json())["result"] or []
        return [l for l in policies if l["name"].startswith(name_prefix)]


@aiohttp_session
async def create_gateway_policy(
    name: str, list_ids: list[str], session: aiohttp.ClientSession
):
    async with session.post(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules",
        json={
            "name": name,
            "description": "Block Ads & Tracking",
            "action": "block",
            "enabled": True,
            "filters": ["dns"],
            "traffic": "or".join(
                [f"any(dns.domains[*] in ${list_id})" for list_id in list_ids]
            ),
            "rule_settings": {
                "block_page_enabled": False,
            },
        },
    ) as resp:
        if resp.status != 200:
            raise Exception("Failed to create Cloudflare firewall policy")
        return (await resp.json())["result"]


@aiohttp_session
async def update_gateway_policy(
    name: str, policy_id: str, list_ids: list[str], session: aiohttp.ClientSession
):
    async with session.put(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules/{policy_id}",
        json={
            "name": name,
            "description": "Block Ads & Tracking",
            "action": "block",
            "enabled": True,
            "filters": ["dns"],
            "traffic": "or".join(
                [f"any(dns.domains[*] in ${list_id})" for list_id in list_ids]
            ),
            "rule_settings": {
                "block_page_enabled": False,
            },
        },
    ) as resp:
        if resp.status != 200:
            raise Exception("Failed to update Cloudflare firewall policy")

        return (await resp.json())["result"]


@aiohttp_session
async def delete_gateway_policy(
    policy_id: str, session: aiohttp.ClientSession
):
    async with session.delete(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_IDENTIFIER}/gateway/rules/{policy_id}",
    ) as resp:
        if resp.status != 200:
            raise Exception("Failed to delete Cloudflare gateway firewall policy")

        return (await resp.json())["result"]
