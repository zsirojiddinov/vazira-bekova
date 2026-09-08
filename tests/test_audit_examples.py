"""
tests/test_audit_examples.py
===============================
`scripts/audit_examples.py` — asosan uning NAMED_IN_TASK ro'yxati va
`CH2_EVX_EXAMPLES` manbasi bilan mosligini tekshiradi. Tarjima natijalari
(pass/fail) `reports/faza_1_audit_examples.md` da (skriptni ishga tushirib
qayta generatsiya qilinadigan hisobotda) qayd etiladi — bu yerda emas.
"""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import audit_examples as script  # noqa: E402


def test_named_in_task_words_exist_in_ch2_evx_examples(isolated_kkt_module):
    """Topshiriqda nomlab o'tilgan 4 ta so'zdan KAMIDA 3 tasi (capabilityies,
    leafes, schoolboys) kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES da ANIQ
    o'zi kabi (xuddi shu yozilishda) topilishi kerak — bu ularning manbasi
    aynan shu ro'yxat ekanini tasdiqlaydi (fabrikatsiya emas)."""
    m = isolated_kkt_module
    en_values = {ex["en"] for ex in m.CH2_EVX_EXAMPLES}
    for word in ("capabilityies", "leafes", "schoolboys"):
        assert word in en_values, f"'{word}' CH2_EVX_EXAMPLES da topilmadi"


def test_will_return_is_not_a_literal_ch2_entry(isolated_kkt_module):
    """"will return" (ibora sifatida) CH2_EVX_EXAMPLES da YO'Q — faqat
    "will" alohida bor. Bu skriptning docx_note/ogohlantirishida aniq
    aytilgan farq — shu holat saqlanib qolganini tasdiqlaydi."""
    m = isolated_kkt_module
    en_values = {ex["en"] for ex in m.CH2_EVX_EXAMPLES}
    assert "will return" not in en_values
    assert "will" in en_values


def test_schoolboys_reference_is_the_known_data_bug(isolated_kkt_module):
    """"schoolboys" uchun CH2_EVX_EXAMPLES dagi "uz" qiymati — "Bojxonalar"
    ("customhouses" bilan bir xil qator) — bu ma'lum, tuzatilmagan
    ma'lumot xatosi (qarang: reports/faza_1.md). Bu test o'sha xato hali
    joyida ekanini kuzatadi (Faza 2 uni tuzatgach, bu test yangilanishi
    kerak)."""
    m = isolated_kkt_module
    entry = next(ex for ex in m.CH2_EVX_EXAMPLES if ex["en"] == "schoolboys")
    assert entry["uz"] == "Bojxonalar"


def test_normalize_available_from_common_module():
    assert script.normalize("Bojxonalar") == "bojxonalar"


# ─────────────────────────────────────────────────────────────────────────
# Aylanma (circular) tekshiruv — provenance funksiyalari.
#
# DIQQAT: `_provenance_for()` ataylab REPO ILDIZIDAGI HAQIQIY UB_en_w.db
# ni o'qiydi (faqat SELECT — repo bazasi buzilmasin degan Faza 0 qoidasi
# shu sabab BUZILMAYDI: bu funksiya hech qachon yozmaydi, faqat o'qiydi).
# Bu testlar ham shu sababli `isolated_kkt_module` FIXTURE'siz — haqiqiy
# repo bazasi ustida — ishlaydi.
# ─────────────────────────────────────────────────────────────────────────

def test_provenance_for_schoolboys_is_fully_circular():
    """"schoolboys" UB_en_w'da FAQAT bitta qatorga ega va u source='chapter2_evx'
    — ya'ni bu so'z faqat load_ch2_evx_examples() orqali kirgan, boshqa
    hech qanday mustaqil manbada yo'q (reports/faza_1.md dagi batafsil
    jadvalning asosi)."""
    rows = script._provenance_for("schoolboys")
    assert len(rows) == 1
    _id, translation, pos, source = rows[0]
    assert source == "chapter2_evx"


def test_provenance_for_much_has_independent_json_source():
    """"much" — 26 ta aylanma-nomzoddan YAGONA istisno: UB_en_w'da IKKITA
    qatorga ega, biri source='json' (1500-so'zlik lug'atdan, CH2_EVX_EXAMPLES'ga
    aloqasi yo'q) — va aynan SHU qator translate_phrase() tomonidan
    tanlanadi (birinchi qator, id bo'yicha eng kichik)."""
    rows = script._provenance_for("much")
    sources = {r[3] for r in rows}
    assert "json" in sources
    assert "chapter2_evx" in sources
    # birinchi (eng kichik id) qator tanlanadi (psb_select_meaning: rows[0])
    assert rows[0][3] == "json"


def test_load_independent_source_headwords_includes_common_words():
    sources = script._load_independent_source_headwords()
    words_1500 = sources["data/1500_EN_UZ_6_POS_sorted.20.json"]
    assert "much" in words_1500
    assert "schoolboys" not in words_1500  # aylanma da'vosining manfiy nazorati
