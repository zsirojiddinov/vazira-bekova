#!/usr/bin/env python3
"""
scripts/build_master_decisions.py
====================================
Himoyaga tayyorgarlik uchun YAGONA ko'rish nuqtasi:
`reports/master_qarorlar_royxati.md` (+ ixtiyoriy HTML sahifa, `--html`).

Uchta Faza 2 hisobotini bitta ro'yxatga jamlaydi — har bir band uchun: qoida/misol
raqami, spec nima deydi, dissertatsiya nima deydi, CH2/kod nima qiladi, kim hal
qilishi kerak:
  - reports/faza_2_spec_vs_dissertation.md — compare_spec_dissertation.py;
  - reports/faza_2_kkt_spec_conformance.md — audit_kkt_spec_conformance.py
    (har bir qoidaning holati, stub va HAQIQIY lug'at bilan tizim chiqishi);
  - reports/faza_2.md — qaror kutilayotgan va past ustuvorlikdagi bandlar
    (+ ular tayanadigan faza_2_er_gap.md, faza_7_backlog.md, faza_2_lexicon_sources.md).
Hisoblanadigan bandlar shu skriptlarning funksiyalarini chaqirib QAYTA HISOBLANADI
(qo'lda ko'chirilmaydi). Kod bilan qayta hisoblab bo'lmaydigan bandlar (97,7%,
280 so'z, ...) — STATIC_ITEMS / PENDING_ITEMS / TECH_ITEMS da, har biri manba
hisobot va bo'limga havola bilan (mazmuni o'sha hisobotdan, yangi da'vo yo'q).

"Kim hal qiladi" — TAKLIF (himoyadan oldin kelishilsin):
  Professor — ilmiy/lingvistik tamoyil: ikki manba ikki xil tarjima/talqin
              bergan joy, kategoriya va formal model doirasi, metrika validligi;
  Vazira    — o'z matni/ma'lumotidagi masala: dissertatsiya o'zbekchasi boshqa
              misolnikiga aynan teng, spec katagi ichki nomuvofiq yoki mezonsiz,
              1 harflik imlo farqi, lug'at yozuvi spec'dan farqli yoki yo'q,
              yo'qolgan ma'lumotni tiklash;
  Dasturchi — qaror SHART EMAS: spec kanonik manba, kodni unga moslash texnik
              ish (alohida "texnik navbat" bo'limida, to'liqlik uchun).
Spec ≠ dissertatsiya qatorlari — `owner_for_diff()`, kod ≠ spec qatorlari —
`owner_for_code_gap()`. "jiddiy" bandlar (dissertatsiya da'vosi kodda
qo'llab-quvvatlanmaydi) hisobot boshida alohida ko'rsatiladi; "hal" bandlar —
qarori qabul qilingan, alohida bo'limda (sana va manba bilan).

`data/desertatsiya.docx` (shaxsiy fayl) talab qilinadi.

Ishlatish:
    python scripts/build_master_decisions.py [--html YO'L]
"""
from __future__ import annotations

import argparse
import html
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
import check_ch2_leakage as ch2l  # noqa: E402
import compare_spec_dissertation as csd  # noqa: E402

DEFAULT_OUT = os.path.join(REPO_ROOT, "reports", "master_qarorlar_royxati.md")
PROF, VAZ, DEV = "Professor", "Vazira", "Dasturchi"
PROF_VAZ = f"{PROF} + {VAZ}"

# Oldingi hisobotlarda OCHIQ deb qayd etilgan, kod bilan qayta hisoblab
# bo'lmaydigan bandlar. Har birining mazmuni `manba` dagi hisobotdan olingan.
STATIC_ITEMS = [
    {"id": "G1", "band": "Dissertatsiya 4.3-jadval — \"97,7%\"", "jiddiy": True,
     "spec": "—",
     "diss": "4.3-jadval («Tarjima foizi», 280 ta so'z): Google 46% / DeepL 72% / Yandex 80% / KKT moduli 97,7%.",
     "kod": "ILOVA skrinshotidagi (image67.png) GUI kartochkasi «So'zlar soni: 280 · O'rtacha aniqlik: 97.7%» bilan "
            "bit-aniq mos. Bu `avg_c` — qattiq kodlangan `conf` konstantalari (0.999/0.970/0.93/0.895/0.0) "
            "o'rtachasi: so'z qaysi kod yo'lidan o'tganini bildiradi, tarjima to'g'riligini o'lchamaydi. Qolgan uch "
            "ustunning hisoblash mezoni docx'da yo'q — to'rt ustunning o'lchov birligi bir xil emas.",
     "kim": f"{PROF_VAZ} — manba hisobot \"shoshilinch muhokama\" ni tavsiya qiladi",
     "manba": "faza_2_confidence_audit.md 0.1, 0.1-qo'shimcha; ch2_leakage_check.md 3.3"},
    {"id": "G2", "band": "4.3-jadvaldagi \"280 ta so'z\" ro'yxati",
     "spec": "—",
     "diss": "Ro'yxatning o'zi docx matnida yo'q; ILOVA rasmlarida faqat qismlar ko'rinadi (1–14, 61–68, 76–100, 93–100).",
     "kod": "Tiklanmagan — shu sabab CH2/1500-lug'at bilan so'z darajasidagi aylanma (leakage) tekshiruvi OCHIQ.",
     "kim": f"{VAZ} — ro'yxatni original tajriba ma'lumotidan tiklash",
     "manba": "faza_2_confidence_audit.md 0.1-qo'shimcha; ch2_leakage_check.md 3.3"},
    {"id": "G4", "band": "SSM metrikasining validligi (taqriz 35–41-bandlar)",
     "spec": "—",
     "diss": "SSM formulasi (M. Xakimov, IJIRSS 8(6) 2025); III bob 3.6–3.8-jadvallar natijalari shu metrika bilan "
             "hisoblangan.",
     "kod": "Formula maqola jadvaliga mos implement qilingan, lekin yuqori SSM = to'g'ri tarjima ekani inson "
            "bahosi/gold bilan HECH QACHON tekshirilmagan. SSM < 0.80 da MDB almashtirishi to'g'ri tarjimani buzgan: "
            "may/might «mumkin» → «Ajratib ko'rsatmoq» (bd79825 da tuzatildi); hozir ham `to ask` → «Ajratib "
            "ko'rsatmoq» (8-bo'lim H2).",
     "kim": PROF,
     "manba": "faza_2_confidence_audit.md 0.1 (#8–9); ch2_leakage_check.md 3.3; bd79825; faza_2.md 4B"},
    {"id": "G6", "band": "Gold to'plam (100_soz) tarjima lug'ati ichida",
     "spec": "—", "diss": "—",
     "kod": "100 ta gold juft 1500-JSON «100 SOZ (MORFEMIK TAHLIL)» kategoriyasi orqali lug'atga yuklanadi (100/100). "
            "Ablatsiya: ta'siri hozircha 0 (56/100 → 56/100), sababi — iboralar ko'p so'zli, qidiruv token bo'yicha. "
            "Yangi gold to'plamlar uchun qoida va CI qo'riqchilari bor.",
     "kim": f"{VAZ} — kategoriyani 1500-JSON dan ajratish (alohida qaror); ungacha 56/100 aylanmadan xoli deb "
            "taqdim etilmaydi (CLAUDE.md)",
     "manba": "faza_2_lexicon_sources.md; CLAUDE.md; faza_3_plan.md"},
    {"id": "G7", "band": "CLLT / LRE / CyS maqolalari bilan bu repodagi tizim aloqasi",
     "spec": "—", "diss": "—",
     "kod": "Maqolalardagi tizim O'zbek→Ingliz, ~27 000 yozuvli lug'at; bu repo — Ingliz→O'zbek, ~1500 so'z.",
     "kim": "Ziyoviddin (professor/Vazira bilan)",
     "hal": "ikkita mustaqil loyiha (foydalanuvchi tasdig'i, 2026-09-12; repoda boshqa joyda qayd etilmagan)",
     "manba": "faza_2_confidence_audit.md 0.3 (ochiq savol edi); qaror — 2026-09-12"},
]

PENDING_ITEMS = [
    {"id": "D2", "band": "2.37 — unlidan keyingi \"-ydi\" (ishla → ishlaydi)",
     "diss": "—",
     "kod": "`make_uzbek(..., \"s\", \"Fe'l\")`: undoshdan keyin -adi (spec), unlidan keyin -ydi (o'zbek imlosi "
            "qoidasi sifatida qo'shilgan, 71908ed).",
     "kim": PROF, "manba": "faza_2.md 5-bo'lim 1"},
]

