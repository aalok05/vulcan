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

@app.route('/api/users/<username>/update', methods=['POST'])
def update_user(username):
    user = users.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    allowed = ["email"]

    for key, value in data.items():
        if key in allowed:
            setattr(user, key, value)
    
    user.save()
    return jsonify({"message": "User updated", "user": user.__dict__})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json

    username = data.get("username")
    email = data.get("email")
    new_user = User(username=username, email=email)

    users[new_user.username] = new_user
    new_user.save()
    
    return jsonify({"message": "User created", "role": new_user.role}), 201