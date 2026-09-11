"""
tests/test_check_leakage.py
==============================
`scripts/check_leakage.py` — `kkt_spec.json` misollari va boshqa to'plamlar
(1500-lug'at, 100_soz, KKT_Terminologik, CH2_EVX_EXAMPLES) kesishmasi.
Bu skript faqat OGOHLANTIRADI — hech qachon xato bilan tugamaydi."""
from __future__ import annotations

import json
import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import check_leakage as script  # noqa: E402

with open(script.SPEC_PATH, encoding="utf-8") as _f:
    SPEC = json.load(_f)
RULE = {r["uid"]: r for r in SPEC["rules"]}


def test_spec_forms_split_base_and_example():
    assert script.spec_forms(RULE["2.7"]) == [("asos", "capability"), ("misol", "capabilities")]
    assert script.spec_forms(RULE["2.9"]) == [("misol", "leaf"), ("asos", "lea"), ("misol", "leaves")]


def test_spec_forms_handle_lists_and_typographic_apostrophe():
    assert [f for _, f in script.spec_forms(RULE["3.22"])] == ["i", "he", "we", "me", "him", "us"]
    assert script.spec_forms(RULE["2.16"]) == [("misol", "student's")]


@pytest.fixture(scope="module")
def overlaps():
    return script.find_overlaps(SPEC, script.load_sources())


def test_known_ch2_overlap_is_reported(overlaps):
    """"processes" spec 2.6 misoli ham, CH2_EVX_EXAMPLES yozuvi ham."""
    row = next(r for r in overlaps if r["uid"] == "2.6" and r["shakl"] == "processes")
    assert row["shakl_manbalar"] == ["CH2_EVX_EXAMPLES"]


def test_stopwords_are_not_reported_as_token_overlap(overlaps):
    for r in overlaps:
        assert not set(r["token_manbalar"]) & script.STOPWORDS


def test_run_always_returns_zero(tmp_path):
    assert script.run(str(tmp_path / "leak.md")) == 0
    assert (tmp_path / "leak.md").read_text(encoding="utf-8").startswith("# Faza 2")
