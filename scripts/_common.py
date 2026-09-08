"""
scripts/_common.py
====================
`scripts/` papkasidagi bir nechta skript (check_100_soz.py, audit_examples.py)
o'rtasida umumiy — solishtirish uchun matn normalizatsiyasi.
"""
from __future__ import annotations

import re
import unicodedata

# Barcha apostrof-shakldagi belgilarni (ASCII ', tipografik ' va ',
# o'zbek modifikator ʻ/ʼ) BITTA kanonik belgiga tenglashtiramiz —
# solishtiruv shu yozilish farqidan aziyat chekmasligi uchun.
_APOSTROPHE_CHARS = "'‘’ʻʼ′`"
_APOSTROPHE_RE = re.compile("[" + re.escape(_APOSTROPHE_CHARS) + "]")


def normalize(s: str | None) -> str | None:
    """Solishtirish uchun: Unicode NFC normalizatsiya, bosh harfni kichik
    harfga o'tkazish, barcha apostrof-shakldagi belgilarni bittasiga
    tenglashtirish, ortiqcha bo'shliqlarni siqish."""
    if s is None:
        return None
    s = unicodedata.normalize("NFC", s)
    s = s.lower()
    s = _APOSTROPHE_RE.sub("'", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s
