async_mode = 'eventlet'

import eventlet
eventlet.monkey_patch()

import names
import time
from threading import Thread
from flask import Flask, render_template
import socketio

sio = socketio.Server(logger=True, async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'
thread = None

@app.route('/')
def index():
    return render_template('index.html')

# @sio.on('disconnect request', namespace='/test')
# def disconnect_request(sid):
#     sio.disconnect(sid, namespace='/test')

# 'join lobby', 'lobby message', 'user joined', 'user left'
# list(sio.manager.get_namespaces())
# list(sio.manager.get_participants('/', None))
# sio.user = [names.get_first_name()]

users = {}

@sio.on('connect')
def connect(sid, environ):
    username = {sid: names.get_first_name()}
    users.update(username) # add new username to users
    print '*' * 50
    print 'connect'
    print username
    print users
    print '*' * 50
    sio.emit('users list', {'users': users, 'username': username})


    @sio.on('lobby message')
    def lobby_message(sid, message):
        print '#' * 50
        print users[sid]
        print message
        print '#' * 50
        sio.emit('lobby message', {'username': users[sid], 'message': message})


@sio.on('disconnect')
def disconnect(sid):
    print '8' * 50
    print users
    del users[sid]
    print 'disconnect'
    print users
    print '8' * 50
    sio.emit('users list', users)


# @sio.on('my broadcast event', namespace='/test')
# def test_broadcast_message(sid, message):
#     sio.emit('my response', {'data': message['data']}, namespace='/test')


# @sio.on('join', namespace='/test')
# def join(sid, message):
#     sio.enter_room(sid, message['room'], namespace='/test')
#     sio.emit('my response', {'data': 'Entered room: ' + message['room']},
#              room=sid, namespace='/test')


# @sio.on('leave', namespace='/test')
# def leave(sid, message):
#     sio.leave_room(sid, message['room'], namespace='/test')
#     sio.emit('my response', {'data': 'Left room: ' + message['room']},
#              room=sid, namespace='/test')


# @sio.on('close room', namespace='/test')
# def close(sid, message):
#     sio.emit('my response',
#              {'data': 'Room ' + message['room'] + ' is closing.'},
#              room=message['room'], namespace='/test')
#     sio.close_room(message['room'], namespace='/test')


# @sio.on('my room message', namespace='/test')
# def send_room_message(sid, message):
#     sio.emit('my response', {'data': message['data']}, room=message['room'],
#              namespace='/test')





if __name__ == '__main__':
    # deploy with eventlet
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('', 7000)), app)
