class UserService:

    def change_password(self, user, old_password, new_password):
        if user["password"] != old_password:
            return "Eski şifre hatalı"

        if len(new_password) < 8:
            return "Yeni şifre en az 8 karakter olmalıdır"

        user["password"] = new_password
        return "Şifre başarıyla değiştirildi"


    def deactivate_user(self, user):
        if user["status"] == "ACTIVE":
            user["status"] = "INACTIVE"
            return "Kullanıcı devre dışı bırakıldı"

        return "Kullanıcı zaten aktif değil"
