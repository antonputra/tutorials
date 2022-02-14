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


def bruteforce(wordlist, password):
    password_hash = hash(password)
    for guess_password in wordlist:
        if hash(guess_password) == password_hash:
            return guess_password


if __name__ == '__main__':
    WORDLIST_URL = 'https://raw.githubusercontent.com/berzerk0/Probable-Wordlists/2df55facf06c7742f2038a8f6607ea9071596128/Real-Passwords/Top12Thousand-probable-v2.txt'
    DATABASE_PATH = 'database.csv'

    wordlist = get_wordlist(WORDLIST_URL)
    print(f'wordlist contains {len(wordlist)} items')

    users = get_users(DATABASE_PATH)
    for user in users:
        password = bruteforce(wordlist, user['password'])
        if password is not None:
            print(f'username: {user["username"]}, password: {password}')
