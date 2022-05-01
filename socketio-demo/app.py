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


def background_thread():
    pass


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8083, debug=True)
