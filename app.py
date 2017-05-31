import eventlet
eventlet.monkey_patch(os=False)
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, send
import utils
from utils import game
import thread
import os
import sys


app = Flask(__name__)
app.secret_key = 'as9pdfuhasodifuhasiodfhuasiodfhuasiodfhuasodifuh'
socketio = SocketIO(app)


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('play'))
    return render_template('login.html')

@app.route('/game')
def play():
    return render_template('index.html', username=session['username'])

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
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # no buffer
    print 'Starting game thread'
    thread.start_new_thread(game.run, ())
    print 'Started game thread'
    app.debug = True
    socketio.run(app, host='0.0.0.0')