TECH_ITEMS = [
    {"id": "H1", "band": "Lug'at teglanishi + `uz_stem()` \"-moq\" kesishi",
     "kod": "Network → «Tarmoq» VERBS'da; `uz_stem()` turkumdan qat'i nazar \"-moq\" ni kesadi (networks → «Taradi»); "
            "apply/comply/imply/rely — Ravish, confer/dump/filter — Ot.",
     "kim": f"{DEV} (`uz_stem()` ni turkumga bog'lash); lug'at teglari — {VAZ} ma'lumoti",
     "manba": "faza_2.md 4A; faza_7_backlog.md 2"},
    {"id": "H2", "band": "CH2 formal modelidagi \"GHA1\" yozuvi",
     "kod": "BM_uz_w dagi CH2 modeli `G(G_HA1) = $[i,1-h3]GHA1i` — SSM ildiz belgisini \"GHA\" deb o'qiydi, tanimaydi "
            "→ `ask` MDB bilan «Ajratib ko'rsatmoq» ga almashadi (2.56 haqiqiy lug'at bilan noto'g'ri, stub bilan TO'LIQ).",
     "kim": DEV, "manba": "faza_2.md 4B"},
]

# Kod ≠ spec (QISMAN) qatorlari uchun: standart qoidadan (L → lug'at ma'lumoti,
# M/N/S → spec'ga moslash) chetga chiqadigan holatlar — har biri sababi bilan.
CODE_GAP_OWNERS = {
    "3.2": (VAZ, "spec sifat + \"-ly\" uchun ikki xil o'zbekcha beradi (3.2 «-lik bilan», 3.9 «-gina»); qaysi so'zga "
                 "qaysi biri — spec'da mezon yo'q (tavsiflar: «Yasama ravish» / «Holat ravishi»)"),
    "3.9": (VAZ, "spec sifat + \"-ly\" uchun ikki xil o'zbekcha beradi (3.2 «-lik bilan», 3.9 «-gina»); qaysi so'zga "
                 "qaysi biri — spec'da mezon yo'q (tavsiflar: «Yasama ravish» / «Holat ravishi»)"),
    "3.24": (VAZ, "spec \"men + ning\" harfma-harf qo'shilsa «menning»; o'zbek imlosida «mening» (kod shuni beradi). "
                  "\"+\" — morfema chegarasimi, natija shaklimi — tasdiqlanmaguncha kodni «menning» ga moslamang"),
    "3.25": (VAZ, "\"men + niki\" imloda «meniki» (kod shuni beradi); qolgan uchtasi \"+ ning\" — 4-bo'lim C·3.25"),
    "3.27": (VAZ, "many/each — 1500-lug'at tarjimasi spec'dan farq qiladi (each uchun 1500-JSON da «Har bir (Olmosh)» "
                  "yozuvi ham bor — qaysi biri tanlanishi texnik); `no` — bosh so'z lug'atda yo'q"),
    "2.54": (DEV, "modal \"ought\" dan keyingi \"to\" → «Ga» (faza_2.md 4C)"),
    "3.3": (DEV, "natija mos; faqat turkum belgisi farq qiladi"),
    "3.4": (DEV, "natija mos; faqat turkum belgisi farq qiladi"),
}

TITLES = {
    "G": "1. Himoya uchun eng muhim ochiq savollar",
    "A": "2. Spec ≠ dissertatsiya II bobi (tarjima farqi)",
    "B": "3. Dissertatsiya II bobining ichki masalalari",
    "C": "4. Spec hujjatining o'zidagi nomuvofiqliklar",
    "D": "5. Nazariy daraja: formal model doirasi",
    "E": "6. Kod ≠ spec, lekin sabab lug'at yoki spec yozuvida — kodni o'zgartirishdan oldin qaror kerak",
    "F": "7. Kodda yo'q (YO'Q) — bosh so'z lug'atda yo'q",
    "T": "8. Texnik navbat — professor/Vazira qarori shart emas (to'liqlik uchun)",
    "R": "9. Hal qilingan bandlar",
}
ORDER = ["G", "A", "B", "C", "D", "E", "F", "T", "R"]


def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def owner_for_diff(row: dict, xm_keys: set[str]) -> tuple[str, str]:
    """Spec ≠ dissertatsiya qatori uchun (egasi, sabab) — MEXANIK qoida."""
    if row["spec_ichki"]:
        return VAZ, "spec katagi ichki nomuvofiq (\"+\" qismlari dissertatsiya bilan bir xil)"
    if csd.en_key(row["en"]) in xm_keys:
        return VAZ, "dissertatsiya o'zbekchasi boshqa spec misolinikiga aynan teng (nusxa xatosi bo'lishi mumkin)"
    d = [normalize(x["uz_marker_word"] or "") for x in row["diss"]]
    if any(levenshtein(normalize(conf._clean(e)), u) <= 1 for e in row["spec"] for u in d):
        return VAZ, "1 harflik imlo farqi"
    return PROF, "ikki manba ikki xil tarjima/talqin beradi"


def owner_for_code_gap(uid: str, tur: str) -> tuple[str, str]:
    """Kod ≠ spec (QISMAN) qatori uchun (egasi, sabab): L turi — natija lug'at
    yozuvidan keladi (lug'at ma'lumoti); M/N/S — spec kanonik, kodni moslash
    texnik ish. Istisnolar — `CODE_GAP_OWNERS`."""
    if uid in CODE_GAP_OWNERS:
        return CODE_GAP_OWNERS[uid]
    if tur == "L":
        return VAZ, "lug'at yozuvi spec'dan farq qiladi yoki bosh so'z lug'atda yo'q — lug'at ma'lumoti"
    return DEV, "spec'ga moslash (spec — kanonik manba)"


def owner_key(kim: str) -> str:
    head = kim.split(" —")[0]
    if head.startswith(PROF_VAZ):
        return PROF_VAZ
    for k in (VAZ, PROF, DEV, "Ziyoviddin"):
        if head.startswith(k):
            return k
    return head


