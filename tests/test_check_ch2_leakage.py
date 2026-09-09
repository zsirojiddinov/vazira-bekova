"""
tests/test_check_ch2_leakage.py
==================================
`scripts/check_ch2_leakage.py` — asl dissertatsiya fayli
(`data/desertatsiya.docx`) qo'shilgandan keyin yozilgan skript, uni
CH2_EVX_EXAMPLES bilan solishtiradi.

MUHIM: `data/desertatsiya.docx` — foydalanuvchining SHAXSIY fayli,
`.gitignore` da aniq chiqarib tashlangan ("repo'ga chiqmasligi kerak"),
demak CI/boshqa klonlarda bu fayl YO'Q. Shu sabab bu modul'dagi BARCHA
testlar shu faylning mavjudligiga bog'liq (`skipif`) — fayl bo'lmasa,
testlar FAIL emas, SKIP bo'ladi (xuddi Faza 1'da `so_zlar_bazasi_un.docx`
yo'qligi bilan bir xil mantiq)."""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import pytest

import check_ch2_leakage as script  # noqa: E402

DOCX_PATH = os.path.join(REPO_ROOT, "data", "desertatsiya.docx")
requires_docx = pytest.mark.skipif(
    not os.path.exists(DOCX_PATH),
    reason="data/desertatsiya.docx shaxsiy fayl, .gitignore'da — bu muhitda yo'q",
)


@pytest.fixture(scope="module")
def docx_items():
    return script.load_docx(DOCX_PATH)


@pytest.fixture(scope="module")
def chapter_bounds(docx_items):
    return script.find_chapter_bounds(docx_items)


@requires_docx
def test_all_four_chapters_found(chapter_bounds):
    """Dissertatsiya "Kirish, to'rtta bob, xulosa..." tuzilishiga ega
    (docx #70) — I/II/III/IV bobning barchasi topilishi kerak."""
    assert set(chapter_bounds.keys()) == {"I", "II", "III", "IV"}
    for ch, (s, e) in chapter_bounds.items():
        assert s < e, f"{ch} bob oralig'i bo'sh: {(s, e)}"


@requires_docx
def test_chapters_appear_in_order(chapter_bounds):
    order = ["I", "II", "III", "IV"]
    starts = [chapter_bounds[c][0] for c in order]
    assert starts == sorted(starts)


@requires_docx
def test_ch2_records_extracted_and_cover_most_examples(docx_items, chapter_bounds):
    """Barcha 52 ta CH2_EVX_EXAMPLES yozuvi docx'dan avtomatik ajratib
    olingan yozuvlar bilan bog'lanishi kerak (EN to'g'ridan-to'g'ri yoki
    UZ-fallback orqali) — bu skriptning asosiy ishlash qobiliyati."""
    import kkt_v20_soz_tartibi as m

    records = script.extract_ch2_records(docx_items, chapter_bounds["II"])
    pairs, _unused = script.match_ch2_examples(m.CH2_EVX_EXAMPLES, records)
    n_matched = sum(1 for p in pairs if p["docx"] is not None)
    assert n_matched == len(m.CH2_EVX_EXAMPLES), (
        f"{len(m.CH2_EVX_EXAMPLES) - n_matched} ta CH2 yozuv docx'dan avtomatik topilmadi"
    )


@requires_docx
def test_schoolboys_mismatch_confirmed_against_real_docx(docx_items, chapter_bounds):
    """reports/faza_1.md da FARAZ qilingan "schoolboys->Bojxonalar — oldingi
    customhouses qatoridan nusxalangan" xulosasi endi HAQIQIY docx bilan
    TASDIQLANADI: docx'da "schoolboys" -> "maktab+bola+lar" ("maktabbolalar"),
    "Bojxonalar" EMAS."""
    import kkt_v20_soz_tartibi as m

    records = script.extract_ch2_records(docx_items, chapter_bounds["II"])
    pairs, _unused = script.match_ch2_examples(m.CH2_EVX_EXAMPLES, records)
    entry = next(p for p in pairs if p["ch2"]["en"] == "schoolboys")
    assert entry["docx"] is not None
    assert entry["ch2"]["uz"] == "Bojxonalar"
    assert entry["docx"]["uz_marker_word"] == "maktabbolalar"
    assert entry["docx"]["uz_marker_word"] != entry["ch2"]["uz"]


@requires_docx
def test_capabilityies_typo_not_present_anywhere_in_docx(docx_items, chapter_bounds):
    """CH2_EVX_EXAMPLES dagi "capabilityies" yozilishi docx'ning HECH bir
    joyida (na paragraf, na jadval) uchramaydi — faqat to'g'ri
    "capabilities" bor. Demak bu — transkripsiya (qo'lda ko'chirish)
    xatosi, dissertatsiyaning o'zida yo'q."""
    full_text = []
    for it in docx_items:
        if it.__class__.__name__ == "Paragraph":
            full_text.append(it.text)
        else:
            for row in it.rows:
                for cell in row.cells:
                    full_text.append(cell.text)
    joined = " ".join(full_text).lower()
    assert "capabilityies" not in joined
    assert "capabilities" in joined


