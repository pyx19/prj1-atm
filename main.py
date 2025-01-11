import json
import random


class Account:
    def __init__(self, id, balance=0, withdrawal_daily_max=50000,
                 withdrawal_frequency=3, withdrawal_transaction_max=20000,
                 deposit_daily_max=150000, deposit_frequency=4, deposit_transaction_max=50000):
        self.id = id
        self.name = f"User{id}"
        self.balance = balance
        self.withdrawal_daily_max = withdrawal_daily_max
        self.withdrawal_frequency = withdrawal_frequency
        self.withdrawal_transaction_max = withdrawal_transaction_max
        self.deposit_daily_max = deposit_daily_max
        self.deposit_frequency = deposit_frequency
        self.deposit_transaction_max = deposit_transaction_max

        # Track daily totals
        self.withdrawal_count = 0
        self.deposit_count = 0
        self.daily_withdrawn = 0
        self.daily_deposited = 0

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
            return True
        return False

    def get_name(self):
        return self.name

    def reset_daily_limits(self):
        """Reset daily withdrawal and deposit totals for a new session."""
        self.daily_withdrawn = 0
        self.daily_deposited = 0
        self.withdrawal_count = 0
        self.deposit_count = 0

    def to_dict(self):
        """Convert account to a dictionary for saving."""
        return {
            "id": self.id,
            "balance": self.balance
        }

    @staticmethod
    def from_dict(data):
        """Create an account from a dictionary."""
        return Account(data["id"], balance=data["balance"])


class Bank:
    def __init__(self):
        self.accounts = {}

    def create_account(self, id):
        if id not in self.accounts:
            self.accounts[id] = Account(id)
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
                self.accounts = {acc_data["id"]: Account.from_dict(acc_data) for acc_data in data}
        except FileNotFoundError:
            for i in range(0, 100000):
                self.create_account(i)


def main():
    bank = Bank()
    bank.load_accounts()  # Load account data from file

    while True:
        print("\nGood Morning!")
        for account in bank.accounts.values():
            account.reset_daily_limits()

        try:
            id = int(input("\nPlease Enter Your account pin: "))
            account = bank.get_account(id)
            if not account:
                print("Invalid Pin. Try again.")
                continue

            print(f"\nHello, {account.get_name()}!")

            while True:
                # Menu
                print("\n1 - Balance \t 2 - Withdraw \t 3 - Deposit \t 4 - Quit")
                selection = int(input("\nEnter your selection: "))

                if selection == 1:  # Balance
                    print(f"Your Balance is: {account.get_balance()}")

                elif selection == 2:  # Withdraw
                    amount = float(input("Enter amount to withdraw: "))
                    if account.withdraw(amount):
                        print(f"Withdrawal successful. Updated Balance: {account.get_balance()}")
                    else:
                        print("Withdrawal failed. You can only withdraw 3 times a day and a maximum of 20000 per transaction or 50000 per day.")

                elif selection == 3:  # Deposit
                    amount = float(input("Enter amount to deposit: "))
                    if account.deposit(amount):
                        print(f"Deposit successful. Updated Balance: {account.get_balance()}")
                    else:
                        print("Deposit failed. You can only deposit 4 times a day and a maximum of 50000 per transaction or 150000 per day.")

                elif selection == 4:  # Quit
                    print("Thank you for banking with us!")
                    bank.save_accounts()  # Save accounts to file before exiting
                    return

                else:
                    print("Invalid selection. Try again.")

        except ValueError:
            print("Invalid input. Please try again.")


if __name__ == "__main__":
    main()
