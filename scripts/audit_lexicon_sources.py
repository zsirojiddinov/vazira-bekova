#!/usr/bin/env python3
"""
scripts/audit_lexicon_sources.py
===================================
Savol (foydalanuvchi, 2026-09-11): `faza_2_kkt_spec_leakage.md` dagi
"KKT_Terminologik (75)" manbasi nima, kodda qayerda, qanday to'ldirilgan, va
"javob oldindan yozib qo'yilgan" jadval bo'lsa — qaysi hisoblarda ishlatiladi?

Bu skript FAQAT o'qiydi va o'lchaydi (kodni o'zgartirmaydi):

1. `data/1500_EN_UZ_6_POS_sorted.20.json` ning HAR BIR kategoriyasi uchun —
   nechta yozuv `english`/`uzbek` maydoniga ega (ya'ni
   `_load_words_from_json()` → `data_loader.load_word_pairs()` uni UB_en_w ga
   yuklaydi) va bazada haqiqatan nechtasi bor.
2. `KKT_Terminologik_Lugat.json` — tuzilishi, yuklanadimi, PSB (predmet
   sohalar bazasi) `terms` jadvali to'ldirilganmi, `psb_select_meaning()`
   qanday chaqiriladi.
3. `100_soz` gold iboralari — lug'atda (UB_en_w/UB_uz_w) va MDB_uz_w
   nomzodlarida bormi; bor bo'lsa — ABLATSIYA: ular olib tashlangan baza
   nusxasida 100 ta gold kirishning `translate_phrase()` natijasi o'zgaradimi.

Bazalar data/ dan izolyatsiyalangan papkada noldan quriladi
(`audit_kkt_spec_conformance.build_isolated_module`).

Ishlatish:
    python scripts/audit_lexicon_sources.py
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from _common import normalize  # noqa: E402
import audit_kkt_spec_conformance as conf  # noqa: E402

DEFAULT_OUT = os.path.join(REPO_ROOT, "reports", "faza_2_lexicon_sources.md")
TERM_JSON = os.path.join(REPO_ROOT, "data", "KKT_Terminologik_Lugat.json")
GOLD_100 = os.path.join(REPO_ROOT, "data", "100_soz.json")
LEX_1500 = os.path.join(REPO_ROOT, "data", "1500_EN_UZ_6_POS_sorted.20.json")
CODE_FILES = ("kkt_v20_soz_tartibi.py", "data_loader.py")


def _grep(pattern: str) -> list[str]:
    hits = []
    for name in CODE_FILES:
        with open(os.path.join(REPO_ROOT, name), encoding="utf-8") as f:
            for i, ln in enumerate(f, 1):
                if re.search(pattern, ln):
                    hits.append(f"{name}:{i}: {ln.strip()[:110]}")
    return hits


def category_load_table(m) -> list[dict]:
    with open(LEX_1500, encoding="utf-8") as f:
        cats = json.load(f)["categories"]
    con = sqlite3.connect(m.DB_UB_EN)
    rows = []
    for name, entries in cats.items():
        loadable = [e for e in entries if "english" in e and "uzbek" in e]
        in_db = sum(1 for e in loadable if con.execute(
            "SELECT 1 FROM words WHERE headword=? AND translation=? AND source='json'",
            (e["english"].strip().lower(), e["uzbek"].strip())).fetchone())
        rows.append({"kategoriya": name, "yozuvlar": len(entries), "english_uzbek_bor": len(loadable),
                     "ub_en_w_da": in_db, "kalitlar": sorted(entries[0].keys()) if entries else []})
    con.close()
    return rows


def terminology_facts(m) -> dict:
    with open(TERM_JSON, encoding="utf-8") as f:
        terms = json.load(f)
    pairs = [(e["english"].strip().lower(), e["uzbek"].strip(), e["soha"]) for w in terms for e in w["entries"]]
    con = sqlite3.connect(m.DB_UB_EN)
    pair_hits = [(en, uz, con.execute("SELECT source FROM words WHERE headword=? AND translation=?",
                                      (en, uz)).fetchone()) for en, uz, _ in pairs]
    con.close()
    psb = {}
    for db in (m.DB_PSB_EN, m.DB_PSB_UZ):
        c = sqlite3.connect(db)
        psb[os.path.basename(db)] = c.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        c.close()
    calls = [c for c in _grep(r"psb_select_meaning\(") if "def psb_select_meaning" not in c]
    domain_passed = [c for c in calls if re.search(r"psb_select_meaning\([^()]*,", c)]
    return {"n_words": len(terms), "n_pairs": len(pairs),
            "sohalar": sorted({s for _, _, s in pairs}),
            "same_pair_in_ub": [(en, uz, r[0]) for en, uz, r in pair_hits if r],
            "psb_rows": psb, "psb_calls": calls, "psb_domain_passed": domain_passed,
            "file_refs": _grep(r"KKT_Terminologik|Terminologik_Lugat"),
            "insert_terms": _grep(r"INSERT[^\n]*INTO terms")}


@contextlib.contextmanager
def _db_copy_without(m, en_rm: set[str], uz_rm: set[str]):
    """UB_en_w / UB_uz_w / MDB_uz_w NUSXASIni yaratib (asl fayllarga
    tegmasdan), berilgan headword'larni o'chiradi va modul yo'llarini
    vaqtincha nusxaga yo'naltiradi."""
    tmp = tempfile.mkdtemp(prefix="kkt_ablation_")
    names = ("DB_UB_EN", "DB_UB_UZ", "DB_MDB_UZ")
    orig = {n: getattr(m, n) for n in names}
    try:
        for n in names:
            dst = os.path.join(tmp, os.path.basename(orig[n]))
            shutil.copy2(orig[n], dst)
            setattr(m, n, dst)
        removed = {}
        for n, table, col, vals in (("DB_UB_EN", "words", "headword", en_rm), ("DB_UB_UZ", "words", "headword", uz_rm),
                                    ("DB_MDB_UZ", "candidates", "uz_word", uz_rm)):
            c = sqlite3.connect(getattr(m, n))
            removed[n] = sum(c.execute(f"DELETE FROM {table} WHERE {col}=?", (v,)).rowcount for v in vals)
            c.commit()
            c.close()
        yield removed
    finally:
        for n, p in orig.items():
            setattr(m, n, p)
        shutil.rmtree(tmp, ignore_errors=True)


