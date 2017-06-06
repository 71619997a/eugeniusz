import sqlite3

f = "data/users.db"

def db_f(func):
    def wrapped(*args, **kwargs):  # handles locking and weird db issues
        try:
            if isinstance(args[0], sqlite3.Connection):  # db is in args
                return func(*args, **kwargs)
        except IndexError:
            pass
        db = sqlite3.connect(f)
        v = func(db, *args, **kwargs)
        db.close()
        return v
    return wrapped


@db_f
def init(db):
    cur = db.cursor()
    cur.execute("CREATE TABLE users (username TEXT, password TEXT, score INTEGER)")
    db.commit()


@db_f
def add_user(db, user, password):
    cur = db.cursor()
    q = "INSERT INTO users VALUES (?, ?, 0)"

    cur.execute(q, (user, password))
    db.commit()


@db_f
def get_all_users(db):
    cur = db.cursor()
    res = cur.execute("SELECT * FROM users")
    L = []
    for row in res:
        L.append((row[0],row[1]))
    return L

@db_f
def incScore(db, player):
    cur = db.cursor()
    q = 'UPDATE users SET score = score + 1 WHERE username=?'
    cur.execute(q, (player.name,))
    db.commit()

@db_f
def getScore(db, user):
    cur = db.cursor()
    q = 'SELECT score FROM users WHERE username=?'
    cur.execute(q, (user,))
    return cur.fetchone()[0]
