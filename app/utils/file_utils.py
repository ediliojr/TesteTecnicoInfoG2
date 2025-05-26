import base64
import uuid
import os
from fastapi import HTTPException

IMAGE_FOLDER = "app/static/images"


def save_base64_image(image_base64: str) -> str:
    try:
        os.makedirs(IMAGE_FOLDER, exist_ok=True)
        image_data = base64.b64decode(image_base64.split(",")[-1])
        filename = f"{uuid.uuid4().hex}.png"
        filepath = os.path.join(IMAGE_FOLDER, filename)

        with open(filepath, "wb") as f:
            f.write(image_data)

        return filename
    except Exception as e:
        raise HTTPException(status_code=400, detail="Imagem inválida")


def delete_image(image_path):
    if image_path:
        try:
            os.remove(os.path.join(IMAGE_FOLDER, image_path))
        except FileNotFoundError:
            pass
