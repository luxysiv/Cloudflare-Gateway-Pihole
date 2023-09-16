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
        for i in range(len(parts) - 1, 0, -1):
            subdomain = '.'.join(parts[i:])
            if self.search(subdomain):
                return True
        return False

def process_domain(domain, trie):
    if not trie.is_subdomain(domain):
        return domain

def filter_subdomains(domains):
    trie = Trie()
    unique_domains = set()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(process_domain, domain, trie) for domain in domains]
        for future in concurrent.futures.as_completed(results):
            result = future.result()
            if result:
                unique_domains.add(result)
                trie.insert(result)

    return list(unique_domains)
