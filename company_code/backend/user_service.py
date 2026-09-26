class UserService:

    def change_password(self, user, old_password, new_password):
        if user["password"] != old_password:
            raise ValueError("Old password is incorrect")

        if len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters")

        user["password"] = new_password

        return {
            "status": "success",
            "message": "Password changed successfully"
        }

    def update_email(self, user, new_email):
        if "@" not in new_email:
            raise ValueError("Invalid email address")

        user["email"] = new_email

        return {
            "status": "success",
            "new_email": new_email
        }
