import os
import time
import requests
import cv2
from datetime import datetime

# Настройки сервера
SERVER_IP = '127.0.0.1'
SERVER_PORT = '5000'
SERVER_URL = f'http://{SERVER_IP}:{SERVER_PORT}'
CHECK_TASK_ENDPOINT = '/api/check_task'
UPLOAD_ENDPOINT = '/api/upload'
CLIENT_ID = 'client_1234'

# Настройки записи видео
VIDEO_DURATION = 600  # Продолжительность записи видео в секундах
VIDEO_FOLDER = 'videos'
FPS = 20  # Частота кадров

if not os.path.exists(VIDEO_FOLDER):
    os.makedirs(VIDEO_FOLDER)

def record_video(video_path):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, FPS, (int(cap.get(3)), int(cap.get(4))))

    start_time = time.time()
    while int(time.time() - start_time) < VIDEO_DURATION:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
        else:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f'Video saved: {video_path}')

def upload_video(video_path):
    with open(video_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(SERVER_URL + UPLOAD_ENDPOINT, files=files)
        if response.status_code == 201:
            print(f'Successfully uploaded: {video_path}')
            file.close()  # Закрываем файл перед удалением
            os.remove(video_path)  # Удалить файл после успешной загрузки
        else:
            print(f'Failed to upload: {video_path} with status code: {response.status_code}')

def check_task():
    response = requests.get(f'{SERVER_URL}{CHECK_TASK_ENDPOINT}', params={'client_id': CLIENT_ID})
    if response.status_code == 200:
        task = response.json()
        if task.get('record'):
            print('Record task received')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_path = os.path.join(VIDEO_FOLDER, f'video_{timestamp}.mp4')
            record_video(video_path)
            upload_video(video_path)
        else:
            print('No record task available')
    else:
        print(f'Failed to check task with status code: {response.status_code}')

def main():
    while True:
        print('Checking for task...')
        check_task()
        print('Sleeping for 1 minute')
        time.sleep(60)  # Спать 1 минуту

if __name__ == "__main__":
    main()