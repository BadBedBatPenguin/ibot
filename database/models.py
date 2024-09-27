from uuid import uuid4

from settings import common_settings


class Item:
    def __init__(
        self,
        _id: str = str(uuid4()),
        name: str | None = None,
        description: str | None = None,
        category: str | None = None,
        subcategory: str | None = None,
        model: str | None = None,
        photo: str | None = None,
        photos: dict | None = None,
        price: str | None = None,
    ):
        self._id = _id
        self.name = name
        self.description = description
        self.category = category
        self.subcategory = subcategory
        self.model = model
        self.photo = photo
        self.photos = photos
        self.price = price

    def dict(self) -> dict:
        return {
            "_id": self._id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "subcategory": self.subcategory,
            "model": self.model,
            "photo": self.photo,
            "photos": self.photos,
            "price": self.price,
        }

    def photos_str(self) -> str:
        if not self.photos:
            return "нет"
        return f"<a href='{self.photos.get('url')}'>{self.photos.get('text', common_settings.default_hyperlink_text)}</a>"

    def __str__(self) -> str:
        return (
            f"Имя: {self.name}\nОписание: {self.description}\nЦена: {self.price}\n"
            f"Фотографии: {self.photos_str() if self.photos else 'нет'}"
        )
