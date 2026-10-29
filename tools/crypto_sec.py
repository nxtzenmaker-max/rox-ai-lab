import hashlib
import base64
import urllib.parse
import secrets
import string

def get_hashes(text: str) -> dict:
    b = text.encode("utf-8")
    return {
        "MD5": hashlib.md5(b).hexdigest(),
        "SHA1": hashlib.sha1(b).hexdigest(),
        "SHA256": hashlib.sha256(b).hexdigest(),
        "SHA512": hashlib.sha512(b).hexdigest()
    }

def b64_encode(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")

def b64_decode(encoded_text: str) -> str:
    try:
        return base64.b64decode(encoded_text.encode("utf-8")).decode("utf-8", errors="replace")
    except Exception as e:
        return f"Decoding error: {e}"

def generate_strong_password(length: int = 16) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(secrets.choice(chars) for _ in range(length))

def hex_encode(text: str) -> str:
    return text.encode("utf-8").hex()

def hex_decode(hex_str: str) -> str:
    try:
        return bytes.fromhex(hex_str).decode("utf-8", errors="replace")
    except Exception as e:
        return f"Hex decode error: {e}"
