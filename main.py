import json
import heapq
import time
from collections import deque
from datetime import datetime, timedelta


class Account:
    def __init__(self, id, balance=0, withdrawal_daily_max=50000,
                 withdrawal_frequency=3, withdrawal_transaction_max=20000,
                 deposit_daily_max=150000, deposit_frequency=4, deposit_transaction_max=50000, transaction_history_size=10):
        self.id = id
        self.name = f"User{id}"
        self.balance = balance
        self.withdrawal_daily_max = withdrawal_daily_max
        self.withdrawal_frequency = withdrawal_frequency
        self.withdrawal_transaction_max = withdrawal_transaction_max
        self.deposit_daily_max = deposit_daily_max
        self.deposit_frequency = deposit_frequency
        self.deposit_transaction_max = deposit_transaction_max

        # Track daily totals and cooldowns
        self.withdrawal_count = 0
        self.deposit_count = 0
        self.daily_withdrawn = 0
        self.daily_deposited = 0
        self.last_transaction_time = None  # Track last transaction time for cooldown

        # Transaction history
        self.transaction_history = deque(maxlen=transaction_history_size)

    def get_balance(self):
        return self.balance

    def can_withdraw(self, amount):
        return (self.withdrawal_count < self.withdrawal_frequency and
                amount <= self.withdrawal_transaction_max and
                amount <= self.balance and
                self.daily_withdrawn + amount <= self.withdrawal_daily_max)

    def withdraw(self, amount):
        if self.can_withdraw(amount):
            self.balance -= amount
            self.withdrawal_count += 1
            self.daily_withdrawn += amount
            self.last_transaction_time = datetime.now()
            self.add_transaction("withdraw", amount)
            return True
        return False

    def can_deposit(self, amount):
        return (self.deposit_count < self.deposit_frequency and
                amount <= self.deposit_transaction_max and
                self.daily_deposited + amount <= self.deposit_daily_max)

    def deposit(self, amount):
        if self.can_deposit(amount):
            self.balance += amount
            self.deposit_count += 1
            self.daily_deposited += amount
            self.last_transaction_time = datetime.now()
            self.add_transaction("deposit", amount)
            return True
        return False

    #use deque to hold transaction history
    def add_transaction(self, transaction_type, amount):
        """Add a transaction to the history."""
        transaction = {
            "type": transaction_type,
            "amount": amount,
            "balance_after": self.balance,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.transaction_history.append(transaction)

    def get_transaction_history(self):
        """Return the transaction history."""
        return list(self.transaction_history)

    def get_name(self):
        return self.name

    def reset_daily_limits(self):
        """Reset daily withdrawal and deposit totals."""
        self.daily_withdrawn = 0
        self.daily_deposited = 0
        self.withdrawal_count = 0
        self.deposit_count = 0

    def to_dict(self):
        """Convert account to a dictionary for saving."""
        return {
            "id": self.id,
            "balance": self.balance,
            "transaction_history": list(self.transaction_history)
        }

    @staticmethod
    def from_dict(data):
        """Create an account from a dictionary."""
        account = Account(data["id"], balance=data["balance"])
        if "transaction_history" in data:
            account.transaction_history.extend(data["transaction_history"])
        return account


class Bank:
    def __init__(self):
        self.accounts = {}
        self.reset_heap = []  # Min-heap to manage daily reset events

    def create_account(self, id):
        if id not in self.accounts:
            account = Account(id)
            self.accounts[id] = account
            self.schedule_reset(account)  # Schedule daily reset
            return True
        return False

    def get_account(self, id):
        return self.accounts.get(id, None)

    def list_accounts(self):
        return self.accounts.keys()

    def save_accounts(self, filename="accounts.json"):
        """Save all accounts to a file."""
        with open(filename, "w") as file:
            json.dump([account.to_dict() for account in self.accounts.values()], file)

    def load_accounts(self, filename="accounts.json"):
        """Load accounts from a file."""
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                for acc_data in data:
                    account = Account.from_dict(acc_data)
                    self.accounts[account.id] = account
                    self.schedule_reset(account)
        except FileNotFoundError:
            for i in range(0, 100000):
                self.create_account(i)


    # using heap to push the earliest reset time on top
    def schedule_reset(self, account):
        """Schedule a daily reset for the given account."""
        reset_time = datetime.now() + timedelta(days=1)
        heapq.heappush(self.reset_heap, (reset_time, account.id))

    def process_resets(self):
        """Process accounts whose daily limits need resetting."""
        current_time = datetime.now()
        while self.reset_heap and self.reset_heap[0][0] <= current_time:
            _, account_id = heapq.heappop(self.reset_heap)
            account = self.get_account(account_id)
            if account:
                account.reset_daily_limits()
                self.schedule_reset(account)  # Schedule the next reset

    def enforce_cooldown(self, account):
        """Check and enforce cooldown between transactions."""
        if account.last_transaction_time:
            cooldown_period = timedelta(seconds=15)  # Example cooldown of 15 seconds
            next_allowed_time = account.last_transaction_time + cooldown_period
            if datetime.now() < next_allowed_time:
                return False, next_allowed_time
        return True, None


def main():
    bank = Bank()
    bank.load_accounts()  # Load account data from file

    while True:
        bank.process_resets()  # Check and reset daily limits dynamically

        print("\nGood Morning!")
        try:
            id = int(input("\nPlease Enter Your account pin: "))
            account = bank.get_account(id)
            if not account:
                print("Invalid Pin. Try again.")
                continue

            print(f"\nHello, {account.get_name()}!")

            while True:
                # Menu
                print("\n1 - Balance \t 2 - Withdraw \t 3 - Deposit \t 4 - Transaction History \t 5 - Quit")
                selection = int(input("\nEnter your selection: "))

                if selection == 1:  # Balance
                    print(f"Your Balance is: {account.get_balance()}")

                elif selection == 2:  # Withdraw
                    can_proceed, wait_time = bank.enforce_cooldown(account)
                    if not can_proceed:
                        print(f"Cooldown in effect. Try again after {wait_time.strftime('%H:%M:%S')}.")
                        continue

                    amount = float(input("Enter amount to withdraw: "))
                    if account.withdraw(amount):
                        print(f"Withdrawal successful. Updated Balance: {account.get_balance()}")
                    else:
                        print("Withdrawal failed. Check limits or balance.")

                elif selection == 3:  # Deposit
                    can_proceed, wait_time = bank.enforce_cooldown(account)
                    if not can_proceed:
                        print(f"Cooldown in effect. Try again after {wait_time.strftime('%H:%M:%S')}.")
                        continue

                    amount = float(input("Enter amount to deposit: "))
                    if account.deposit(amount):
                        print(f"Deposit successful. Updated Balance: {account.get_balance()}")
                    else:
                        print("Deposit failed. Check limits.")

                elif selection == 4:  # Transaction History
                    history = account.get_transaction_history()
                    if not history:
                        print("No transactions found.")
                    else:
                        print("\nRecent Transactions:")
                        for txn in history:
                            print(f"- {txn['timestamp']}: {txn['type']} ${txn['amount']} (Balance: ${txn['balance_after']})")

                elif selection == 5:  # Quit
                    print("Thank you for banking with us!")
                    bank.save_accounts()  # Save accounts to file before exiting
                    return

                else:
                    print("Invalid selection. Try again.")

        except ValueError:
            print("Invalid input. Please try again.")


if __name__ == "__main__":
    main()