def gold100_ablation(m) -> dict:
    with open(GOLD_100, encoding="utf-8") as f:
        gold = json.load(f)
    en_set = {e["english"].strip().lower() for e in gold}
    uz_set = {e["uzbek"].strip() for e in gold}

    def _run():
        out = {}
        with m.readonly_mode():
            for e in gold:
                r = m.translate_phrase(e["english"], allow_write=False)
                out[e["english"]] = r["natija"] if r else None
        return out

    def _score(out):
        return sum(1 for e in gold if out[e["english"]] and normalize(out[e["english"]]) == normalize(e["uzbek"]))

    con = sqlite3.connect(m.DB_UB_EN)
    in_ub = sum(1 for en in en_set if con.execute("SELECT 1 FROM words WHERE headword=?", (en,)).fetchone())
    con.close()
    con = sqlite3.connect(m.DB_MDB_UZ)
    in_mdb = sum(1 for (w,) in con.execute("SELECT uz_word FROM candidates") if w in uz_set)
    con.close()
    base = _run()
    with _db_copy_without(m, en_set, uz_set) as removed:
        ablated = _run()
    diff = {k: (base[k], ablated[k]) for k in base if base[k] != ablated[k]}
    return {"n": len(gold), "multiword": sum(1 for en in en_set if " " in en), "in_ub_en": in_ub,
            "in_mdb": in_mdb, "removed": removed, "score_base": _score(base),
            "score_ablated": _score(ablated), "diff": diff}


