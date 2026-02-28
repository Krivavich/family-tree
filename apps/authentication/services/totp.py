import base64
import hashlib
import hmac
import struct
import time


def _normalize_base32(secret: str) -> bytes:
    pad = "=" * (-len(secret) % 8)
    return base64.b32decode((secret.upper() + pad).encode("utf-8"))


def totp_now(secret: str, period: int = 30, digits: int = 6, for_time: int | None = None) -> str:
    counter = int((for_time or int(time.time())) / period)
    key = _normalize_base32(secret)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % (10**digits)
    return str(code_int).zfill(digits)


def verify_totp(secret: str, code: str, skew_steps: int = 1, period: int = 30) -> bool:
    now = int(time.time())
    for step in range(-skew_steps, skew_steps + 1):
        if hmac.compare_digest(totp_now(secret, period=period, for_time=now + step * period), code):
            return True
    return False
