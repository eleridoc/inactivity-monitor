# --------------------------------------------------------------------
# 🔐 ENCRYPTION UTILITIES FOR SECURE PASSWORD STORAGE
# --------------------------------------------------------------------

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from core.paths import KEY_PATH


def generate_key():
    """
    Generate a new Fernet encryption key and store it at KEY_PATH.

    The directory is created if it doesn't exist, and the file's permissions
    are restricted to read/write for the owner only (chmod 600).
    """
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)  # Ensure parent folder exists

    with open(KEY_PATH, "wb") as f:
        f.write(key)

    # Limit permissions to prevent unauthorized access
    os.chmod(KEY_PATH, 0o600)


def load_key():
    """
    Load the Fernet encryption key from disk.

    Returns:
        bytes: The key as bytes.

    Raises:
        FileNotFoundError: If the key file does not exist.
    """
    if not os.path.exists(KEY_PATH):
        raise FileNotFoundError(f"Encryption key not found at {KEY_PATH}")
    with open(KEY_PATH, "rb") as f:
        return f.read()


def encrypt_password(password: str) -> str:
    """
    Encrypt a plaintext password using Fernet encryption.

    Args:
        password (str): The password in plaintext.

    Returns:
        str: The encrypted password as a base64 string.
    """
    key = load_key()
    f = Fernet(key)
    encrypted = f.encrypt(password.encode())  # Encode to bytes, then encrypt
    return encrypted.decode()  # Return as string (base64 format)


def decrypt_password(encrypted: str) -> str:
    """
    Decrypt a previously encrypted password using Fernet.

    Args:
        encrypted (str): The base64-encoded encrypted password.

    Returns:
        str: The decrypted plaintext password.

    Raises:
        ValueError: If the token is invalid or corrupted.
    """
    key = load_key()
    f = Fernet(key)

    try:
        return f.decrypt(encrypted.encode()).decode()
    except InvalidToken:
        raise ValueError(
            "Invalid encryption token. The key may be incorrect or corrupted."
        )
