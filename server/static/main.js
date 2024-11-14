function addRow() {
    const scheduleTable = document.getElementById('scheduleTable').querySelector('tbody');
    const row = scheduleTable.insertRow();
    row.dataset.id = null;
    const cell1 = row.insertCell(0);
    const cell2 = row.insertCell(1);
    const cell3 = row.insertCell(2);
    cell1.innerHTML = '<input type="text" placeholder="Название">';
    cell2.innerHTML = '<input type="time">';
    cell3.innerHTML = '<button class="delete-btn" onclick="deleteRow(this)">Удалить</button>';
}

function deleteRow(button) {
    const row = button.parentNode.parentNode;
    const id = row.dataset.id;
    if (id) {
        fetch('/api/items/' + id, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            row.remove();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    } else {
        row.remove();
    }
}

function saveTable() {
    const scheduleTable = document.getElementById('scheduleTable').querySelector('tbody');
    const rows = scheduleTable.rows;
    const data = [];
    for (let i = 0; i < rows.length; i++) {
        const id = rows[i].dataset.id || null;
        const title = rows[i].cells[0].children[0].value;
        const time = rows[i].cells[1].children[0].value;
        data.push({ id, title, time });
    }

    console.log('Sending data:', data);  // Вывод для отладки

    fetch('/api/items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        location.reload();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const uploadFileInput = document.getElementById('uploadFile');

    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to WebSocket server');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from WebSocket server');
    });

    socket.on('record', (message) => {
        console.log('Received:', message);
        if (message === 'record') {
            alert('Recording started');
        }
    });

    document.getElementById('addRowButton').addEventListener('click', addRow);

    function deleteVideo(button) {
        const videoDiv = button.parentNode;
        const videoId = videoDiv.dataset.id;

        fetch('/api/videos/' + videoId, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            videoDiv.remove();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    window.deleteVideo = deleteVideo;

    function uploadFile() {
        const file = uploadFileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        fetch('/api/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            location.reload();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    window.uploadFile = uploadFile;
});
