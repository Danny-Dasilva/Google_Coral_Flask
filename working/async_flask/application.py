from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from threading import Thread, Event
from UpdateString import RandomThread

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False
socketio = SocketIO(app, async_mode='threading')
aSync = RandomThread(socketio)

@app.route('/')
def index():
    return render_template('index.html')


def socketServer():
    socketio.run(app, host="0.0.0.0")

if __name__ == '__main__':
    socketServer()

