"""
tests/test_audit_er_gap.py
=============================
`scripts/audit_er_gap.py` — Faza 2 "-er" bo'shlig'i (sifat+er vs fe'l+er)
hisobotini generatsiya qiladigan skript. Bu yerda faqat skriptning ISHLASH
mexanizmi (klassifikatsiya funksiyalari, sonlarning ichki mosligi)
tekshiriladi — natija RAQAMLARI `reports/faza_2_er_gap.md`da (skriptni
ishga tushirib qayta generatsiya qilinadigan hisobotda).
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import audit_er_gap as script  # noqa: E402


def test_get_er_rules_finds_exactly_two_pos_guarded_variants():
    """MORPH_RULES da "-er" ATAYLAB ikki marta uchraydi (Ot/agentiv,
    Fe'l-cheklovli; Sifat/qiyosiy, cheklovsiz) — reports/faza_1.md da
    hujjatlashtirilgan holat hali ham joyida ekanini tekshiradi."""
    rules = script.get_er_rules()
    assert len(rules) == 2
    poses = {r[2] for r in rules}
    assert poses == {"Ot", "Sifat"}


def test_classify_dictionary_er_words_every_row_has_a_group():
    categories = script.load_dictionary_categories()
    er_fns = script.get_er_rules()[0][1]
    rows = script.classify_dictionary_er_words(categories, er_fns)
    assert len(rows) > 0
    valid_groups = {"SIFAT+ER (qiyosiy)", "FE'L+ER (agentiv)", "ANIQLANMAGAN"}
    for r in rows:
        assert r["group"] in valid_groups
        assert r["word"].lower().endswith("er")


def test_classify_dictionary_finds_consumer_and_encoder_as_agentive():
    """"Consumer" (consume+r) va "Encoder" (encode+r) — ildizi VERBS
    kategoriyasida MUSTAQIL mavjud bo'lgan, avtomatik aniqlanadigan
    fe'l+er nomzodlari (qo'lda tekshirilgan, reports/faza_2_er_gap.md
    metodika bo'limi)."""
    categories = script.load_dictionary_categories()
    er_fns = script.get_er_rules()[0][1]
    rows = script.classify_dictionary_er_words(categories, er_fns)
    by_word = {r["word"]: r["group"] for r in rows}
    assert by_word["Consumer"] == "FE'L+ER (agentiv)"
    assert by_word["Encoder"] == "FE'L+ER (agentiv)"


def test_classify_ch2_examples_has_zero_agentive_entries():
    """CH2_EVX_EXAMPLES (dissertatsiya II bobi) da bitta-so'zli "-er"
    yozuvlarining BARCHASI qiyosiy daraja (Sifat/Ravish POS) — hech
    qanday agentiv (Ot POS, fe'l+er) misoli yo'q."""
    rows = script.classify_ch2_examples()
    assert len(rows) > 0
    assert all(r["group"] == "SIFAT+ER (qiyosiy)" for r in rows)


def test_check_dissertation_theory_returns_none_or_consistent_dict():
    """Docx mavjud bo'lmasa None, mavjud bo'lsa izchil struktura qaytishi
    kerak (bu muhitda ikkalasi ham bo'lishi mumkin — .gitignore'dagi
    shaxsiy fayl)."""
    result = script.check_dissertation_theory(script.DOCX_PATH)
    if result is None:
        assert not os.path.exists(script.DOCX_PATH)
    else:
        assert "agentive_mentions" in result
        assert isinstance(result["agentive_mentions"], list)
