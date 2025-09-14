from fastapi import Form


class UserInput():
    def __init__(
            self,
            face_name: str = Form(),
            email: str = Form(),
            password: str = Form(),
            is_active: bool = Form(True),
            role: str = Form("PHARMACIST")
    ):
        self.face_name = face_name
        self.email = email
        self.password = password
        self.is_active = is_active
        self.role = role

    def dict(self):
        return {
            "face_name": self.face_name,
            "email": self.email,
            "password": self.password,
            "is_active": self.is_active,
            "role": self.role
        }
