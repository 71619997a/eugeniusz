import eventlet
eventlet.monkey_patch(os=False)
from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit
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
    if not 'username' in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        game.addUser(session['username'])
        return home()
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''
    
@socketio.on('getdata')
def givedata(json):
    emit('data', game.data(json))

if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # no buffer
    print 'Starting game thread'
    thread.start_new_thread(game.run, ())
    print 'Started game thread'
    app.debug = True
    socketio.run(app, host='0.0.0.0')
