#!/usr/bin/env python3
"""
scripts/check_leakage.py
===========================
Rasmiy spesifikatsiya misollari (`data/kkt_spec.json`) bilan boshqa baholash
to'plamlari orasidagi SO'Z KESISHMALARINI ro'yxatlaydi.

Nega kerak: `kkt_spec.json` dagi 87 qoida misoli — formal qoida to'g'ri
implement qilinganini tekshirish uchun (`tests/test_kkt_spec_conformance.py`).
Gold to'plamlar esa — end-to-end tarjima sifati uchun. Ular ARALASHTIRILMAYDI.
Lekin bir xil so'z (masalan "capabilities") ikkala joyda ham uchrasa, buni
bilib turish kerak: masalan qoidani "tuzatish" o'sha gold natijani ham
o'zgartiradi. **Bu leakage EMAS — faqat ogohlantirish.** Skript hech qachon
xato kodi bilan tugamaydi.

Solishtiriladigan manbalar:
  - `data/1500_EN_UZ_6_POS_sorted.20.json` — 6 asosiy kategoriya (1500-so'zlik lug'at)
  - `data/100_soz.json` — 100 so'zlik gold (inglizcha iboralar)
  - `data/KKT_Terminologik_Lugat.json` — ko'p ma'noli terminlar
  - `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` — II bob misollari (audit to'plami)

Ikki daraja:
  1. **Shakl** — spec misolidagi to'liq shakl (masalan "capabilities",
     "a network") yoki "+" dan oldingi asos ("capability") manbadagi
     yozuv bilan (normallashtirilgandan keyin) AYNAN teng.
  2. **Token** — ko'p so'zli spec shaklidagi mazmunli so'z (artikl/"to"/
     "and"/"of" dan tashqari) manbadagi biror yozuvning tokeni bilan teng.

Ishlatish:
    python scripts/check_leakage.py
    python scripts/check_leakage.py --no-out
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, SCRIPT_DIR)

from _common import normalize  # noqa: E402

SPEC_PATH = os.path.join(REPO_ROOT, "data", "kkt_spec.json")
DEFAULT_OUT = os.path.join(REPO_ROOT, "reports", "faza_2_kkt_spec_leakage.md")

_MAIN_1500 = ("NOUNS (OTLAR)", "VERBS (FE'LLAR)", "ADJECTIVES (SIFATLAR)", "ADVERBS (RAVISHLAR)",
              "PRONOUNS (OLMOSHLAR)", "CONJUNCTIONS & PREPOSITIONS (BOG'LOVCHI / KO'MAKCHI)")
# Token darajasida e'tiborsiz qoldiriladigan funksional so'zlar (juda ko'p
# iborada tabiiy ravishda uchraydi — ogohlantirish shovqini bo'lardi).
STOPWORDS = {"a", "an", "the", "to", "and", "of"}
_TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?")


def _norm(s: str) -> str:
    return normalize(s.replace("(", "").replace(")", "").replace("…", "")) or ""


def spec_forms(rule: dict) -> list[tuple[str, str]]:
    """Spec qoidasining inglizcha misol katagidan (tur, shakl) juftlari:
    "misol" — "+" siz to'liq shakl, "asos" — "+" li bo'lakdagi birinchi qism.
    Masalan "capability + ies = capabilities" -> [("asos","capability"),
    ("misol","capabilities")]; "I / he / we – me / him / us" -> 6 ta misol."""
    out = []
    for item in re.split(r"=|→|,|/|–", rule["en_misol"]):
        item = item.strip()
        if not item:
            continue
        kind, form = ("asos", item.split("+")[0]) if "+" in item else ("misol", item)
        form = _norm(form)
        if form and (kind, form) not in out:
            out.append((kind, form))
    return out


def load_sources() -> dict[str, list[str]]:
    """Har bir manba -> normallashtirilgan inglizcha yozuvlar ro'yxati."""
    src: dict[str, list[str]] = {}
    with open(os.path.join(REPO_ROOT, "data", "1500_EN_UZ_6_POS_sorted.20.json"), encoding="utf-8") as f:
        cats = json.load(f)["categories"]
    src["1500-lug'at"] = [_norm(e["english"]) for k in _MAIN_1500 for e in cats[k]]
    with open(os.path.join(REPO_ROOT, "data", "100_soz.json"), encoding="utf-8") as f:
        src["100_soz"] = [_norm(e["english"]) for e in json.load(f)]
    with open(os.path.join(REPO_ROOT, "data", "KKT_Terminologik_Lugat.json"), encoding="utf-8") as f:
        src["KKT_Terminologik"] = [_norm(e["english"]) for w in json.load(f) for e in w["entries"]]
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        import kkt_v20_soz_tartibi as m
    src["CH2_EVX_EXAMPLES"] = [_norm(ex["en"]) for ex in m.CH2_EVX_EXAMPLES]
    return src


