import eventlet
eventlet.monkey_patch(os=False)
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import utils
from utils.game import data
import thread
import os
import sys


app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('getdata')
def givedata(json):
    emit(data(json))

if __name__ == '__main__':
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # no buffer
    print 'Starting game thread'
    thread.start_new_thread(utils.game.run, ())
    print 'Started game thread'
    app.debug = True
    socketio.run(app, host='0.0.0.0')
