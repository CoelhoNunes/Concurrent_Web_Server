from flask import Flask, request, render_template, jsonify
import logging
import threading

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for users and messages
users = set()
chat_histories = {}  # Stores conversations per user
client_lock = threading.Lock()  # Ensure thread-safe operations


@app.route('/')
def index():
    """Serve the chat interface."""
    logging.info("Homepage accessed.")
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    """Register a new username."""
    username = request.form.get('username')
    if username:
        with client_lock:  # Thread-safe access to shared resources
            users.add(username)
            if username not in chat_histories:
                chat_histories[username] = []  # Initialize chat history for the new user
            logging.info(f"User registered: {username}")
        return jsonify({"status": "User registered", "username": username, "users": list(users)}), 200
    else:
        return jsonify({"error": "Username is required"}), 400


@app.route('/chat', methods=['POST'])
def chat():
    """Handle a message from a registered user."""
    username = request.form.get('username')
    message = request.form.get('message')

    if username and message and username in users:
        with client_lock:  # Ensure thread-safe access to chat histories
            user_message = f"{username}: {message}"
            chat_histories[username].append(user_message)
            logging.info(f"Message from {username}: {message}")

            # Server response to simulate interaction
            server_response = (f"Server: Thanks for your message, {username}! Soon I'll be enhanced by AI to have "
                               f"better conversations!")
            chat_histories[username].append(server_response)
            logging.info("Server response sent.")

        return jsonify({"user_message": user_message, "server_response": server_response}), 200
    else:
        return jsonify({"error": "Username and valid message required, or user is not registered."}), 400


@app.route('/messages/<username>', methods=['GET'])
def get_messages(username):
    """Return chat history for a specific user."""
    with client_lock:  # Ensure thread-safe read access
        return jsonify(chat_histories.get(username, [])), 200


@app.route('/delete/<username>', methods=['POST'])
def delete_chat(username):
    """Delete chat history for a specific user."""
    with client_lock:
        if username in chat_histories:
            chat_histories[username] = []  # Clear user's chat history
            logging.info(f"Chat history cleared for {username}")
            return jsonify({"status": f"Chat history cleared for {username}"}), 200
        else:
            return jsonify({"error": "User not found"}), 404


@app.route('/users', methods=['GET'])
def get_users():
    """Return list of all registered users."""
    with client_lock:  # Ensure thread-safe read access
        return jsonify(list(users)), 200


if __name__ == '__main__':
    # Running with Gunicorn will replace this section in production
    app.run(host='0.0.0.0', port=5000)
