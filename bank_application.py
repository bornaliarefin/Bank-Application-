import os
import datetime

SAVING_FILE = "saving_accounts.txt"
CURRENT_FILE = "current_accounts.txt"
CUSTOMER_FILE = "customers.txt"
TRANSACTION_FILE = "transactions.txt"

class Transaction:
    def __init__(self, account_number, trans_type, amount):
        self.transaction_id = f"T{int(datetime.datetime.now().timestamp())}"
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.account_number = account_number
        self.trans_type = trans_type
        self.amount = amount

    def save(self):
        with open(TRANSACTION_FILE, "a") as f:
            f.write(f"Transaction ID: {self.transaction_id}\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Account: {self.account_number}\n")
            f.write(f"Type: {self.trans_type}\n")
            f.write(f"Amount: {self.amount:.2f}\n\n")

class Account:
    def __init__(self, account_number, customer, balance=0.0):
        self.account_number = account_number
        self.customer = customer
        self.balance = balance

    def deposit(self, amount):
        if amount <= 0:
            print("Deposit amount must be positive.")
            return
        self.balance += amount
        print(f"Deposited ${amount}. New balance: ${self.balance:.2f}")
        Transaction(self.account_number, "Deposit", amount).save()

    def withdraw(self, amount):
        if amount <= 0:
            print("Withdrawal amount must be positive.")
            return False
        if amount > self.balance:
            print("Insufficient balance.")
            return False
        self.balance -= amount
        print(f"Withdrew ${amount}. New balance: ${self.balance:.2f}")
        Transaction(self.account_number, "Withdrawal", amount).save()
        return True

    def check_balance(self):
        print(f"Current balance: ${self.balance:.2f}")

class SavingAccount(Account):
    interest_rate = 0.035

    def add_monthly_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        print(f"Interest added: ${interest:.2f}. New balance: ${self.balance:.2f}")

class CurrentAccount(Account):
    def __init__(self, account_number, customer, balance=0.0, overdraw_limit=500.0):
        super().__init__(account_number, customer, balance)
        self.overdraw_limit = overdraw_limit

    def withdraw(self, amount):
        if amount <= 0:
            print("Withdrawal amount must be positive.")
            return False
        if amount > (self.balance + self.overdraw_limit):
            print("Withdrawal exceeds overdraw limit.")
            return False
        self.balance -= amount
        print(f"Withdrew ${amount}. New balance: ${self.balance:.2f}")
        Transaction(self.account_number, "Withdrawal", amount).save()
        return True

class Customer:
    def __init__(self, name, address, contact):
        self.name = name
        self.address = address
        self.contact = contact
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

def view_transactions():
    if not os.path.exists(TRANSACTION_FILE):
        print("No transaction history found.")
        return
    print("\n=== Transaction History ===")
    with open(TRANSACTION_FILE, "r") as f:
        print(f.read())

def get_float_input(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid amount. Please enter a number.")

def load_accounts(customer):
    # Load saving accounts
    if os.path.exists(SAVING_FILE):
        with open(SAVING_FILE, "r") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 5):
                acc_no = lines[i].split(":")[1].strip()
                cust_name = lines[i+1].split(":")[1].strip()
                bal = float(lines[i+2].split(":")[1].strip())
                acc = SavingAccount(acc_no, cust_name, bal)
                customer.add_account(acc)

    # Load current accounts
    if os.path.exists(CURRENT_FILE):
        with open(CURRENT_FILE, "r") as f:
            lines = f.readlines()
            for i in range(0, len(lines), 5):
                acc_no = lines[i].split(":")[1].strip()
                cust_name = lines[i+1].split(":")[1].strip()
                bal = float(lines[i+2].split(":")[1].strip())
                limit = float(lines[i+3].split(":")[1].strip())
                acc = CurrentAccount(acc_no, cust_name, bal, limit)
                customer.add_account(acc)

def main():
    print("===== Welcome to Bornali's Bank CLI =====")
    try:
        name = input("Enter customer name: ")
        address = input("Enter address: ")
        contact = input("Enter contact number: ")
        customer = Customer(name, address, contact)

        # Load accounts from files
        load_accounts(customer)

        while True:
            print("\nMenu:")
            print("1. Create Saving Account")
            print("2. Create Current Account")
            print("3. Deposit")
            print("4. Withdraw")
            print("5. Check Balance")
            print("6. View Transaction History")
            print("7. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                acc_no = input("Enter account number: ")
                bal = get_float_input("Initial deposit: ")
                acc = SavingAccount(acc_no, customer.name, bal)
                customer.add_account(acc)
                with open(SAVING_FILE, "a") as f:
                    f.write(f"Account Number: {acc_no}\nCustomer: {customer.name}\nBalance: {bal:.2f}\nInterest Rate: {SavingAccount.interest_rate*100:.1f}%\n\n")
                print("Saving account created.")

            elif choice == "2":
                acc_no = input("Enter account number: ")
                bal = get_float_input("Initial deposit: ")
                acc = CurrentAccount(acc_no, customer.name, bal)
                customer.add_account(acc)
                with open(CURRENT_FILE, "a") as f:
                    f.write(f"Account Number: {acc_no}\nCustomer: {customer.name}\nBalance: {bal:.2f}\nOverdraw Limit: {acc.overdraw_limit:.2f}\n\n")
                print("Current account created.")

            elif choice == "3":
                acc_no = input("Enter account number to deposit: ")
                amount = get_float_input("Enter amount: ")
                for acc in customer.accounts:
                    if acc.account_number == acc_no:
                        acc.deposit(amount)
                        break
                else:
                    print("Account not found.")

            elif choice == "4":
                acc_no = input("Enter account number to withdraw from: ")
                amount = get_float_input("Enter amount: ")
                for acc in customer.accounts:
                    if acc.account_number == acc_no:
                        acc.withdraw(amount)
                        break
                else:
                    print("Account not found.")

            elif choice == "5":
                acc_no = input("Enter account number to check balance: ")
                for acc in customer.accounts:
                    if acc.account_number == acc_no:
                        acc.check_balance()
                        break
                else:
                    print("Account not found.")

            elif choice == "6":
                view_transactions()

            elif choice == "7":
                with open(CUSTOMER_FILE, "a") as f:
                    f.write(f"Name: {customer.name}\nAddress: {customer.address}\nContact: {customer.contact}\nAccounts: {[acc.account_number for acc in customer.accounts]}\n\n")
                print("Thank you for using Bornali's Bank!")
                break

            else:
                print("Invalid option. Please try again.")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
