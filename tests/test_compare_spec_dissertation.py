"""
tests/test_compare_spec_dissertation.py
==========================================
`scripts/compare_spec_dissertation.py` — spec ↔ dissertatsiya II bobi ↔
CH2_EVX_EXAMPLES nomuvofiqliklari (reports/faza_2_spec_vs_dissertation.md).

`data/desertatsiya.docx` shaxsiy fayl (.gitignore) — yo'q muhitda (CI) SKIP."""
from __future__ import annotations

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import compare_spec_dissertation as script  # noqa: E402

requires_docx = pytest.mark.skipif(not os.path.exists(script.DEFAULT_DOCX),
                                   reason="data/desertatsiya.docx shaxsiy fayl — bu muhitda yo'q")


@pytest.fixture(scope="module")
def recs():
    items = script.ch2l.load_docx(script.DEFAULT_DOCX)
    return script.ch2l.extract_ch2_records(items, script.ch2l.find_chapter_bounds(items)["II"])


@pytest.fixture(scope="module")
def rows(recs, isolated_kkt_module):
    return script.build_rows(script.conf.load_spec(), recs, isolated_kkt_module.CH2_EVX_EXAMPLES)


def _row(rows, uid, en):
    return next(r for r in rows if r["uid"] == uid and r["en"] == en)


@requires_docx
def test_will_return_spec_differs_from_dissertation(rows):
    r = _row(rows, "2.62", "will return")
    assert r["spec_diss"] == "FARQ"
    assert [d["uz_marker_word"] for d in r["diss"]] == ["qaytadi"]
    assert r["ch2"] == []


@requires_docx
def test_cleverer_flags_spec_internal_inconsistency(rows):
    """2.21: spec natija katagi "aqillroq", uning "+" qismlari esa "aqilliroq" —
    dissertatsiya bilan bir xil."""
    r = _row(rows, "2.21", "cleverer")
    assert r["spec_diss"] == "FARQ"
    assert r["spec_ichki"] == "aqilliroq"


@requires_docx
def test_sent_matches_one_of_two_spec_readings(rows):
    """2.65: spec "sent" uchun ikki o'qish beradi (yubordi / yuborgan) —
    dissertatsiyaning "yuborgan" i biriga mos, FARQ emas."""
    assert _row(rows, "2.65", "sent")["spec_diss"] == "mos"


@requires_docx
def test_ch2_follows_dissertation_not_spec_for_contents(rows):
    r = _row(rows, "2.15", "contents")
    assert (r["spec_diss"], r["ch2_diss"], r["ch2_spec"]) == ("FARQ", "mos", "FARQ")


@requires_docx
def test_cross_match_finds_second_gayer_as_gayest_translation(recs):
    xm = script.cross_matches(recs)
    hit = [x for x in xm if x["rec"]["en_marker_word"] == "gayer"]
    assert len(hit) == 1
    assert any(u == "2.30" for u, _, _ in hit[0]["other"])
