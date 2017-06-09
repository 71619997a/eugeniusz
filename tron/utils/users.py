import sqlite3
import hashlib
import sql
from constants import DIR

f = DIR + "data/users.db"


def hash(a):
    return hashlib.sha512(a).hexdigest()

def login(name, pw):
    """Return vals:
    True - Successful authentication
    False - Failed authentication
    """
    c = sql.get_all_users()
    for user in c:
        if name == user[0]:
            if hash(pw) == user[1]:
                return True
            return False
    return False

def register(name, pw):
    if not (name.isalnum()):
        return False, "Username must be alphanumeric"
    c = sql.get_all_users()
    for user in c:
        if name == user[0]:
            return False, "Username taken"
    sql.add_user(name, hash(pw))
    return True, "User added"
