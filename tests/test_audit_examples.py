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
