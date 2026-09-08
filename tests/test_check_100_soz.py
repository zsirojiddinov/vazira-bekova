"""
tests/test_check_100_soz.py
==============================
`scripts/check_100_soz.py` ning docx-parsing va normalizatsiya
funksiyalarini tekshiradi (tarjima natijalarining o'zi emas — bu
`tests/test_translate_phrase_kkt.py` da alohida qamrab olingan; bu yerda
faqat skriptning "gold to'plamni to'g'ri o'qiyaptimi" va "normalizatsiya
to'g'ri ishlayaptimi" savoliga javob beriladi)."""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import check_100_soz as script  # noqa: E402


def test_load_gold_set_reads_all_100_entries():
    gold = script.load_gold_set(os.path.join(REPO_ROOT, "data", "100_soz.docx"))
    assert len(gold) == 100
    numbers = [g["no"] for g in gold]
    assert numbers == list(range(1, 101))


def test_load_gold_set_first_and_last_entries_match_docx():
    """docx'dan o'qilgan qiymatlar aynan hujjatdagi holicha (fabrikatsiya
    qilinmagan) — bu test shu haqiqiylikni tasdiqlaydi."""
    gold = script.load_gold_set(os.path.join(REPO_ROOT, "data", "100_soz.docx"))
    first = gold[0]
    assert first["source_en"] == "from our books"
    assert first["reference_uz"] == "kitoblarimizdan"
    assert first["morphemes"] == "kitob+lar+imiz+dan"
    last = gold[-1]
    assert last["source_en"] == "of your results"
    assert last["reference_uz"] == "natijalaringizning"


def test_normalize_lowercases_and_unifies_apostrophes():
    assert script.normalize("Ma’lumotlarimizdan") == "ma'lumotlarimizdan"
    assert script.normalize("O‘qituvchilarimizdan") == "o'qituvchilarimizdan"
    assert script.normalize("KITOB") == "kitob"


def test_normalize_collapses_whitespace():
    assert script.normalize("  bir   ikki  ") == "bir ikki"


def test_normalize_none_stays_none():
    assert script.normalize(None) is None
