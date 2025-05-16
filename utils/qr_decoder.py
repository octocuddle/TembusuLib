# utils/qr_decoder.py

from pyzbar.pyzbar import decode
from PIL import Image
import io

def decode_qr(image_path: str) -> str | None:
    """
    Attempts to decode a QR code from the given image file path.
    Returns the first detected QR code content, or None.
    """
    try:
        image = Image.open(image_path).convert("RGB")
        results = decode(image)
        if results:
            return results[0].data.decode("utf-8")
        return None
    except Exception as e:
        print(f"[QR DECODER ERROR] {e}")
        return None