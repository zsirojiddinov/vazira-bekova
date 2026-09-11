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
from _common import normalize  # noqa: E402


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


def test_classify_full_chapter2_examples_returns_none_or_superset_of_ch2():
    """`classify_full_chapter2_examples()` (2026-09-09, `check_ch2_leakage.py`
    orqali II bobning TO'LIQ namunalarini ishlatadi) — docx yo'q bo'lsa None,
    bo'lsa CH2_EVX_EXAMPLES dagi 5 ta "-er" so'zning HAMMASINI o'z ichiga
    olishi va ularning barchasi hali ham SIFAT+ER (hech qanday agentiv)
    bo'lishi kerak."""
    full_rows = script.classify_full_chapter2_examples(script.DOCX_PATH)
    if full_rows is None:
        assert not os.path.exists(script.DOCX_PATH)
        return
    ch2_rows = script.classify_ch2_examples()
    # apostrof shakllari (ASCII ' vs modifier-harf ʻ) farqli bo'lishi mumkin
    # (CH2_EVX_EXAMPLES qo'lda yozilgan, docx'dan ekstraktsiya esa xom
    # Unicode belgini saqlaydi) — shu sabab normalize() bilan solishtiramiz.
    full_words = {(normalize(r["word"]), normalize(r["uzbek"])) for r in full_rows}
    for r in ch2_rows:
        key = (normalize(r["word"]), normalize(r["uzbek"]))
        assert key in full_words, f"{r['word']}/{r['uzbek']} to'liq ro'yxatda yo'q"
    assert all(r["group"] == "SIFAT+ER (qiyosiy)" for r in full_rows), (
        "II bobning to'liq (CH2 + qo'shimcha) namunalarida ham agentiv fe'l+er topilmasligi kerak edi"
    )
    # "larger"/"bigger" — CH2_EVX_EXAMPLES'da YO'Q, lekin II bobning o'zida bor.
    extra_words = {r["word"] for r in full_rows if not r["in_ch2_evx_examples"]}
    assert {"larger", "bigger"} <= extra_words


def test_kkt_spec_has_er_only_as_comparative_and_no_agentive_category():
    """Rasmiy spesifikatsiya (data/kkt_spec.json): "-er" faqat qiyosiy
    daraja qoidalarida (Sifat 2.21/2.23/2.25/2.27/2.29, Ravish 3.3);
    agentiv (fe'l+er -> shaxs oti) kategoriyasi YO'Q — faza_2_er_gap.md 6-bo'lim."""
    spec = script.check_kkt_spec()
    assert spec is not None
    assert [r["uid"] for r in spec["er_rules"]] == ["2.21", "2.23", "2.25", "2.27", "2.29", "3.3"]
    assert {r["pos"] for r in spec["er_rules"]} == {"Sifat", "Ravish"}
    assert [f for _, _, f in spec["er_forms"]] == ["cleverer", "larger", "bigger", "busier", "gayer", "faster"]
    assert spec["agentive_hits"] == []
    assert spec["ot_er_or_words"] == []
    assert [r["uid"] for r in spec["verb_to_noun"]] == ["2.13"]  # yagona fe'l->ot qoidasi: -ation