def find_overlaps(spec: dict, sources: dict[str, list[str]]) -> list[dict]:
    """Har bir spec shakli uchun: qaysi manbada SHAKL darajasida, qaysida
    TOKEN darajasida uchraydi (faqat kamida bittasi bo'lsa qaytariladi)."""
    form_sets = {name: set(entries) for name, entries in sources.items()}
    token_sets = {name: {t for e in entries for t in _TOKEN_RE.findall(e)} for name, entries in sources.items()}
    rows = []
    for rule in spec["rules"]:
        for kind, form in spec_forms(rule):
            shakl = sorted(n for n, s in form_sets.items() if form in s)
            tokens = [t for t in _TOKEN_RE.findall(form) if t not in STOPWORDS] if " " in form else []
            token_hits = {t: sorted(n for n, s in token_sets.items() if t in s) for t in tokens}
            token_hits = {t: ns for t, ns in token_hits.items() if ns}
            if shakl or token_hits:
                rows.append({"uid": rule["uid"], "pos": rule["pos"], "tur": kind, "shakl": form,
                             "shakl_manbalar": shakl, "token_manbalar": token_hits})
    return rows


def render(spec: dict, sources: dict[str, list[str]], rows: list[dict]) -> str:
    names = list(sources)
    L = ["# Faza 2 — `kkt_spec.json` misollari va boshqa to'plamlar kesishmasi (ogohlantirish)", ""]
    L.append(f"**Generatsiya vaqti:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    L.append("**Buyruq:** `python scripts/check_leakage.py`")
    L.append("")
    L.append("**Bu leakage EMAS.** `kkt_spec.json` misollari faqat formal qoidani tekshiradi "
             "(`tests/test_kkt_spec_conformance.py`) va gold to'plamlarga QO'SHILMAGAN. Bu ro'yxat — bir xil so'z "
             "ikkala joyda uchrasa, bilib turish uchun: masalan shu qoida o'zgartirilsa, quyidagi to'plamlardagi "
             "natija ham o'zgarishi mumkin.")
    L.append("")
    L.append("Manbalar (normallashtirilgan yozuvlar soni): "
             + ", ".join(f"`{n}` ({len(v)})" for n, v in sources.items()) + ".")
    L.append("")
    L.append("- `1500-lug'at` — 1500-JSON ning 6 asosiy kategoriyasi; `100_soz` — gold iboralar; `CH2_EVX_EXAMPLES` — "
             "kod ichidagi II bob misollari (lug'atga `source='chapter2_evx'` bilan yoziladi).")
    L.append("- `KKT_Terminologik` — `data/KKT_Terminologik_Lugat.json`: 20 ta ko'p ma'noli so'z × soha bo'yicha "
             "ma'nolar (soni — (inglizcha, o'zbekcha, soha) yozuvlar). **Kod bu faylni ishlatmaydi** (yuklanmaydi, PSB "
             "bo'sh). 100_soz gold iboralari esa lug'atga YUKLANADI, lekin natijaga ta'sir qilmaydi — ikkalasi ham "
             "o'lchangan: `reports/faza_2_lexicon_sources.md`.")
    L.append("")
    shakl_rows = [r for r in rows if r["shakl_manbalar"]]
    L.append("## 1. Shakl darajasida (to'liq shakl yoki asos aynan teng)")
    L.append("")
    per_src = {n: sum(1 for r in shakl_rows if n in r["shakl_manbalar"]) for n in names}
    L.append("Manba bo'yicha: " + ", ".join(f"`{n}`: **{c}**" for n, c in per_src.items()) + ".")
    L.append("")
    L.append("| spec qoidasi | POS | tur | shakl | " + " | ".join(names) + " |")
    L.append("|---|---|---|---|" + "---|" * len(names))
    for r in shakl_rows:
        L.append(f"| {r['uid']} | {r['pos']} | {r['tur']} | {r['shakl']} | "
                 + " | ".join("⚠" if n in r["shakl_manbalar"] else "" for n in names) + " |")
    L.append("")
    tok_rows = [r for r in rows if r["token_manbalar"]]
    L.append("## 2. Token darajasida (ko'p so'zli spec shaklidagi mazmunli so'z)")
    L.append("")
    L.append(f"E'tiborsiz qoldirilgan funksional so'zlar: {', '.join(sorted(STOPWORDS))}.")
    L.append("")
    L.append("| spec qoidasi | shakl | token → manbalar |")
    L.append("|---|---|---|")
    for r in tok_rows:
        L.append(f"| {r['uid']} | {r['shakl']} | "
                 + "; ".join(f"{t} → {', '.join(ns)}" for t, ns in r["token_manbalar"].items()) + " |")
    L.append("")
    return "\n".join(L)


def run(out_path: str | None) -> int:
    with open(SPEC_PATH, encoding="utf-8") as f:
        spec = json.load(f)
    sources = load_sources()
    rows = find_overlaps(spec, sources)
    for r in rows:
        if r["shakl_manbalar"]:
            print(f"OGOHLANTIRISH: spec {r['uid']} \"{r['shakl']}\" ({r['tur']}) — "
                  f"{', '.join(r['shakl_manbalar'])} da ham bor")
    print(f"Jami: shakl darajasida {sum(1 for r in rows if r['shakl_manbalar'])}, "
          f"token darajasida {sum(1 for r in rows if r['token_manbalar'])} ta kesishma (leakage emas).")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(render(spec, sources, rows) + "\n")
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
