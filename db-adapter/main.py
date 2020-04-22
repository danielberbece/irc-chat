import paho.mqtt.client as mqtt
import sys, os
import mysql.connector
from mysql.connector import errorcode
import json
from datetime import datetime, timezone
import time
import re

db_client = None

def log(message, error = False):
	dateTimeObj = datetime.now()
	timestampStr = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S")

	print(timestampStr + " " + message)

def get_current_time():
	local_time = datetime.now(timezone.utc).astimezone()
	return local_time.isoformat()


def get_channel(topic):
	return topic.split("/")[0]


def get_user(topic):
	return topic.split("/")[1]

def timestamp_valid(timestmp):
	try:
		dateutil.parser.parse(timestmp)
		return True
	except e:
		return False
		

def save(topic, payload):
	global db_client

	if db_client == None:
		db_client = create_db_client()
		if db_client == None:
			return

	cursor = db_client.cursor()

	insert_query = (
		"""INSERT INTO rooms (room_name, messages_no) VALUES (%s, %s)""")

	try:
		cursor.execute(insert_query, (get_channel(topic), 1))
	except Exception as e:
		get_messages_query = ("""SELECT messages_no FROM rooms WHERE room_name = %s""")
		update_query = ("""UPDATE rooms SET messages_no = %s WHERE room_name = %s""")
		cursor.execute(get_messages_query, (get_channel(topic),))
		for (messages_no,) in cursor:
			cursor.execute(update_query, (1 + messages_no, get_channel(topic)))

	db_client.commit()
	cursor.close()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc): 
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("#")

 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	log("Received a message by topic [" + msg.topic + "]")
	try:
		save(msg.topic, msg.payload)
	except Exception as e:
		log("Error on message received: " + str(e), True)


def create_db_client():
	print("Connecting to db")
	dbname = "chat"
	host = "db"

	conn = None

	try:
		conn = mysql.connector.connect(user='root', password='secret',
							  host=host,
							  database=dbname, auth_plugin='mysql_native_password')
		cursor = conn.cursor()
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with your user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(err)
	return conn


if __name__ == "__main__":

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	 
	client.connect("mosquitto", 1883, 60)
	 
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	client.loop_forever()