from flask import Flask, request, jsonify
from dataclasses import dataclass

app = Flask(__name__)

@dataclass
class User:
    username: str
    email: str
    role: str = "user"
    is_active: bool = True
    
    # In a real app, this would be DB model
    def save(self):
        print(f"Saving user {self.username} with role {self.role}")

# Mock DB
users = {
    "alice": User("alice", "alice@example.com")
}

@app.route('/api/users/<username>/update', methods=['POST'])
def update_user(username):
    user = users.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    
    # Vulnerability: Mass Assignment
    # The code iterates over ALL keys in the JSON payload and sets them on the user object.
    # An attacker can send {"role": "admin"} or {"is_superuser": true} even if they shouldn't be able to.
    
    for key, value in data.items():
        # Missing check: if key in ['role', 'is_admin'] and not current_user.is_admin: ...
        
        if hasattr(user, key):
            setattr(user, key, value)
    
    user.save()
    return jsonify({"message": "User updated", "user": user.__dict__})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    
    # Vulnerability: Mass Assignment in creation
    # Attacker sends {"username": "hacker", "password": "...", "role": "admin"}
    # The generic constructor or object mapper blindly accepts it.
    
    new_user = User(**data)
    users[new_user.username] = new_user
    new_user.save()
    
    return jsonify({"message": "User created", "role": new_user.role}), 201
