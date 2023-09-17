import concurrent.futures
from collections import defaultdict

class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def is_subdomain(self, domain):
        parts = domain.split('.')
        return any(self.search('.'.join(parts[i:])) for i in range(len(parts) - 1, 0, -1))

def filter_subdomains(domains):
    trie = Trie()

    def process_domain(domain):
        if not trie.is_subdomain(domain):
            return domain

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_domain, domains))
    
    unique_domains = [d for d in results if d is not None]

    return unique_domains
