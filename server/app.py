from flask import render_template, request
import threading
import json

from models import db, Video
from routes import bp as routes_bp
from common import connections, client_ids
from client_handler import load_schedule, Item, app, socketio, schedule_jobs

# Регистрация маршрутов
app.register_blueprint(routes_bp)

with app.app_context():
    db.create_all()
    load_schedule()  # Инициализация расписания при старте

@app.route('/')
def index():
    print("Loading index page...")
    items = Item.query.all()
    print(f"Items from database: {items}")
    videos = Video.query.all()
    print(f"Videos from database: {videos}")
    return render_template('index.html', items=items, videos=videos)

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: SID={request.sid}, Address={request.remote_addr}")
    connections.append(request.sid)
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: SID={request.sid}, Address={request.remote_addr}")
    connections.remove(request.sid)
    if request.sid in client_ids:
        del client_ids[request.sid]
    print(f'Client disconnected: {request.sid}')

@socketio.on('message')
def handle_message(message):
    print(f'Received message from SID={request.sid}: {message}')
    try:
        data = json.loads(message)
        if data['type'] == 'ID':
            client_id = data['id']
            client_ids[request.sid] = client_id
            print(f'Client ID {client_id} registered for SID {request.sid}')
        elif data['type'] == 'record':
            client_id = data.get('id')
            if client_id in client_ids.values():
                target_sid = list(client_ids.keys())[list(client_ids.values()).index(client_id)]
                socketio.emit('record', to=target_sid)
                print(f'Sent record command to client {client_id} with SID {target_sid}')
            else:
                print(f'Client ID {client_id} not found')
    except json.JSONDecodeError:
        print(f'Invalid JSON message: {message}')
    except Exception as e:
        print(f'Error handling message: {e}')


if __name__ == "__main__":
    threading.Thread(target=schedule_jobs).start()
    print("Starting server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)