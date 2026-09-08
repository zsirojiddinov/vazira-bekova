"""
tests/test_translate_phrase_kkt.py
=====================================
`translate_phrase_kkt()` — ANIQ "predlog+egalik+ot(+ko'plik)" (D+M2+C(+X))
naqshini bazadan ID orqali tarjima qiluvchi funksiya.

Bu yerdagi kutilgan qiymatlar (`reference_uz`) FABRIKATSIYA QILINMAGAN —
loyihada allaqachon mavjud, INSON tomonidan tayyorlangan etalon to'plamdan
(`data/100_soz.docx`, 100 ta juftlik) SO'ZMA-SO'Z ko'chirilgan (Qoida 1).
Bu fayl o'sha 100 tadan 19 tasini (barcha 10 ot × "from our X" naqshi +
"books" uchun barcha 5 predlog naqshi) qamrab oladi — to'liq 100 tasini
avtomatik yuklab, foiz hisoblaydigan skript alohida: `scripts/check_100_soz.py`.

MUHIM: bu yerdagi natijalar JORIY (2026-09-08) kod holatini aks ettiradi.
Ba'zi holatlar ATAYLAB `xfail` bilan belgilangan — bular Faza 0/2 da
allaqachon hujjatlashtirilgan, TUZATILMAGAN kamchiliklar (Qoida 3: gold
test faqat o'lchov, kodni bu testlarga moslab TUZATMAYMIZ). Agar kimdir
Faza 2 da shu xatolarni tuzatsa, mos xfail belgisi XPASS ko'rsatadi —
bu signal bo'lib, o'sha `xfail` shu commitda olib tashlanishi kerak."""
from __future__ import annotations

import pytest


# (no, english, reference_uz) — data/100_soz.docx dan (1-jadval qatorlari).
OK_CASES = [
    (1, "from our books", "kitoblarimizdan"),
    (2, "from your books", "kitoblaringizdan"),
    (3, "to our books", "kitoblarimizga"),
    (4, "to your books", "kitoblaringizga"),
    (5, "in our books", "kitoblarimizda"),
    (6, "in your books", "kitoblaringizda"),
    (9, "of our books", "kitoblarimizning"),
    (10, "of your books", "kitoblaringizning"),
    (11, "from our houses", "uylarimizdan"),
    (31, "from our students", "talabalarimizdan"),
    (41, "from our teachers", "o'qituvchilarimizdan"),
]

# Ma'lum, hujjatlashtirilgan kamchiliklar (Faza 0 topilmasi: bosh harf
# muammosi — uz_stem/setup_database faqat inglizcha bosh so'zni .lower()
# qiladi, o'zbekcha tarjima docx'dagi holicha qoladi).
CAPITALIZATION_BUG_CASES = [
    (61, "from our data", "ma'lumotlarimizdan"),
    (81, "from our studies", "tadqiqotlarimizdan"),
    (91, "from our results", "natijalarimizdan"),
]

# Ma'lum, hujjatlashtirilgan kamchilik: topshiriqda aytilgan "yetishmayotgan
# 3 ta ot" — bu so'zlar hozircha lug'atda YO'Q (yoki topilmayapti), shu
# sabab funksiya butunlay None qaytaradi.
MISSING_NOUN_CASES = [
    (21, "from our schools", "maktablarimizdan"),
    (51, "from our programs", "dasturlarimizdan"),
    (71, "from our articles", "maqolalarimizdan"),
]


@pytest.mark.parametrize("no,en,ref", OK_CASES, ids=lambda v: v if isinstance(v, str) else str(v))
def test_translate_phrase_kkt_matches_gold(isolated_kkt_module, no, en, ref):
    m = isolated_kkt_module
    with m.readonly_mode():
        result = m.translate_phrase_kkt(en)
    assert result is not None, f"#{no} '{en}' — translate_phrase_kkt None qaytardi"
    assert result["natija"] == ref


@pytest.mark.parametrize("no,en,ref", CAPITALIZATION_BUG_CASES)
@pytest.mark.xfail(reason="Bosh harf muammosi (Faza 0 topilmasi, reports/faza_0.md #3-band, "
                           "asl taqriz 6/53/60/90-bandlar): setup_database() faqat inglizcha "
                           "headword'ni .lower() qiladi, o'zbekcha tarjima docx'dagi holicha "
                           "qoladi. Tuzatish Faza 2 vazifasi.", strict=True)
def test_translate_phrase_kkt_capitalization_bug(isolated_kkt_module, no, en, ref):
    m = isolated_kkt_module
    with m.readonly_mode():
        result = m.translate_phrase_kkt(en)
    assert result is not None, f"#{no} '{en}' — translate_phrase_kkt None qaytardi"
    assert result["natija"] == ref


@pytest.mark.parametrize("no,en,ref", MISSING_NOUN_CASES)
@pytest.mark.xfail(reason="Lug'atda yo'q ot (topshiriqda aytilgan 'yetishmayotgan 3 ta ot' bilan "
                           "bir xil toifadagi muammo): bu so'z UB_en_w'da headword sifatida "
                           "topilmaydi, funksiya None qaytaradi. Lug'atni to'ldirish — inson "
                           "qarori (Qoida 1: gold ma'lumot/lug'at to'ldirishni Claude qilmaydi).",
                     strict=True)
def test_translate_phrase_kkt_missing_noun(isolated_kkt_module, no, en, ref):
    m = isolated_kkt_module
    with m.readonly_mode():
        result = m.translate_phrase_kkt(en)
    assert result is not None, f"#{no} '{en}' — translate_phrase_kkt None qaytardi"
    assert result["natija"] == ref


@pytest.mark.parametrize("en", ["our books", "your books"])
def test_translate_phrase_kkt_returns_none_for_bare_two_word_phrase(isolated_kkt_module, en):
    """"our books"/"your books" — predlogsiz, ATIGI 2 so'z. Bu
    translate_phrase_kkt() UCHUN naqshdan tashqarida (funksiya docstringi:
    "predlog+egalik+OT" — kamida 3 so'z talab qiladi, len(words)<3 bo'lsa
    darhol None qaytaradi). Bu XATO EMAS — funksiyaning atayin cheklovi;
    tushum kelishigi ("-ni") qo'shish qarori translate_phrase_general()
    zimmasida va Faza 2'da inson qaroriga muhtoj (reports/accusative_analysis.md,
    hali yozilmagan — Faza 2 ishi)."""
    m = isolated_kkt_module
    with m.readonly_mode():
        result = m.translate_phrase_kkt(en)
    assert result is None
