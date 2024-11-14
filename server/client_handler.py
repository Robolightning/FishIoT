import time
import schedule
from werkzeug.utils import secure_filename
from queue import Queue
from flask import request, jsonify
from flask_socketio import emit
from models import Video
import os
from common import app, socketio, db, Item

# Очередь задач
task_queue = Queue()

# Путь для загрузок
uploads_path = os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER'])
if not os.path.exists(uploads_path):
    os.makedirs(uploads_path)

# Подключение клиента
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: SID={request.sid}, Address={request.remote_addr}")
    emit('connected', {'message': 'Connected to server'})

# Обработка поступающих задач по расписанию
@app.route('/api/check_task', methods=['GET'])
def check_task():
    client_id = request.args.get('client_id')
    if not client_id:
        return jsonify({'record': False})
    
    # Проверяем есть ли задача для клиента
    if not task_queue.empty():
        task = task_queue.get()
        return jsonify({'record': True, 'task_id': task['task_id']})
    else:
        return jsonify({'record': False})

# Получение видео от клиента
@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        print('No file part in the request')
        return jsonify(status="error", message="No file part"), 400

    file = request.files['file']
    if file.filename == '':
        print('No selected file')
        return jsonify(status="error", message="No selected file"), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(uploads_path, filename)

    try:
        file.save(filepath)
        print(f"Video {filename} saved successfully at {filepath}")

        new_video = Video(filename=filename)
        db.session.add(new_video)
        db.session.commit()
        print(f"Video {filename} added to database")
    except Exception as e:
        print(f"Error saving video {filename}: {e}")
        return jsonify(status="error", message=str(e)), 500
    
    return jsonify(status="success", filename=filename), 201

def load_schedule():
    with app.app_context():
        print("Loading schedule...")
        schedule.clear()
        items = Item.query.all()
        for item in items:
            print(f"Scheduling job for {item.time}")
            schedule.every().day.at(item.time).do(add_task_to_queue, task_id=item.id)
        print("Schedule loaded")

def add_task_to_queue(task_id):
    task_queue.put({'task_id': task_id})
    print(f"Task {task_id} added to queue")

def schedule_jobs():
    while True:
        with app.app_context():
            schedule.run_pending()
            time.sleep(1)