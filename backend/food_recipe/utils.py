from PIL import Image
import io
import secrets
import string

def random_alphanumeric_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def random_numeric_string(length: int) -> str:
    characters = string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def optimize_picture(picture):
    img = Image.open(picture)

    width, height = img.size
    new_width = min(width, 1290)
    new_height = int((new_width / width) * height)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    img = img.convert("RGB")
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=60)
    output.seek(0)

    return output.read()
