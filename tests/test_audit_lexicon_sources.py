"""
tests/test_audit_lexicon_sources.py
======================================
`scripts/audit_lexicon_sources.py` — lug'at manbalari (reports/faza_2_lexicon_sources.md).

Qo'riqlanadigan faktlar:
- `KKT_Terminologik_Lugat` kod tomonidan ishlatilmaydi (yuklanmaydi, PSB bo'sh).
- 100_soz GOLD iboralari lug'atga yuklanadi (1500-JSON ichidagi "100 SOZ"
  kategoriyasi orqali) — lekin `translate_phrase()` natijasiga TA'SIR QILMAYDI.
  Kimdir butun ibora bo'yicha qidiruv qo'shsa, oxirgi test yiqiladi va gold
  javoblar to'g'ridan-to'g'ri qaytayotgani (aylanma baholash) ko'rinib qoladi.
"""
from __future__ import annotations

import os
import sqlite3
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import audit_lexicon_sources as script  # noqa: E402


def test_terminology_dictionary_is_not_loaded_anywhere(isolated_kkt_module):
    m = isolated_kkt_module
    term = script.terminology_facts(m)
    assert (term["n_words"], term["n_pairs"]) == (20, 75)
    assert term["file_refs"] == []
    assert term["insert_terms"] == []
    assert set(term["psb_rows"].values()) == {0}
    assert term["psb_domain_passed"] == []


def test_1500_json_terminology_category_is_skipped_but_gold_category_is_loaded(isolated_kkt_module):
    rows = {r["kategoriya"]: r for r in script.category_load_table(isolated_kkt_module)}
    assert rows["KKT TERMINOLOGIK LUGAT (KO'P MA'NOLI TERMINLAR)"]["ub_en_w_da"] == 0
    assert rows["100 SOZ (MORFEMIK TAHLIL)"]["ub_en_w_da"] == 100


def test_gold_100_rows_do_not_change_translate_phrase_outputs(isolated_kkt_module):
    m = isolated_kkt_module
    paths = (m.DB_UB_EN, m.DB_UB_UZ, m.DB_MDB_UZ)
    abl = script.gold100_ablation(m)
    assert abl["in_ub_en"] == 100 and abl["in_mdb"] == 100
    assert abl["diff"] == {}, f"100_soz gold qatorlari natijaga ta'sir qilyapti: {abl['diff']}"
    assert abl["score_base"] == abl["score_ablated"]
    assert (m.DB_UB_EN, m.DB_UB_UZ, m.DB_MDB_UZ) == paths  # yo'llar tiklandi
    con = sqlite3.connect(m.DB_UB_EN)  # asl baza o'zgarmagan
    assert con.execute("SELECT COUNT(*) FROM words WHERE headword='from our books'").fetchone()[0] == 1
    con.close()
