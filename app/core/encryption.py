"""
Encryption utilities for sensitive data storage.
"""
from cryptography.fernet import Fernet
from app.core.settings import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """
    Derive a Fernet-compatible key from the SECRET_KEY.
    """
    # Use SECRET_KEY to derive a 32-byte key for Fernet
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value.
    
    Args:
        value: Plain text string to encrypt
        
    Returns:
        Encrypted string (base64 encoded)
    """
    if not value:
        return ""
    
    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(value.encode())
    return encrypted.decode()


def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt an encrypted string value.
    
    Args:
        encrypted_value: Encrypted string (base64 encoded)
        
    Returns:
        Decrypted plain text string
    """
    if not encrypted_value:
        return ""
    
    key = get_encryption_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_value.encode())
    return decrypted.decode()
