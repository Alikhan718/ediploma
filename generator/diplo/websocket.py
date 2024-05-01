# python3 -m flask --app websocket.py run --debug --port=5001
# run command # nohup python3 -m flask --app websocket.py run --debug --port=5001 &

import json
from flask import Flask
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_cors import CORS
from flask import request
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = Flask(__name__)
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
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        return connection, cursor

    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None, None


@socketio.on("connect")
def handle_connect():
    print("Client connected!")


@socketio.on("deploy_user_join")
def handle_user_join(university_id):
    print(f"UNIVERSITY_ID: {university_id}")
    connection, cursor = connectDatabase()
    if connection is None or cursor is None:
        print("Error connecting to the database.")
    print(f"User {university_id} joined!")

    cursor.execute(f"SELECT progress, max_progress, info_fetch_progress FROM diploma_generations WHERE university_id = {university_id} and finished_at is null")
    existing_record = cursor.fetchone()
    progress = 0
    max_progress = -1
    if existing_record:
        progress = existing_record[0]
        max_progress = existing_record[1]
        info_fetch_progress = existing_record[2]

        emit("deploy-api", {"progress": progress, "max_progress": max_progress, "cid": request.sid, "info_fetch_progress": info_fetch_progress})

    cursor.execute("LISTEN diploma_generations_notification;")

    while progress != max_progress:
        connection.poll()
        while connection.notifies and progress != max_progress:
            notify = connection.notifies.pop(0)
            data = json.loads(notify.payload)
            progress = data['progress']
            max_progress = data['max_progress']
            hash = data['hash']
            info_fetch_progress = data['info_fetch_progress']
            print(data)
            emit("deploy-api", {"progress": progress, "max_progress": max_progress, "hash": hash, "info_fetch_progress": info_fetch_progress})
            # print(f"Got NOTIFY: {notify.pid}, {notify.channel}, {notify.payload}")


@socketio.on("new_message")
def handle_new_message(message):
    print(f"New message: {message}")
    username = None
    for user in users:
        if users[user] == request.sid:
            username = user
    emit("chat", {"message": message, "username": username}, broadcast=True)


@app.route('/websocket', methods=['GET', "POST"])
def index():
    return "Hi page"



socketio.run(app, host="0.0.0.0", debug=False, port=5001, allow_unsafe_werkzeug=True)
