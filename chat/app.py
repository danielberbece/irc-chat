#!/usr/bin/python3
from threading import Lock
import eventlet
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from flask_mqtt import Mqtt
from prometheus_flask_exporter import PrometheusMetrics
import random, string
import requests

async_mode = 'eventlet'

# Set debug active or not 
DEBUG = True

API_URL = 'http://api:8081'

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'mosquitto'
app.config['MQTT_BROKER_PORT'] = 1883

mqtt = Mqtt(app)
socketio = SocketIO(app, async_mode=async_mode)

metrics = PrometheusMetrics(app)
metrics.info('chat_info', 'Application info', version='1.0.3')

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/chat')
def chat_client_message(message):
   mqtt.publish("%s/%s"%(rooms()[0], session['username']), payload=bytes(message['data'], 'utf-8'))


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    message_room = message.topic.split('/')[0];
    print("message room is %s"%message_room)
    socketio.emit('log', {'data': message.payload.decode(), 'username': message.topic.split("/")[1]}, namespace='/chat',
        room=message_room)

# Logging only for debug mode
@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    if DEBUG:
        print(level, buf)


@socketio.on('join_room', namespace='/chat')
def join(message):
    print('Received join request for room ' + message['room'] + '. Previous room: ' + str(rooms()))
    for room in rooms():
        mqtt.unsubscribe('%s/#'%room)
        leave_room(room)
    join_room(message['room'])
    mqtt.subscribe('%s/#'%message['room'])
    emit('log',
         {'data': 'User %s entered room :%s:'%(session['username'], message['room'])}, room=rooms()[0])


@socketio.on('set_username', namespace='/chat')
def set_username(message):
    session['username'] = message['username']
    response = requests.post('%s/add_user'%API_URL, json={'username': message['username']})

    data = {'result': 'error'}
    if response.json()['result'] == 'success':
        data = {'data': 'New username is ' + message['username'], 'result': 'success'}

    emit('username_response', data, room=rooms()[0])


@socketio.on('connect', namespace='/chat')
def chat_client_connect():
    api_response = requests.get('%s/rooms'%API_URL)
    available_rooms = ['all']
    if api_response:
        available_rooms = api_response.json()
    for room in rooms():
        leave_room(room)
    join_room(available_rooms[0])
    mqtt.subscribe('%s/#'%rooms()[0])
    emit('on_connect', {'log': 'Welcome to Docker-Chat! Feel free to roam around :)', 'rooms': available_rooms}, room=rooms()[0])


@socketio.on('disconnect', namespace='/chat')
def chat_client_disconnect():
    if 'username' in session:
        requests.post('%s/remove_user'%API_URL, json={'username': session['username']})
        print('Client %s disconnected'%session['username'], request.sid)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
