from src import (
    info,
    ip_pattern, 
    domain_pattern, 
    replace_pattern
)

def convert_to_domain_list(block_content: str, white_content: str) -> list[str]:
    """
    Converts the block content and white list content to a final list of domains.

    Args:
        block_content (str): Content containing domains to be blocked.
        white_content (str): Content containing whitelisted domains.

    Returns:
        list[str]: A sorted list of final domains after applying whitelist filtering.
    """
    white_domains = set()
    block_domains = set()

    extract_domains(white_content, white_domains)
    info(f"Number of whitelisted domains: {len(white_domains)}")

    extract_domains(block_content, block_domains)
    block_domains = remove_subdomains_if_higher(block_domains)
    info(f"Number of blocked domains: {len(block_domains)}")

    final_domains = sorted(list(block_domains - white_domains))
    info(f"Number of final domains: {len(final_domains)}")

    return final_domains

def extract_domains(content: str, domains: set[str]) -> None:
    """
    Extracts domains from the provided content and adds them to the given set.

    Args:
        content (str): Content containing domains to extract.
        domains (set[str]): Set to store extracted domains.
    """
    for line in content.splitlines():
        if line.startswith(("#", "!", "/")) or line == "":
            continue

        cleaned_line = line.lower().strip().split("#")[0].split("^")[0].replace("\r", "")
        domain = replace_pattern.sub("", cleaned_line, count=1)

        try:
            # Convert domain to ASCII (IDNA encoding)
            domain = domain.encode("idna").decode("utf-8", "replace")
            # Validate the domain against patterns and add to the set if valid
            if domain_pattern.match(domain) and not ip_pattern.match(domain):
                domains.add(domain)
        except Exception:
            pass  # Ignore exceptions for invalid domain encodings

def remove_subdomains_if_higher(domains: set[str]) -> set[str]:
    """
    Removes subdomains if a higher-level domain is present in the set.

    Args:
        domains (set[str]): Set of domains to filter.

    Returns:
        set[str]: A set of top-level domains without lower subdomains.
    """
    top_level_domains = set()
    
    for domain in domains:
        parts = domain.split(".")
        is_lower_subdomain = False
            
        # Check if any higher-level domain exists in the set
        for i in range(1, len(parts)):
            higher_domain = ".".join(parts[i:])
            if higher_domain in domains:
                is_lower_subdomain = True
                break
                    
        if not is_lower_subdomain:
            top_level_domains.add(domain)
                
    return top_level_domains
