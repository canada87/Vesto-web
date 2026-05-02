"""
Script per generare le icone PNG della PWA.
Richiede Pillow: pip install pillow
Eseguire una volta dalla cartella icons/: python generate_icons.py
"""
from PIL import Image, ImageDraw

def make_icon(size):
    img = Image.new("RGB", (size, size), color="#2E4057")
    draw = ImageDraw.Draw(img)
    margin = size // 6
    draw.ellipse([margin, margin, size - margin, size - margin], fill="#048A81")
    img.save(f"icon-{size}.png")
    print(f"Generata icon-{size}.png")

make_icon(192)
make_icon(512)
