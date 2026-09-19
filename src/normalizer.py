"""
Usage:
    from normalizer import normalize_text
    clean = normalize_text("Meraaa order!!!   cancel krdo 😭😭")
"""

import re
import unicodedata

ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u2060\ufeff]")
MULTISPACE_RE = re.compile(r"\s+")
REPEATED_PUNCT_RE = re.compile(r"([!?.,;:])\1{2,}")
REPEATED_CHAR_RE = re.compile(r"([A-Za-z])\1{3,}", re.IGNORECASE)

# Keep punctuation/emojis. These replacements only remove obvious transport noise.
MENTION_RE = re.compile(r"(?<!\w)@\w+")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize_text(text: str) -> str:
    """Apply conservative normalization while preserving semantic cues."""
    if text is None:
        return ""
    
    text = str(text)
    text = unicodedata.normalize("NFKC", text)
    text = REPEATED_CHAR_RE.sub(r"\1\1", text)
    text = REPEATED_PUNCT_RE.sub(r"\1\1", text)
    text = MULTISPACE_RE.sub(" ", text).strip()

    return text


if __name__ == "__main__":
    print("This can't run as a Standalone")
