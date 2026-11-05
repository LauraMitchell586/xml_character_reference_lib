"""Decode XML character references.

This package exposes the public decoding function :func:`decode` and the
:class:`DecodeError` raised on malformed input.
"""

from .core import DecodeError, decode

__all__ = ["decode", "DecodeError"]
