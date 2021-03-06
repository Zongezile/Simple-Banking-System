import random
import sqlite3

# SQL
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
#cur.execute("DELETE FROM card")
#conn.commit()
cur.execute(
    "CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);")
conn.commit()


def luhn_algorithm(peace_of_card):
    sum = 0
    index = 1
    for x in peace_of_card:
        if index % 2 == 1:
            x = 2 * int(x)
        if int(x) > 9:
            x = int(x) - 9
        sum += int(x)
        index += 1
    return sum


def create_account():
    # Generate Card Number
    account_identifier = str(random.randint(0, 999999999))
    if len(account_identifier) < 9:
        while len(account_identifier) < 9:
            account_identifier = "0" + account_identifier

    sum = 8 + luhn_algorithm(account_identifier)

    if sum % 10 == 0:
        checksum = 0
    else:
        checksum = 10 - (sum % 10)

    new_card = "400000" + str(account_identifier) + str(checksum)

    # Generate PIN
    new_pin = str(random.randint(0, 9999))
    if len(new_pin) < 4:
        while len(new_pin) < 4:
            new_pin = "0" + new_pin

    print("\nYour card has been created")
    print("Your card number:")
    print(new_card)
    print("Your card PIN:")
    print(new_pin)
    print("")

    cur.execute("INSERT INTO card(number, pin) VALUES(?, ?);", (new_card, new_pin))
    conn.commit()


def log():
    card = input("\nEnter your card number: \n")
    pin = input("Enter your PIN: \n")
    cur.execute("SELECT * FROM card WHERE number = ? AND pin = ?;", (card, pin))
    if cur.fetchone() is not None:
        menu_2 = ""
        print("\nYou have successfully logged in! \n")
        while menu_2 != "0":
            menu_2 = input("1. Balance \n2. Add income \n3. Do transfer \n4. Close account \n5. Log out \n0. Exit\n")
            if menu_2 == "1":
                cur.execute("SELECT balance FROM card WHERE number = ?;", (card,))
                print("\nBalance: ", cur.fetchone()[0], "\n")
            elif menu_2 == "2":
                money = input("Enter income: \n")
                cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (money, card))
                conn.commit()
                print("Income was added!\n")
            elif menu_2 == "3":
                do_transfer(card)
            elif menu_2 == "4":
                cur.execute("DELETE FROM card WHERE number = ?;", (card,))
                conn.commit()
                print("\nThe account has been closed!\n")
                return
            elif menu_2 == "5":
                print("\nYou have successfully logged out! \n")
                return
        return "0"
    else:
        print("\nWrong card number or PIN!\n")
        return


def do_transfer(card):
    print("\nTransfer")
    to_where = input("Enter card number:\n")
    cur.execute("SELECT * FROM card WHERE number = ?;", (to_where,))
    sum = 0

    if len(to_where) == 16:
        sum = luhn_algorithm(to_where[0:15]) + int(to_where[15])

    if to_where == card:
        print("You can't transfer money to the same account!\n")
        return
    elif sum % 10 != 0:
        print("Probably you made a mistake in the card number. Please try again! \n")
        return
    elif cur.fetchone() is None:
        print("Such a card does not exist.")
        return
    else:
        how_much = int(input("Enter how much money you want to transfer: \n"))
        cur.execute("SELECT balance FROM card WHERE number = ?;", (card,))
        if how_much > int(cur.fetchone()[0]):
            print("Not enough money! \n")
            return
        else:
            cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?;", (how_much, card))
            conn.commit()
            cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (how_much, to_where))
            conn.commit()
            print("Success!\n")


def menu():
    menu = ""
    while menu != "0":
        menu = input('''1. Create an account \n2. Log into account \n0. Exit\n''')
        if menu == "1":
            create_account()
        elif menu == "2":
            menu = log()
    print("\nBye!")


menu()
