import time
import random


# Test Account class
class Account:
    def __init__(self, id, balance=0):
        self.id = id
        self.balance = balance


# TrieNode and AccountTrie
class TrieNode:
    def __init__(self):
        self.children = {}
        self.account = None


class AccountTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, id, account):
        node = self.root
        for char in str(id):
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.account = account

    def search(self, id):
        node = self.root
        for char in str(id):
            if char not in node.children:
                return None
            node = node.children[char]
        return node.account


# Benchmarking
def benchmark_lookup():
    num_accounts = 1_000_000
    lookup_count = 100_000

    # Generate test data
    accounts_dict = {}
    account_trie = AccountTrie()

    print("Populating accounts...")

    for i in range(num_accounts):
        account = Account(i, balance=random.randint(0, 10000))
        accounts_dict[i] = account
        account_trie.insert(i, account)

    print("Accounts populated.")

    # Random IDs for lookup
    lookup_ids = random.sample(range(num_accounts), lookup_count)

    # Benchmark dictionary
    print("Benchmarking dictionary lookup...")
    start_time = time.time()
    for account_id in lookup_ids:
        _ = accounts_dict.get(account_id)
    dict_time = time.time() - start_time
    print(f"Dictionary lookup time: {dict_time:.4f} seconds")

    # Benchmark trie
    print("Benchmarking trie lookup...")
    start_time = time.time()
    for account_id in lookup_ids:
        _ = account_trie.search(account_id)
    trie_time = time.time() - start_time
    print(f"Trie lookup time: {trie_time:.4f} seconds")

    # Compare results
    print("\nComparison:")
    print(f"Trie is {dict_time / trie_time:.2f}x faster than dictionary (or slower).")


# Run the benchmark
if __name__ == "__main__":
    benchmark_lookup()
