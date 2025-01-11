import time
import random

# Simulate a dictionary with 10,000 accounts
accounts = {i: f"Account-{i}" for i in range(10000, 20000)}

# Measure time to perform 10,000 random lookups
start_time = time.time()
for _ in range(10000):
    random_id = random.randint(10000, 19999)
    account = accounts[random_id]
end_time = time.time()

print(f"Performed 10,000 searches in {end_time - start_time:.4f} seconds.")
