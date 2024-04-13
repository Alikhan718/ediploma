from time import sleep

from flask import Flask
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_cors import CORS
from flask import request
import psycopg2

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)

users = []
progresses = {}


def connectDatabase():
    # Database connection parameters
    host = "109.248.170.239"
    port = 5432
    database = "postgres"
    user = "postgres"
    password = "7Vow1e2v0v7x"
    # Establish a connection to the database
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print('connected')
        # Create a cursor object
        cursor = connection.cursor()
        return connection, cursor

    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None, None


@socketio.on("connect")
def handle_connect():
    print("Client connected!")


@socketio.on("user_join")
def handle_user_join(username):
    connection, cursor = connectDatabase()
    if connection is None or cursor is None:
        print("Error connecting to the database.")

    print(f"User {username} joined!")
    if request.sid not in users:
        users.append(request.sid)
        start = 0
        if username in progresses:
            start = progresses[username]

        for i in range(start, 100):
            sleep(0.1)

            progresses[username] = i + 1
            emit("chat", {"progress": i + 1, "cid": request.sid})
        emit("chat", {"progress": progresses[username], "cid": request.sid})
        users.remove(request.sid)


@socketio.on("new_message")
def handle_new_message(message):
    print(f"New message: {message}")
    username = None
    for user in users:
        if users[user] == request.sid:
            username = user
    emit("chat", {"message": message, "username": username}, broadcast=True)