def _cell(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ")


def build(docx_path: str) -> dict:
    import audit_er_gap

    spec = conf.load_spec()
    items = ch2l.load_docx(docx_path)
    recs = ch2l.extract_ch2_records(items, ch2l.find_chapter_bounds(items)["II"])
    tmp = tempfile.mkdtemp(prefix="kkt_master_")
    try:
        m = conf.build_isolated_module(tmp)
        evs = {e["uid"]: e for e in conf.evaluate_all(m, spec)}
        ch2 = list(m.CH2_EVX_EXAMPLES)
        gold_ni = gold_accusative_gap(m)
        extra_aff = conf._code_affixes_not_in_spec(None, m)
        psb = psb_rows(m)
        pos_v2 = dict(m.POS_V2)
    finally:
        if tmp in sys.path:
            sys.path.remove(tmp)
        shutil.rmtree(tmp, ignore_errors=True)
    rows = csd.build_rows(spec, recs, ch2)
    return {"spec": spec, "recs": recs, "evs": evs, "ch2": ch2, "rows": rows,
            "xm": csd.cross_matches(recs), "gold_ni": gold_ni, "extra_aff": extra_aff, "psb": psb,
            "pos_v2": pos_v2,
            "er_theory": audit_er_gap.check_dissertation_theory(docx_path),
            "er_spec": audit_er_gap.check_kkt_spec()}


def gold_accusative_gap(m) -> dict:
    """100_soz gold: tizim chiqishi (GUI kabi, readonly) etalondan FAQAT oxiridagi
    "-ni" bilan farq qiladigan qatorlar — joriy kod bilan qayta sanaladi."""
    with open(os.path.join(REPO_ROOT, "data", "100_soz.json"), encoding="utf-8") as f:
        gold = json.load(f)
    mis, ni = [], []
    for e in gold:
        out = normalize(conf.system_output(m, e["english"])["natija"])
        ref = normalize(e["uzbek"])
        if out != ref:
            mis.append(e)
            if ref == out + "ni":
                ni.append(e)
    return {"n": len(gold), "mis": len(mis), "ni": len(ni), "misol": [(e["english"], e["uzbek"]) for e in ni[:2]]}


def psb_rows(m) -> dict[str, int | None]:
    """Predmet sohalar bazasi (PSB) `terms` jadvalidagi qatorlar soni."""
    out = {}
    for path in (m.DB_PSB_EN, m.DB_PSB_UZ):
        if not os.path.exists(path):
            out[os.path.basename(path)] = None
            continue
        con = sqlite3.connect(path)
        try:
            out[os.path.basename(path)] = con.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        finally:
            con.close()
    return out


def _pair(pairs: list[dict], en: str) -> dict | None:
    return next((p for p in pairs if p["en"] == en), None)


def _yol(p: dict) -> str:
    """Tizim chiqishidagi har bir token qayerdan kelgani (lug'at manbasi / qoida)."""
    parts = []
    for t in p["tokens"]:
        if not t["found"]:
            parts.append(f"{t['word']}: lug'atda yo'q")
        elif t["sources"]:
            src = ", ".join(conf._SOURCE_LABEL.get(s, s) for s in t["sources"])
            parts.append(f"{t['word']}: {src}" + (" → MDB almashtirdi" if "MDB_uz_w" in t["method"] else ""))
        else:
            parts.append(f"{t['word']}: qoida -{t['suffix'] or '∅'}")
    return "; ".join(parts)


def _fmt(p: dict, yol: bool = True) -> str:
    s = f"`{p['en']}` → «{p['natija']}»"
    return s + (f" ({_yol(p)})" if yol else "")


def kod_state(ev: dict, en: str) -> str:
    """Bitta spec misoli uchun kodning holati: holat qaysi natijadan aniqlangan
    (L — haqiqiy lug'at, M/N/S — stub) va haqiqiy lug'at bilan chiqish."""
    real = _pair(ev["real"], en)
    if ev["tur"] == "L":
        return f"Holat: {ev['holat']}. Tizim: {_fmt(real)}."
    mech = _pair(ev["mech"], en)
    return (f"Holat: {ev['holat']} — stub (kodga faqat spec o'zagi berilgan): «{mech['natija']}». "
            f"Haqiqiy lug'at bilan: {_fmt(real)}.")


def _ch2_only(ev: dict) -> bool:
    """Conformance hisobotidagi ta'rif: topilgan har bir token (\"to\" dan tashqari)
    FAQAT CH2_EVX_EXAMPLES yozuvidan kelgan."""
    return all(t["sources"] == ["chapter2_evx"] for p in ev["real"] for t in p["tokens"]
               if t["found"] and t["word"] != "to")


def toliq_breakdown(evs: dict) -> dict:
    """TO'LIQ MOS qoidalarining to'liq taqsimoti — har bir qism nomi bilan, yig'indi
    tekshiruvi bilan (hech bir qoida tushib qolmasligi uchun).

    L turi (holat haqiqiy lug'at bilan): aylanma (faqat CH2) / mustaqil.
    M/N/S turi (holat stub bilan): xuddi shu misol haqiqiy lug'at bilan noto'g'ri /
    to'g'ri faqat CH2 orqali / to'g'ri CH2 siz."""
    toliq = [e for e in evs.values() if e["holat"] == conf.TOLIQ]
    tl = [e for e in toliq if e["tur"] == "L"]
    tm = [e for e in toliq if e["tur"] != "L"]
    b = {"toliq": toliq, "tl": tl, "tm": tm,
         "tl_ch2": [e for e in tl if _ch2_only(e)],
         "tm_bad": [e for e in tm if not all(p["mos"] for p in e["real"])]}
    b["tl_ind"] = [e for e in tl if e not in b["tl_ch2"]]
    b["tm_ch2"] = [e for e in tm if e not in b["tm_bad"] and _ch2_only(e)]
    b["tm_ind"] = [e for e in tm if e not in b["tm_bad"] and e not in b["tm_ch2"]]
    assert len(b["tl_ch2"]) + len(b["tl_ind"]) == len(tl)
    assert len(b["tm_bad"]) + len(b["tm_ch2"]) + len(b["tm_ind"]) == len(tm)
    assert len(tl) + len(tm) == len(toliq)
    return b


def collect(d: dict) -> dict:
    """Barcha bandlar (bo'lim, ID, 5 ustun, egasi, jiddiy/hal belgisi) va yig'ma sonlar —
    Markdown va HTML shu bitta ma'lumotdan chiqariladi."""
    spec, evs, rows, xm, recs, ch2 = d["spec"], d["evs"], d["rows"], d["xm"], d["recs"], d["ch2"]
    rule_by = {r["uid"]: r for r in spec["rules"]}
    xm_keys = {csd.en_key(x["rec"]["en_marker_word"]) for x in xm}
    diff = [r for r in rows if r["spec_diss"] == "FARQ"]
    diff_uids = {r["uid"] for r in diff}

    entries: list[dict] = []

    def add(sec, id_, band, spec_, diss, kod, kim, manba, jiddiy=False, hal=None):
        entries.append({"sec": "R" if hal else sec, "id": id_, "band": band, "spec": spec_, "diss": diss,
                        "kod": kod, "kim": kim, "manba": manba, "jiddiy": jiddiy, "hal": hal,
                        "owner": owner_key(kim)})

    def diss_summary(uid: str) -> str:
        """Shu qoida misollari dissertatsiya II bobida nima deydi (compare_spec_dissertation qatorlaridan)."""
        rr = [r for r in rows if r["uid"] == uid]
        same = [r for r in rr if r["spec_diss"] == "mos"]
        farq = [r for r in rr if r["spec_diss"] == "FARQ"]
        parts = []
        if same:
            parts.append("Spec bilan bir xil: " + "; ".join(f"«{x['uz_marker_word']}»" for r in same for x in r["diss"]))
        if farq:
            parts.append("Spec'dan FARQ: " + "; ".join(f"`{r['en']}` → «{x['uz_marker_word']}» (#{x['uz_idx']})"
                                                   for r in farq for x in r["diss"]) + f" — 2-bo'lim A·{uid}")
        if not parts:
            return "II bobda avtomatik topilmadi"
        n = len(same) + len(farq)
        return "; ".join(parts) + ("" if n == len(rr) else f" ({n}/{len(rr)} misol topildi)")

    # ── 1. Himoya uchun eng muhim ochiq savollar ──
    for it in STATIC_ITEMS:
        add("G", it["id"], it["band"], it["spec"], it["diss"], it["kod"], it["kim"], it["manba"],
            jiddiy=it.get("jiddiy", False), hal=it.get("hal"))

    w_ok = [w for w in spec["pos_weights_manba"] if d["pos_v2"].get(w["kalit"]) == w["vazn"]]
    add("G", "G3", "So'z turkumi vaznlarining ilmiy asosi (taqriz 28-band)",
        "; ".join(w["docx_matn"] for w in spec["pos_weights_manba"]), "—",
        f"{len(w_ok)}/{len(spec['pos_weights_manba'])} vazn `POS_V2` da spec bilan bit-aniq bir xil (taqriz 27-band — "
        "qiymatlar MANBASI shu); qolgani (U, L) kodda kalit sifatida yo'q (8-bo'lim H5). Nega aynan shu qiymatlar — "
        "ILMIY ASOSI (28-band) ochiq.",
        f"{VAZ} (professor bilan)", "faza_2_kkt_spec_conformance.md 3-bo'lim")

    g = d["gold_ni"]
    ex = "; ".join(f"\"{en}\" → \"{uz}\"" for en, uz in g["misol"])
    ni_rules = ("2.55b", "2.59", "3.22", "3.26")
    add("G", "G5", "100_soz gold'dagi \"-ni\" (tushum kelishigi) fe'lsiz iborada",
        "Umumiy tushum kelishigi qoidasi yo'q. \"-ni\" faqat misollarda: "
        + "; ".join(f"{u} «{rule_by[u]['uz_misol']}»" for u in ni_rules) + ".",
        f"100_soz (gold) etaloni fe'lsiz iborada ham -ni beradi (masalan {ex}).",
        f"Joriy kod: {g['n']} tadan {g['mis']} tasi etalonga mos emas; shundan {g['ni']} tasi etalondan FAQAT oxirgi "
        "\"-ni\" bilan farq qiladi. (Faza 1 dagi \"20 ta\" — boshqa mezon: \"our X\"/\"your X\" naqshidagi bandlar.)",
        f"{VAZ} (professor bilan) — gold etalon ma'lumoti", "faza_1.md (44 qator tarkibi, \"Nima ishlamadi\")")

    b = toliq_breakdown(evs)

    def uids(es):
        return ", ".join(e["uid"] for e in es) or "—"

    n_ch2 = len(b["tm_ch2"]) + len(b["tl_ch2"])
    n_ind = len(b["tm_ind"]) + len(b["tl_ind"])
    add("G", "G8", f"\"{len(b['toliq'])} ta TO'LIQ MOS\" ni qanday taqdim etish",
        f"{len(spec['rules'])} qoida — rasmiy spesifikatsiya.", "—",
        f"TO'LIQ MOS {len(b['toliq'])} = M/N/S turi {len(b['tm'])} (holat stub bilan — formal qoida lug'atdan "
        f"mustaqil) + L turi {len(b['tl'])} (holat haqiqiy lug'at bilan). Conformance hisobotidagi "
        f"\"{len(b['toliq']) - len(b['tl_ch2'])} mustaqil\" = {len(b['tm'])} M/N/S + {len(b['tl_ind'])} L "
        f"({uids(b['tl_ind'])} — 1500-lug'at yozuvidan); \"{len(b['tl_ch2'])} aylanma\" = qolgan L "
        f"({uids(b['tl_ch2'])} — natija FAQAT CH2 dan). "
        f"Haqiqiy lug'at bilan (GUI'da) {len(b['toliq'])} tadan: {len(b['tm_bad'])} tasi noto'g'ri — hammasi "
        f"M/N/S ({uids(b['tm_bad'])}); {n_ch2} tasi to'g'ri, lekin faqat CH2 yozuvi orqali — {len(b['tm_ch2'])} "
        f"M/N/S ({uids(b['tm_ch2'])}) + {len(b['tl_ch2'])} L aylanma; {n_ind} tasi CH2 siz to'g'ri — "
        f"{len(b['tm_ind'])} M/N/S ({uids(b['tm_ind'])}) + {len(b['tl_ind'])} L ({uids(b['tl_ind'])}). "
        f"Tekshiruv: {len(b['tm_bad'])} + {n_ch2} + {n_ind} = {len(b['toliq'])}.",
        f"{PROF_VAZ} — himoyada qaysi raqam va qanday izoh bilan keltiriladi",
        "faza_2_kkt_spec_conformance.md 0, 0.1, 2.1; faza_2.md 1")

    psb = ", ".join(f"{k}={v}" for k, v in d["psb"].items())
    add("G", "G9", "Predmet sohalar bazasi (PSB) — ko'p ma'noli so'zlar",
        "—", "IV bob (#1138): «PSB_en_w KTsida semantik noaniqlikni bartaraf etishning asosiy mexanizmi hisoblanadi».",
        f"PSB `terms` jadvali bo'sh ({psb} qator); `KKT_Terminologik_Lugat.json` (20 so'z × soha) yuklanmaydi; "
        "`psb_select_meaning()` domain'siz chaqiriladi → har doim birinchi ma'no. Ya'ni dissertatsiya \"asosiy "
        "mexanizm\" deb tasvirlagan qism kodda ishlamaydi.",
        f"{VAZ} (professor bilan) — PSB to'ldiriladimi yoki IV bob matni aniqlashtiriladimi",
        "faza_2_lexicon_sources.md 2; ch2_leakage_check.md 3.3", jiddiy=True)

    # ── 2. Spec ≠ dissertatsiya ──
    for r in diff:
        kim, sabab = owner_for_diff(r, xm_keys)
        diss = "; ".join(f"«{x['uz_marker_word']}» (#{x['uz_idx']})" for x in r["diss"])
        add("A", f"A·{r['uid']}", f"{r['uid']} `{r['en']}` — {rule_by[r['uid']]['tavsif']}",
            f"`{r['spec_cell']}`", diss, f"CH2: {csd.ch2_label(r)}. {kod_state(evs[r['uid']], r['en'])}",
            f"{kim} — {sabab}", "faza_2_spec_vs_dissertation.md 1")

    # ── 3. Dissertatsiya II bobining ichki masalalari ──
    diff_keys = {csd.en_key(r["en"]) for r in diff}
    for x in xm:
        rec = x["rec"]
        k = csd.en_key(rec["en_marker_word"])
        if k in diff_keys:
            continue  # 2-bo'limda allaqachon bor
        own = "; ".join(f"{u} `{e}` → {v}" for u, e, v in x["own"]) or "spec'da yo'q"
        other = "; ".join(f"{u} `{e}` → {v}" for u, e, v in x["other"])
        ch2_same = [c for c in ch2 if csd.en_key(c["en"]) == k and conf.compare(c["uz"], rec["uz_marker_word"], True)]
        kod = ("CH2 da ham shu yozuv bor: " + "; ".join(f"`{c['en']}` → «{c['uz']}»" for c in ch2_same)
               + " (lug'atga yoziladi)") if ch2_same else "CH2 da bu yozuv yo'q"
        real = [p for e in evs.values() for p in e["real"] if csd.en_key(p["en"]) == k]
        if real:
            kod += f". Tizim chiqishi: «{real[0]['natija']}»"
        kim = (f"{VAZ} — dissertatsiya matnidagi nusxa/yorliq xatosi bo'lishi mumkin" if x["own"] else
               f"{VAZ} — inglizcha shakl farqi (II bob `{rec['en_marker_word']}`, spec "
               + ", ".join(f"`{e}`" for _, e, _ in x["other"]) + "), o'zbekchasi bir xil")
        add("B", f"B·#{rec['en_idx']}", f"II bob #{rec['en_idx']}: `{rec['en_marker_word']}`",
            f"O'z misoli: {own}", f"«{rec['uz_marker_word']}» — {other} bilan bir xil", kod, kim,
            "faza_2_spec_vs_dissertation.md 1.1, 4")
    notfound: dict[str, list[str]] = {}
    for r in rows:
        if r["spec_diss"] is None:
            notfound.setdefault(r["uid"], []).append(r["en"])
    add("B", "B·5", f"{sum(len(v) for v in notfound.values())} ta spec misoli II bobda avtomatik topilmadi",
        "; ".join(f"{u}: {', '.join(ens)}" for u, ens in notfound.items()),
        "Avtomatik ajratish faqat \"Ingliz tilida EVX ... / Oʻzbek tilida EVIX ...\" paragraf naqshini taniydi — "
        "topilmadi ≠ dissertatsiyada yo'q (masalan olmosh ro'yxatlari jadval ichida bo'lishi mumkin).",
        "—", f"{VAZ} — qo'lda tasdiqlash: II bobda bormi va qanday tarjima bilan",
        "faza_2_spec_vs_dissertation.md 5")

    # ── 4. Spec hujjatining o'zidagi nomuvofiqliklar ──
    for r in spec["rules"]:
        if not r.get("izoh"):
            continue
        kod = f"Holat: {evs[r['uid']]['holat']}"
        if r["uid"] in diff_uids:
            kod += f" (spec ≠ dissertatsiya farqi ham bor — 2-bo'lim A·{r['uid']})"
        add("C", f"C·{r['uid']}", f"{r['uid']} — {r['tavsif']}", r["izoh"], diss_summary(r["uid"]), kod,
            f"{VAZ} — spec hujjati matni", "data/kkt_spec.json → izoh")
    for i, h in enumerate(spec["hujjat_izohlari"], 1):
        add("C", f"C·H{i}", "Spec hujjati (umumiy)", h, "—", "—", VAZ, "data/kkt_spec.json → hujjat_izohlari")

    # ── 5. Nazariy daraja ──
    er_t, er_s = d["er_theory"], d["er_spec"]
    add("D", "D1", "Agentiv \"-er\" (teacher, worker)",
        f"\"-er\" faqat {len(er_s['er_rules'])} ta qiyosiy daraja qoidasida ("
        + ", ".join(r["uid"] for r in er_s["er_rules"]) + f"); agentiv kalit so'zlar: {len(er_s['agentive_hits'])} ta.",
        f"I bob 1.3-jadval (ot yasovchi suffikslar): \"-er\" {'BOR' if er_t and er_t['noun_suffix_table_has_er'] else '—'}; "
        "II bob misollarida faqat qiyosiy.",
        "`MORPH_RULES` da agentiv qoida bor (C←G), make_uzbek uni qiyosiy \"-roq\" deb sintez qiladi "
        "(worker → «Ishlaroq»).", PROF, "faza_2_er_gap.md 6; faza_2.md 5-bo'lim 2")
    for it in PENDING_ITEMS:
        add("D", it["id"], it["band"], f"Faqat undosh holati: {rule_by['2.37']['uz_misol']}.", it["diss"], it["kod"],
            it["kim"], it["manba"])
    tested = {p["aff"] for p in conf.PROBES.values() if p["aff"]}
    n_table = len(er_t["noun_suffix_table"] or []) if er_t else 0
    add("D", "D3", "Kodda bor, spec'da yo'q affikslar (teskari yo'nalish)",
        f"Spec misollari bilan tekshiriladigan affikslar: {len(tested)} ta (M turidagi qoidalar).",
        f"I bob 1.3-jadval: {n_table} ta ot yasovchi suffiks (nazariy inventar, izohsiz)." if n_table else "—",
        f"`MORPH_RULES` dagi {len(d['extra_aff'])} ta affiks hech bir spec misoli bilan qamralmagan: "
        + ", ".join(f"`-{a}`" for a in d["extra_aff"]) + ".",
        f"{PROF} — formal model doirasi: spec kengaytiriladimi yoki bu qoidalar \"spec'dan tashqari\" deb belgilanadimi",
        "faza_2_kkt_spec_conformance.md 3-bo'lim")
    add("D", "D4", "Spec operatorlari (1-jadval) kodda",
        "; ".join(f"{op['belgi']} — {op['mano']}" for op in spec["operators"]), "—",
        "⊕ — biriktirish sifatida ishlatiladi; V — \"yoki\" amali sifatida ISHLATILMAYDI (`KKT_SYMBOLS` da «umumiy BB» "
        "ma'nosida); ⇓ — kodda yo'q; $ — formal model satrida faqat matn sifatida hosil qilinadi, tanlash amali "
        "hisoblanmaydi.",
        f"{PROF} — formal model semantikasi: operatorlar hisoblanishi shartmi",
        "faza_2_kkt_spec_conformance.md 3-bo'lim (Operatorlar)")

    # ── 6. Kod ≠ spec (QISMAN); qaror kerak bo'lganlari 6-bo'limda, texniklari 8-bo'limda ──
    for uid, ev in evs.items():
        if ev["holat"] != conf.QISMAN or uid in diff_uids:
            continue
        r = rule_by[uid]
        kim, sabab = owner_for_code_gap(uid, ev["tur"])
        if ev["tur"] == "L":
            bad = [p for p in ev["real"] if not p["mos"]]
            kod = ("Haqiqiy lug'at: " + "; ".join(_fmt(p) for p in bad[:4]) + (" …" if len(bad) > 4 else "")
                   + f" ({ev['n_mos']}/{ev['n_jami']} mos).")
        else:
            bad = [p for p in ev["mech"] if not p["mos"]]
            if bad:
                kod = ("Stub: " + "; ".join(f"`{p['en']}` → «{p['natija']}»" for p in bad[:3])
                       + f" ({ev['n_mos']}/{ev['n_jami']} mos).")
            else:
                t = ev.get("tahlil") or {}
                kod = f"Stub: natija mos, lekin kod so'zni {t.get('pos') or '—'} deb belgilaydi (spec bo'limi: {r['pos']})."
            kod += " Haqiqiy lug'at bilan: " + "; ".join(f"«{p['natija']}»" for p in ev["real"][:3]) + "."
        add("E" if kim != DEV else "T", f"E·{uid}", f"{uid} — {r['tavsif']}", f"`{r['en_misol']}` ⟹ `{r['uz_misol']}`",
            diss_summary(uid), kod, f"{kim} — {sabab}", "faza_2_kkt_spec_conformance.md 2")

    # ── 7. Kodda yo'q (YO'Q) ──
    for uid, ev in evs.items():
        if ev["holat"] != conf.YOQ:
            continue
        r = rule_by[uid]
        if ev["tur"] == "L":
            add("F", f"F·{uid}", f"{uid} — {r['tavsif']}", f"`{r['en_misol']}` ⟹ `{r['uz_misol']}`",
                diss_summary(uid), "Bosh so'z lug'atda yo'q — " + "; ".join(_fmt(p, False) for p in ev["real"]),
                f"{VAZ} — lug'at ma'lumoti (Faza 7)", "faza_7_backlog.md 1")
        else:
            add("T", f"F·{uid}", f"{uid} — {r['tavsif']}", f"`{r['en_misol']}` ⟹ `{r['uz_misol']}`",
                diss_summary(uid), "Stub: " + "; ".join(_fmt(p, False) for p in ev["mech"]) + " — o'zak tanilmadi",
                f"{DEV} — noqoida jadval (ro'yxat dissertatsiya II bobida)", "faza_7_backlog.md 3")

    # ── 8. Texnik navbat ──
    for it in TECH_ITEMS:
        add("T", it["id"], it["band"], "—", "—", it["kod"], it["kim"], it["manba"])

    same_ch2_diff = [r for r in rows if r["spec_diss"] == "mos" and r["ch2_diss"] == "FARQ"]
    both_diff = [r for r in diff if r["ch2"] and r["ch2_spec"] != "mos" and r["ch2_diss"] != "mos"]
    diss_keys = {csd.en_key(x["en_marker_word"]) for x in recs}
    orphans = [c for c in ch2 if csd.en_key(c["en"]) not in diss_keys]
    by_en: dict[str, list[dict]] = {}
    for c in ch2:
        by_en.setdefault(csd.en_key(c["en"]), []).append(c)
    dups = [v for v in by_en.values() if len({normalize(c["uz"]) for c in v}) > 1]
    parts = []
    if same_ch2_diff:
        parts.append("II bob va spec bir xil, CH2 boshqacha: " + "; ".join(
            f"`{r['en']}` → CH2 «{', '.join(c['uz'] for c in r['ch2'])}» (II bob/spec «{r['spec'][0]}»)"
            for r in same_ch2_diff))
    if both_diff:
        parts.append("CH2 ikkala manbadan farq: " + "; ".join(
            f"`{r['en']}` → CH2 «{', '.join(c['uz'] for c in r['ch2'])}» (II bob «{r['diss'][0]['uz_marker_word']}», "
            f"spec «{r['spec'][0]}»)" for r in both_diff))
    if orphans:
        parts.append("II bobda bunday yozilish yo'q (transkripsiya): " + ", ".join(
            f"`{c['en']}` → «{c['uz']}»" for c in orphans))
    if dups:
        parts.append("Bir inglizcha shaklga bir necha yozuv: " + "; ".join(
            f"`{v[0]['en']}` → " + " / ".join(f"«{c['uz']}»" for c in v) for v in dups))
    add("T", "H3", "CH2_EVX_EXAMPLES nusxasidagi xatolar", "—", "(har bir holatda qavs ichida)",
        ". ".join(parts) + ". Hammasi lug'atga `source='chapter2_evx'` bilan yoziladi.",
        f"{DEV} — CH2 ni II bob matniga moslash (bir necha yozuvli shakllar — 3-bo'lim qaroriga bog'liq)",
        "faza_2_spec_vs_dissertation.md 1, 2; faza_2_kkt_spec_conformance.md 5; ch2_leakage_check.md 1")
    multi = [c["en"] for c in ch2 if " " in c["en"].strip()]
    add("T", "H4", "CH2 dagi ko'p so'zli headword'lar", "—", "—",
        f"{len(multi)} ta ko'p so'zli CH2 yozuvi (" + ", ".join(f"`{x}`" for x in multi) + ") lug'atga yoziladi, "
        "lekin qidiruv token bo'yicha — ular ishlatilmaydi. Butun ibora bo'yicha qidiruv qo'shilsa, avval "
        "`tests/test_audit_lexicon_sources.py` (100_soz gold ham lug'atda — CLAUDE.md).",
        DEV, "faza_7_backlog.md 2; CLAUDE.md")
    yord = next(w for w in spec["pos_weights_manba"] if w["kalit"] == "Yordamchi")
    add("T", "H5", f"Yordamchi so'z turkumlari ({yord['belgi']}) — {yord['vazn']}",
        f"Vazn jadvalida 9-turkum: «{yord['docx_matn']}».", "—",
        "`POS_V2`/`POS_KKT` da kalit yo'q; 0.07 faqat \"eng\" (P2_D) uchun qattiq yozilgan; U/L SSM ildiz belgisi "
        "sifatida qo'shilgan (bd79825).", DEV, "faza_2_kkt_spec_conformance.md 3-bo'lim")

    for e in entries:
        if e["sec"] == "G":
            e["_k"] = (not e["jiddiy"], int(e["id"][1:]))
    by_sec = {s: [e for e in entries if e["sec"] == s] for s in ORDER}
    by_sec["G"].sort(key=lambda e: e["_k"])
    owners_open: dict[str, int] = {}
    for e in entries:
        if e["sec"] != "R":
            owners_open[e["owner"]] = owners_open.get(e["owner"], 0) + 1
    return {"entries": entries, "by_sec": by_sec, "owners_open": owners_open, "breakdown": b,
            "holat_n": {h: sum(1 for e in evs.values() if e["holat"] == h) for h in conf.HOLATLAR},
            "n_rules": len(spec["rules"]),
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def render(d: dict) -> str:
    """Markdown hisobot (reports/master_qarorlar_royxati.md)."""
    return render_md(collect(d))


def _band_md(e: dict) -> str:
    return ("⚠ JIDDIY — " if e["jiddiy"] else "") + e["band"]


def _kim_md(e: dict) -> str:
    return f"✓ HAL QILINDI — {e['hal']}. Mas'ul: {e['kim']}" if e["hal"] else e["kim"]


def render_md(c: dict) -> str:
    by_sec, b, hn = c["by_sec"], c["breakdown"], c["holat_n"]
    jiddiy = [e for e in c["entries"] if e["jiddiy"]]
    L = ["# Master qarorlar ro'yxati — himoyaga tayyorgarlik uchun yagona ko'rish nuqtasi", ""]
    L.append(f"**Generatsiya vaqti:** {c['generated']}")
    L.append("**Buyruq:** `python scripts/build_master_decisions.py` (`make master`) — `data/desertatsiya.docx` talab qilinadi.")
    L.append("")
    L.append("Bu fayl uchta Faza 2 hisobotini bitta ro'yxatga jamlaydi: `faza_2_spec_vs_dissertation.md` (spec ↔ "
             "dissertatsiya ↔ CH2), `faza_2_kkt_spec_conformance.md` (kodning spec'ga mosligi) va `faza_2.md` "
             "(qaror kutilayotgan va past ustuvorlikdagi bandlar), hamda ular tayanadigan `faza_2_er_gap.md`, "
             "`faza_7_backlog.md`, `faza_2_lexicon_sources.md`. 1-bo'limda — oldingi auditlardagi himoya uchun muhim "
             "ochiq savollar (`faza_2_confidence_audit.md`, `ch2_leakage_check.md`, `faza_1.md`). Hisoblanadigan "
             "bandlar har safar kodni chaqirib qayta hosil qilinadi; qolganlari manba hisobotdan (\"Manba\" ustuni).")
    L.append("")
    L.append("## ⚠ Eng og'ir topilmalar — himoyadan oldin hal qilinishi shart")
    L.append("")
    L.append("Ikkalasida ham dissertatsiya matnidagi da'vo kodda qo'llab-quvvatlanmaydi. Og'irligi bir xil.")
    L.append("")
    for e in jiddiy:
        L.append(f"- **{e['id']} — {e['band']}.** Dissertatsiya: {e['diss']} Kod: {e['kod']} "
                 f"**Kim hal qiladi:** {e['kim']}.")
    L.append("")
    L.append("**Ustunlarni qanday o'qish kerak:**")
    L.append("- **Spec** — `data/kkt_spec.json` (← `kkt_qoidalari.docx`), loyihaning kanonik manbasi; kod unga "
             "moslashtirilmoqda.")
    L.append("- **Dissertatsiya** — `data/desertatsiya.docx` II bobidan AVTOMATIK ajratilgan EVX/EVIX juftlari "
             "(#N — docx paragraf indeksi). \"Topilmadi\" ≠ \"dissertatsiyada yo'q\".")
    L.append("- **CH2** — `CH2_EVX_EXAMPLES`: dissertatsiya misollarining kodga qo'lda ko'chirilgan nusxasi, lug'atga "
             "`source='chapter2_evx'` bilan yoziladi.")
    L.append("- **Holat** — conformance hisobotidagi holat. M/N/S turidagi qoidalarda u **stub** bilan aniqlanadi "
             "(kodga faqat spec o'zagi beriladi — formal qoida lug'atdan mustaqil tekshiriladi); **haqiqiy lug'at "
             "bilan** — foydalanuvchi GUI'da ko'radigan natija. Ikkalasi farq qilishi mumkin (G8).")
    L.append("")
    L.append("**\"Kim hal qiladi\" — TAKLIF** (mexanik qoida + har bir istisno sababi bilan; himoyadan oldin kelishilsin):")
    L.append(f"- **{PROF}** — ilmiy/lingvistik tamoyil: ikki manba ikki xil tarjima/talqin bergan joy, kategoriya va "
             "formal model doirasi, metrika validligi.")
    L.append(f"- **{VAZ}** — o'z matni/ma'lumotidagi masala: dissertatsiya o'zbekchasi boshqa misolnikiga aynan teng; "
             "spec katagi ichki nomuvofiq yoki mezonsiz; 1 harflik imlo farqi; lug'at yozuvi spec'dan farqli yoki yo'q; "
             "yo'qolgan ma'lumotni tiklash.")
    L.append(f"- **{DEV}** — qaror shart emas (spec kanonik, kodni moslash texnik ish); faqat 8-bo'limda.")
    L.append("")
    L.append("## 0. Qisqa ko'rinish")
    L.append("")
    L.append("| Bo'lim | Bandlar |")
    L.append("|---|---|")
    for s in ORDER:
        L.append(f"| {TITLES[s]} | {len(by_sec[s])} |")
    L.append(f"| **Jami** | **{len(c['entries'])}** (ochiq {len(c['entries']) - len(by_sec['R'])}, "
             f"hal qilingan {len(by_sec['R'])}) |")
    L.append("")
    L.append("| Kim hal qiladi (taklif, ochiq bandlar) | Bandlar |")
    L.append("|---|---|")
    for k, n in sorted(c["owners_open"].items(), key=lambda x: -x[1]):
        L.append(f"| {k} | {n} |")
    L.append("")
    L.append(f"Kodning umumiy holati ({c['n_rules']} spec qoidasi): TO'LIQ MOS {hn[conf.TOLIQ]} "
             f"({hn[conf.TOLIQ] - len(b['tl_ch2'])} mustaqil / {len(b['tl_ch2'])} CH2 orqali aylanma; haqiqiy lug'at "
             f"bilan tarkibi — G8), QISMAN MOS {hn[conf.QISMAN]}, YO'Q {hn[conf.YOQ]}, ZID {hn[conf.ZID]}. "
             "Ba'zi qoidalar ikki bo'limda uchraydi (masalan 2.50, 2.58 — 2-bo'limda tarjima tanlovi, 7-bo'limda "
             "lug'at bo'shlig'i): bu ikki alohida qaror.")
    L.append("")
    for s in ORDER:
        sec = by_sec[s]
        if not sec:
            continue
        L.append(f"## {TITLES[s]}")
        L.append("")
        L.append("| ID | Qoida / misol | Spec nima deydi | Dissertatsiya nima deydi | CH2 / kod nima qiladi | Kim hal qiladi | Manba |")
        L.append("|---|---|---|---|---|---|---|")
        for e in sec:
            cells = [e["id"], _band_md(e), e["spec"], e["diss"], e["kod"], _kim_md(e), e["manba"]]
            L.append("| " + " | ".join(_cell(x) for x in cells) + " |")
        L.append("")
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════
#  HTML sahifa (Artifact sifatida chop etishga tayyor: <html>/<head>/<body>
#  teglarisiz — ular chop etishda qo'shiladi; lokal ko'rish uchun charset bor)
# ═══════════════════════════════════════════════════════════════════
_OWNER_CLASS = {PROF: "prof", VAZ: "vaz", PROF_VAZ: "pv", DEV: "dev"}

_HTML_HEAD = """<meta charset="utf-8">
<title>KKT himoya qarorlari</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Literata:opsz,wght@7..72,500;7..72,650&display=swap">
<style>
:root {
  --ground: #F2F5F5; --surface: #FFFFFF; --sunken: #E7EDED; --line: #D2DCDC;
  --ink: #132121; --muted: #566868; --accent: #136A70;
  --crit: #A3321E; --crit-soft: #F7E4DF; --crit-line: #E4B4A9;
  --ok: #2B7446; --ok-soft: #DFF0E5;
  --warn: #93600A; --warn-soft: #F5E9D2;
  --prof: #34438F; --prof-soft: #E3E6F5;
  --vaz: #0F6A70; --vaz-soft: #D7EDEE;
  --pv: #7A3E78; --pv-soft: #F1E2F0;
  --dev: #55626A; --dev-soft: #E5E9EB;
  --display: "Literata", "Georgia", "Times New Roman", serif;
  --body: "IBM Plex Sans", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  --mono: "IBM Plex Mono", "SFMono-Regular", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground: #0E1616; --surface: #152020; --sunken: #1B2828; --line: #2B3B3B;
    --ink: #E2EBEB; --muted: #94A7A7; --accent: #5CC3C9;
    --crit: #F08C76; --crit-soft: #3A1E18; --crit-line: #6B3A2F;
    --ok: #7CCB98; --ok-soft: #173022;
    --warn: #E3B25E; --warn-soft: #3A2C12;
    --prof: #A9B4F0; --prof-soft: #232A4C;
    --vaz: #5CC3C9; --vaz-soft: #133638;
    --pv: #E0A6DD; --pv-soft: #3A2239;
    --dev: #A9B5BB; --dev-soft: #243035;
  }
}
:root[data-theme="dark"] {
  --ground: #0E1616; --surface: #152020; --sunken: #1B2828; --line: #2B3B3B;
  --ink: #E2EBEB; --muted: #94A7A7; --accent: #5CC3C9;
  --crit: #F08C76; --crit-soft: #3A1E18; --crit-line: #6B3A2F;
  --ok: #7CCB98; --ok-soft: #173022;
  --warn: #E3B25E; --warn-soft: #3A2C12;
  --prof: #A9B4F0; --prof-soft: #232A4C;
  --vaz: #5CC3C9; --vaz-soft: #133638;
  --pv: #E0A6DD; --pv-soft: #3A2239;
  --dev: #A9B5BB; --dev-soft: #243035;
}
[hidden] { display: none !important; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--ground); color: var(--ink); font: 15px/1.55 var(--body);
       padding-inline: 20px; padding-block: 0 64px; }
.wrap { max-width: 1160px; margin: 0 auto; }
a { color: var(--accent); }
a:focus-visible, button:focus-visible, input:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
code { font: 0.86em/1.4 var(--mono); background: var(--sunken); padding: 0.05em 0.3em; border-radius: 3px;
       overflow-wrap: anywhere; }
.lbl { font: 500 11px/1.3 var(--mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }

header.top { padding-block: 40px 20px; display: grid; gap: 12px; }
header.top .lbl { color: var(--accent); }
h1 { font: 650 clamp(30px, 4.4vw, 44px)/1.1 var(--display); margin: 0; text-wrap: balance; letter-spacing: -0.01em; }
.lead { max-width: 68ch; margin: 0; color: var(--muted); }
.meta { display: flex; flex-wrap: wrap; gap: 6px 20px; font: 13px/1.4 var(--mono); color: var(--muted); }

.crit { display: grid; gap: 14px; margin-block: 8px 28px; }
.crit-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 16px; }
.crit-head h2 { font: 650 22px/1.2 var(--display); margin: 0; color: var(--crit); }
.crit-head p { margin: 0; color: var(--muted); }
.crit-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 14px; }
.crit-card { background: var(--crit-soft); border: 1px solid var(--crit-line); border-radius: 4px; padding: 18px 20px;
             display: grid; gap: 10px; align-content: start; }
.crit-card h3 { font: 600 17px/1.35 var(--body); margin: 0; text-wrap: balance; }
.crit-card dl { margin: 0; display: grid; gap: 8px; }
.crit-card dd { margin: 2px 0 0; }
.crit-card a { font: 500 13px/1 var(--mono); }

.pill { display: inline-block; font: 600 11px/1 var(--mono); letter-spacing: 0.06em; text-transform: uppercase;
        padding: 5px 7px 4px; border-radius: 3px; white-space: nowrap; }
.pill.crit-p { background: var(--crit); color: var(--surface); }
.pill.ok-p { background: var(--ok-soft); color: var(--ok); }
.chip { display: inline-block; font: 500 12px/1.2 var(--body); padding: 4px 8px; border-radius: 3px; white-space: nowrap;
        background: var(--dev-soft); color: var(--dev); }
.chip.o-prof { background: var(--prof-soft); color: var(--prof); }
.chip.o-vaz { background: var(--vaz-soft); color: var(--vaz); }
.chip.o-pv { background: var(--pv-soft); color: var(--pv); }
.chip.o-dev { background: var(--dev-soft); color: var(--dev); }

.status { display: grid; gap: 8px; margin-block: 0 24px; }
.bar { display: flex; height: 12px; border-radius: 2px; overflow: hidden; background: var(--sunken); }
.bar span { display: block; height: 100%; }
.s-toliq { background: var(--ok); } .s-qisman { background: var(--warn); }
.s-yoq { background: var(--crit); } .s-zid { background: var(--ink); }
.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 13px; color: var(--muted);
          font-variant-numeric: tabular-nums; }
.legend i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; vertical-align: -1px; }
.legend b { color: var(--ink); font-weight: 600; }

.controls { position: sticky; top: 0; z-index: 5; background: var(--ground); border-bottom: 1px solid var(--line);
            padding-block: 12px; display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; }
.filters { display: flex; flex-wrap: wrap; gap: 6px; }
.filters button { font: 500 13px/1 var(--body); color: var(--ink); background: var(--surface); border: 1px solid var(--line);
                  border-radius: 3px; padding: 7px 10px; cursor: pointer; font-variant-numeric: tabular-nums; }
.filters button span { color: var(--muted); margin-left: 4px; }
.filters button[aria-pressed="true"] { background: var(--ink); color: var(--ground); border-color: var(--ink); }
.filters button[aria-pressed="true"] span { color: inherit; opacity: 0.75; }
.search { display: flex; align-items: center; gap: 8px; margin-left: auto; }
.search input { font: 14px/1.2 var(--body); color: var(--ink); background: var(--surface); border: 1px solid var(--line);
                border-radius: 3px; padding: 7px 10px; width: min(260px, 60vw); }
.shown { font: 13px/1 var(--mono); color: var(--muted); font-variant-numeric: tabular-nums; }

nav.toc { display: flex; flex-wrap: wrap; gap: 4px 18px; padding-block: 16px 4px; font-size: 13px; }
nav.toc a { text-decoration: none; color: var(--muted); }
nav.toc a:hover { color: var(--accent); }
nav.toc b { color: var(--ink); font-weight: 600; font-variant-numeric: tabular-nums; }

section.sec { margin-top: 36px; }
section.sec > h2 { font: 650 21px/1.25 var(--display); margin: 0 0 4px; text-wrap: balance; }
section.sec > h2 small { font: 500 13px/1 var(--mono); color: var(--muted); margin-left: 8px; }
section.sec > p.note { margin: 0 0 10px; color: var(--muted); max-width: 72ch; }
.list { border-top: 1px solid var(--line); }
.band { display: grid; grid-template-columns: 150px 1fr; gap: 6px 22px; padding-block: 18px;
        border-bottom: 1px solid var(--line); }
.band-id { display: flex; flex-direction: column; align-items: flex-start; gap: 7px; }
.band-id .id { font: 500 14px/1.2 var(--mono); }
.band-title { font: 600 16px/1.4 var(--body); margin: 0 0 10px; text-wrap: balance; }
.triad { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px 22px; margin: 0; }
.triad dt { margin-bottom: 3px; }
.triad dd { margin: 0; overflow-wrap: break-word; }
.triad dd.empty { color: var(--muted); }
.band-foot { display: flex; flex-wrap: wrap; gap: 6px 28px; margin-top: 12px; font-size: 14px; }
.band-foot p { margin: 0; }
.band-foot .src { color: var(--muted); font-size: 13px; }
.band.is-crit { background: var(--crit-soft); padding-inline: 14px; margin-inline: -14px; border-radius: 3px; }
.sec-T .band-title, .sec-T .triad dd { color: var(--muted); }
.sec-R .band { opacity: 0.85; }

@media (max-width: 860px) {
  .band { grid-template-columns: 1fr; }
  .band-id { flex-direction: row; flex-wrap: wrap; align-items: center; }
  .triad { grid-template-columns: 1fr; }
  .search { margin-left: 0; }
}
@media print {
  .controls, nav.toc { display: none; }
  body { background: #FFFFFF; color: #000000; }
  .band { break-inside: avoid; }
}
</style>
"""

_HTML_SCRIPT = """<script>
(function () {
  var bands = Array.prototype.slice.call(document.querySelectorAll('.band'));
  var norm = function (s) { return s.toLowerCase().replace(/[\\u02bb\\u02bc\\u2018\\u2019`']/g, "'"); };
  var texts = bands.map(function (b) { return norm(b.textContent); });
  var chips = Array.prototype.slice.call(document.querySelectorAll('[data-owner-filter]'));
  var q = document.getElementById('q');
  var shown = document.getElementById('shown');
  var owner = 'all';
  function apply() {
    var t = norm(q.value.trim()), n = 0;
    bands.forEach(function (b, i) {
      var ok = (owner === 'all' || b.dataset.owner === owner) && (!t || texts[i].indexOf(t) !== -1);
      b.hidden = !ok; if (ok) n++;
    });
    document.querySelectorAll('section.sec').forEach(function (s) {
      s.hidden = !s.querySelector('.band:not([hidden])');
    });
    shown.textContent = n;
  }
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      owner = c.dataset.ownerFilter;
      chips.forEach(function (x) { x.setAttribute('aria-pressed', String(x === c)); });
      apply();
    });
  });
  q.addEventListener('input', apply);
})();
</script>
"""


def _h(s: str) -> str:
    """Matnni HTML uchun xavfsiz qiladi; `...` → <code>...</code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(s or "", quote=True))


def _anchor(id_: str) -> str:
    return "band-" + (re.sub(r"[^A-Za-z0-9]+", "-", id_).strip("-") or "x")


def _chip(owner: str) -> str:
    return f'<span class="chip o-{_OWNER_CLASS.get(owner, "dev")}">{html.escape(owner)}</span>'


def _band_html(e: dict) -> str:
    def dd(v):
        return '<dd class="empty">—</dd>' if (v or "—").strip() in {"—", ""} else f"<dd>{_h(v)}</dd>"

    pills = ""
    if e["jiddiy"]:
        pills += '<span class="pill crit-p">Jiddiy</span>'
    if e["hal"]:
        pills += '<span class="pill ok-p">Hal qilindi</span>'
    kim = (f"<strong>Hal qilindi:</strong> {_h(e['hal'])}. Mas'ul: {_h(e['kim'])}" if e["hal"] else _h(e["kim"]))
    return (f'<article class="band{" is-crit" if e["jiddiy"] else ""}" id="{_anchor(e["id"])}" '
            f'data-owner="{html.escape(e["owner"], quote=True)}">'
            f'<div class="band-id"><span class="id">{html.escape(e["id"])}</span>{_chip(e["owner"])}{pills}</div>'
            f'<div><h3 class="band-title">{_h(e["band"])}</h3>'
            f'<dl class="triad"><div><dt class="lbl">Spec</dt>{dd(e["spec"])}</div>'
            f'<div><dt class="lbl">Dissertatsiya</dt>{dd(e["diss"])}</div>'
            f'<div><dt class="lbl">CH2 / kod</dt>{dd(e["kod"])}</div></dl>'
            f'<div class="band-foot"><p><span class="lbl">Kim hal qiladi</span> {kim}</p>'
            f'<p class="src"><span class="lbl">Manba</span> {_h(e["manba"])}</p></div></div></article>')


_SEC_NOTES = {
    "T": "Bu bandlar professor yoki Vazira qarorini talab qilmaydi: spec kanonik manba, kodni unga moslash texnik "
         "ish. Ro'yxat to'liq bo'lishi uchun keltirilgan.",
    "R": "Qarori qabul qilingan bandlar — sana va manba bilan. Qayta ochilmaydi.",
}


def render_html(c: dict) -> str:
    by_sec, b, hn = c["by_sec"], c["breakdown"], c["holat_n"]
    entries = c["entries"]
    jiddiy = [e for e in entries if e["jiddiy"]]
    n_open = len(entries) - len(by_sec["R"])
    out = [_HTML_HEAD, '<div class="wrap">']
    out.append('<header class="top"><span class="lbl">Faza 2 · KKT spesifikatsiyasi ↔ dissertatsiya ↔ kod</span>'
               '<h1>KKT himoya qarorlari</h1>'
               f'<p class="lead">Spec, dissertatsiya II bobi va kod bir-biridan farq qiladigan har bir joy — kim hal '
               f'qilishi kerakligi bilan. {n_open} ta ochiq band, {len(by_sec["R"])} ta hal qilingan. '
               '"Kim hal qiladi" — taklif, himoyadan oldin kelishilsin.</p>'
               f'<div class="meta"><span>Yaratilgan: {html.escape(c["generated"])}</span>'
               '<span>make master</span><span>reports/master_qarorlar_royxati.md</span></div></header>')

    out.append('<section class="crit" aria-labelledby="crit-h"><div class="crit-head">'
               '<h2 id="crit-h">Eng og\'ir topilmalar</h2>'
               '<p>Ikkalasida ham dissertatsiya da\'vosi kodda qo\'llab-quvvatlanmaydi. Og\'irligi bir xil.</p></div>'
               '<div class="crit-grid">')
    for e in jiddiy:
        out.append(f'<article class="crit-card"><div><span class="pill crit-p">{html.escape(e["id"])} · Jiddiy'
                   f'</span></div><h3>{_h(e["band"])}</h3><dl>'
                   f'<div><dt class="lbl">Dissertatsiyada</dt><dd>{_h(e["diss"])}</dd></div>'
                   f'<div><dt class="lbl">Kodda</dt><dd>{_h(e["kod"])}</dd></div>'
                   f'<div><dt class="lbl">Kim hal qiladi</dt><dd>{_h(e["kim"])}</dd></div></dl>'
                   f'<a href="#{_anchor(e["id"])}">Ro\'yxatda ko\'rish ↓</a></article>')
    out.append('</div></section>')

    total = c["n_rules"]
    segs = [(conf.TOLIQ, "s-toliq"), (conf.QISMAN, "s-qisman"), (conf.YOQ, "s-yoq"), (conf.ZID, "s-zid")]
    out.append('<section class="status" aria-label="Kodning spec qoidalariga mosligi">'
               f'<span class="lbl">Kodning {total} ta spec qoidasiga mosligi</span><div class="bar">')
    for h, cls in segs:
        if hn[h]:
            out.append(f'<span class="{cls}" style="width:{hn[h] / total * 100:.2f}%" title="{h}: {hn[h]}"></span>')
    out.append('</div><div class="legend">')
    for h, cls in segs:
        extra = (f" ({hn[h] - len(b['tl_ch2'])} mustaqil / {len(b['tl_ch2'])} CH2 orqali aylanma — G8)"
                 if h == conf.TOLIQ else "")
        out.append(f'<span><i class="{cls}"></i>{html.escape(h)} <b>{hn[h]}</b>{html.escape(extra)}</span>')
    out.append('</div></section>')

    owners_all: dict[str, int] = {}
    for e in entries:
        owners_all[e["owner"]] = owners_all.get(e["owner"], 0) + 1
    out.append('<div class="controls"><div class="filters" role="group" aria-label="Kim hal qiladi bo\'yicha filtr">'
               f'<button type="button" id="f-all" data-owner-filter="all" aria-pressed="true">Hammasi'
               f'<span>{len(entries)}</span></button>')
    for i, (k, n) in enumerate(sorted(owners_all.items(), key=lambda x: -x[1])):
        out.append(f'<button type="button" id="f-{i}" data-owner-filter="{html.escape(k, quote=True)}" '
                   f'aria-pressed="false">{html.escape(k)}<span>{n}</span></button>')
    out.append('</div><label class="search" for="q"><span class="lbl">Qidirish</span>'
               '<input id="q" type="search" placeholder="2.58, ergashmoq, PSB…" autocomplete="off"></label>'
               f'<span class="shown"><span id="shown">{len(entries)}</span> ta band</span></div>')

    out.append('<nav class="toc" aria-label="Bo\'limlar">')
    for s in ORDER:
        if by_sec[s]:
            out.append(f'<a href="#sec-{s}">{html.escape(TITLES[s].split(" — ")[0])} <b>{len(by_sec[s])}</b></a>')
    out.append('</nav>')

    for s in ORDER:
        sec = by_sec[s]
        if not sec:
            continue
        out.append(f'<section class="sec sec-{s}" id="sec-{s}"><h2>{html.escape(TITLES[s])}'
                   f'<small>{len(sec)}</small></h2>')
        if s in _SEC_NOTES:
            out.append(f'<p class="note">{html.escape(_SEC_NOTES[s])}</p>')
        out.append('<div class="list">' + "".join(_band_html(e) for e in sec) + '</div></section>')
    out.append('</div>')
    out.append(_HTML_SCRIPT)
    return "\n".join(out)


def run(docx_path: str, out_path: str | None, html_path: str | None = None) -> int:
    if not os.path.exists(docx_path):
        print(f"XATO: {docx_path} topilmadi (shaxsiy fayl, .gitignore'da).", file=sys.stderr)
        return 1
    c = collect(build(docx_path))
    report = render_md(c)
    print(f"[master ro'yxat tayyor — {len(c['entries'])} band, shundan hal qilingan {len(c['by_sec']['R'])}]")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print(f"[yozildi: {out_path}]")
    if html_path:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(render_html(c) + "\n")
        print(f"[html yozildi: {html_path}]")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docx", default=csd.DEFAULT_DOCX)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--no-out", action="store_true")
    ap.add_argument("--html", default=None, help="HTML sahifani shu yo'lga ham yozish (ixtiyoriy)")
    args = ap.parse_args()
    return run(args.docx, None if args.no_out else args.out, args.html)


if __name__ == "__main__":
    raise SystemExit(main())
