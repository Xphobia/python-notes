
import time
import nonblock
import subprocess
from threading import Lock

import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

socketio = SocketIO()
socketio.init_app(app, async_mode='eventlet', cors_allowed_origins='*')


@socketio.on('connect')
def connect():
    print('Client connected')


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')


@socketio.on('message')
def handle_message(msg):
    print('Message: ' + msg)
    send(msg, broadcast=False)


@socketio.on('command', namespace='/shell')
def handle_command(command):
    print('Command: ' + command)
    emit('server_response', 'hello world!')
    with Lock():
        thread = socketio.start_background_task(target=background_thread, command=command)
        thread.join()


def background_thread(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        time.sleep(1)
        error = nonblock.nonblock_read(process.stderr)
        if not error:
            break
        else:
            print("command: %s error==>" % command)
            print(error)
            with app.test_request_context('/'):
                socketio.emit('server_response', error, namespace='/shell')

    line = ''
    while True:
        time.sleep(0.5)
        output = nonblock.nonblock_read(process.stdout, 256)
        if output is None:
            break
        if output:
            idx = output.find("\n")
            if idx == -1:
                line += output
            else:
                line += output[:idx]
                msg = line.strip()
                print(msg)
                with app.test_request_context('/'):
                    socketio.emit('server_response', msg, namespace='/shell')
                line = output[idx:]
        else:
            print('nothing to read !')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8083, debug=True)
