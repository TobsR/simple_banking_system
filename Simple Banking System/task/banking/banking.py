# Write your code here
import sqlite3
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS card;")
cur.execute("CREATE TABLE card ("
            "'id' INTEGER PRIMARY KEY,"
            "'number' TEXT,"
            "'pin' TEXT,"
            "'balance' INTEGER DEFAULT 0"
            ");")

"""
@staticmethod
def luhn(n):
    r = [int(ch) for ch in str(n)][::-1]  # Generates an integer list of CC num, then reverses it.
    # sum(r[0::2]) sums all the "even" index nums
    # For every "odd" index num (for d in r[1::2]) divmod multiplies d by 2 (luhn req) then divides by 10
    # if the num is 16 for example, the result is 1.6. divmod then adds the 1 and 6 to get 7 (luhn req).
    # The resulting value of adding the even sum and odd sum is then modulo 10. If that result is 0, CC num is good.
    # https://cscircles.cemc.uwaterloo.ca/visualize
    return (sum(r[0::2]) + sum(sum(divmod(d * 2, 10)) for d in r[1::2])) % 10 == 0
"""

def main_menu():
    account = {}
    option = 999
    while option != 0:
        print("1. Create an account\n2. Log into account\n0. Exit")
        option = int(input())
        if option == 1:
            create_account(account)
        elif option == 2:
            login()
            if option == 0:
                return


def create_account(account):
    import random
    account['id_number'] = "400000"
    for i in range(9):
        account['id_number'] += str(random.randint(0, 9))
    check_sum = create_checksum(account['id_number'])
    # check_sum = create_checksum('400000844943340')
    account['id_number'] += str(check_sum)
    account['pin_code'] = ""
    for i in range(4):
        account['pin_code'] += str(random.randint(0, 9))
    account['balance'] = 0

    cur.execute(f"SELECT id FROM card WHERE number = {account['id_number']};")
    for row in cur:
        print(row)

    cur.execute("INSERT INTO card ('number', 'pin')"
                f" VALUES ({account['id_number']}, {account['pin_code']});")
    conn.commit()

    print("\nYour card has been created")
    print(f"Your card number:\n{account['id_number']}")
    print(f"Your card PIN:\n{account['pin_code']}\n")


def create_checksum(check):
    counter = 0
    for i in range(len(check)):
        number = int(check[i])
        if i % 2 == 0:
            number *= 2
        if number > 9:
            number -= 9
        counter += number
    if counter % 10 == 0:
        return 0
    else:
        return 10 - (counter % 10)



def login():
    print("\nEnter your card number:")
    id_number = str(input())
    print("Enter your PIN:")
    pin_code = str(input())

    cur.execute(f"SELECT number,pin FROM card WHERE number = {id_number};")
    row = cur.fetchone()
    if row is None:
        print("\nWrong card number or PIN!\n")
        return
    while row is not None:
        if id_number == str(row[0]) and pin_code == str(row[1]):
            print("\nYou have successfully logged in!\n")
            menu(id_number)
        row = cur.fetchone()
    print("\nWrong card number or PIN!\n")
    return

def menu(id_number):
    option = 999
    while option != 0:
        print("""
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
        """)
        option = int(input())
        if option == 1:
            cur.execute("SELECT balance FROM card WHERE number = " + id_number + ";")
            row = cur.fetchone()
            print(f"\nBalance: {row[0]}\n")
        elif option == 2:
            add_income(id_number)
        elif option == 3:
            transfer_income(id_number)
        elif option == 4:
            close_account(id_number)
            option = 0
        elif option == 5:
            print("\nYou have successfully logged out!\n")
            return
        else:
            print("\nBye!\n")
            exit()

def add_income(id_number):
    print("Enter income:")
    cur.execute(f"UPDATE card SET balance = balance + {str(input())} WHERE number = {str(id_number)};")
    conn.commit()
    print("Income was added!")

def transfer_income(id_number):
    print("Enter card number:")
    check_number = str(input())

    if check_number[-1] != str(create_checksum(check_number[:len(check_number) - 1])):
        print("Probably you made a mistake in the card number. Please try again!")
        return

    cur.execute(f"SELECT * FROM card WHERE number = {check_number};")
    row = cur.fetchone()
    if row is None:
        print("Such a card does not exist.")
        return

    print("Enter how much money you want to transfer:")
    check_sum = str(input())

    cur.execute(f"SELECT * FROM card WHERE number = {id_number} and balance >= {check_sum};")
    row = cur.fetchone()
    if row is None:
        print("Not enough money!")
        return

    cur.execute(f"UPDATE card SET balance = balance + {check_sum} WHERE number = {str(check_number)};")
    cur.execute(f"UPDATE card SET balance = balance - {check_sum} WHERE number = {str(id_number)};")
    conn.commit()
    print("Success!")

def close_account(id_number):
    cur.execute(f"DELETE FROM card WHERE number = {str(id_number)};")
    conn.commit()
    print("The account has been closed!")

main_menu()
