#!/usr/bin/env python3
"""
scripts/check_100_soz.py
==========================
`data/100_soz.docx` — INSON tomonidan tayyorlangan 100 ta EN->UZ etalon
juftlik (dissertatsiya "100 ta etalon" to'plami) — ni to'g'ridan-to'g'ri
docx'dan yuklab, har birini `translate_phrase(..., allow_write=False)`
orqali (READ-ONLY rejimda — .db fayllarga yozmaydi) o'tkazadi va natijani
etalon bilan (apostrof + bosh harf normalizatsiyasi bilan) solishtiradi.

MUHIM (Qoida 1, 3, 5):
  - Etalon (`reference_uz`) qiymatlari BU SKRIPT TOMONIDAN TO'QILMAGAN —
    ular allaqachon `data/100_soz.docx` da mavjud, inson tayyorlagan
    ma'lumot. Skript faqat O'QIYDI va SOLISHTIRADI.
  - Natija — qanday chiqsa, SHUNDAY YOZILADI. Xato ko'p chiqsa ham
    `try/except: pass` bilan ko'milmaydi, kod bu natijani yaxshilash uchun
    o'zgartirilmaydi (bu skriptning ishi emas).
  - Chiqish soni HAR DOIM shu buyruq bilan qayta hisoblanadi — qo'lda
    kiritilgan raqam yo'q.

Ishlatish:
    python scripts/check_100_soz.py
    python scripts/check_100_soz.py --docx data/100_soz.docx --out reports/faza_1_100soz_baseline.md
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, SCRIPT_DIR)

try:
    from docx import Document
except ImportError:
    print("XATOLIK: python-docx o'rnatilmagan (pip install -r requirements.txt).", file=sys.stderr)
    raise SystemExit(1)

from _common import normalize  # scripts/_common.py — check_100_soz.py va audit_examples.py umumiy


def load_gold_set(docx_path: str) -> list[dict]:
    """data/100_soz.docx dagi 1-jadval qatorlarini (sarlavha jadvali +
    100 ta 4-ustunli ma'lumot jadvali) o'qiydi. Ustunlar: №, O'zbekcha so'z,
    Morfemalarga ajratilishi, Etalon inglizcha tarjima.

    DIQQAT: docx faylda 101-200-jadvallar HAM bor — bular alohida
    (2-ustunli, faqat inglizcha ibora) ilova ro'yxati, bu yerda E'TIBORGA
    OLINMAYDI (asosiy 4-ustunli etalon jadvali bilan takrorlanadi, qo'shimcha
    ma'lumot bermaydi)."""
    doc = Document(docx_path)
    rows = []
    for table in doc.tables:
        if len(table.columns) != 4:
            continue
        cells = [c.text.strip() for c in table.rows[0].cells]
        no_text = cells[0]
        if not no_text.isdigit():
            continue  # sarlavha jadvali ("№", ...) — o'tkazib yuboriladi
        rows.append({
            "no": int(no_text),
            "reference_uz": cells[1],
            "morphemes": cells[2],
            "source_en": cells[3],
        })
    rows.sort(key=lambda r: r["no"])
    return rows


def run(docx_path: str, out_path: str | None) -> int:
    import kkt_v20_soz_tartibi as m

    gold = load_gold_set(docx_path)
    if not gold:
        print(f"XATOLIK: {docx_path} dan birorta ham etalon qator o'qilmadi.", file=sys.stderr)
        return 1

    results = []
    for item in gold:
        en = item["source_en"]
        with m.readonly_mode():
            r = m.translate_phrase(en, allow_write=False)
        hyp_raw = r["natija"] if r else None
        ref_norm = normalize(item["reference_uz"])
        hyp_norm = normalize(hyp_raw)
        exact_match_raw = (hyp_raw == item["reference_uz"])
        exact_match_norm = (hyp_norm == ref_norm) and hyp_norm is not None
        results.append({
            **item,
            "hypothesis_raw": hyp_raw,
            "exact_match_raw": exact_match_raw,
            "exact_match_normalized": exact_match_norm,
        })

    total = len(results)
    n_exact_raw = sum(1 for r in results if r["exact_match_raw"])
    n_exact_norm = sum(1 for r in results if r["exact_match_normalized"])
    n_none = sum(1 for r in results if r["hypothesis_raw"] is None)
    n_wrong_text = total - n_exact_norm - n_none

    lines = []
    lines.append("# 100_soz.docx gold-set natijasi (avtomatik qayta hisoblangan)")
    lines.append("")
    lines.append(f"**Generatsiya vaqti:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}Z")
    lines.append(f"**Manba:** `{os.path.relpath(docx_path, REPO_ROOT)}` ({total} ta etalon juftlik)")
    lines.append(f"**Buyruq:** `python scripts/check_100_soz.py`")
    lines.append("**Rejim:** `translate_phrase(text, allow_write=False)` — bazaga yozilmagan.")
    lines.append("")
    lines.append("## Umumiy natija")
    lines.append("")
    lines.append(f"- Jami: **{total}**")
    lines.append(f"- Aniq mos (normalizatsiyasiz, xom matn): **{n_exact_raw}/{total}**")
    lines.append(f"- Aniq mos (apostrof+bosh harf normalizatsiyasi bilan): **{n_exact_norm}/{total}**")
    lines.append(f"- `None` qaytardi (tarjima topilmadi): **{n_none}/{total}**")
    lines.append(f"- Natija qaytardi, lekin matn mos emas: **{n_wrong_text}/{total}**")
    lines.append("")
    lines.append(
        "Bu son — Faza 0'dagi tasdiqlanmagan 56/100 va 80/100 o'rniga birinchi "
        "RASMAN, shu skript bilan qayta ishlab chiqariladigan natija "
        "(reports/faza_0.md, \"Tasdiqlanmagan (eski) natijalar\" bo'limiga qarang)."
    )
    lines.append("")
    lines.append("## Mos kelmagan qatorlar")
    lines.append("")
    lines.append("| № | Ingliz (kirish) | Etalon | Chiqish | Sabab |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        if r["exact_match_normalized"]:
            continue
        if r["hypothesis_raw"] is None:
            sabab = "None (tarjima topilmadi)"
        elif r["exact_match_raw"]:
            sabab = "mos (normalizatsiyasiz allaqachon aniq)"
        else:
            sabab = "matn farq qiladi"
        lines.append(f"| {r['no']} | {r['source_en']} | {r['reference_uz']} | "
                      f"{r['hypothesis_raw']!r} | {sabab} |")
    lines.append("")

    report = "\n".join(lines)
    print(report)

    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print(f"\n[yozildi: {out_path}]", file=sys.stderr)

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--docx", default=os.path.join(REPO_ROOT, "data", "100_soz.docx"))
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "reports", "faza_1_100soz_baseline.md"))
    ap.add_argument("--no-out", action="store_true", help="faylga yozmaslik, faqat konsolga chiqarish")
    args = ap.parse_args()
    return run(args.docx, None if args.no_out else args.out)


if __name__ == "__main__":
    raise SystemExit(main())
