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
    allowed_fields = {"email"}  # username, role, is_active cannot be modified by regular users
    
    for key, value in data.items():
        if key in allowed_fields and hasattr(user, key):
            setattr(user, key, value)
    
    user.save()
    return jsonify({"message": "User updated", "user": user.__dict__})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    allowed_signup_fields = {"username", "email"}
    
    filtered = {k: v for k, v in data.items() if k in allowed_signup_fields}
    new_user = User(**filtered)
    
    users[new_user.username] = new_user
    new_user.save()
    
    return jsonify({"message": "User created", "role": new_user.role}), 201