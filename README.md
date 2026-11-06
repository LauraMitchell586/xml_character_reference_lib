# xml_character_reference_lib

Decode XML character references (both `&#DDDD;` and `&#xHHHH;` forms) in a
Python string.

```python
from xml_character_reference_lib import decode, DecodeError

decode("caf&#233;")
# 'café'

decode("&#x1F600;")
# '😀'

try:
    decode("&#xD800;")
except DecodeError as exc:
    print(exc)
    # character reference '&#xD800;' is not a legal XML character
```

The package exports exactly two names: `decode(text: str) -> str` and
`DecodeError`, a subclass of `ValueError`.

## Why this exists

XML parsers decode character references as part of parsing, but sometimes you
have a string that came from somewhere else — a log line, a configuration
value, a hand-written fixture — and you want the characters without pulling in
a full parser. This library does that one job.

The trade-off is strictness. XML 1.0 section 2.2 lists the characters a
reference may name. A reference to a surrogate code point, to U+0000, or to
U+FFFE is not well-formed XML. This decoder raises `DecodeError` for those
instead of substituting U+FFFD, because a caller who is decoding XML needs to
know the input is not well-formed. If you would rather have a replacement
character, catch `DecodeError` and substitute it yourself.

## The awkward edge

Decoding is single-pass. `decode("&#38;#65;")` returns `"&#65;"`, not
`"A"`. That matches an XML parser, which substitutes the character into the
text and does not then re-read it as markup. If you need repeated decoding,
call `decode` again yourself — but be aware that doing so can turn text that
was safely escaped into markup.

An ampersand that does not begin a reference is passed through unchanged, so
`decode("a & b")` returns `"a & b"`. If you need to reject such input, scan
the result for a remaining `&` after decoding.

## Tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
