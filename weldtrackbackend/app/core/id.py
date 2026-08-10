"""Shared ULID generation and SQLAlchemy column helpers."""

import secrets
import time

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column

ULID_LENGTH = 26
ULID_CHARS = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid() -> str:
    """Return a canonical 26-character ULID.

    ULIDs contain a 48-bit millisecond timestamp followed by 80 random bits,
    making them sortable by creation time while remaining safe to generate in
    multiple application processes.
    """
    value = (int(time.time() * 1000) << 80) | secrets.randbits(80)
    encoded = [ULID_CHARS[0]] * ULID_LENGTH
    for position in range(ULID_LENGTH - 1, -1, -1):
        encoded[position] = ULID_CHARS[value & 0x1F]
        value >>= 5
    return "".join(encoded)


def ulid_primary_key(**kwargs):
    """Create a string ULID primary-key column."""
    return mapped_column(
        String(ULID_LENGTH), primary_key=True, default=new_ulid, **kwargs
    )


def ulid_foreign_key(target: str, *, ondelete: str | None = None, **kwargs):
    """Create a string column referencing another ULID primary key."""
    return mapped_column(
        String(ULID_LENGTH), ForeignKey(target, ondelete=ondelete), **kwargs
    )
