from __future__ import annotations

import base64

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet() -> Fernet:
    key = settings.SECRET_KEY.encode("utf-8")
    while len(key) < 32:
        key += key
    return Fernet(base64.urlsafe_b64encode(key[:32]))


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt(value: str) -> str:
    try:
        return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return ""


def mask_secret(value: str, show: int = 4) -> str:
    if len(value) <= show:
        return "*" * len(value)
    return value[:show] + "*" * (len(value) - show)