@requires_docx
def test_will_return_now_exists_in_docx_chapter2(docx_items, chapter_bounds):
    """reports/faza_1_audit_examples.md "will return CH2_EVX_EXAMPLES da
    yo'q" deb qayd etgan edi va bu haligacha to'g'ri (CH2_EVX_EXAMPLES da
    yo'q) — LEKIN endi ma'lum bo'ldiki, "will return"->"qaytadi" misoli II
    bobning O'ZIDA bor, faqat CH2_EVX_EXAMPLES ga kiritilmagan."""
    import kkt_v20_soz_tartibi as m

    en_values = {ex["en"] for ex in m.CH2_EVX_EXAMPLES}
    assert "will return" not in en_values  # hali ham CH2 ro'yxatida yo'q

    records = script.extract_ch2_records(docx_items, chapter_bounds["II"])
    matched = [r for r in records if script.normalize(r["en_marker_word"]) == "will return"]
    assert matched, "\"will return\" II bobda topilishi kerak edi"
    assert script.normalize(matched[0]["uz_marker_word"]) == "qaytadi"


@requires_docx
def test_leakage_search_finds_only_bibliography_hits(docx_items, chapter_bounds):
    """III/IV bobda CH2 headword'lari bo'yicha qidiruv joriy holatda
    FAQAT adabiyotlar ro'yxati (bibliografiya) ichida topiladi — hisobot
    jadvali/foiz ko'rsatkichlari ICHIDA emas (aylanma baholash xavfi
    yo'qligining bir dalili)."""
    import kkt_v20_soz_tartibi as m

    unique_en = sorted({ex["en"].strip().lower() for ex in m.CH2_EVX_EXAMPLES}, key=len, reverse=True)
    hits = script.search_leakage(docx_items, chapter_bounds, ["III", "IV"], unique_en)
    assert all(not h["in_table"] for h in hits), "Jadval ichida topilgan hit bor — qo'lda tekshirilishi kerak"


@requires_docx
def test_summarize_leakage_by_headword_includes_zero_hit_words(docx_items, chapter_bounds):
    """Har bir headword — hatto hech qanday moslik topilmagan bo'lsa ham —
    natija ro'yxatida ALOHIDA qator sifatida ko'rinishi kerak (foydalanuvchi
    so'rovi, 2026-09-09: "topilmadi" xulosasi reproduksiya qilinishi kerak)."""
    import kkt_v20_soz_tartibi as m

    unique_en = sorted({ex["en"].strip().lower() for ex in m.CH2_EVX_EXAMPLES}, key=len, reverse=True)
    hits = script.search_leakage(docx_items, chapter_bounds, ["III", "IV"], unique_en)
    summary = script.summarize_leakage_by_headword(unique_en, hits, ["III", "IV"])
    assert len(summary) == len(unique_en)
    by_word = {r["headword"]: r for r in summary}
    assert by_word["will"]["total"] == 0  # umumiy so'z, III/IV da topilmasligi kutiladi
    assert by_word["information"]["total"] > 0  # bibliografiyada bir necha marta uchraydi
    for r in summary:
        assert r["total"] == r["per_chapter"].get("III", 0) + r["per_chapter"].get("IV", 0)


@requires_docx
def test_list_evaluation_context_blocks_includes_the_headline_accuracy_table(docx_items, chapter_bounds):
    """Dissertatsiyaning yagona raqamli aniqlik jadvali (4.3-jadval, "Tarjima
    foizi", 97,7%) mustaqil "aniqlik/foiz" inventarizatsiyasida ko'rinishi
    kerak — bu jadval "280 ta so'z" ustida hisoblanganini, lekin o'sha 280
    so'zning matni yo'qligini reports/ch2_leakage_check.md aniq qayd etadi."""
    blocks = script.list_evaluation_context_blocks(docx_items, chapter_bounds, ["III", "IV"])
    assert any("97,7%" in b["snippet"] or "Tarjima foizi" in b["snippet"] for b in blocks)


@requires_docx
def test_extract_ch2_records_infers_pos_from_formal_model(docx_items, chapter_bounds):
    """POS avtomatik ravishda formal model tenglamasining BIRINCHI harfidan
    (KKT belgisi) chiqarilishi kerak — Claude tomonidan qo'lda emas."""
    records = script.extract_ch2_records(docx_items, chapter_bounds["II"])
    by_word = {r["en_marker_word"]: r for r in records if r["en_marker_word"]}
    assert by_word["will"]["inferred_pos"] == "Fe'l"  # G(G4) = ...
    assert by_word["here"]["inferred_pos"] == "Ravish"  # N(N) = ...
    assert by_word["one"]["inferred_pos"] == "Son"  # F(F) = ...
    assert by_word["I"]["inferred_pos"] == "Olmosh"  # M(M1) = ...
    assert by_word["larger"]["inferred_pos"] == "Sifat"  # P5(P_S) = ...
