"""
tests/test_build_master_decisions.py
=======================================
`scripts/build_master_decisions.py` — himoyaga tayyorgarlik uchun yagona
qarorlar ro'yxati (reports/master_qarorlar_royxati.md).

`owner_for_diff()`, `owner_for_code_gap()` va `levenshtein()` — sof funksiyalar
(har doim sinaladi); to'liq ro'yxat `data/desertatsiya.docx` ni talab qiladi —
yo'q muhitda (CI) SKIP.
"""
from __future__ import annotations

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import build_master_decisions as script  # noqa: E402

requires_docx = pytest.mark.skipif(not os.path.exists(script.csd.DEFAULT_DOCX),
                                   reason="data/desertatsiya.docx shaxsiy fayl — bu muhitda yo'q")


def _row(en, spec, diss, spec_ichki=None):
    return {"en": en, "spec": [spec], "diss": [{"uz_marker_word": diss}], "spec_ichki": spec_ichki}


def _line(report, id_):
    return next(ln for ln in report.splitlines() if ln.startswith(f"| {id_} |"))


def test_levenshtein():
    assert script.levenshtein("imkoniyatlar", "imkonyatlar") == 1
    assert script.levenshtein("maktab bolalari", "maktabbolalar") == 2


def test_owner_rule_is_mechanical():
    """Mexanik qoida: spec ichki nomuvofiqligi / boshqa misol tarjimasi / 1 harflik
    imlo → Vazira; qolgan tarjima farqlari → Professor."""
    assert script.owner_for_diff(_row("cleverer", "aqillroq", "aqilliroq", "aqilliroq"), set())[0] == script.VAZ
    assert script.owner_for_diff(_row("busier", "bandroq", "kattaroq"), {"busier"})[0] == script.VAZ
    assert script.owner_for_diff(_row("capabilities", "imkoniyatlar", "imkonyatlar"), set())[0] == script.VAZ
    assert script.owner_for_diff(_row("will return", "qaytmoq", "qaytadi"), set())[0] == script.PROF
    assert script.owner_for_diff(_row("schoolboys", "maktab bolalari", "maktabbolalar"), set())[0] == script.PROF


def test_code_gap_owner():
    """Kod ≠ spec: L (lug'at) → Vazira, M/N/S → Dasturchi; spec yozuvi/mezon
    masalasi (3.24 "men + ning" ↔ imlo "mening", 3.2/3.9 "-ly") → Vazira, kod
    o'zgartirilmasdan oldin."""
    assert script.owner_for_code_gap("3.24", "L")[0] == script.VAZ
    assert script.owner_for_code_gap("3.2", "M")[0] == script.VAZ
    assert script.owner_for_code_gap("3.26", "L")[0] == script.VAZ
    assert script.owner_for_code_gap("2.54", "L")[0] == script.DEV
    assert script.owner_for_code_gap("2.63", "M")[0] == script.DEV


def test_owner_key():
    assert script.owner_key("Professor + Vazira — sabab") == "Professor + Vazira"
    assert script.owner_key("Vazira (professor bilan) — sabab") == "Vazira"
    assert script.owner_key("Dasturchi (`uz_stem()`); lug'at teglari — Vazira ma'lumoti") == "Dasturchi"


@pytest.fixture(scope="module")
def built():
    return script.build(script.csd.DEFAULT_DOCX)


@requires_docx
def test_toliq_breakdown_accounts_for_every_rule(built):
    """G8: TO'LIQ MOS ning har bir qismi nomi bilan; hech bir qoida tushib qolmaydi
    (24 + 8 + 3 = 35 — faqat M/N/S; "37 mustaqil" = 35 M/N/S + 2 L)."""
    b = script.toliq_breakdown(built["evs"])
    parts = b["tm_bad"] + b["tm_ch2"] + b["tm_ind"] + b["tl_ch2"] + b["tl_ind"]
    assert sorted(e["uid"] for e in parts) == sorted(e["uid"] for e in b["toliq"])
    assert len(b["toliq"]) - len(b["tl_ch2"]) == len(b["tm"]) + len(b["tl_ind"])
    line = _line(script.render(built), "G8")
    for e in b["tl_ind"]:
        assert e["uid"] in line


@requires_docx
def test_critical_and_resolved_items(built):
    report = script.render(built)
    for id_ in ("G1", "G9"):
        assert "⚠ JIDDIY" in _line(report, id_)
    assert "HAL QILINDI" in _line(report, "G7")
    # hal qilingan band ochiq bandlar egalari jadvaliga kirmaydi
    assert "| Ziyoviddin |" not in report


@requires_docx
def test_html_page_matches_markdown(built):
    c = script.collect(built)
    page = script.render_html(c)
    assert "<title>KKT himoya qarorlari</title>" in page
    assert "<html" not in page and "<body" not in page  # Artifact skeleti chop etishda qo'shiladi
    assert page.count('<article class="band') == len(c["entries"])
    assert 'id="band-G9"' in page and page.count("crit-card") >= 2


@requires_docx
def test_master_list_contains_key_defense_items(isolated_kkt_module):
    report = script.render(script.build(script.csd.DEFAULT_DOCX))
    for needle in ("| G1 |", "97,7%", "| G2 |", "| G8 |", "| G9 |", "| A·2.62 |", "| D1 |", "| F·2.36 |",
                   "| C·2.7 |", "eng qulay"):
        assert needle in report, needle
    # 2.62 — professor qarori, 2.21 — Vazira (spec katagi)
    assert "| Professor" in _line(report, "A·2.62") and "| Vazira" in _line(report, "A·2.21")
    # M turida holat stub bilan aniqlanadi — haqiqiy lug'at natijasi ham alohida ko'rsatiladi
    line_226 = _line(report, "A·2.26")
    assert "stub" in line_226 and "[biggest?]" in line_226
    # 2.58 — II bobda bor (spec'dan farqli), "topilmadi" deb yozilmasligi kerak
    line_258 = _line(report, "F·2.58")
    assert "ergashmoq" in line_258 and "avtomatik topilmadi" not in line_258
    # 3.24: kod «Mening» imlo bo'yicha to'g'ri — texnik navbatga emas, Vazira qaroriga
    assert "| Vazira" in _line(report, "E·3.24")
    assert "| Dasturchi" in _line(report, "E·2.63")
