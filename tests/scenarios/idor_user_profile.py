from flask import Flask, request, jsonify
from textwrap import dedent

app = Flask(__name__)

# Mock database
users_db = {
    1: {"id": 1, "username": "admin", "email": "admin@example.com", "private_notes": "Server keys: XYZ"},
    2: {"id": 2, "username": "alice", "email": "alice@example.com", "private_notes": "My diary..."},
    3: {"id": 3, "username": "bob", "email": "bob@example.com", "private_notes": "I hate my boss"}
}

def get_current_user():
    # Mock auth - returns User ID 3 (Bob)
    return {"id": 3, "username": "bob"}

@app.route('/api/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401

    if current_user["id"] != user_id:
        return jsonify({"error": "Forbidden"}), 403

    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user)

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    import os
    file_path = f"./documents/{doc_id}"

    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "File not found", 404