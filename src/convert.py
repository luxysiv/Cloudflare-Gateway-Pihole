import logging
from src import replace_pattern, domain_pattern, ip_pattern

def convert_to_domain_list(block_content: str, white_content: str):
    # Process the downloaded content to extract domains
    white_domains = set()
    block_domains = set()

    # Process white content 
    for line in white_content.splitlines():
        white_domain = convert_domains(line)
        if white_domain:
            white_domains.add(white_domain)

    logging.info(f"Number of white domains: {len(white_domains)}")

    # Process block content 
    for line in block_content.splitlines():
        block_domain = convert_domains(line)
        if block_domain:
            block_domains.add(block_domain)

    filtered_domains = remove_subdomains(block_domains)

    logging.info(f"Number of block domains: {len(filtered_domains)}")
        
    final_domains = sorted(list(filtered_domains - white_domains))
        
    logging.info(f"Number of final domains: {len(final_domains)}")
        
    return final_domains

def convert_domains(line: str):
    # Convert a line into a valid domain name
    if line.startswith(("#", "!", "/")) or line == "":
        return None

    linex = line.lower().strip().split("#")[0].split("^")[0].replace("\r", "")
    domain = replace_pattern.sub("", linex, count=1)
    try:
        domain = domain.encode("idna").decode("utf-8", "replace")
        if domain_pattern.match(domain) and not ip_pattern.match(domain):
            return domain
    except Exception:
        pass
    return None

def remove_subdomains(domains: set[str]) -> set[str]:
    top_level_domains = set()
    
        for domain in domains:
            parts = domain.split(".")
            
            is_subdomain = False            
            for i in range(1, len(parts)):
                higher_domain = ".".join(parts[i:])
                if higher_domain in domains:
                    is_subdomain = True
                    break
                    
            if not is_subdomain:
                top_level_domains.add(domain)
                
        return top_level_domains
