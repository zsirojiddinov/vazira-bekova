"""
tests/test_gold_separation.py
================================
Gold test to'plamlari baza manbalaridan FIZIK ajratilganini qo'riqlovchi
testlar (`CLAUDE.md`, `reports/faza_3_plan.md` — qabul mezonlari).

Sabab: mavjud 100_soz gold juftlari 1500-JSON ichidagi "100 SOZ" kategoriyasi
orqali lug'atga yuklangan (`reports/faza_2_lexicon_sources.md`). Kelajakdagi
gold to'plamlar `gold/` papkasida (repo ildizida, `data/` EMAS) saqlanadi.
Format: `gold/*.json` — JSON ro'yxat, har bir element kamida
{"english": str, "uzbek": str} maydonlariga ega.

1. Manba darajasi — baza qurilishi (audit hook bilan) `gold/` dagi birorta
   faylni OCHMAYDI va `data/` dan faqat ma'lum manbalarni o'qiydi.
2. Natija darajasi — `gold/*.json` dagi test-case'lar qurilgan lug'atda yo'q.
3. Statik — `scripts/` dagi har bir `translate_phrase(` chaqiruvi
   `allow_write=False` bilan (aks holda natija bazaga keshlanadi).
"""
from __future__ import annotations

import ast
import contextlib
import glob
import io
import json
import os
import sqlite3
import sys

import pytest

from conftest import REPO_ROOT, _build_databases, _make_isolated_copy

GOLD_DIR_NAME = "gold"

# Baza qurilishi `data/` dan o'qishi RUXSAT etilgan manbalar. Yangi loader
# boshqa fayl o'qisa — test yiqiladi: fayl gold EMASLIGI tasdiqlanib, shu
# ro'yxatga ONGLI ravishda qo'shilishi kerak.
ALLOWED_DATA_SOURCES = {
    "data/1500_EN_UZ_6_POS_sorted.20.json",
    "data/Table_English 1-7 Vazn Type 2 14.02.2024.json",
    "data/Lotinda Table_Uzbek 1-7 Vazn 11.02.2025.json",
}

CANARY = {"english": "canary gold phrase zeta", "uzbek": "kanareyka gold iborasi zeta"}

# sys.addaudithook ni o'chirib bo'lmaydi — bitta marta, bayroq bilan ro'yxatga olinadi.
_REC = {"on": False, "paths": []}


def _audit_hook(event, args):
    if _REC["on"] and event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        _REC["paths"].append(os.fsdecode(args[0]))


sys.addaudithook(_audit_hook)


@contextlib.contextmanager
def _record_opens():
    _REC["paths"] = []
    _REC["on"] = True
    try:
        yield _REC["paths"]
    finally:
        _REC["on"] = False


def _fresh_build_with_canary_gold(dest):
    """`dest` ga izolyatsiyalangan nusxa + `gold/canary.json` (qoida gold
    turishi kerak deb aytgan joy) yaratadi, bazani audit hook ostida quradi.
    Qaytaradi: (modul, ochilgan fayllar — dest ga nisbatan)."""
    dest.mkdir()
    _make_isolated_copy(str(dest))
    gold_dir = dest / GOLD_DIR_NAME
    gold_dir.mkdir()
    (gold_dir / "canary.json").write_text(json.dumps([CANARY], ensure_ascii=False), encoding="utf-8")

    for name in ("kkt_v20_soz_tartibi", "data_loader"):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(dest))
    try:
        with _record_opens() as paths, contextlib.redirect_stdout(io.StringIO()):
            import kkt_v20_soz_tartibi as m
            assert m.SCRIPT_DIR == str(dest), "izolyatsiya buzilgan"
            _build_databases(m)
        root = os.path.realpath(str(dest))
        rel = {os.path.relpath(os.path.realpath(p), root) for p in paths
               if os.path.realpath(p).startswith(root + os.sep)}
        return m, rel
    finally:
        sys.path.remove(str(dest))
        for name in ("kkt_v20_soz_tartibi", "data_loader"):
            sys.modules.pop(name, None)


# ═══════════════════════════════════════════════════════════════════
#  1. Manba darajasi
# ═══════════════════════════════════════════════════════════════════
def test_db_build_never_opens_gold_dir_and_reads_only_known_sources(tmp_path):
    m, opened = _fresh_build_with_canary_gold(tmp_path / "env")

    # Salbiy nazorat: hook haqiqatan ishlayapti — ma'lum manbalar ko'rindi.
    data_opened = {p.replace(os.sep, "/") for p in opened if p.startswith("data" + os.sep)}
    assert ALLOWED_DATA_SOURCES <= data_opened, f"hook ma'lum manbalarni ko'rmadi: {data_opened}"

    gold_opened = [p for p in opened if p.split(os.sep)[0] == GOLD_DIR_NAME]
    assert not gold_opened, f"baza qurilishi gold/ faylini ochdi: {gold_opened}"

    unexpected = data_opened - ALLOWED_DATA_SOURCES
    assert not unexpected, (
        f"baza qurilishi data/ dan YANGI manbani o'qidi: {sorted(unexpected)} — agar bu gold EMAS "
        "bo'lsa, ALLOWED_DATA_SOURCES ga ongli qo'shing; gold bo'lsa — gold/ ga ko'chiring (CLAUDE.md)"
    )

    # Natija: kanareyka ibora qurilgan lug'atda ham, MDB nomzodlarida ham yo'q.
    con = sqlite3.connect(m.DB_UB_EN)
    assert con.execute("SELECT COUNT(*) FROM words WHERE headword=?", (CANARY["english"],)).fetchone()[0] == 0
    con.close()
    con = sqlite3.connect(m.DB_UB_UZ)
    assert con.execute("SELECT COUNT(*) FROM words WHERE headword=?", (CANARY["uzbek"],)).fetchone()[0] == 0
    con.close()
    con = sqlite3.connect(m.DB_MDB_UZ)
    assert con.execute("SELECT COUNT(*) FROM candidates WHERE uz_word=?", (CANARY["uzbek"],)).fetchone()[0] == 0
    con.close()


