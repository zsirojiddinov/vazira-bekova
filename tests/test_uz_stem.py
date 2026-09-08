"""
tests/test_uz_stem.py
======================
`uz_stem()` — DB'ga bog'liq bo'lmagan sof (pure) funksiya. Kodning o'zida
yozilgan qoida: (1) "/" yoki "|" bo'yicha ajratib BIRINCHI bo'lakni oladi,
(2) qavs ichidagi izohni ("...") olib tashlaydi, (3) oxiridagi "moq"ni
kesadi. Bu testlar o'sha qoidani QAYD ETADI (regression baseline) — har bir
kutilgan qiymat funksiyaning o'zini ishga tushirib TASDIQLANGAN (Faza 1
tayyorlash paytida), fabrikatsiya qilinmagan.
"""
from __future__ import annotations

import pytest


@pytest.mark.parametrize("raw,expected", [
    ("kitob", "kitob"),                          # o'zgarishsiz
    ("kitob/kitoblar", "kitob"),                  # "/" bo'yicha — birinchi bo'lak
    ("kitob | kitob-lar", "kitob"),                # "|" bo'yicha, bo'shliqlar bilan
    ("ishlamoq", "ishla"),                         # fe'l infinitiv "-moq" kesiladi
    ("o'qi(fe'l)moq", "o'qi"),                     # qavsdagi izoh olib tashlanadi, so'ng -moq
    ("  kitob  ", "kitob"),                        # boshi/oxiridagi bo'shliq
    ("ishla (fe'l) moq", "ishla"),                 # qavsdan keyin ham bo'shliqli "moq"
    ("kitob(ot)", "kitob"),                        # qavsdagi POS-belgisi olib tashlanadi
    ("a", "a"),                                    # juda qisqa — o'zgarishsiz
    ("moq", ""),                                   # butun so'z "moq" bo'lsa — bo'sh qoladi
    ("kmoq", "k"),                                 # "moq" bilan tugagan har qanday satr kesiladi
])
def test_uz_stem_matches_current_rule(isolated_kkt_module, raw, expected):
    m = isolated_kkt_module
    assert m.uz_stem(raw) == expected
