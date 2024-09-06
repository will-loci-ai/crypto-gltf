from __future__ import annotations

import binascii
import secrets
import time
from base64 import urlsafe_b64decode as b64d
from base64 import urlsafe_b64encode as b64e

from crypto_gltf.data.types import EncryptionResponse
from cryptography.fernet import InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pydantic import BaseModel


class AAD(BaseModel):
    """Additional associated data"""

    timestamp: bytes
    iv: bytes
    tag: bytes

    @classmethod
    def b64d(cls, aad_b64: bytes, block_size: int) -> AAD:
        try:
            data = b64d(aad_b64)
        except (TypeError, binascii.Error):
            raise InvalidToken
        timestamp, iv, tag = data[:8], data[8 : block_size // 8 + 8], data[-16:]
        return cls(timestamp=timestamp, iv=iv, tag=tag)

    @property
    def b64e(self) -> bytes:
        """URL and filesystem safe b64 format"""
        return b64e(self.timestamp + self.iv + self.tag)


def aes_gcm_encrypt(
    message: bytes, key: bytes
) -> EncryptionResponse[bytes, bytes, bytes]:
    """encrypt message using AES-GCM cipher"""

    current_time = int(time.time()).to_bytes(8, "big")
    algorithm = algorithms.AES(key)
    iv = secrets.token_bytes(algorithm.block_size // 8)
    cipher = Cipher(algorithm, modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encryptor.authenticate_additional_data(current_time)

    ciphertext = encryptor.update(message) + encryptor.finalize()
    aad = b64e(current_time + iv + encryptor.tag)

    assert len(aad) == 56

    return EncryptionResponse[bytes, bytes, bytes](
        ciphertext=ciphertext, aad=aad, key=key
    )


def aes_gcm_decrypt(ciphertext: bytes, aad_b64: bytes, key: bytes, ttl=None) -> bytes:
    """decrypt token using AES-GCM cipher"""

    algorithm = algorithms.AES(key)
    aad = AAD.b64d(aad_b64=aad_b64, block_size=algorithm.block_size)

    if ttl is not None:
        current_time = int(time.time())
        time_encrypted = int.from_bytes(aad.timestamp, "big")
        if time_encrypted + ttl < current_time or current_time + 60 < time_encrypted:
            # too old or created well before our current time + 1 h to account for clock skew
            raise InvalidToken

    cipher = Cipher(algorithm, modes.GCM(aad.iv, aad.tag), backend=default_backend())
    decryptor = cipher.decryptor()
    decryptor.authenticate_additional_data(aad.timestamp)
    return decryptor.update(ciphertext) + decryptor.finalize()
