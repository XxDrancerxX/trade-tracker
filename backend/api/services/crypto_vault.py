import os
from cryptography.fernet import Fernet
# Not using it for now - might be useful later
# Usefull if we want to encrypt/decrypt data in other ways than full-disk encryption (e.g., encrypting specific fields in a database).
# Keep the key secret and safe. Store it in an environment variable or a secure vault.
# You can generate a key with: Fernet.generate_key()        

class CryptoVault:#Used by the serializer on write, and later by use-cases on read.
    """Field-level encryption using Fernet. Keep FIELD_ENCRYPTION_KEY in env."""
    def __init__(self, key: bytes | None = None):
        key = key or os.getenv("FIELD_ENCRYPTION_KEY", "").encode()
        if not key:
            raise RuntimeError("FIELD_ENCRYPTION_KEY missing")
        self._fernet = Fernet(key)

    def enc(self, plaintext: str) -> bytes:
        return self._fernet.encrypt(plaintext.encode())
   
    def dec(self, ciphertext: bytes) -> str:     
        # Accept either bytes (preferred) or str token for convenience
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode()
        # Decrypt first (returns bytes), then decode to utf-8 string
        return self._fernet.decrypt(ciphertext).decode()


