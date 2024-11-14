from flask import Flask, current_app
from flask_socketio import SocketIO
from models import Item, db
import os

connections = []
client_ids = {}  # Добавим client_ids в common.py

# Убедимся, что путь к базе данных указан корректно
database_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

# Создание папки для базы данных, если её нет
if not os.path.exists("instance"):
    os.makedirs("instance")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)

socketio = SocketIO(app, ping_interval=20, ping_timeout=40)  # Убедимся, что тайм-ауты заданы правильно

# Создание папки для загрузок, если её нет
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])