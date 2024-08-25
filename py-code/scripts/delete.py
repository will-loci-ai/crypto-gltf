from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(b"aaaaaaaaaa")
f.decrypt(token)

import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = os.urandom(32)
iv = os.urandom(16)
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
encryptor = cipher.encryptor()
ct1 = encryptor.update(b"a secret message") + encryptor.finalize()
decryptor = cipher.decryptor()
print(decryptor.update(ct1) + decryptor.finalize())

import os

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

data = b"a secret message"
aad = b"authenticated but unencrypted data"
key = ChaCha20Poly1305.generate_key()
chacha = ChaCha20Poly1305(key)
nonce = os.urandom(12)
ct2 = chacha.encrypt(nonce, data, aad)
chacha.decrypt(nonce, ct2, aad)


for i in [10, 100, 200]:
    val = b"a" * i
    token = f.encrypt(val)
    print(len(token))
    print(len(token) - i)
    print()
print()