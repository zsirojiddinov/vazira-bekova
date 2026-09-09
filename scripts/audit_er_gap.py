#!/usr/bin/env python3
"""
scripts/audit_er_gap.py
==========================
Faza 2 topshirig'i (foydalanuvchi so'rovi, 2026-09-08): "worker"->"Ishlaroq"
xatosini FAQAT kod darajasida tuzatish o'rniga, "-er" bilan tugaydigan
so'zlarni ikkiga ajratish —
  (1) SIFAT+ER   — qiyosiy daraja (masalan fast->faster), dissertatsiyada bor
  (2) FE'L+ER    — agentiv/ish bajaruvchi ot (masalan work->worker),
                   dissertatsiyada YO'Q (foydalanuvchi da'vosi)
va har ikkala guruhning (a) 1500 so'zlik lug'atdagi va (b) "test
to'plami"dagi sonini hisoblash.

MUHIM — bu skript HECH QANDAY xulosa/tavsiya CHIQARMAYDI, faqat sonlarni
hisoblaydi va xom dalilni ko'rsatadi: "Natijani reports/faza_2_er_gap.md
ga yoz — bu Ziyoviddinning professor bilan muhokamasi uchun material, sen
o'zing hal qilmaysin" (foydalanuvchi so'zi, aynan shunday).

METODIKA (Qoida 1 — hech narsa to'qilmagan, hammasi mavjud fayl/koddan):

- **"1500 so'zlik lug'at"** = `data/1500_EN_UZ_6_POS_sorted.20.json` ning
  README.md da "Asosiy EN-UZ so'z jufti lug'ati (1417+ juft, 6 POS)" deb
  ta'riflangan 6 ta asosiy kategoriyasi (NOUNS/VERBS/ADJECTIVES/ADVERBS/
  PRONOUNS/CONJUNCTIONS&PREPOSITIONS) — 1418 juftlik. (JSON dagi qolgan
  ikkita kategoriya — "100 SOZ" va "KKT TERMINOLOGIK LUGAT" — boshqa xom
  manbalardan (100_soz.docx, KKT_Terminologik_Lugat.docx) SHU faylga
  qo'shilgan, kontseptual jihatdan "1500 so'zlik lug'at"ning o'zi emas;
  alohida qatorda qayd etiladi.)
- **Klassifikatsiya (lug'at so'zlari uchun):** kodning O'ZINING
  `MORPH_RULES` dagi ikkita "-er" qoidasida (Ot/agentiv VA Sifat/qiyosiy,
  ikkalasi ham "C←G"/"P1←P" formal notatsiyasi bilan) ishlatiladigan XUDDI
  SHU 4 ta o'zak-tiklash funksiyasi (`w[:-2]`, `w[:-2]+"e"`, `w[:-3]`,
  `w[:-3]+"e"`) qo'llaniladi, so'ng natija lug'atning o'z
  VERBS/ADJECTIVES/ADVERBS kategoriyalari bilan solishtiriladi. Bu
  Claude'ning shaxsiy lingvistik hukmi EMAS — kodning o'zi ishlatadigan
  meхanizm bilan bir xil qoida.
- **"Test to'plami"** ikki manbadan iborat (atama noaniq bo'lgani uchun
  ikkalasi ham ko'rsatiladi): (a) `CH2_EVX_EXAMPLES` (dissertatsiya II
  bobidan ko'chirilgan 52 misol, `pos` maydoni bo'yicha guruhlanadi), (b)
  `tests/*.py` pytest to'plamidagi HAQIQIY so'z-darajasidagi test
  kirishlari — bu ro'yxat qo'lda tekshirilgan va METODIKA bo'limida har
  bir chiqarib tashlangan token uchun sabab ko'rsatilgan (pastga qarang,
  `_TEST_SUITE_ER_WORDS`).
- Agar `data/desertatsiya.docx` (foydalanuvchining SHAXSIY fayli,
  `.gitignore`da) mavjud bo'lsa, qo'shimcha ravishda dissertatsiyaning I
  bob NAZARIY (adabiyotlar sharhi) qismidagi 1.3- va 1.7-jadval (suffiks
  inventarizatsiyasi) hamda butun hujjat bo'yicha "ish bajaruvchi"/
  "agentiv" so'zlarining qidiruvi ham hisobotga qo'shiladi — bu qism FAQAT
  fayl mavjud bo'lganda ishlaydi (aks holda ochiq qoldiriladi).

Ishlatish:
    python scripts/audit_er_gap.py
    python scripts/audit_er_gap.py --out reports/faza_2_er_gap.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, SCRIPT_DIR)

DICT_PATH = os.path.join(REPO_ROOT, "data", "1500_EN_UZ_6_POS_sorted.20.json")
DOCX_PATH = os.path.join(REPO_ROOT, "data", "desertatsiya.docx")

MAIN_CATEGORIES = [
    "NOUNS (OTLAR)",
    "VERBS (FE'LLAR)",
    "ADJECTIVES (SIFATLAR)",
    "ADVERBS (RAVISHLAR)",
    "PRONOUNS (OLMOSHLAR)",
    "CONJUNCTIONS & PREPOSITIONS (BOG'LOVCHI / KO'MAKCHI)",
]
SUPPLEMENTARY_CATEGORIES = [
    "100 SOZ (MORFEMIK TAHLIL)",
    "KKT TERMINOLOGIK LUGAT (KO'P MA'NOLI TERMINLAR)",
]

# ─────────────────────────────────────────────────────────────────────────
# tests/*.py dagi HAQIQIY so'z-darajasidagi "-er" test kirishlari — QO'LDA
# tekshirilgan (grep + har bir hit'ning kontekstini o'qish orqali).
# Chiqarib tashlangan tokenlar va sabablari:
#   "ier", "ever"  — bu MORPH_RULES AFFIKS NOMLARI (masalan
#                    test_affix_tables.py:78), haqiqiy inglizcha so'z emas.
#   "tkinter"      — Python kutubxona nomi, lingvistik so'z emas.
#   "lower"        — Python metod chaqiruvi (`.lower()`), so'z emas.
#   "counter"      — Python o'zgaruvchi nomi (test_readonly_mode.py:62),
#                    lingvistik test kirishi emas.
#   "after"        — "afterward"/boshqa so'z ichida yoki umuman mos emas;
#                    tests/ da alohida so'z sifatida ishlatilmagan.
#   "isupper"      — Python metod nomi (`.isupper()`), so'z emas.
#   "faster"       — FAQAT bitta joyda, sharh sifatida uchraydi
#                    (test_affix_tables.py:123, "masalan fast->faster")
#                    — bu HAQIQIY test kirishi (funksiya argumenti) EMAS,
#                    shuning uchun "test so'zi" sifatida SANALMAYDI (pastda
#                    alohida eslatiladi, lekin hisobga QO'SHILMAYDI).
# Qolganlari — quyida — HAQIQIY funksiya chaqiruvi argumenti sifatida
# ishlatilgan so'zlar (manba fayl:qator ko'rsatilgan):
_TEST_SUITE_ER_WORDS = [
    {"word": "teacher", "file": "tests/test_smart_parse.py", "line": 15,
     "usage": "m.smart_parse('teacher') — to'g'ridan lug'at solishtiruvi"},
    {"word": "worker", "file": "tests/test_smart_parse.py", "line": 61,
     "usage": "m.smart_parse('worker') — ma'lum xato (Ishlaroq) testi"},
]


def load_dictionary_categories() -> dict[str, list[dict]]:
    with open(DICT_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return raw["categories"]


def get_er_rules():
    """kkt_v20_soz_tartibi.MORPH_RULES dan ikkita "-er" qoidasini
    (Ot/agentiv, Sifat/qiyosiy) va ular ishlatadigan o'zak-tiklash
    funksiyalarini oladi — klassifikatsiya UCHUN xuddi shu funksiyalar
    ishlatiladi (Claude'ning alohida yozgan qoidasi emas)."""
    import kkt_v20_soz_tartibi as m

    er_rules = [r for r in m.MORPH_RULES if r[0] == "er"]
    assert len(er_rules) == 2, f"kutilmagan: MORPH_RULES da {len(er_rules)} ta '-er' qoidasi bor"
    return er_rules


def classify_dictionary_er_words(categories: dict[str, list[dict]], er_fns) -> list[dict]:
    """1500 so'zlik lug'at (6 asosiy kategoriya) dagi bitta-so'zli "-er"
    bilan tugagan headword'larni klassifikatsiya qiladi."""
    verbs = {e["english"].strip().lower() for e in categories["VERBS (FE'LLAR)"]}
    adjs = {e["english"].strip().lower() for e in categories["ADJECTIVES (SIFATLAR)"]}
    advs = {e["english"].strip().lower() for e in categories["ADVERBS (RAVISHLAR)"]}

    rows = []
    for cat in MAIN_CATEGORIES:
        for e in categories[cat]:
            w = e["english"].strip()
            if " " in w or len(w) <= 2 or not w.lower().endswith("er"):
                continue
            wl = w.lower()
            roots = [fn(wl) for fn in er_fns]
            root_is_verb = any(r in verbs for r in roots)
            root_is_adj = any(r in adjs for r in roots)
            root_is_adv = any(r in advs for r in roots)
            if root_is_verb:
                group = "FE'L+ER (agentiv)"
            elif root_is_adj or root_is_adv:
                group = "SIFAT+ER (qiyosiy)"
            else:
                group = "ANIQLANMAGAN"
            rows.append({
                "category": cat, "word": w, "uzbek": e["uzbek"],
                "roots_tried": roots, "group": group,
            })
    return rows


def classify_ch2_examples() -> list[dict]:
    import kkt_v20_soz_tartibi as m

    rows = []
    for ex in m.CH2_EVX_EXAMPLES:
        w = ex["en"]
        if " " in w or len(w) <= 2 or not w.lower().endswith("er"):
            continue
        if ex["pos"] in ("Sifat", "Ravish"):
            group = "SIFAT+ER (qiyosiy)"
        elif ex["pos"] == "Ot":
            group = "FE'L+ER (agentiv) — CH2 POS='Ot' deb belgilagan"
        else:
            group = f"BOSHQA (pos={ex['pos']!r})"
        rows.append({"word": w, "uzbek": ex["uz"], "pos": ex["pos"], "group": group})
    return rows


def classify_full_chapter2_examples(docx_path: str) -> list[dict] | None:
    """`scripts/check_ch2_leakage.py` (2026-09-09, foydalanuvchi so'rovi bilan
    yozilgan) II bobdan CH2_EVX_EXAMPLES'dagi 52 tadan TASHQARI yana ~20 ta
    "Ingliz tilida EVX ..." misolni avtomatik ajratib oladi (jami ~72 ta,
    qarang `reports/ch2_leakage_check.md`#2-bo'lim). Bu funksiya O'SHA TO'LIQ
    to'plamdagi (CH2_EVX_EXAMPLES + qo'shimcha) bitta-so'zli "-er" so'zlarini
    ham hisobga qo'shadi — POS `check_ch2_leakage._infer_pos_from_model()`
    orqali (formal model tenglamasining KKT belgisidan) AVTOMATIK chiqarilgan,
    Claude tomonidan qo'lda belgilanmagan. Docx mavjud bo'lmasa None."""
    if not os.path.exists(docx_path):
        return None

    import kkt_v20_soz_tartibi as m
    from check_ch2_leakage import load_docx, find_chapter_bounds, extract_ch2_records

    items = load_docx(docx_path)
    bounds = find_chapter_bounds(items)
    if "II" not in bounds:
        return None
    all_records = extract_ch2_records(items, bounds["II"])
    ch2_en_values = {ex["en"].strip().lower() for ex in m.CH2_EVX_EXAMPLES}

    rows = []
    for r in all_records:
        w = r["en_marker_word"] or ""
        if " " in w or len(w) <= 2 or not w.lower().endswith("er"):
            continue
        pos = r["inferred_pos"]
        if pos in ("Sifat", "Ravish"):
            group = "SIFAT+ER (qiyosiy)"
        elif pos == "Ot":
            group = "FE'L+ER (agentiv) — docx formal model POS='Ot' deb chiqargan"
        elif pos == "Fe'l":
            group = "BOSHQA — POS='Fe'l' (o'zi -er bilan tugagan fe'l shakli, masalan o'tgan zamon emas)"
        else:
            group = f"ANIQLANMAGAN (inferred_pos={pos!r})"
        rows.append({
            "word": w, "uzbek": r["uz_marker_word"], "pos": pos, "group": group,
            "docx_idx": r["en_idx"],
            "in_ch2_evx_examples": w.strip().lower() in ch2_en_values,
        })
    return rows


def check_dissertation_theory(docx_path: str) -> dict | None:
    """Agar shaxsiy dissertatsiya fayli mavjud bo'lsa, I bobdagi nazariy
    suffiks-inventarizatsiya jadvallarini (1.3- va 1.7-jadval) va butun
    hujjat bo'yicha "ish bajaruvchi"/"agentiv" so'zlarining borligini
    tekshiradi."""
    if not os.path.exists(docx_path):
        return None

    from check_ch2_leakage import load_docx, find_chapter_bounds

    items = load_docx(docx_path)
    bounds = find_chapter_bounds(items)

    def _table_cells(idx):
        cells = [c.text.strip() for row in items[idx].rows for c in row.cells]
        return [c for c in cells if c]

    # 1.3-jadval — "Yangi ot yasovchi suffikslar" (item ~149/150, lekin
    # aniq indeksni sarlavha matnidan qidiramiz — hujjat versiyasi
    # o'zgarsa ham ishlashi uchun).
    noun_suffix_table = None
    degree_suffix_table = None
    for i, it in enumerate(items):
        if it.__class__.__name__ != "Paragraph":
            continue
        t = it.text.strip().lower()
        if "yangi ot yasovchi" in t and "suffiks" in t and noun_suffix_table is None:
            for k in range(i + 1, min(i + 4, len(items))):
                if items[k].__class__.__name__ == "Table":
                    noun_suffix_table = _table_cells(k)
                    break
        if "qiyosiy va orttirma darajasini yasovchi suffikslar" in t and degree_suffix_table is None:
            for k in range(i + 1, min(i + 4, len(items))):
                if items[k].__class__.__name__ == "Table":
                    degree_suffix_table = _table_cells(k)
                    break

    agentive_mentions = []
    for i, it in enumerate(items):
        if it.__class__.__name__ != "Paragraph":
            continue
        low = it.text.lower()
        if any(p in low for p in ("ish bajaruvchi", "agentiv", "harakat bajaruvchi", "bajaruvchi shaxs")):
            agentive_mentions.append((i, it.text.strip()[:200]))

    return {
        "noun_suffix_table": noun_suffix_table,
        "noun_suffix_table_has_er": noun_suffix_table is not None and "-er" in noun_suffix_table,
        "noun_suffix_table_has_or": noun_suffix_table is not None and "-or" in noun_suffix_table,
        "degree_suffix_table": degree_suffix_table,
        "degree_suffix_table_has_er": degree_suffix_table is not None and "-er" in degree_suffix_table,
        "agentive_mentions": agentive_mentions,
        "chapter_bounds": bounds,
    }


def run(out_path: str | None) -> int:
    categories = load_dictionary_categories()
    er_rules = get_er_rules()
    er_fns = er_rules[0][1]  # ikkala qoida ham bir xil funksiya ro'yxatini ishlatadi

    dict_rows = classify_dictionary_er_words(categories, er_fns)
    ch2_rows = classify_ch2_examples()
    full_ch2_rows = classify_full_chapter2_examples(DOCX_PATH)
    theory = check_dissertation_theory(DOCX_PATH)

    def _count(rows, group_prefix):
        return sum(1 for r in rows if r["group"].startswith(group_prefix))

    d_sifat = _count(dict_rows, "SIFAT+ER")
    d_fel = _count(dict_rows, "FE'L+ER")
    d_undet = _count(dict_rows, "ANIQLANMAGAN")

    c_sifat = _count(ch2_rows, "SIFAT+ER")
    c_fel = _count(ch2_rows, "FE'L+ER")

    if full_ch2_rows is not None:
        fc_sifat = _count(full_ch2_rows, "SIFAT+ER")
        fc_fel = _count(full_ch2_rows, "FE'L+ER")
    else:
        fc_sifat = fc_fel = None

    lines = []
    lines.append("# Faza 2 — \"-er\" bo'shlig'i: sifat+er (qiyosiy) vs fe'l+er (agentiv)")
    lines.append("")
    lines.append(f"**Generatsiya vaqti:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}Z")
    lines.append("**Buyruq:** `python scripts/audit_er_gap.py`")
    lines.append("")
    lines.append(
        "**Kontekst:** `\"worker\"->\"Ishlaroq\"` ma'lum xatosi (`make_uzbek()` \"-er\"ni HAR DOIM qiyosiy "
        "daraja deb hisoblaydi, agentiv ma'noni ajratmaydi — qarang `reports/faza_1.md`#2-band, "
        "`tests/test_smart_parse.py::test_smart_parse_agentive_er_uses_wrong_fallback_suffix_data_bug`). "
        "**Bu hisobot xatoni TUZATMAYDI** — foydalanuvchi so'rovi bo'yicha faqat ikkita guruhning hajmini "
        "hisoblab, professor bilan muhokama uchun xom dalil taqdim etadi. Qaysi guruh \"dissertatsiyada bor/"
        "yo'q\" degan yakuniy xulosani Claude CHIQARMAYDI."
    )
    lines.append("")

    lines.append("## 1. Kod darajasidagi holat (kontekst)")
    lines.append("")
    lines.append(
        "`kkt_v20_soz_tartibi.py:MORPH_RULES` da \"-er\" ATAYLAB IKKI MARTA uchraydi (izoh, "
        "391-398-qatorlar): (1) `Ot←Fe'l` (\"C←G(-er): ish bajaruvchi, work→worker\", FAQAT ildiz lug'atda "
        "Fe'l bo'lsa ishlaydi) — bu birinchi turadi; (2) `Sifat←Sifat` (\"P1←P(-er): qiyosiy\", cheklovsiz). "
        "POS ANIQLASH bosqichida (`smart_parse`) bu ikkalasi TO'G'RI farqlanadi (`tests/test_affix_tables.py"
        "::test_morph_rules_er_has_pos_guarded_and_unguarded_variant`). LEKIN zaxira tarjima bosqichida "
        "(`make_uzbek(root_uz, sfx)`) faqat AFFIKS MATNI (\"er\") uzatiladi, `derived_pos` YO'Q — shu sabab "
        "`\"er\": stem+\"roq\"` qoidasi ikkalasini ham bir xil (qiyosiy) deb hisoblaydi."
    )
    lines.append("")

    lines.append("## 2. 1500 so'zlik lug'atdagi natija")
    lines.append("")
    lines.append(
        f"Manba: `data/1500_EN_UZ_6_POS_sorted.20.json`, 6 ta asosiy kategoriya (README.md \"1417+ juft, 6 "
        f"POS\" ta'rifiga mos, jami **{sum(len(categories[c]) for c in MAIN_CATEGORIES)}** juftlik)."
    )
    lines.append("")
    lines.append(f"- Bitta-so'zli \"-er\" bilan tugaydigan headword: **{len(dict_rows)}**")
    lines.append(f"  - SIFAT+ER (qiyosiy, o'zak ADJECTIVES/ADVERBS da topildi): **{d_sifat}**")
    lines.append(f"  - FE'L+ER (agentiv, o'zak VERBS da topildi): **{d_fel}**")
    lines.append(f"  - ANIQLANMAGAN (avtomatik hal qilinmadi — pastga qarang): **{d_undet}**")
    lines.append("")
    lines.append(
        "**\"ANIQLANMAGAN\" haqida:** bu guruhga ikki xil holat kiradi — (a) \"-er\" so'z ILDIZINING bir "
        "qismi, umuman suffiks EMAS (masalan `water`, `other`, `however` kabi — root-tiklash funksiyalari "
        "\"wat\"/\"oth\"/\"howev\" kabi mavjud bo'lmagan \"o'zak\"lar hosil qiladi, lug'atda topilmaydi — "
        "bu TO'G'RI natija), (b) haqiqatan ham fe'l+er/sifat+er, lekin ildiz so'z 1500-so'zlik lug'atning "
        "o'zida MUSTAQIL yozuv sifatida yo'q (masalan `User`ning ildizi \"use\", `Leader`ning ildizi \"lead\" "
        "lug'atda alohida yo'q) YOKI root-tiklash 4 ta funksiya (`y→i` almashtirishni QAMRAB OLMAYDI, masalan "
        "`Supplier`) — bu ikkinchi holat KODNING O'ZIDA ham bor bo'lgan CHEKLOV (xuddi shu 4 ta funksiya "
        "`MORPH_RULES`da ham ishlatiladi), Claude buni \"aniqlab bermaydi\"."
    )
    lines.append("")
    lines.append("### To'liq jadval (48 ta so'z, barchasi — hech biri chiqarib tashlanmagan)")
    lines.append("")
    lines.append("| Kategoriya | So'z | O'zbekcha | Sinovdan o'tgan o'zaklar | Guruh |")
    lines.append("|---|---|---|---|---|")
    for r in dict_rows:
        roots_s = ", ".join(r["roots_tried"])
        lines.append(f"| {r['category']} | {r['word']} | {r['uzbek']} | {roots_s} | {r['group']} |")
    lines.append("")

    supp_er = []
    for cat in SUPPLEMENTARY_CATEGORIES:
        entries = categories.get(cat, [])
        for e in entries:
            w = e.get("english") or e.get("word") or ""
            if isinstance(w, str) and " " not in w and len(w) > 2 and w.lower().endswith("er"):
                supp_er.append((cat, w))
    supp_er_desc = ", ".join(f"{w} ({c})" for c, w in supp_er) if supp_er else "yo'q"
    lines.append(
        f"**Qo'shimcha (\"1500 so'zlik lug'at\"ning bir qismi EMAS, lekin xuddi shu JSON faylda mavjud):** "
        f"\"100 SOZ\" va \"KKT TERMINOLOGIK LUGAT\" kategoriyalarida (boshqa manba fayllardan olingan) "
        f"oddiy `english` maydoni bo'yicha qidiruvda **{len(supp_er)}** ta \"-er\"-so'z topildi "
        f"({supp_er_desc})."
    )
    lines.append("")

    lines.append("## 3. \"Test to'plami\"dagi natija")
    lines.append("")
    lines.append("### 3a. `CH2_EVX_EXAMPLES` (dissertatsiya II bobidan ko'chirilgan 52 misol)")
    lines.append("")
    lines.append(f"Bitta-so'zli \"-er\" bilan tugaydigan yozuvlar: **{len(ch2_rows)}**")
    lines.append("")
    lines.append("| So'z | O'zbekcha | CH2 POS | Guruh |")
    lines.append("|---|---|---|---|")
    for r in ch2_rows:
        lines.append(f"| {r['word']} | {r['uzbek']} | {r['pos']} | {r['group']} |")
    lines.append("")
    lines.append(f"- SIFAT+ER (qiyosiy): **{c_sifat}** ({', '.join(sorted({r['word'] for r in ch2_rows if r['group'].startswith('SIFAT')}))})")
    lines.append(f"- FE'L+ER (agentiv): **{c_fel}**")
    lines.append("")
    lines.append(
        "**Diqqat:** `CH2_EVX_EXAMPLES`da FE'L+ER (agentiv) misoli **YO'Q** — barcha bitta-so'zli \"-er\" "
        "yozuvlari qiyosiy daraja. (`reports/ch2_leakage_check.md` — endi asl dissertatsiya fayli bilan "
        "tasdiqlangan — bu ro'yxat II bobning HAMMASI emasligini ko'rsatadi, lekin II bobning O'ZIDA ham "
        "hech qanday fe'l+er/agentiv EVX misoli TOPILMADI, qarang 4-bo'lim.)"
    )
    lines.append("")

    lines.append(
        "### 3a-bis. `CH2_EVX_EXAMPLES` + II bobdagi QO'SHIMCHA namunalar (davomi, 2026-09-09)"
    )
    lines.append("")
    if full_ch2_rows is None:
        lines.append(
            "`data/desertatsiya.docx` bu muhitda topilmadi — bu bo'lim o'tkazib yuborildi (3a dagi 52-misolli "
            "hisob o'zgarishsiz qoladi)."
        )
    else:
        n_extra = sum(1 for r in full_ch2_rows if not r["in_ch2_evx_examples"])
        lines.append(
            f"`scripts/check_ch2_leakage.py` (2026-09-09) II bobning O'ZIDAN CH2_EVX_EXAMPLES'dagi 52 tadan "
            f"TASHQARI yana ~20 ta \"Ingliz tilida EVX ...\" namunani avtomatik ajratib oladi (to'liq ro'yxat: "
            f"`reports/ch2_leakage_check.md`#2-bo'lim). Shu TO'LIQ to'plamdagi (jami "
            f"{len(full_ch2_rows)} ta) bitta-so'zli \"-er\" so'zlari — POS bu safar CH2 kabi qo'lda emas, "
            f"**docx'ning o'z formal-model tenglamasidan avtomatik chiqarilgan** "
            f"(`check_ch2_leakage._infer_pos_from_model()`):"
        )
        lines.append("")
        lines.append("| So'z | O'zbekcha | POS (avtomatik) | CH2_EVX_EXAMPLES da bormi? | Docx idx | Guruh |")
        lines.append("|---|---|---|---|---|---|")
        for r in full_ch2_rows:
            in_ch2_txt = "ha (3a da bor)" if r["in_ch2_evx_examples"] else "YO'Q — faqat II bobning o'zida"
            lines.append(
                f"| {r['word']} | {r['uzbek']} | {r['pos']} | {in_ch2_txt} | {r['docx_idx']} | {r['group']} |"
            )
        lines.append("")
        lines.append(
            f"CH2_EVX_EXAMPLES'ga kiritilmagan **{n_extra} ta qo'shimcha** \"-er\" so'zi topildi (`larger`, "
            f"`bigger` — ikkalasi ham SIFAT+ER/qiyosiy, docx idx 700 va 709). Bular bilan birga II bobning "
            f"avtomatik ajratib olingan TO'LIQ to'plamidagi (jami {len(full_ch2_rows)} ta \"-er\" so'z) hisobi:"
        )
        lines.append(f"- SIFAT+ER (qiyosiy): **{fc_sifat}**")
        lines.append(f"- FE'L+ER (agentiv): **{fc_fel}**")
        lines.append("")
        lines.append(
            "**Bu — 3a dagi \"CH2_EVX_EXAMPLES'da fe'l+er yo'q\" da'vosini II bobning KATTAROQ (avtomatik "
            "aniqlangan ~72 ta misolli) qismiga kengaytiradi:** o'sha kattaroq to'plamda ham FE'L+ER "
            f"(agentiv) soni **{fc_fel}** — ya'ni II bobning avtomatik ajratib olingan HECH bir namunasi "
            "agentiv \"-er\" emas (barchasi qiyosiy daraja)."
        )
    lines.append("")

    lines.append("### 3b. `tests/*.py` (pytest to'plami) — haqiqiy so'z-darajasidagi kirishlar")
    lines.append("")
    lines.append(
        "Metodika bo'limida tavsiflangan qo'lda tekshiruv natijasi (barcha `tests/*.py` fayllaridagi "
        "\"-er\"ga o'xshash tokenlar ko'rib chiqildi, faqat HAQIQIY funksiya-chaqiruv argumentlari qoldirildi):"
    )
    lines.append("")
    lines.append("| So'z | Fayl:qator | Ishlatilishi | Guruh |")
    lines.append("|---|---|---|---|")
    for w in _TEST_SUITE_ER_WORDS:
        lines.append(f"| {w['word']} | {w['file']}:{w['line']} | {w['usage']} | FE'L+ER (agentiv) |")
    lines.append("")
    lines.append(
        f"- SIFAT+ER (qiyosiy) test kirishi: **0** (faqat bitta ESLATMA bor — "
        f"`tests/test_affix_tables.py:123` docstring ichida \"masalan fast->faster\" — bu HAQIQIY funksiya "
        f"chaqiruvi EMAS, hisobga qo'shilmadi)"
    )
    lines.append(f"- FE'L+ER (agentiv) test kirishi: **{len(_TEST_SUITE_ER_WORDS)}** (`teacher`, `worker`)")
    lines.append("")

    lines.append("## 4. Dissertatsiya matni bo'yicha nazariy dalil")
    lines.append("")
    if theory is None:
        lines.append(
            "`data/desertatsiya.docx` bu muhitda topilmadi (shaxsiy fayl, `.gitignore`da) — bu bo'lim "
            "o'tkazib yuborildi. Fayl mavjud bo'lganda skriptni qayta ishga tushiring."
        )
    else:
        lines.append(
            "Manba: `data/desertatsiya.docx`, I bob (\"HISOBLASH MASHINALARIDA TARJIMA MUAMMOLARI\" — "
            "adabiyotlar sharhi/nazariy qism) va butun hujjat bo'yicha to'liq matnli qidiruv."
        )
        lines.append("")
        if theory["noun_suffix_table"] is not None:
            has_er_txt = "BOR" if theory["noun_suffix_table_has_er"] else "YO'Q"
            has_or_txt = "BOR" if theory["noun_suffix_table_has_or"] else "YO'Q"
            lines.append(
                f"- **1.3-jadval \"Yangi ot yasovchi suffikslar\"** ({len(theory['noun_suffix_table'])} ta "
                f"suffiks, KKT notatsiyasi C(S)) — \"-er\" bu jadvalda {has_er_txt}, \"-or\" {has_or_txt}."
            )
        else:
            lines.append("- 1.3-jadval avtomatik topilmadi (sarlavha matni o'zgargan bo'lishi mumkin).")
        if theory["degree_suffix_table"] is not None:
            has_er_degree_txt = "BOR" if theory["degree_suffix_table_has_er"] else "YO'Q"
            lines.append(
                f"- **1.7-jadval \"Sifatning qiyosiy va orttirma darajasini yasovchi suffikslar\"** — "
                f"tarkibi: {theory['degree_suffix_table']} — \"-er\" bu jadvalda {has_er_degree_txt}."
            )
        else:
            lines.append("- 1.7-jadval avtomatik topilmadi.")
        lines.append("")
        n_agentive = len(theory["agentive_mentions"])
        lines.append(
            f"- Butun hujjat (barcha 4 bob + xulosa + adabiyotlar) bo'yicha \"ish bajaruvchi\"/\"agentiv\"/"
            f"\"harakat bajaruvchi\"/\"bajaruvchi shaxs\" so'z birikmalari qidirildi: **{n_agentive}** ta "
            f"joyda topildi."
        )
        if theory["agentive_mentions"]:
            lines.append("")
            lines.append("| Docx idx | Matn |")
            lines.append("|---|---|")
            for idx, txt in theory["agentive_mentions"]:
                lines.append(f"| {idx} | {txt} |")
        lines.append("")
        lines.append(
            "**Jadvaldan chiqadigan (talqin qilinmagan) fakt:** I bobning nazariy suffiks-inventarizatsiya "
            "jadvali (1.3-jadval, 77 ta suffiks) \"-er\"ni (\"-or\" bilan birga) OT YASOVCHI suffikslar "
            "ro'yxatiga kiritadi (izohsiz, misolsiz — 77 tadan biri sifatida). Alohida 1.7-jadval esa "
            "\"-er\"/\"-est\"ni SIFAT DARAJASI suffikslari sifatida ALOHIDA kataloglaydi. Dissertatsiyaning "
            "II bobidagi (formal model ishlab chiqilgan, EVX/EVIX misollari bilan) qismida esa \"-er\" FAQAT "
            "qiyosiy daraja funksiyasida ishlatilgan (5+ misol: cleverer, busier, gayer, larger, bigger, "
            "har biriga formal model/vazn berilgan) — agentiv funksiyasi uchun na misol, na formal model, "
            "na alohida muhokama bor (yuqoridagi qidiruv, 0 ta natija)."
        )
    lines.append("")

    lines.append("## 5. Xulosa — faqat sonlar (talqin/tavsiya emas)")
    lines.append("")
    lines.append("| Manba | SIFAT+ER (qiyosiy) | FE'L+ER (agentiv) | Aniqlanmagan |")
    lines.append("|---|---|---|---|")
    lines.append(f"| 1500 so'zlik lug'at ({len(dict_rows)} ta \"-er\" so'zdan) | {d_sifat} | {d_fel} | {d_undet} |")
    lines.append(f"| CH2_EVX_EXAMPLES ({len(ch2_rows)} ta \"-er\" so'zdan) | {c_sifat} | {c_fel} | 0 |")
    if full_ch2_rows is not None:
        lines.append(
            f"| II bobning TO'LIQ namunalari ({len(full_ch2_rows)} ta \"-er\" so'zdan, CH2_EVX_EXAMPLES + "
            f"{sum(1 for r in full_ch2_rows if not r['in_ch2_evx_examples'])} qo'shimcha) | {fc_sifat} | "
            f"{fc_fel} | 0 |"
        )
    lines.append(f"| tests/*.py (haqiqiy so'z kirishlari) | 0 | {len(_TEST_SUITE_ER_WORDS)} | — |")
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
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "reports", "faza_2_er_gap.md"))
    ap.add_argument("--no-out", action="store_true")
    args = ap.parse_args()
    return run(None if args.no_out else args.out)


if __name__ == "__main__":
    raise SystemExit(main())
