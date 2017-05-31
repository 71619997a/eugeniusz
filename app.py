import eventlet
import sqlite3
eventlet.monkey_patch(os=False)
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, send
import utils
from utils import game
from utils import users as u
from utils import sql
import thread
import os
import sys

app = Flask(__name__)
app.secret_key = 'as9pdfuhasodifuhasiodfhuasiodfhuasiodfhuasodifuh'
socketio = SocketIO(app)

@app.route('/')
def home():
    if "user" in session:
        return redirect(url_for('play'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #session['user'] = request.form['username']
        user = request.form['username']
        pw = request.form['password']
        if request.form.get('login'):
            print 'Login'
            return auth(user,pw)
        elif request.form.get('register'):
            print 'Register'
            return reg(user,pw)
        print 'None??'
        return redirect(url_for('home'))
    return render_template('login.html')

        # <form method="post">
        #     <p><input type=text name=username>
        #     <p><input type=submit value=Login>
        # </form>

def auth(user,pw):
    s = u.login(user,pw)
    if s == True:
        session["user"] = user
        print 'Done login'
        return redirect(url_for("play"))
    return redirect(url_for("login", var="Login failed"))

def reg(user,pw):
    s,m = u.register(user, pw)
    if s == True:
        session["user"] = user
        return redirect(url_for("play"))
    return redirect(url_for("login", var=m))

@app.route('/game')
def play():
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['user'])

@socketio.on('getdata')
def givedata(json):
    print 'client requested data'
    emit('data', game.data(json))

@socketio.on('sendinput')
def updatedata(json):
    print 'client sent data'
    game.update(json)

@socketio.on('connect')
def ct():
    emit('getname')

@socketio.on('givename')
def newuser(json):
    print 'name got'
    game.addUser(json['username'])

if __name__ == '__main__':
    f = "data/users.db"
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        db = sqlite3.connect(f)
        sql.init(db)
        db.close()
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # no buffer
    print 'Starting game thread'
    thread.start_new_thread(game.run, ())
    print 'Started game thread'
    app.debug = True
    socketio.run(app, host='0.0.0.0')
