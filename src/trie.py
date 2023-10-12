from collections import defaultdict

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_end = False

def remove_subdomains(domains):
    root = TrieNode()

    for domain in domains:
        parts = domain.split(".")
        current = root
        
        for i in range(len(parts) - 1, -1, -1):
            part = parts[i]
            current = current.children[part]
        
        current.is_end = True
    
    final_domains = set()

    for domain in domains:
        parts = domain.split(".")
        current = root
        
        for i in range(len(parts) - 1, -1, -1):
            part = parts[i]
            current = current.children[part]
            
            if current.is_end:
                final_domains.add(".".join(parts[i:]))
                break

    return final_domains
    