# ═══════════════════════════════════════════════════════════════════
#  2. Natija darajasi — haqiqiy gold/ to'plamlar
# ═══════════════════════════════════════════════════════════════════
def _load_gold_cases() -> list[tuple[str, dict]]:
    files = sorted(glob.glob(os.path.join(REPO_ROOT, GOLD_DIR_NAME, "*.json")))
    cases = []
    for path in files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list), f"{path}: gold fayl JSON ro'yxat bo'lishi kerak"
        for i, e in enumerate(data):
            assert isinstance(e, dict) and isinstance(e.get("english"), str) and isinstance(e.get("uzbek"), str), (
                f"{path}[{i}]: har bir element {{'english': str, 'uzbek': str}} bo'lishi kerak"
            )
            cases.append((os.path.relpath(path, REPO_ROOT), e))
    return cases


def test_gold_dir_cases_absent_from_built_lexicon(isolated_kkt_module):
    cases = _load_gold_cases()
    if not cases:
        pytest.skip("gold/*.json hali yo'q — Faza 3 da gold to'plam qo'shilganda avtomatik faollashadi")
    m = isolated_kkt_module
    ub_en, ub_uz, mdb = (sqlite3.connect(p) for p in (m.DB_UB_EN, m.DB_UB_UZ, m.DB_MDB_UZ))
    leaked = []
    for src, e in cases:
        en, uz = e["english"].strip().lower(), e["uzbek"].strip()
        hits = []
        if ub_en.execute("SELECT 1 FROM words WHERE headword=?", (en,)).fetchone():
            hits.append("UB_en_w")
        if ub_uz.execute("SELECT 1 FROM words WHERE headword=?", (uz,)).fetchone():
            hits.append("UB_uz_w")
        if mdb.execute("SELECT 1 FROM candidates WHERE uz_word=?", (uz,)).fetchone():
            hits.append("MDB_uz_w")
        if hits:
            leaked.append((src, en, uz, hits))
    for c in (ub_en, ub_uz, mdb):
        c.close()
    assert not leaked, (
        "gold test-case'lar qurilgan bazada bor (CLAUDE.md — fizik ajratish SHART). Agar biror so'z 1500-lug'atda "
        f"mustaqil ravishda bo'lsa, u holatni alohida hujjatlashtiring: {leaked[:10]}"
    )


# ═══════════════════════════════════════════════════════════════════
#  3. Statik — baholash skriptlari bazaga yozmaydi
# ═══════════════════════════════════════════════════════════════════
def _translate_phrase_calls_without_readonly(path: str) -> list[str]:
    """Fayldagi HAQIQIY `translate_phrase(...)` / `m.translate_phrase(...)`
    chaqiruvlarini (ast orqali — satr/izoh ichidagi eslatmalar hisobga
    olinmaydi) topib, `allow_write=False` kalit so'zli argumenti yo'qlarini
    qaytaradi."""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=path)
    bad = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
        if name != "translate_phrase":
            continue
        ok = any(kw.arg == "allow_write" and isinstance(kw.value, ast.Constant) and kw.value.value is False
                 for kw in node.keywords)
        if not ok:
            bad.append(f"{os.path.relpath(path, REPO_ROOT)}:{node.lineno}")
    return bad


def test_scripts_call_translate_phrase_only_with_allow_write_false():
    """scripts/ dagi har bir `translate_phrase(...)` chaqiruvi
    `allow_write=False` bilan — oddiy rejimda natija `db_insert(..., "auto")`
    bilan bazaga keshlanadi va keyingi baholashda lug'at javobiga aylanadi."""
    offenders = []
    for path in sorted(glob.glob(os.path.join(REPO_ROOT, "scripts", "*.py"))):
        offenders += _translate_phrase_calls_without_readonly(path)
    assert not offenders, "allow_write=False siz translate_phrase chaqiruvi: " + ", ".join(offenders)


def test_static_checker_detects_missing_allow_write(tmp_path):
    """Salbiy nazorat: tekshiruvchi haqiqatan ushlaydi (bo'sh o'tib ketmaydi)."""
    bad = tmp_path / "bad.py"
    bad.write_text("m.translate_phrase('x')\nm.translate_phrase('y', allow_write=False)\n"
                   "s = 'translate_phrase(z)'\n", encoding="utf-8")
    assert [x.rsplit(":", 1)[1] for x in _translate_phrase_calls_without_readonly(str(bad))] == ["1"]
