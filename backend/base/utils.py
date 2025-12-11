import qrcode
from io import BytesIO
import base64

def generate_qr_base64(url):
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"
