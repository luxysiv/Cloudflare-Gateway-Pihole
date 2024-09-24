import re
from src import ids_pattern

def split_domain_list(domains: list[str], chunk_size: int) -> list[list[str]]:
    """
    Splits a list of domains into smaller chunks.

    Args:
        domains (list[str]): The list of domains to be split.
        chunk_size (int): The size of each chunk.

    Yields:
        list[str]: Chunks of the original list, each of size `chunk_size`.
    """
    for i in range(0, len(domains), chunk_size):
        yield domains[i:i + chunk_size]

def safe_sort_key(list_item: dict) -> int:
    """
    Extracts a numeric key from a list item for safe sorting.

    Args:
        list_item (dict): The list item from which to extract the key.

    Returns:
        int: The extracted numeric key, or infinity if no match is found.
    """
    match = re.search(r'\d+', list_item["name"])
    return int(match.group()) if match else float('inf')

def extract_list_ids(rule: dict) -> set[str]:
    """
    Extracts list IDs from a given rule's traffic data.

    Args:
        rule (dict): The rule from which to extract list IDs.

    Returns:
        set[str]: A set of extracted list IDs.
    """
    if not rule or not rule.get('traffic'):
        return set()
    return set(ids_pattern.findall(rule['traffic']))
