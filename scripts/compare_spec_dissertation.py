#!/usr/bin/env python3
"""
scripts/compare_spec_dissertation.py
=======================================
Rasmiy KKT spesifikatsiyasi (`data/kkt_spec.json` ← `kkt_qoidalari.docx`) va
dissertatsiya (`data/desertatsiya.docx`, II bob EVX/EVIX misollari) orasidagi
BARCHA nomuvofiqliklarni bitta hisobotga jamlaydi:
`reports/faza_2_spec_vs_dissertation.md`.

Uchta manba solishtiriladi:
  SPEC  — kkt_spec.json misollari (audit_kkt_spec_conformance.PROBES dagi
          kirish/kutilgan juftlar — docx katagidan, kuzatiluvchanlik testi bilan);
  DISS  — dissertatsiya II bobi, `check_ch2_leakage.extract_ch2_records()`
          orqali AVTOMATIK ajratilgan "Ingliz tilida EVX ... / Oʻzbek tilida
          EVIX ..." juftlari (xom matn va docx indeksi bilan);
  CH2   — `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` — dissertatsiyaning kodga
          qo'lda ko'chirilgan nusxasi (lug'atga `source='chapter2_evx'` bilan
          yoziladi).

Bu skript HECH QAYSI manbani "to'g'ri" deb e'lon qilmaydi — faqat farqni,
xom matnni va kodning joriy holatini ko'rsatadi (qaror — professor).

Solishtiruv: inglizcha kalit — normalize + defis=bo'shliq; o'zbekcha —
`audit_kkt_spec_conformance.compare()` (normalize, qavsli izohsiz). Bitta
inglizcha shaklga spec bir nechta o'zbekcha bersa (2.65 "sent"), ulardan
biriga mos kelishi yetarli.

`data/desertatsiya.docx` — shaxsiy fayl (.gitignore). Yo'q bo'lsa skript xato
bilan to'xtaydi (check_ch2_leakage.py kabi).

Ishlatish:
    python scripts/compare_spec_dissertation.py
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from _common import normalize  # noqa: E402
import audit_kkt_spec_conformance as conf  # noqa: E402
import check_ch2_leakage as ch2l  # noqa: E402

DEFAULT_DOCX = os.path.join(REPO_ROOT, "data", "desertatsiya.docx")
DEFAULT_OUT = os.path.join(REPO_ROOT, "reports", "faza_2_spec_vs_dissertation.md")


def en_key(s: str | None) -> str:
    return normalize((s or "").replace("-", " ")) or ""


def _mos(uz: str | None, exps: list[str], single: bool) -> bool:
    return bool(uz) and any(conf.compare(uz, e, single) for e in exps)


def build_rows(spec: dict, recs: list[dict], ch2: list[dict]) -> list[dict]:
    """Har bir (spec qoidasi, inglizcha shakl) uchun bitta qator."""
    diss_by = {}
    for r in recs:
        diss_by.setdefault(en_key(r["en_marker_word"]), []).append(r)
    ch2_by = {}
    for ex in ch2:
        ch2_by.setdefault(en_key(ex["en"]), []).append(ex)
    rule_by = {r["uid"]: r for r in spec["rules"]}

    rows = []
    for rule in spec["rules"]:
        groups: dict[str, list[str]] = {}
        for en, exp in conf.PROBES[rule["uid"]]["juftlar"]:
            groups.setdefault(en, []).append(exp)
        for en, exps in groups.items():
            single = " " not in en.strip()
            d = diss_by.get(en_key(en), [])
            c = ch2_by.get(en_key(en), [])
            d_uz = [r["uz_marker_word"] for r in d]
            c_uz = [x["uz"] for x in c]
            spec_diss = None if not d else ("mos" if any(_mos(u, exps, single) for u in d_uz) else "FARQ")
            ch2_spec = None if not c else ("mos" if any(_mos(u, exps, single) for u in c_uz) else "FARQ")
            ch2_diss = None if not (c and d) else (
                "mos" if any(_mos(cu, [du], single) for cu in c_uz for du in d_uz if du) else "FARQ")
            alt = conf._docx_components(rule_by[rule["uid"]]["uz_misol"])
            rows.append({"uid": rule["uid"], "pos": rule["pos"], "en": en, "spec": exps,
                         "spec_cell": rule["uz_misol"], "diss": d, "ch2": c,
                         "spec_diss": spec_diss, "ch2_spec": ch2_spec, "ch2_diss": ch2_diss,
                         "spec_ichki": alt if (alt and any(_mos(u, [alt], single) for u in d_uz)) else None})
    return rows


def cross_matches(recs: list[dict]) -> list[dict]:
    """DISS yozuvi darajasida: o'zbekchasi O'Z inglizcha shakli uchun spec
    kutganiga mos EMAS, lekin BOSHQA (inglizchasi farqli) spec misolining
    o'zbekchasiga aynan teng bo'lgan holatlar — masalan II bobdagi ikkinchi
    "gayer" → "eng sho'x" (spec 2.30 "gayest" ning o'zbekchasi)."""
    pairs = [(uid, en, exp) for uid, pr in conf.PROBES.items() for en, exp in pr["juftlar"]]
    out = []
    for r in recs:
        uz = r["uz_marker_word"]
        if not uz:
            continue
        k = en_key(r["en_marker_word"])
        single = " " not in (r["en_marker_word"] or "").strip()
        own = [(u, e, x) for u, e, x in pairs if en_key(e) == k]
        if own and any(conf.compare(uz, x, single) for _, _, x in own):
            continue
        other = [(u, e, x) for u, e, x in pairs if en_key(e) != k and conf.compare(uz, x, True)]
        if other:
            out.append({"rec": r, "own": own, "other": other})
    return out


def ch2_label(row: dict) -> str:
    if not row["ch2"]:
        return "CH2 da yo'q"
    vals = ", ".join(f"«{x['uz']}»" for x in row["ch2"])
    if row["ch2_diss"] == "mos" and row["ch2_spec"] != "mos":
        return f"{vals} — dissertatsiya bilan bir xil"
    if row["ch2_spec"] == "mos" and row["ch2_diss"] != "mos":
        return f"{vals} — spec bilan bir xil"
    if row["ch2_spec"] == "mos" and row["ch2_diss"] == "mos":
        return f"{vals} — ikkalasi bilan"
    return f"{vals} — ikkalasidan ham farq"


def conformance_status(spec: dict):
    """(uid → holat, izolyatsiyalangan modul) — holat conformance hisoboti bilan bir xil mantiqda."""
    tmp = tempfile.mkdtemp(prefix="kkt_specdiss_")
    try:
        m = conf.build_isolated_module(tmp)
        return {e["uid"]: e["holat"] for e in conf.evaluate_all(m, spec)}, m
    finally:
        if tmp in sys.path:
            sys.path.remove(tmp)
        shutil.rmtree(tmp, ignore_errors=True)


def render(spec, rows, recs, ch2, holat, er_theory, er_spec, docx_path) -> str:
    diff = [r for r in rows if r["spec_diss"] == "FARQ"]
    same = [r for r in rows if r["spec_diss"] == "mos"]
    notfound = [r for r in rows if r["spec_diss"] is None]
    used = {en_key(r["en"]) for r in rows}
    diss_only = [r for r in recs if en_key(r["en_marker_word"]) not in used]
    diss_keys = {en_key(r["en_marker_word"]) for r in recs}
    ch2_orphan = [ex for ex in ch2 if en_key(ex["en"]) not in diss_keys]

    L = ["# Spesifikatsiya ↔ dissertatsiya: barcha nomuvofiqliklar", ""]
    L.append(f"**Generatsiya vaqti:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    L.append("**Buyruq:** `python scripts/compare_spec_dissertation.py` (`make specdiss`)")
    L.append(f"**Manbalar:** SPEC = `data/kkt_spec.json` (sha256 `{spec['manba']['sha256'][:16]}…`); "
             f"DISS = `{os.path.relpath(docx_path, REPO_ROOT)}` II bobi ({len(recs)} ta avtomatik ajratilgan "
             f"EVX/EVIX juftligi); CH2 = `CH2_EVX_EXAMPLES` ({len(ch2)} ta, dissertatsiyaning kodga qo'lda "
             "ko'chirilgan nusxasi).")
    L.append("")
    L.append("**Bu hisobot hech qaysi manbani \"to'g'ri\" deb e'lon qilmaydi** — farqni, xom matnni va kodning "
             "joriy holatini ko'rsatadi. Qaror — professor. Kod hozir SPEC ga moslashtirilmoqda (kanonik manba).")
    L.append("")

    L.append("## 0. Qisqa xulosa")
    L.append("")
    L.append(f"- Spec misollari (qoida × inglizcha shakl): **{len(rows)}**. Dissertatsiya II bobida avtomatik "
             f"topilgani: **{len(same) + len(diff)}** — shundan o'zbekchasi **mos: {len(same)}**, "
             f"**FARQ: {len(diff)}**. Topilmagani: {len(notfound)} (5-bo'lim).")
    L.append(f"- Yozuv darajasida: {len(cross_matches(recs))} ta II bob yozuvining o'zbekchasi BOSHQA spec misolinikiga "
             "aynan teng (1.1-bo'lim).")
    L.append(f"- Dissertatsiya II bobida bor, spec'da yo'q misollar: {len(diss_only)} (4-bo'lim).")
    L.append(f"- FARQ qatorlarida CH2 (kod nusxasi) qaysi manbaga ergashadi: "
             f"dissertatsiyaga — {sum(1 for r in diff if r['ch2_diss'] == 'mos' and r['ch2_spec'] != 'mos')}, "
             f"spec'ga — {sum(1 for r in diff if r['ch2_spec'] == 'mos' and r['ch2_diss'] != 'mos')}, "
             f"CH2 da yo'q — {sum(1 for r in diff if not r['ch2'])}, ikkalasidan farq — "
             f"{sum(1 for r in diff if r['ch2'] and r['ch2_spec'] != 'mos' and r['ch2_diss'] != 'mos')}.")
    L.append(f"- Spec'ning o'z katagidagi nomuvofiqliklar: {sum(1 for r in spec['rules'] if r.get('izoh'))} ta "
             "qoidada (3-bo'lim). Nazariy daraja: agentiv \"-er\" (6-bo'lim).")
    L.append("")

    L.append(f"## 1. Spec ≠ dissertatsiya ({len(diff)} ta)")
    L.append("")
    L.append("| qoida | EN | SPEC (docx katagi) | DISS II bob (xom matn, docx idx) | CH2_EVX_EXAMPLES | kodning joriy holati |")
    L.append("|---|---|---|---|---|---|")
    for r in diff:
        diss = "; ".join(f"«{d['uz_marker_word']}» (\"{(d['uz_marker_raw'] or '').strip()[:50]}\", #{d['uz_idx']})"
                         for d in r["diss"])
        note = (f" ⚠ spec katagining \"+\" qismlari («{r['spec_ichki']}») DISS bilan bir xil — spec katagi ichki "
                "nomuvofiq" if r["spec_ichki"] else "")
        L.append(f"| {r['uid']} | {r['en']} | `{r['spec_cell']}`{note} | {diss} | {ch2_label(r)} | {holat[r['uid']]} |")
    L.append("")
    xm = cross_matches(recs)
    L.append(f"### 1.1 Yozuv darajasida: dissertatsiya o'zbekchasi BOSHQA spec misolinikiga aynan teng ({len(xm)} ta)")
    L.append("")
    L.append("Inglizcha kalit bo'yicha solishtiruv buni ko'rmaydi (masalan bir inglizcha shakl ikki marta uchrasa). "
             "Har bir II bob yozuvi alohida: o'z inglizcha shakli uchun spec kutgan o'zbekchaga mos emas, lekin "
             "boshqa (inglizchasi farqli) spec misolining o'zbekchasi bilan bir xil.")
    L.append("")
    L.append("| DISS (idx) | DISS EN → UZ | o'z spec misoli | xuddi shu o'zbekcha — boshqa spec misoli |")
    L.append("|---|---|---|---|")
    for x in xm:
        r = x["rec"]
        own = "; ".join(f"{u} `{e}` → {v}" for u, e, v in x["own"]) or "spec'da yo'q"
        other = "; ".join(f"{u} `{e}` → {v}" for u, e, v in x["other"])
        L.append(f"| #{r['en_idx']} | `{r['en_marker_word']}` → «{r['uz_marker_word']}» | {own} | {other} |")
    L.append("")
    L.append("\"kodning joriy holati\" — `reports/faza_2_kkt_spec_conformance.md` dagi holat (SPEC ga nisbatan). "
             "Masalan QISMAN + \"CH2 dissertatsiya bilan bir xil\" — lug'at dissertatsiya qiymatini beradi, spec esa "
             "boshqasini talab qiladi; TO'LIQ — kod spec'ga moslashtirilgan (dissertatsiyadan farqli).")
    L.append("")

    L.append(f"## 2. Spec = dissertatsiya, lekin CH2 (kod nusxasi) farq qiladi ({len([r for r in same if r['ch2_diss'] == 'FARQ'])} ta) va CH2 transkripsiya xatolari")
    L.append("")
    L.append("| qoida | EN | SPEC = DISS | CH2 |")
    L.append("|---|---|---|---|")
    for r in same:
        if r["ch2_diss"] == "FARQ":
            L.append(f"| {r['uid']} | {r['en']} | {', '.join(r['spec'])} | {', '.join(x['uz'] for x in r['ch2'])} |")
    L.append("")
    L.append(f"Inglizcha kaliti dissertatsiya II bobidagi birorta misolga to'g'ri kelmagan CH2 yozuvlari "
             f"({len(ch2_orphan)} ta — asosan transkripsiya xatosi, `reports/ch2_leakage_check.md`): "
             + ", ".join(f"`{ex['en']}` → «{ex['uz']}»" for ex in ch2_orphan) + ".")
    L.append("")

    L.append("## 3. Spec'ning o'zidagi nomuvofiqliklar (`data/kkt_spec.json` → `izoh`)")
    L.append("")
    for r in spec["rules"]:
        if r.get("izoh"):
            L.append(f"- **{r['uid']}** ({r['pos']}): {r['izoh']}")
    L.append("")
    for h in spec["hujjat_izohlari"]:
        L.append(f"- Hujjat darajasida: {h}")
    L.append("")

    L.append(f"## 4. Dissertatsiya II bobida bor, spec'da yo'q ({len(diss_only)} ta)")
    L.append("")
    for d in diss_only:
        L.append(f"- `{d['en_marker_word']}` → «{d['uz_marker_word']}» (#{d['en_idx']}, POS {d['inferred_pos'] or '—'})")
    L.append("")

    L.append(f"## 5. Spec misollari — dissertatsiya II bobida avtomatik topilmagan ({len(notfound)} ta)")
    L.append("")
    L.append("Avtomatik ajratish faqat \"Ingliz tilida EVX ... / Oʻzbek tilida EVIX ...\" paragraf naqshini "
             "taniydi — **topilmadi ≠ dissertatsiyada yo'q** (masalan olmosh ro'yxatlari jadval ichida bo'lishi mumkin).")
    L.append("")
    by_uid: dict[str, list[str]] = {}
    for r in notfound:
        by_uid.setdefault(r["uid"], []).append(r["en"])
    L.append("; ".join(f"{u}: {', '.join(ens)}" for u, ens in by_uid.items()) + ".")
    L.append("")

    L.append("## 6. Nazariy daraja — agentiv \"-er\"")
    L.append("")
    if er_theory and er_spec:
        L.append(f"- DISS I bob 1.3-jadval (\"Yangi ot yasovchi suffikslar\", {len(er_theory['noun_suffix_table'] or [])} ta): "
                 f"\"-er\" {'BOR' if er_theory['noun_suffix_table_has_er'] else 'yoq'}.")
        L.append(f"- SPEC: \"-er\" faqat {len(er_spec['er_rules'])} ta qiyosiy daraja qoidasida ("
                 + ", ".join(r["uid"] for r in er_spec["er_rules"]) + f"); agentiv kalit so'zlar: "
                 f"{len(er_spec['agentive_hits'])} ta.")
        L.append("- Kod: agentiv qoida bor (`MORPH_RULES`), spec'da asosi yo'q — professor qarorini kutmoqda "
                 "(`reports/faza_2_er_gap.md` 6-bo'lim).")
    L.append("")
    return "\n".join(L)


def run(docx_path: str, out_path: str | None) -> int:
    if not os.path.exists(docx_path):
        print(f"XATO: {docx_path} topilmadi (shaxsiy fayl, .gitignore'da).", file=sys.stderr)
        return 1
    import audit_er_gap

    spec = conf.load_spec()
    items = ch2l.load_docx(docx_path)
    recs = ch2l.extract_ch2_records(items, ch2l.find_chapter_bounds(items)["II"])
    holat, m = conformance_status(spec)
    rows = build_rows(spec, recs, m.CH2_EVX_EXAMPLES)
    report = render(spec, rows, recs, m.CH2_EVX_EXAMPLES, holat,
                    audit_er_gap.check_dissertation_theory(docx_path), audit_er_gap.check_kkt_spec(), docx_path)
    diff = sum(1 for r in rows if r["spec_diss"] == "FARQ")
    print(f"{len(rows)} spec misoli: DISS bilan mos {sum(1 for r in rows if r['spec_diss'] == 'mos')}, "
          f"FARQ {diff}, topilmadi {sum(1 for r in rows if r['spec_diss'] is None)}")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print(f"[yozildi: {out_path}]")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docx", default=DEFAULT_DOCX)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--no-out", action="store_true")
    args = ap.parse_args()
    return run(args.docx, None if args.no_out else args.out)


if __name__ == "__main__":
    raise SystemExit(main())
