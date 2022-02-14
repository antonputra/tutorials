import csv
import hashlib
from urllib.request import urlopen


def hash(password):
    result = hashlib.sha256(password.encode())
    return result.hexdigest()


def get_wordlist(url):
    try:
        with urlopen(url) as f:
            wordlist = f.read().decode('utf-8').splitlines()
            return wordlist
    except Exception as e:
        print(f'failed to get wordlist: {e}')
        exit(1)


def get_users(path):
    try:
        result = []
        with open(path) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                result.append(dict(row))
            return result
    except Exception as e:
        print(f'failed to get users: {e}')
        exit(1)


def get_rainbow_table(path):
    try:
        result = []
        with open(path) as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                result.append(dict(row))
            return result
    except Exception as e:
        print(f'failed to get rainbow table: {e}')
        exit(1)


def match_hash(users, rainbow_table):
    for user in users:
        password_hash = hash(user['password'])
        for row in rainbow_table:
            if password_hash == row['hash']:
                print(
                    f'username: {user["username"]}, password {row["password"]}')


if __name__ == '__main__':
    WORDLIST_URL = 'https://raw.githubusercontent.com/berzerk0/Probable-Wordlists/2df55facf06c7742f2038a8f6607ea9071596128/Real-Passwords/Top12Thousand-probable-v2.txt'
    DATABASE_PATH = 'database.csv'
    RAINBOW_TABLE_PATH = 'rainbow_table.csv'

    users = get_users(DATABASE_PATH)
    rainbow_table = get_rainbow_table(RAINBOW_TABLE_PATH)
    match_hash(users, rainbow_table)
