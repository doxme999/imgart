from flask import Flask, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, send, emit
from threading import Lock
import os
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

clients = 0
typing_users = set()
lock = Lock()

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/get-emojis')
def get_emojis():
    emoji_dir = os.path.join(app.static_folder, "emojis")  # Folder where emojis are stored
    emojis = [url_for('static', filename=f"emojis/{img}") for img in os.listdir(emoji_dir) if img.endswith((".png", ".jpg", ".gif"))]
    return jsonify(emojis)  # Returns the list of images as JSON

@socketio.on('connect')
def handle_connect():
    global clients
    with lock:
        clients += 1
    update_status()

@socketio.on('disconnect')
def handle_disconnect():
    global clients
    with lock:
        clients -= 1
        typing_users.discard(request.sid)
    update_status()

@socketio.on('message')
def handle_message(msg):
    # Message processing (text or image)
    send({
        'username': msg['username'],
        'usercolor': msg['usercolor'],
        'text': msg.get('text', ''),  # Use get() with a default value
        'image': msg.get('image', None)  # If it's an image, it's here
    }, broadcast=True)
    # The user stops typing after sending
    with lock:
        if request.sid in typing_users:
            typing_users.remove(request.sid)
    update_status()

@socketio.on('typing')
def handle_typing(is_typing):
    with lock:
        if is_typing:
            typing_users.add(request.sid)
        else:
            typing_users.discard(request.sid)
    update_status()

def update_status():
    with lock:
        if typing_users:
            count = len(typing_users)
            status = f"{count} user{' is' if count == 1 else 's are'} typing..."
        else:
            status = f"{clients} user{' connected' if clients == 1 else ' users connected'}"
    emit('status', status, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)