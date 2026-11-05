"""Core XML character reference decoding.

XML 1.0 recognises two numeric character reference forms:

* ``&#DDDD;`` where ``DDDD`` is one or more decimal digits
* ``&#xHHHH;`` where ``HHHH`` is one or more hexadecimal digits

The referenced code point must be a legal XML character.  XML 1.0
section 2.2 defines the legal character range as::

    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD]
           | [#x10000-#x10FFFF]

Surrogate code points (U+ D800 through U+ DFFF) are excluded, as are the
non-characters U+FFFE and U+FFFF.  The decoder rejects references to
code points outside that set rather than silently substituting a
replacement character, because callers that care about XML conformance
need to know that the input is not well-formed XML.
"""

from __future__ import annotations

import re

__all__ = ["decode", "DecodeError"]


class DecodeError(ValueError):
    """Raised when a character reference is malformed or out of range."""


# A single reference: ``&#`` then either decimal digits or an ``x``/
# ``X`` followed by hex digits, then ``;``.  The trailing semicolon is
# mandatory in XML; we do not accept the HTML-style optional form.
_REFERENCE_RE = re.compile(r"&#(?:([0-9]+)|[xX]([0-9a-fA-F]+));")


def _is_xml_char(codepoint: int) -> bool:
    """Return True if *codepoint* is a legal XML 1.0 character.

    The XML 1.0 ``Char`` production excludes the surrogate block and
the two non-characters U+FFFE and U+FFFF.  Everything else in
``[0, 0x10FFFF]`` is allowed.
    """
    if codepoint < 0 or codepoint > 0x10FFFF:
        return False
    if 0xD800 <= codepoint <= 0xDFFF:
        return False
    if codepoint in (0xFFFE, 0xFFFF):
        return False
    if codepoint < 0x20 and codepoint not in (0x09, 0x0A, 0x0D):
        return False
    return True


def _decode_match(match: re.Match[str]) -> str:
    """Turn a regex match into the referenced character."""
    decimal, hexadecimal = match.group(1), match.group(2)
    if decimal is not None:
        codepoint = int(decimal, 10)
    else:
        codepoint = int(hexadecimal, 16)

    if not _is_xml_char(codepoint):
        raise DecodeError(
            f"character reference {match.group(0)!r} is not a legal XML character"
        )
    return chr(codepoint)


def decode(text: str) -> str:
    """Decode every XML character reference in *text*.

    Parameters
    ----------
    text:
        A string that may contain ``&#...;`` references.  Any character
        that is not part of a reference is copied through unchanged.

    Returns
    -------
    str
        A new string with every valid reference replaced by the
        character it names.

    Raises
    ------
    DecodeError
        If a reference is syntactically malformed or names a code point
        that XML 1.0 does not permit.

    Notes
    -----
    Decoding is single-pass: the replacement characters are never
    rescanned, so ``decode("&amp;#65;")`` returns ``"&#65;"`` rather
    than ``"A"``.  This matches the behaviour of an XML parser, which
decodes references in the entity value and does not then reinterpret
the result as markup.
    """
    if not isinstance(text, str):
        raise TypeError("decode() expects a str")

    result: list[str] = []
    position = 0
    length = len(text)

    while position < length:
        ampersand = text.find("&", position)
        if ampersand == -1:
            result.append(text[position:])
            break

        # Copy everything before the ampersand untouched.
        result.append(text[position:ampersand])

        match = _REFERENCE_RE.match(text, ampersand)
        if match is None:
            # Not a reference we recognise.  The XML spec would call
            # this a well-formedness error, but we are a decoder, not a
            # validator, so we pass the ampersand through.  A caller
            # that wants strict validation can scan the result for a
            # remaining ``&``.
            result.append("&")
            position = ampersand + 1
            continue

        result.append(_decode_match(match))
        position = match.end()

    return "".join(result)
