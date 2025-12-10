from flask import Flask, request, jsonify
from textwrap import dedent
import os

app = Flask(__name__)

users_db = {
    1: {"id": 1, "username": "admin", "email": "admin@example.com", "private_notes": "Server keys: XYZ"},
    2: {"id": 2, "username": "alice", "email": "alice@example.com", "private_notes": "My diary..."},
    3: {"id": 3, "username": "bob", "email": "bob@example.com", "private_notes": "I hate my boss"}
}

def get_current_user():
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

    sanitized_user = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }

    return jsonify(sanitized_user)

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    base_dir = os.path.abspath("./documents")
    target_path = os.path.abspath(os.path.join(base_dir, doc_id))
    if not target_path.startswith(base_dir + os.sep):
        return "Invalid document ID", 400
    try:
        with open(target_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "File not found", 404