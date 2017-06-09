import eventlet
import sqlite3
eventlet.monkey_patch(os=False)
import os
from utils import constants
DIR = os.path.dirname(__file__) or '.'
DIR += '/'
constants.setDir(DIR)
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, send, SocketIOTestClient
import utils
from utils import gameManager as gm
from utils import users as u
from utils import sql
import thread
import sys


app = Flask(__name__)
app.secret_key = 'as9pdfuhasodifuhasiodfhuasiodfhuasiodfhuasodifuh'
socketio = SocketIO(app)

print 'work'

f = DIR + "data/users.db"
print f
if not os.path.exists(f) or os.path.getsize(f) == 0:
    db = sqlite3.connect(f)
    sql.init(db)
    db.close()
    # sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # no buffer
print 'Starting game thread'
gm.createGame('game1', size=2000, maxplayers=4, speed=5)
thread.start_new_thread(gm.run, ())
print 'Started game thread'

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('server'))
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
    return render_template('login.html', var = request.args.get('var'))

        # <form method="post">
        #     <p><input type=text name=username>
        #     <p><input type=submit value=Login>
        # </form>

def auth(user,pw):
    s = u.login(user,pw)
    if s == True:
        session["user"] = user
        print 'Done login'
        return redirect(url_for("server"))
    return redirect(url_for("login", var="Login failed"))

def reg(user,pw):
    s,m = u.register(user, pw)
    if s == True:
        session["user"] = user
        return redirect(url_for("server"))
    return redirect(url_for("login", var=m))

@app.route('/logout/')
def onlogout():
    session.pop('user')
    return redirect(url_for('home'))

@app.route('/game/', methods=['POST'])
def play():
    if request.method == 'POST':
        gamename = request.form['submit']
        #gamename = request.args.get('value')
        #print "GAME NAME: ", gamename
        if "user" not in session:
            return redirect(url_for('login'))
        settings = gm.getGame(gamename).settings
        return render_template('index.html', username=session['user'], gamename=gamename, settings=settings)
    return render_template('server.html', gamelist=gm.games)

@app.route('/servers/')
def server():
    if 'user' in session:
        return render_template('server.html', gamelist=gm.games)
    return redirect(url_for('login'))

@app.route('/user/')
def user():
    if 'user' in session:
        print 'IOOOOOOOOOOOOOOOOOOOOOOOOOOO'
        print session['user']
        return render_template('user.html', name=session['user'], wins = sql.getWins(  session['user']  ), losses=sql.getLosses(session['user']) )
    return resirect(url_for('login'))

@app.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['servername']
        players = int(request.form['numPlayers'])
        if players < 2 or players > 4:
            return render_template('create.html', err="invalid player size")
        speed = int(request.form['playerspeed'])
        size = int(request.form['size'])
        if size < 1000 or size > 10000:
            return render_template('create.html')
        gm.createGame(name, size=size, maxplayers=players, speed=speed)
        return render_template("index.html", username=session['user'], gamename=name, settings=gm.getGame(name).settings)
    return render_template('create.html')


@socketio.on('getdata')
def givedata(json):
    data = gm.data(json)
    if data is not None:
        emit('data', gm.data(json))

@socketio.on('sendinput')
def updatedata(json):
    gm.update(json)

@socketio.on('connect')
def ct():
    emit('getname')

@socketio.on('givename')
def newuser(json):
    print 'name got'
    print json
    gm.join(json['username'], json['gamename'])

if __name__ == '__main__':
    app.debug = True
    # test
    # tc = SocketIOTestClient(app, socketio)
    # tc.connect()
    # print 'connection done'
    # tc.emit('givename', {'username': 'me', 'gamename': 'game1'})
    # print 'givename done'
    # tc.emit('sendinput', {'username': 'me', 'key': 'A', 'event': 'keyboard'})
    # print 'sendinput done'
    # tc.emit('getdata', {'username': 'me', 'wallnums': {}})
    # print 'getdata done'

    socketio.run(app, host='0.0.0.0')
