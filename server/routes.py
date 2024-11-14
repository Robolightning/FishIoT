from flask import Blueprint, request, jsonify, send_from_directory
from models import db, Video
from werkzeug.utils import secure_filename
import os
from common import connections, Item, current_app
from client_handler import load_schedule, uploads_path

bp = Blueprint('routes', __name__)

@bp.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.all()
    items_list = [item.to_dict() for item in items]
    print(f"Retrieved items: {items_list}")  # Отладочный вывод
    return jsonify(items_list)

@bp.route('/api/items', methods=['POST'])
def create_item():
    data = request.json
    print(f"Received data for creation: {data}")
    try:
        for item_data in data:
            if item_data['id'] is None or item_data['id'] == 'null':
                new_item = Item(title=item_data['title'], time=item_data['time'])
                db.session.add(new_item)
            else:
                item = Item.query.get(item_data['id'])
                if item:
                    item.title = item_data.get('title', item.title)
                    item.time = item_data.get('time', item.time)
        db.session.commit()
        load_schedule()  # Перезагрузить расписание после сохранения данных
        print("Schedule reloaded after item creation")  # Отладочный вывод
    except Exception as e:
        print(f"Error inserting data: {e}")
        return jsonify(status="error", message=str(e)), 500
    return jsonify(status="success"), 201

@bp.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    print(f"Deleting item: {item}")
    try:
        db.session.delete(item)
        db.session.commit()
        load_schedule()  # Перезагрузить расписание после удаления данных
        print("Schedule reloaded after item deletion")  # Отладочный вывод
    except Exception as e:
        print(f"Error deleting data: {e}")
        return jsonify(status="error", message=str(e)), 500
    return jsonify({'message': 'Item deleted'})

@bp.route('/api/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify(status="error", message="No file part"), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(status="error", message="No selected file"), 400
    filename = secure_filename(file.filename)
    try:
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        new_video = Video(filename=filename)
        db.session.add(new_video)
        db.session.commit()
        print(f"Video uploaded: {filename}")  # Отладочный вывод
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify(status="error", message=str(e)), 500
    return jsonify(status="success", filename=filename), 201

@bp.route('/api/videos/<int:video_id>', methods=['DELETE'])
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    print(f"Deleting video: {video.filename}")
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], video.filename))
        db.session.delete(video)
        db.session.commit()
        print(f"Video deleted: {video.filename}")  # Отладочный вывод
    except Exception as e:
        print(f"Error deleting video: {e}")
        return jsonify(status="error", message=str(e)), 500
    return jsonify({'message': 'Video deleted'})

@bp.route('/download/<filename>', methods=['GET'])
def download_video(filename):
    file_path = os.path.join(uploads_path, filename)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return jsonify(status="error", message="File not found"), 404

    print(f"Downloading video: {filename} from {file_path}")
    return send_from_directory(
        uploads_path,
        filename,
        as_attachment=True,
        mimetype='video/mp4',
        conditional=True
    )

@bp.route('/api/start_recording', methods=['POST'])
def start_recording():
    message = 'record'
    print("Starting recording...")  # Отладочный вывод
    for ws in connections:
        print(f"Sending 'record' message to {ws}")  # Отладочный вывод
        try:
            ws.send(message)
        except Exception as e:
            print(f"Error sending 'record' message: {e}")  # Отладочный вывод
    return jsonify({'message': 'Recording started'}), 200