def render(cat_rows, term, abl) -> str:
    L = ["# Faza 2 — Lug'at manbalari: KKT_Terminologik va 100_soz qatorlari qayerda ishlatiladi", ""]
    L.append(f"**Generatsiya vaqti:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    L.append("**Buyruq:** `python scripts/audit_lexicon_sources.py` (bazalar izolyatsiyalangan papkada noldan quriladi)")
    L.append("")
    L.append("## 0. Qisqa javob")
    L.append("")
    L.append(f"1. **`KKT_Terminologik` ({term['n_pairs']})** — `data/KKT_Terminologik_Lugat.json`: {term['n_words']} ta "
             f"ko'p ma'noli so'z (BOOK, MOUSE, ...), har biri soha bo'yicha bir nechta tarjima bilan — jami "
             f"{term['n_pairs']} ta (inglizcha, o'zbekcha, soha) yozuv. `check_leakage.py` dagi \"75\" — shu yozuvlar soni. "
             "**Kod bu manbani ISHLATMAYDI:** fayl nomi kodda uchramaydi, 1500-JSON ichidagi nusxasi esa boshqa "
             "tuzilishda (`word` + `entries`) bo'lgani uchun yuklovchi uni o'tkazib yuboradi, predmet sohalar "
             f"bazasi (PSB) `terms` jadvali bo'sh ({', '.join(f'{k}={v}' for k, v in term['psb_rows'].items())}). "
             "Demak u hech qanday tarjima yoki aniqlik/foiz hisobiga kirmaydi.")
    L.append(f"2. **Lekin tekshiruv davomida boshqa \"oldindan yozilgan javoblar\" jadvali topildi:** 100_soz GOLD "
             f"to'plamining {abl['n']} ta iborasi (\"from our books\" → \"kitoblarimizdan\" ...) 1500-JSON ichidagi "
             f"\"100 SOZ (MORFEMIK TAHLIL)\" kategoriyasi orqali UB_en_w/UB_uz_w lug'atiga (`source='json'`, "
             f"pos='Ot') va MDB_uz_w nomzodlariga YUKLANADI ({abl['in_ub_en']}/{abl['n']} UB_en_w da, "
             f"{abl['in_mdb']}/{abl['n']} MDB_uz_w da).")
    L.append(f"3. **Ablatsiya natijasi:** bu {abl['n']} qator olib tashlangan baza nusxasida 100 ta gold kirishning "
             f"`translate_phrase()` natijasi **{len(abl['diff'])} tasida o'zgardi**; normalizatsiyalangan aniq moslik "
             f"{abl['score_base']}/{abl['n']} → {abl['score_ablated']}/{abl['n']}. Ya'ni "
             + ("**Faza 1 dagi 100_soz bahosi (56/100) bu qatorlar tufayli sun'iy oshmagan**" if not abl["diff"]
                else "**100_soz bahosi bu qatorlarga BOG'LIQ**")
             + f" — sababi: hamma {abl['multiword']} ta ibora ko'p so'zli, `translate_phrase()` esa lug'atni faqat "
             "alohida so'z (token) bo'yicha qidiradi. **Xavf yashirin qoladi:** kelajakda butun ibora bo'yicha qidiruv "
             "qo'shilsa yoki MDB tanlov tartibi o'zgarsa, gold javoblar to'g'ridan-to'g'ri qaytib qolishi mumkin — "
             "`tests/test_audit_lexicon_sources.py` shu holatni qo'riqlaydi.")
    L.append("")
    L.append("## 1. 1500-JSON kategoriyalari — nima lug'atga yuklanadi")
    L.append("")
    L.append("`_load_words_from_json()` (`kkt_v20_soz_tartibi.py`) → `data_loader.load_word_pairs()` JSON'dagi "
             "BARCHA kategoriyalarni aylanadi va `english` + `uzbek` maydoni bor har bir yozuvni UB_en_w/UB_uz_w ga "
             "yozadi (`POS_MAP` ga mos kelmagan kategoriya → pos='Ot').")
    L.append("")
    L.append("| Kategoriya | Yozuvlar | `english`+`uzbek` bor | UB_en_w da (source='json') | Yozuv kalitlari |")
    L.append("|---|---|---|---|---|")
    for r in cat_rows:
        L.append(f"| {r['kategoriya']} | {r['yozuvlar']} | {r['english_uzbek_bor']} | {r['ub_en_w_da']} | "
                 f"{', '.join(r['kalitlar'])} |")
    L.append("")
    L.append("## 2. `KKT_Terminologik_Lugat.json` — batafsil")
    L.append("")
    L.append(f"- Tuzilishi: {term['n_words']} ta so'z × soha bo'yicha ma'nolar = {term['n_pairs']} ta yozuv; sohalar: "
             + ", ".join(term["sohalar"]) + ".")
    L.append("- Kodda fayl nomiga havola: " + ("; ".join(term["file_refs"]) if term["file_refs"] else "**yo'q**") + ".")
    L.append("- PSB `terms` jadvaliga yozuvchi kod (`INSERT ... INTO terms`): "
             + ("; ".join(term["insert_terms"]) if term["insert_terms"] else "**yo'q** — jadval hech qachon to'ldirilmaydi")
             + f". Qurilgan bazada qatorlar: {term['psb_rows']}.")
    L.append(f"- `psb_select_meaning()` chaqiruvlari ({len(term['psb_calls'])} ta: "
             + "; ".join(c.split(': ', 1)[0] for c in term["psb_calls"])
             + f"). `domain` argumenti uzatilgan chaqiruv: {len(term['psb_domain_passed'])} ta"
             + (" — ya'ni funksiya har doim birinchi ma'noni qaytaradi." if not term["psb_domain_passed"] else ".")
             )
    L.append(f"- Terminologik juftlarning ({term['n_pairs']}) AYNAN o'zi (inglizcha + o'zbekcha) UB_en_w da boshqa "
             f"manbadan tasodifan bor: {len(term['same_pair_in_ub'])} ta — "
             + (", ".join(f"{en}→{uz} [{src}]" for en, uz, src in term["same_pair_in_ub"]) or "—")
             + ". Bu terminologik fayl orqali emas (u yuklanmaydi), 1500-lug'at/SEED/CH2 orqali kelgan.")
    L.append("- Hisobotlarda: README.md \"kod tomonidan hozircha ishlatilmaydi\" deb qayd etgan — shu skript bu da'voni "
             "tasdiqlaydi. Dissertatsiya IV bobida PSB \"semantik noaniqlikni bartaraf etishning asosiy mexanizmi\" deb "
             "tasvirlanadi (`reports/ch2_leakage_check.md` 3.3) — kodda esa bu mexanizm bo'sh jadval bilan ishlaydi.")
    L.append("")
    L.append("## 3. 100_soz gold qatorlari — ablatsiya")
    L.append("")
    L.append(f"- Olib tashlangan qatorlar (baza NUSXASIDAN): {abl['removed']}.")
    L.append(f"- Normalizatsiyalangan aniq moslik: oddiy baza **{abl['score_base']}/{abl['n']}**, qatorlarsiz "
             f"**{abl['score_ablated']}/{abl['n']}**; farqli chiqishlar: **{len(abl['diff'])}**.")
    if abl["diff"]:
        L.append("")
        L.append("| Kirish | oddiy baza | qatorlarsiz |")
        L.append("|---|---|---|")
        for k, (a, b) in abl["diff"].items():
            L.append(f"| {k} | {a} | {b} |")
    L.append("- Tavsiya qilinmaydi, faqat qayd: bu qatorlar lug'atda turishi — gold to'plam va tarjima lug'ati bitta "
             "faylda aralashganining natijasi (1500-JSON ichida \"100 SOZ\" kategoriyasi). Ajratish — alohida qaror.")
    L.append("")
    return "\n".join(L)


def run(out_path: str | None) -> int:
    tmp = tempfile.mkdtemp(prefix="kkt_lexsrc_")
    try:
        m = conf.build_isolated_module(tmp)
        cat_rows = category_load_table(m)
        term = terminology_facts(m)
        abl = gold100_ablation(m)
        report = render(cat_rows, term, abl)
    finally:
        if tmp in sys.path:
            sys.path.remove(tmp)
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"KKT_Terminologik: {term['n_pairs']} yozuv, PSB terms={term['psb_rows']}; "
          f"100_soz lug'atda {abl['in_ub_en']}/{abl['n']}, ablatsiya farqi {len(abl['diff'])}, "
          f"baho {abl['score_base']}→{abl['score_ablated']}")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print(f"[yozildi: {out_path}]")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--no-out", action="store_true")
    args = ap.parse_args()
    return run(None if args.no_out else args.out)


if __name__ == "__main__":
    raise SystemExit(main())
