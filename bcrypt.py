import os
import base64
import hashlib


def gensalt() -> bytes:
    return base64.b64encode(os.urandom(16))


def hashpw(password: bytes, salt: bytes) -> bytes:
    if not isinstance(salt, bytes):
        salt = salt.encode()
    dk = hashlib.pbkdf2_hmac("sha256", password, salt, 100000)
    return salt + b"$" + base64.b64encode(dk)


def checkpw(password: bytes, hashed: bytes) -> bool:
    if not isinstance(hashed, bytes):
        hashed = hashed.encode()
    salt, hash_part = hashed.split(b"$", 1)
    dk = hashlib.pbkdf2_hmac("sha256", password, salt, 100000)
    return base64.b64encode(dk) == hash_part