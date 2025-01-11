import time

class Account:
    def __init__(self, id, balance=0):
        self.id = id
        self.balance = balance

# Create 10,000 accounts and measure time
start_time = time.time()
accounts = {i: Account(i) for i in range(10000, 20000)}
end_time = time.time()

print(f"Created 10,000 accounts in {end_time - start_time:.4f} seconds.")

# Simulate random lookups
import random

lookup_start = time.time()
for _ in range(10000):
    random_id = random.randint(10000, 19999)
    account = accounts[random_id]
lookup_end = time.time()

print(f"Performed 10,000 random lookups in {lookup_end - lookup_start:.4f} seconds.")
