from fastapi import Form


class MedicineInput:
    def __init__(
            self,
            name: str = Form(...),
            description: str = Form(...),
            stock: int = Form(...)
    ):
        self.name = name
        self.description = description
        self.stock = stock

    def dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "stock": self.stock
        }
