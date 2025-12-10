from flask import Flask, request, jsonify
from dataclasses import dataclass

app = Flask(__name__)

@dataclass
class User:
    username: str
    email: str
    role: str = "user"
    is_active: bool = True
    
    def save(self):
        print(f"Saving user {self.username} with role {self.role}")

users = {
    "alice": User("alice", "alice@example.com")
}

ALLOWED_UPDATE_FIELDS = {"email", "is_active"}
ALLOWED_CREATE_FIELDS = {"username", "email"}

@app.route('/api/users/<username>/update', methods=['POST'])
def update_user(username):
    user = users.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json or {}
    for key, value in data.items():
        if key in ALLOWED_UPDATE_FIELDS:
            setattr(user, key, value)
    
    user.save()
    return jsonify({"message": "User updated", "user": user.__dict__})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json or {}
    safe_data = {k: v for k, v in data.items() if k in ALLOWED_CREATE_FIELDS}
    
    new_user = User(**safe_data)
    users[new_user.username] = new_user
    new_user.save()
    
    return jsonify({"message": "User created", "role": new_user.role}), 201