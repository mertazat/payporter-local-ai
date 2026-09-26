from datetime import datetime


class UserProfileService:
    def __init__(self):
        self.profiles = {}

    def create_profile(self, user_id, name, email):
        if user_id in self.profiles:
            return {"error": "Profile already exists"}

        profile = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "phone": None,
            "address": None,
            "created_at": datetime.now().isoformat()
        }

        self.profiles[user_id] = profile
        return profile

    def get_profile(self, user_id):
        profile = self.profiles.get(user_id)

        if not profile:
            return {"error": "Profile not found"}

        return profile

    def update_profile(self, user_id, name=None, email=None, phone=None):
        profile = self.profiles.get(user_id)

        if not profile:
            return {"error": "Profile not found"}

        if name:
            profile["name"] = name

        if email:
            profile["email"] = email

        if phone:
            profile["phone"] = phone

        return profile

    def update_address(self, user_id, address):
        profile = self.profiles.get(user_id)

        if not profile:
            return {"error": "Profile not found"}

        profile["address"] = address
        return profile

    def delete_profile(self, user_id):
        if user_id not in self.profiles:
            return {"error": "Profile not found"}

        del self.profiles[user_id]

        return {"message": "Profile deleted successfully"}
