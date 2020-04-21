import paho.mqtt.client as mqtt
import sys
 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	global room
	client.subscribe('%s/#'%room)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
 
def on_message(client, userdata, msg):
	global username
	username_msg = msg.topic.split('/')[1]
	if username_msg != username:
		print('\r' + username_msg + "> " + msg.payload.decode("utf-8"))
		print('ME> ', end='', flush=True)
 
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect("127.0.0.1", 1883, 60)
 
username = input('Enter your username: ')
room = input('Select chatroom: ')

client.loop_start()

while True:
	message = input('ME> ')
	client.publish("%s/%s"%(room, username), payload=bytes(message, 'utf-8'))