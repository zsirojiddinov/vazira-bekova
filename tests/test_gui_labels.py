"""
tests/test_gui_labels.py
==========================
Faza 2 / Ustuvorlik 0.2. "O'rtacha aniqlik" GUI statistikakartochkasi
(va soʻz darajasidagi inline "Aniqlik: X%" yozuvi) `conf` maydonining —
qattiq kodlangan konstanta (0.999/0.970/0.93/0.895/0.0, qarang
`_smart_parse_core`) — oʻrtachasini/oʻzini koʻrsatadi. Bu koʻrsatkich
tarjima MAZMUNAN TOʻGʻRILIGINI EMAS, soʻz qaysi morfologik kod yoʻlidan
oʻtganini bildiradi. Bu chalkashuv dissertatsiya skrinshotlari bilan
bevosita tasdiqlangan — toʻliq dalil: reports/faza_2_confidence_audit.md.

Bu test faqat YANGI YORLIQ/IZOH MATNINING toʻgʻri ekanini va eski
chalkashtiruvchi satr qolib ketmaganini tekshiradi. **HISOBLASH
MANTIGʻIGA** (`avg_c`, `conf` konstantalari) HECH TEGILMAGAN — bu qat'iy
qoida (natijaga qarab kod tuzatilmaydi, vazn/konstantalar oʻzgartirilmaydi)
va shu test buni buzmasligini alohida tasdiqlaydi (`test_conf_constants_unchanged`).

DIQQAT: haqiqiy Tk oynasi bu yerda HECH QACHON ochilmaydi — CI (Ubuntu,
displeysiz) muhitda `tk.Tk()` chaqiruvi ishlamaydi. Shu sabab bu test
faqat (a) modul darajasidagi konstantalarni va (b) GUI metodlarining
MANBA KODINI (`inspect.getsource`) tekshiradi.
"""
from __future__ import annotations

import inspect


def test_accuracy_card_label_no_longer_says_aniqlik(isolated_kkt_module):
    m = isolated_kkt_module
    assert m.ACC_CARD_LABEL == "Parse ishonchi (morfologik)"
    assert "aniqlik" not in m.ACC_CARD_LABEL.lower()


def test_accuracy_card_note_explains_what_it_really_measures(isolated_kkt_module):
    m = isolated_kkt_module
    note = m.ACC_CARD_NOTE.lower()
    # Izoh tarjima to'g'riligini ANIQ inkor qilishi shart — bu yorliq
    # o'zgartirishning butun maqsadi (qarang faza_2_confidence_audit.md).
    assert "to'g'rilig" in note
    assert "emas" in note


def test_inline_per_word_label_updated_too(isolated_kkt_module):
    m = isolated_kkt_module
    assert m.ACC_INLINE_LABEL == "Parse ishonchi"


def test_stats_card_uses_label_constants_not_hardcoded_old_string(isolated_kkt_module):
    """_build_stats_cards eski "O'rtacha aniqlik" satrini to'g'ridan-to'g'ri
    hardcode qilmasligini, ACC_CARD_LABEL/ACC_CARD_NOTE konstantalaridan
    foydalanishini tekshiradi — kelajakda kimdir labelni qayta hardcode
    qilib qo'yishining oldini oladi."""
    m = isolated_kkt_module
    src = inspect.getsource(m.MTSystem._build_stats_cards)
    assert "ACC_CARD_LABEL" in src
    assert "ACC_CARD_NOTE" in src
    assert "O'rtacha aniqlik" not in src


def test_inline_draw_uses_label_constant_not_hardcoded_old_string(isolated_kkt_module):
    m = isolated_kkt_module
    src = inspect.getsource(m.MTSystem._draw_en_parse)
    assert "ACC_INLINE_LABEL" in src
    assert "Aniqlik" not in src


def test_stat_card_helper_supports_optional_note(isolated_kkt_module):
    """_stat_card yordamchisi note= parametrini qabul qilishini va berilsa
    kartochkaga qo'shimcha Label sifatida chizishini manba kodi orqali
    tekshiradi (haqiqiy widget CI'da yaratib bo'lmaydi — displey yo'q)."""
    m = isolated_kkt_module
    src = inspect.getsource(m.MTSystem._stat_card)
    assert "note=None" in src
    assert "if note" in src


def test_conf_constants_unchanged(isolated_kkt_module):
    """QOIDA: bu Faza (label aniqlashtirish) `conf` qiymatlarini
    O'ZGARTIRMASLIGI SHART — faqat nom/izoh. Konstantalar hali ham
    dissertatsiya/kod audit hisobotida hujjatlashtirilgan qiymatlarga teng
    ekanini tekshiradi (reports/faza_2_confidence_audit.md, 0.1-jadval)."""
    m = isolated_kkt_module
    src = inspect.getsource(m._smart_parse_core)
    assert "conf\":0.999" in src.replace(" ", "")
    assert "conf\":0.970" in src.replace(" ", "")
    assert "conf\":0.93ifnotpfxelse0.895" in src.replace(" ", "")
