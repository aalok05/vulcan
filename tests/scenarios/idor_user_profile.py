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
    # Vulnerability: IDOR / BOLA
    # The application checks if the user is logged in...
    current_user = get_current_user()
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401
    
    # ...BUT it fails to check if current_user.id == user_id
    # or if current_user is an admin.
    # Any logged-in user can query ANY user_id.
    
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Vulnerability: Excessive Data Exposure
    # Returning the entire user object including 'private_notes'
    return jsonify(user)

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    # Vulnerability: Path Traversal
    # LLM might catch this if it realizes the context of 'read_file' without sanitization
    # though Semgrep often catches generic traversals too.
    # The nuance here is the context of an API endpoint.
    import os
    file_path = f"./documents/{doc_id}"
    
    # Missing: if '..' in doc_id or not os.path.normpath...
    
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "File not found", 404
