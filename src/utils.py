import os
import re
import json
import http.client
from src import ids_pattern, CACHE_FILE
from src.cloudflare import get_lists, get_rules, get_list_items


class GithubAPI:
    BASE_URL = "api.github.com"
    GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY')
    HEADERS = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Mozilla/5.0"
    }

    @staticmethod
    def request(method, url, body=None):
        conn = http.client.HTTPSConnection(GithubAPI.BASE_URL)
        conn.request(method, url, body, headers=GithubAPI.HEADERS)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return json.loads(data) if data else {}

    @staticmethod
    def delete(url):
        return GithubAPI.request("DELETE", url)

    @staticmethod
    def get(url):
        return GithubAPI.request("GET", url)


def load_cache():
    try:
        if is_running_in_github_actions():
            workflow_status, completed_run_ids = get_latest_workflow_status()
            
            delete_completed_workflows(completed_run_ids)

            if workflow_status == 'success':
                if os.path.exists(CACHE_FILE):
                    with open(CACHE_FILE, 'r') as file:
                        return json.load(file)

        elif os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as file:
                return json.load(file)
    except json.JSONDecodeError:
        return {"lists": [], "rules": [], "mapping": {}}

    return {"lists": [], "rules": [], "mapping": {}}


def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file)


def get_current_lists(cache, list_name):
    if cache["lists"]:
        return cache["lists"]
    current_lists = get_lists(list_name)
    cache["lists"] = current_lists
    save_cache(cache)
    return current_lists


def get_current_rules(cache, rule_name):
    if cache["rules"]:
        return cache["rules"]
    current_rules = get_rules(rule_name)
    cache["rules"] = current_rules
    save_cache(cache)
    return current_rules


def get_list_items_cached(cache, list_id):
    if list_id in cache["mapping"]:
        return cache["mapping"][list_id]
    items = get_list_items(list_id)
    cache["mapping"][list_id] = items
    save_cache(cache)
    return items


def safe_sort_key(list_item):
    match = re.search(r'\d+', list_item["name"])
    return int(match.group()) if match else float('inf')


def extract_list_ids(rule):
    if not rule or not rule.get('traffic'):
        return set()
    return set(ids_pattern.findall(rule['traffic']))


def delete_completed_workflows(completed_run_ids):
    if completed_run_ids:
        for run_id in completed_run_ids:
            delete_url = f"/repos/{GithubAPI.GITHUB_REPOSITORY}/actions/runs/{run_id}"
            GithubAPI.delete(delete_url)


def get_latest_workflow_status():
    WORKFLOW_RUNS_URL = f"/repos/{GithubAPI.GITHUB_REPOSITORY}/actions/runs?per_page=5"

    runs_data = GithubAPI.get(WORKFLOW_RUNS_URL).get('workflow_runs', [])
    completed_runs = [run for run in runs_data if run['status'] == 'completed']

    if completed_runs:
        latest_run = completed_runs[0]
        completed_run_ids = [run['id'] for run in completed_runs]
        return latest_run['conclusion'], completed_run_ids

    return None, []


def is_running_in_github_actions():
    return os.getenv('GITHUB_ACTIONS') == 'true'


def delete_cache(completed_run_ids=None):
    CACHE_URL = f"/repos/{GithubAPI.GITHUB_REPOSITORY}/actions/caches"

    caches = GithubAPI.get(CACHE_URL).get('actions_caches', [])
    for cache_id in [cache['id'] for cache in caches]:
        GithubAPI.delete(f"{CACHE_URL}/{cache_id}")

    if completed_run_ids:
        delete_completed_workflows(completed_run_ids)
