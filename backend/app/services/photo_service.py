from PIL import Image
import io
import os

PHOTOS_DIR = os.getenv("PHOTOS_DIR", "/app/photos")
MAX_SIZE = 400
JPEG_QUALITY = 78


def save_photo(item_id: str, file_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(file_bytes))
    img = img.convert("RGB")
    img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
    filename = f"photo_{item_id}.jpg"
    path = os.path.join(PHOTOS_DIR, filename)
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    img.save(path, "JPEG", quality=JPEG_QUALITY)
    return filename


def delete_photo(item_id: str) -> None:
    path = os.path.join(PHOTOS_DIR, f"photo_{item_id}.jpg")
    if os.path.exists(path):
        os.remove(path)
