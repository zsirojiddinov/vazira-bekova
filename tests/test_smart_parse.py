"""
tests/test_smart_parse.py
============================
`smart_parse()` — so'z darajasidagi 21-qadamli tahlil (to'g'ridan bazadan
topish + affiks-asosida hosila qidirish). Bu yerdagi qiymatlar bazaning
JORIY holatidan (data/ dagi manba fayllar + kod) to'g'ridan-to'g'ri
o'qib olingan — hech biri fabrikatsiya qilinmagan (Qoida 1)."""
from __future__ import annotations

import pytest


@pytest.mark.parametrize("word,expected_pos,expected_uz", [
    ("book", "Ot", "kitob"),
    ("teacher", "Ot", "o'qituvchi"),
])
def test_smart_parse_direct_dictionary_hit(isolated_kkt_module, word, expected_pos, expected_uz):
    """So'z UB_en_w'da to'g'ridan-to'g'ri headword sifatida bor —
    hech qanday affiks-ajratish kerak emas."""
    m = isolated_kkt_module
    with m.readonly_mode():
        r = m.smart_parse(word)
    assert r["found"] is True
    assert r["pos"] == expected_pos
    assert r["uz"] == expected_uz
    assert r["method"] == "UB_en_w[ID]→UB_uz_w[ID]"


@pytest.mark.parametrize("word,expected_pos,expected_uz", [
    ("students", "Ot", "talabalar"),
    ("teachers", "Ot", "o'qituvchilar"),
])
def test_smart_parse_derives_regular_plural_correctly(isolated_kkt_module, word, expected_pos, expected_uz):
    """So'z o'zi UB_en_w'da YO'Q (faqat birlik shakli bor) — MORPH_RULES
    orqali ko'plik affiksi ("-s") ajratilib, o'zak lug'atdan topiladi va
    to'g'ri ko'plik shaklida qaytariladi. Bu — tizimning ISHLAYOTGAN
    (to'g'ri) yo'li, faqat ma'lum xato holatlar emas."""
    m = isolated_kkt_module
    with m.readonly_mode():
        r = m.smart_parse(word)
    assert r["found"] is True
    assert r["pos"] == expected_pos
    assert r["uz"] == expected_uz


@pytest.mark.parametrize("word", [
    "capabilities",  # -ies qoidasi ishlaydi, lekin "capability" o'zi lug'atda yo'q
    "school",        # topshiriqdagi "yetishmayotgan 3 ta ot"dan biri
    "running",       # -ing orqali "run"ga tiklanadi, lekin "run" lug'atda yo'q
    "biggest",       # -est/ikkilanish qoidasi qamrab olmagan/o'zak topilmagan
])
def test_smart_parse_word_not_in_dictionary(isolated_kkt_module, word):
    m = isolated_kkt_module
    with m.readonly_mode():
        r = m.smart_parse(word)
    assert r["found"] is False
    assert r["uz"] is None


def test_smart_parse_agentive_er_uses_wrong_fallback_suffix_data_bug(isolated_kkt_module):
    """YANGI TOPILMA (Faza 1 tayyorlash paytida aniqlangan): "worker" so'zi
    uchun POS to'g'ri aniqlanadi (Ot — "ish bajaruvchi", MORPH_RULES dagi
    birinchi "-er" qoidasi, req_root_pos="Fe'l" orqali, "work" fe'l sifatida
    topiladi) — lekin QM_en_w->QM_uz_w ID moslashuvi topilmagani uchun
    zaxira `make_uzbek(root, "er")` ishlatiladi, U ESA "-er"ni HAR DOIM
    QIYOSIY DARAJA deb hisoblaydi (`stem+"roq"`), agentiv/ish-bajaruvchi
    ma'nosini AJRATMAYDI. Natija: "work"+"roq"="ishlaroq" — mazmunsiz
    (kutilgan "ishchi" kabi bo'lishi kerak edi).

    Sabab: make_uzbek() faqat AFFIKS MATNIGA ("er") qarab ishlaydi, lekin
    derived_pos ("Ot" vs "Sifat") argument sifatida UZATILMAYDI — shu
    sabab ikkita xilma-xil "-er" ma'nosini (ish bajaruvchi / qiyosiy
    daraja) ANIQLAY OLMAYDI. Tuzatish — Faza 2 vazifasi (Claude bu yerda
    tuzatmaydi, Qoida 3/6)."""
    m = isolated_kkt_module
    with m.readonly_mode():
        r = m.smart_parse("worker")
    assert r["found"] is True
    assert r["pos"] == "Ot", "POS to'g'ri aniqlangan (bu qism ishlayapti)"
    assert r["uz"] == "Ishlaroq", (
        "Kutilgan JORIY (xato) natija endi boshqacha chiqyapti — agar "
        "tuzatilgan bo'lsa, shu testni yangilang."
    )


@pytest.mark.parametrize("word,uz_with_wrong_case", [
    ("algorithms", "Algoritmlar"),
    ("models", "Modellar"),
])
def test_smart_parse_capitalization_bug_on_derived_plural(isolated_kkt_module, word, uz_with_wrong_case):
    """Faza 0'da hujjatlashtirilgan bosh harf muammosi (reports/faza_0.md,
    asl taqriz 6/53/60/90-bandlar) — nafaqat to'g'ridan-to'g'ri lug'at
    yozuvlarida, balki KO'PLIK orqali HOSIL QILINGAN so'zlarda ham
    ko'rinadi (o'zak tarjimasi bosh harfli bo'lgani uchun "lar" qo'shilsa
    ham bosh harf saqlanib qoladi)."""
    m = isolated_kkt_module
    with m.readonly_mode():
        r = m.smart_parse(word)
    assert r["found"] is True
    assert r["uz"] == uz_with_wrong_case
    assert r["uz"][0].isupper(), "Bu bosh harf xatosining o'zi — kutilgan JORIY holat"
