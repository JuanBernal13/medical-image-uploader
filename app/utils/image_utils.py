import io
from typing import Tuple
from PIL import Image

def get_image_dimensions(file_content: bytes) -> Tuple[int, int]:
    try:
        with Image.open(io.BytesIO(file_content)) as img:
            return img.width, img.height
    except Exception:
        return 0, 0
