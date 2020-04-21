from sanic import Sanic
from sanic.response import json
import mysql.connector
from mysql.connector import errorcode
from time import sleep

app = Sanic()
db_conn = None

def create_db_client():
    print("Connecting to db")
    dbname = "chat"
    host = "db"

    TABLES = {}
    TABLES['rooms'] = (
        "CREATE TABLE `rooms` ("
        "  `room_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `room_name` varchar(100) NOT NULL,"
        "  `messages_no` int(10) NULL,"
        "  PRIMARY KEY (`room_no`), UNIQUE KEY `room_name` (`room_name`)"
        ") ENGINE=InnoDB")

    TABLES['users'] = (
        "CREATE TABLE `users` ("
        "  `user_no` int(4) NOT NULL AUTO_INCREMENT,"
        "  `user_name` varchar(40) NOT NULL,"
        "  `user_password` varchar(40) NOT NULL,"
        "  `messages_no` int(10) NULL,"
        "  PRIMARY KEY (`user_no`), UNIQUE KEY `user_name` (`user_name`)"
        ") ENGINE=InnoDB")
    conn = None

    tryagain = True
    while tryagain:
        tryagain = False
        try:
            conn = mysql.connector.connect(user='root', password='secret',
                                  host=host,
                                  database=dbname, auth_plugin='mysql_native_password')
            cursor = conn.cursor()

            for table_name in TABLES:
                table_description = TABLES[table_name]
                try:
                    print("Creating table {}: ".format(table_name), end='')
                    cursor.execute(table_description)
                except mysql.connector.Error as err:
                    if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                        print("already exists.")
                    else:
                        print(err.msg)
                else:
                    print("OK")
            conn.commit()
            cursor.close()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            elif err.errno == 2003:     # interface error
                tryagain = True
                sleep(1)
            else:
                print(err)
    return conn

def gain_conn():
    global db_conn
    if db_conn is None:
        db_conn = create_db_client()
    if db_conn is None:
        print('Err: Database connection is still none')
        exit(0)

@app.route("/users", methods=['GET'])
async def get_users(request):
    gain_conn()
    users = []
    cursor = db_conn.cursor()
    query = ("SELECT user_name FROM users")
    cursor.execute(query)
    for (user_name,) in cursor:
        users.append(user_name)
    cursor.close()
    return json(users)


@app.route("/rooms", methods=['GET'])
async def get_rooms(request):
    gain_conn()
    rooms = []

    cursor = db_conn.cursor()
    query = ("SELECT room_name FROM rooms")
    cursor.execute(query)
    for (room_name,) in cursor:
        rooms.append(room_name)
    cursor.close()
    return json(rooms)


@app.route("/add_user", methods=['POST'])
async def add_user(request):
    gain_conn()
    data = request.json
    response = {'result': 'error'}
    if data and data['username']:
        add_user_q = ("INSERT INTO users "
              "(user_name, user_password, messages_no) "
              "VALUES (%(user_name)s, %(user_password)s, %(messages_no)s)")
        add_user_data = {'user_name': data['username'], 'user_password': 'pass', 'messages_no': 0}
        cursor = db_conn.cursor()
        try:
            cursor.execute(add_user_q, add_user_data)
            db_conn.commit()
            response['result'] = 'success'
        except Exception as e:
            print('Invalid insert for username ' + data['username'] + '\n' + str(e))
        finally:
            cursor.close()

    return json(response)

@app.route("/remove_user", methods=['POST'])
async def remove_user(request):
    gain_conn()
    data = request.json
    response = {'result': 'error'}
    if data and data['username']:
        delete_user_q = ("DELETE FROM users WHERE user_name = %(user_name)s")
        delete_user_data = {'user_name': data['username']}
        cursor = db_conn.cursor()
        try:
            cursor.execute(delete_user_q, delete_user_data)
            db_conn.commit()
            response['result'] = 'success'
        except Exception as e:
            print('Invalid delete for username ' + data['username'] + '\n' + str(e))
        finally:
            cursor.close()

    return json(response)

@app.route("/")
async def root(request):
    return json({"Docker-chat": "api"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
    if db_conn is not None:
        db_conn.close()
