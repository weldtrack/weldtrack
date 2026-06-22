import base64
import hashlib
import hmac
import secrets

from app.core.config import PASSWORD_HASH_ITERATIONS, PASSWORD_HASH_PREFIX

"""
Password hashing and verification utilities.
"""


def hash_password(password: str) -> str:
    # Security: Using a unique salt for each password hash to prevent rainbow table attacks
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return f"{PASSWORD_HASH_PREFIX}${base64.b64encode(salt).decode('utf-8')}${base64.b64encode(digest).decode('utf-8')}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, salt_value, digest_value = hashed_password.split("$", 2)
    except ValueError:
        return False

    if algorithm != PASSWORD_HASH_PREFIX:
        return False

    salt = base64.b64decode(salt_value.encode("utf-8"))
    expected_digest = base64.b64decode(digest_value.encode("utf-8"))
    # Security: Using hmac.compare_digest for constant-time comparison to prevent timing attacks
    candidate_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return hmac.compare_digest(candidate_digest, expected_digest)
