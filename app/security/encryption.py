"""
MEDICARE Security and Data Protection Layer.
Implements field-level local symmetric encryption (Fernet / AES-CBC + HMAC-SHA256)
for sensitive patient information, secure password hashing, and input sanitization.
"""
import os
import base64
import hashlib
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger("medicare.security")

class SecurityManager:
    """Manages encryption keys, cipher creation, and safe string handling."""

    def __init__(self, key_file_path: Path | str = None):
        self.key_file = Path(key_file_path) if key_file_path else Path(__file__).parent.parent.parent / "data" / ".medicare.key"
        self._cipher = None
        self._init_cipher()

    def _init_cipher(self):
        """Generates or loads local machine encryption key."""
        try:
            if self.key_file.exists():
                with open(self.key_file, "rb") as f:
                    key = f.read().strip()
            else:
                self.key_file.parent.mkdir(parents=True, exist_ok=True)
                key = Fernet.generate_key()
                with open(self.key_file, "wb") as f:
                    f.write(key)
                # On Unix/Android, restrict permissions
                try:
                    os.chmod(self.key_file, 0o600)
                except Exception:
                    pass
            self._cipher = Fernet(key)
        except Exception as e:
            logger.warning("Could not initialize local encryption cipher: %s. Running unencrypted.", e)
            self._cipher = None

    def encrypt_text(self, plain_text: str) -> str:
        """Encrypts sensitive string field into base64 ciphertext."""
        if not plain_text or not self._cipher:
            return plain_text
        try:
            token = self._cipher.encrypt(plain_text.encode("utf-8"))
            return token.decode("ascii")
        except Exception as e:
            logger.error("Encryption error: %s", e)
            return plain_text

    def decrypt_text(self, cipher_text: str) -> str:
        """Decrypts base64 ciphertext back to plaintext string."""
        if not cipher_text or not self._cipher:
            return cipher_text
        try:
            decrypted = self._cipher.decrypt(cipher_text.encode("ascii"))
            return decrypted.decode("utf-8")
        except Exception:
            # If not ciphertext or decryption fails, return as-is
            return cipher_text

    @staticmethod
    def hash_passcode(passcode: str, salt: bytes = None) -> tuple[str, str]:
        """Derives a secure SHA-256 hash with salt for optional application lock."""
        if not salt:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(passcode.encode("utf-8"))
        return (base64.b64encode(key).decode("ascii"), base64.b64encode(salt).decode("ascii"))

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitizes user input to prevent control code or delimiter injection."""
        if not input_str:
            return ""
        # Remove null bytes and non-printable control characters
        return "".join(c for c in str(input_str) if c.isprintable()).strip()
