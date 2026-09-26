import hashlib
import secrets
from datetime import datetime, timedelta


class AuthService:
    def __init__(self):
        self.users = {}
        self.sessions = {}

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, role="user"):
        if username in self.users:
            return {"error": "User already exists"}

        self.users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "active": True
        }

        return {"message": "User registered successfully"}

    def login(self, username, password):
        user = self.users.get(username)

        if not user:
            return {"error": "User not found"}

        if not user["active"]:
            return {"error": "User account is disabled"}

        if user["password"] != self.hash_password(password):
            return {"error": "Invalid password"}

        token = secrets.token_hex(16)

        self.sessions[token] = {
            "username": username,
            "expires_at": datetime.now() + timedelta(hours=1)
        }

        return {"token": token}

    def validate_session(self, token):
        session = self.sessions.get(token)

        if not session:
            return False

        if datetime.now() > session["expires_at"]:
            del self.sessions[token]
            return False

        return True

    def logout(self, token):
        if token in self.sessions:
            del self.sessions[token]

        return {"message": "Logged out successfully"}
