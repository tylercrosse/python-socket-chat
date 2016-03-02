import random
import string
import time
import names
from threading import Thread
from flask import Flask, render_template
import socketio
import eventlet
eventlet.monkey_patch()

async_mode = 'eventlet'

sio = socketio.Server(logger=True, async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'
thread = None

@app.route('/')
def index():
    return render_template('index.html')


users = {}

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@sio.on('connect', namespace='/lobby')
def connect_lobby(sid, environ):
    username = {sid: names.get_first_name()}
    users.update(username) # add new username to users
    print '*' * 50
    print 'connect'
    print username
    print users
    print '*' * 50
    sio.emit('users list', {'users': users, 'username': username}, namespace='/lobby')


    @sio.on('lobby message', namespace='/lobby')
    def lobby_message(sid, message):
        print '#' * 50
        print users[sid]
        print message
        print '#' * 50
        sio.emit('lobby message', {'username': users[sid], 'message': message}, namespace='/lobby')


#   // 'play button'
#     // -> if no rooms w/ 1 player, create room
#       // -> lobby chat while waiting for other players
#     // -> if room w/ 1 player, join room, leave lobby
#       // -> game chat begins


    @sio.on('join game', namespace='/lobby')
    def join_game(sid):
        print 'x' * 50
        print users[sid]
        try:
            sio.manager.rooms['/games']
            rooms = sio.manager.rooms['/games']
            print 'there are some rooms'
            print rooms
            for key in rooms:
                if len(rooms[key]) < 2:
                    print 'room room entered'
                    sio.enter_room(sid, key, '/games')
                    sio.emit('game joined', {'game': key, 'user': {sid: users[sid]}}, namespace='/lobby')
                    # entered game w/ 2 players, leave lobby?
                else:
                    print 'no rooms with waiting player, new one created'
                    create_room(sid)
        except KeyError:
            print 'no rooms, new one created'
            create_room(sid)
        print 'x' * 50

    def create_room(sid):
        room_num = id_generator()
        sio.enter_room(sid, room_num, '/games')
        print sid
        sio.emit('game created', {'game': room_num, 'user': {sid: users[sid]}}, namespace='/lobby')


# list(sio.manager.get_namespaces())
# list(sio.manager.get_participants('/', None))
# sio.user = [names.get_first_name()]


    @sio.on('disconnect')
    def disconnect(sid):
        print '8' * 50
        print users
        del users[sid]
        print 'print: lobby disconnect'
        print users
        sio.emit('users list', users, namespace='/lobby')


if __name__ == '__main__':
    # deploy with eventlet
    eventlet.wsgi.server(eventlet.listen(('', 7000)), app)
