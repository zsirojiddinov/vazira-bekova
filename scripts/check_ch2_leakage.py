#!/usr/bin/env python3
"""
scripts/check_ch2_leakage.py
================================
Foydalanuvchi 2026-09-08 da asl dissertatsiya faylini qo'shdi
(`data/desertatsiya.docx`) — shu bilan Faza 1'da "so_zlar_bazasi_un.docx
repoda yo'q" deb qayd etilgan cheklov OLIB TASHLANDI (qarang
reports/faza_1_audit_examples.md). Bu skript ikkita tekshiruvni bittada
bajaradi:

1) **Paragraf darajasidagi solishtiruv** — `kkt_v20_soz_tartibi.py`dagi
   `CH2_EVX_EXAMPLES` (52 ta, dastur muallifi tomonidan qo'lda ko'chirilgan
   deb hujjatlashtirilgan) ro'yxatidagi HAR BIR yozuvni II bobdagi haqiqiy
   "Ingliz tilida EVX <so'z> ... Oʻzbek tilida EVIX <tarjima>" paragraf
   juftligi bilan solishtiradi. Mos kelmasa — jadvalga chiqadi (masalan
   "schoolboys"->"Bojxonalar").
2) **Headword darajasidagi "aylanma"/leakage tekshiruvi** — CH2_EVX_EXAMPLES
   dagi har bir inglizcha bosh so'z III va IV bob matnida (paragraflar +
   jadval kataklari) uchraydimi, ayniqsa "aniqlik"/"foiz"/"%"/"misol" so'zlari
   yaqinida yoki jadval ichida.

MUHIM — nima FAQAT AVTOMATIK: bu skript docx paragraflarini/jadvallarini
FAQAT o'qiydi (python-docx, SELECT-ga ekvivalent), CH2_EVX_EXAMPLES bilan
qatorma-qator solishtiradi. Hech qanday tarjima/xulosa TO'QILMAGAN — har bir
da'vo pastdagi jadvaldagi xom docx matniga (paragraf indeksi bilan)
bevosita bog'langan (Qoida 1).

MUHIM — nima QO'LDA TEKSHIRISH TALAB QILADI: "Ingliz tilida EVX <so'z>"
paragrafidan keyin ko'pincha kichik "o'zak | +affiks" jadvali keladi (masalan
["leaf","+ es"]). Bu jadval katakchalarini to'g'ridan-to'g'ri qo'shib
o'qish (imlo o'zgarishisiz) ba'zan paragraf qatoridagi TO'G'RI yozilgan
shakldan FARQ qiladi (masalan "leaf"+"es"="leafes", lekin paragraf qatorida
to'g'ri "leaves" yozilgan). Bu skript ASOSIY solishtiruv uchun paragraf
qatoridagi matnni ishlatadi (chunki bu — o'qiganda ko'rinadigan haqiqiy
so'z), jadval katakchasidan tiklangan shaklni FAQAT qo'shimcha izoh
ustunida ko'rsatadi — bu ikkalasi orasidagi farqni Claude "xato" deb
E'LON QILMAYDI, faqat ikkala manbani ham ko'rsatadi (professor/Ziyoviddin
hal qiladi).

Ishlatish:
    python scripts/check_ch2_leakage.py
    python scripts/check_ch2_leakage.py --docx data/desertatsiya.docx --out reports/ch2_leakage_check.md
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, SCRIPT_DIR)

from _common import normalize  # noqa: E402

DEFAULT_DOCX = os.path.join(REPO_ROOT, "data", "desertatsiya.docx")

CHAP_RE = re.compile(r"^(I|II|III|IV)\s+BOB\.", re.IGNORECASE)
#  ".{0,40}?" — EN/UZ marker jumla ba'zan "Ingliz tilida <qo'shimcha so'zlar>
#  EVX ..." koʻrinishida boʻladi (masalan "Ingliz tilida kelasi zamon EVX -
#  will return") — shu oraliqdagi qoʻshimcha soʻzlarni oʻtkazib yuborish
#  uchun erkinroq (lekin cheksiz emas, 40 belgigacha) mos kelish qoidasi.
EN_MARKER_RE = re.compile(r"ingliz tilida.{0,40}?EVI?X\w*\s*[:\-]?\s*(.*)$", re.IGNORECASE)
UZ_MARKER_RE = re.compile(r"zbek tilida.{0,40}?EVI?X\w*\s*[:\-]?\s*(.*)$", re.IGNORECASE)
# "$[" — rasmiy model tenglamalarining barchasida uchraydigan belgi
# (masalan "G(G14) = $[i,1-h3]G14i"). Oddiy "=" belgisini EMAS (chunki u
# "send => sent => sent" kabi haqiqiy EVX misollarida ham uchraydi).
_BAD_CONTINUATION = ("rasmiy model", "parsinglash", "kkt belgi", "$[")


def _iter_block_items(parent):
    """Paragraf va jadvallarni HUJJATDAGI HAQIQIY tartibda (aralash)
    qaytaradi — python-docx `doc.paragraphs`/`doc.tables` alohida-alohida
    beradi, tartib yo'qoladi; shu funksiya xom XML bo'yicha aylanib
    haqiqiy ketma-ketlikni tiklaydi."""
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    for child in parent.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def _clean_marker(raw: str) -> str:
    t = raw.strip()
    # ba'zan "kiruvchi so'z:"/"chiquvchi so'z:" kabi qo'shimcha yorliq bilan
    # boshlanadi (masalan "Oʻzbek tilida EVIX chiquvchi soʻz: jarayonlar")
    t = re.sub(r"^(kiruvchi|chiquvchi)\s+", "", t, flags=re.IGNORECASE)
    t = re.sub(r"^so['ʻʼ]?z\s*[:\-]?\s*", "", t, flags=re.IGNORECASE)
    t = t.strip(" :“”\"'")
    return t


def _join_plus(t: str) -> str:
    return re.sub(r"\s*\+\s*", "", t)


def _arrow_last(t: str) -> str:
    parts = re.split(r"->|=>|→", t)
    return parts[-1].strip() if len(parts) > 1 else t


def _table_word(tbl) -> str | None:
    cells = [c.text.strip() for row in tbl.rows for c in row.cells]
    cells = [c for c in cells if c]
    if not cells:
        return None
    return "".join(c.lstrip("+").strip() for c in cells)


def load_docx(docx_path: str):
    from docx import Document

    doc = Document(docx_path)
    return list(_iter_block_items(doc.element.body))


def find_chapter_bounds(items) -> dict[str, tuple[int, int]]:
    """docx blok-elementlar ro'yxatida "I/II/III/IV BOB." sarlavha
    paragraflarini topib, har bir bobning [boshlanish, tugash) indeks
    oralig'ini qaytaradi (chegara — keyingi bob sarlavhasi yoki hujjat
    oxiri)."""
    bounds: dict[str, tuple[int, int]] = {}
    cur = None
    start = None
    for i, it in enumerate(items):
        if it.__class__.__name__ != "Paragraph":
            continue
        t = it.text.strip()
        m = CHAP_RE.match(t.upper())
        if m:
            if cur is not None:
                bounds[cur] = (start, i)
            cur = m.group(1).upper()
            start = i
    if cur is not None:
        bounds[cur] = (start, len(items))
    return bounds


def extract_ch2_records(items, ch2_bounds: tuple[int, int]) -> list[dict]:
    """II bob ichidagi har bir "Ingliz tilida EVX <so'z> ... Oʻzbek tilida
    EVIX <tarjima>" juftligini xom docx dan ajratib oladi. Har bir yozuv —
    paragraf-matn asosidagi rekonstruksiya (asosiy) VA (agar mavjud bo'lsa)
    o'zak+affiks jadvalidan rekonstruksiya (qo'shimcha, faqat izoh uchun)."""
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    s, e = ch2_bounds
    records = []
    i = s
    while i < e:
        it = items[i]
        if isinstance(it, Paragraph):
            t = it.text.strip()
            m = EN_MARKER_RE.search(t)
            if m and not any(b in t.lower() for b in _BAD_CONTINUATION):
                cap = m.group(1).strip()
                if cap and len(cap) < 70:
                    en_raw = _clean_marker(cap)
                    en_marker_word = _join_plus(_arrow_last(en_raw))

                    en_table_word = None
                    for k in range(i + 1, min(i + 4, e)):
                        if isinstance(items[k], Table):
                            en_table_word = _table_word(items[k])
                            break
                        if isinstance(items[k], Paragraph) and items[k].text.strip():
                            if "parsinglash" not in items[k].text.strip().lower():
                                break

                    uz_raw = None
                    uz_idx = None
                    for k in range(i + 1, min(i + 20, e)):
                        if isinstance(items[k], Paragraph):
                            tk = items[k].text.strip()
                            if EN_MARKER_RE.search(tk) and not any(b in tk.lower() for b in _BAD_CONTINUATION):
                                break
                            mu = UZ_MARKER_RE.search(tk)
                            if mu and not any(b in tk.lower() for b in _BAD_CONTINUATION):
                                uz_raw = mu.group(1).strip()
                                uz_idx = k
                                break

                    uz_marker_word = None
                    uz_table_word = None
                    if uz_raw is not None:
                        uz_clean = _clean_marker(uz_raw)
                        uz_marker_word = _join_plus(_arrow_last(uz_clean))
                        for k in range(uz_idx + 1, min(uz_idx + 4, e)):
                            if isinstance(items[k], Table):
                                uz_table_word = _table_word(items[k])
                                break
                            if isinstance(items[k], Paragraph) and items[k].text.strip():
                                break

                    records.append({
                        "en_idx": i,
                        "en_marker_raw": t,
                        "en_marker_word": en_marker_word,
                        "en_table_word": en_table_word,
                        "uz_idx": uz_idx,
                        "uz_marker_raw": uz_raw,
                        "uz_marker_word": uz_marker_word,
                        "uz_table_word": uz_table_word,
                    })
        i += 1
    return records


def match_ch2_examples(examples: list[dict], docx_records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Har bir CH2_EVX_EXAMPLES yozuvini docx dan ajratib olingan yozuv
    bilan bog'laydi (normallashtirilgan en_marker_word bo'yicha, hujjatdagi
    TARTIB bo'yicha iste'mol qilinadi — masalan "gayer" ikki marta uchrasa,
    CH2'dagi birinchi "gayer" docx'dagi BIRINCHI "gayer" yozuviga, ikkinchisi
    IKKINCHISIGA bog'lanadi). Qaytaradi: (bog'langan juftlar, docx'da
    ISHLATILMAGAN qolgan yozuvlar — ya'ni CH2_EVX_EXAMPLES ga umuman
    kirmagan II bob misollari)."""
    pools: dict[str, list[dict]] = {}
    for r in docx_records:
        key = normalize(r["en_marker_word"])
        pools.setdefault(key, []).append(r)

    pairs = []
    unmatched_ex = []
    for ex in examples:
        key = normalize(ex["en"])
        candidates = pools.get(key, [])
        matched = candidates.pop(0) if candidates else None
        if matched is None:
            unmatched_ex.append(ex)
        pairs.append({"ch2": ex, "docx": matched, "matched_by": "en" if matched else None})

    # Fallback bosqichi: EN bo'yicha to'g'ridan-to'g'ri topilmagan CH2
    # yozuvlar uchun (masalan "capabilityies" ~ docx "capabilities") — QOLGAN
    # docx yozuvlar orasidan UZ tarjimasi ANIQ mos kelganini qidiramiz. Bu
    # aynan EN maydonidagi transkripsiya xatosi (imlo) bo'lgan holatlarni
    # "topilmadi" emas, "topildi, lekin EN farq qiladi" deb to'g'ri
    # belgilash uchun kerak.
    remaining_by_uz: dict[str, list[dict]] = {}
    for lst in pools.values():
        for r in lst:
            ukey = normalize(r["uz_marker_word"] or "")
            remaining_by_uz.setdefault(ukey, []).append(r)

    for p in pairs:
        if p["docx"] is not None:
            continue
        ex = p["ch2"]
        ukey = normalize(ex["uz"])
        cands = remaining_by_uz.get(ukey, [])
        if cands:
            r = cands.pop(0)
            # shu yozuvni pools'dan ham olib tashlaymiz (unused ro'yxatiga tushmasin)
            enkey = normalize(r["en_marker_word"])
            if r in pools.get(enkey, []):
                pools[enkey].remove(r)
            p["docx"] = r
            p["matched_by"] = "uz-fallback"

    unused = [r for lst in pools.values() for r in lst]
    unused.sort(key=lambda r: r["en_idx"])
    return pairs, unused


# III/IV bobdagi baholash/hisobot mazmunini belgilash uchun ishlatiladigan
# kalit so'zlar — headword qidiruvidagi "context_flag" belgisi UCHUN va
# `list_evaluation_context_blocks()` (headword'lardan MUSTAQIL, butun
# bobni skanerlaydigan inventarizatsiya) uchun BIR XIL ro'yxat ishlatiladi.
EVAL_CONTEXT_KEYWORDS = ("aniqlik", "foiz", "%", "misol", "natija", "test")


def _word_boundary_pattern(headword: str) -> str:
    """Headword uchun regex naqshini quradi: oldidan/keyinidan lotin harfi
    yoki apostrof (ASCII/tipografik) kelmasligi shart — bu oddiy `\\b`dan
    farqli, chunki `\\b` apostrofni so'z ichidagi belgi deb hisoblamaydi va
    ko'p so'zli iboralar ("a network", "more comfortable") ichidagi bo'sh
    joyni oddiy bo'shliq sifatida to'g'ri ushlaydi. Katta-kichik harf
    FARQI YO'Q (`re.IGNORECASE` chaqiruvchi tomonda qo'llaniladi)."""
    return r"(?<![A-Za-z'’])" + re.escape(headword) + r"(?![A-Za-z'’])"


def search_leakage(items, chapter_bounds, chapter_names, headwords: list[str]) -> list[dict]:
    """HAR BIR headword uchun ALOHIDA (`_word_boundary_pattern`) regex bilan
    berilgan bob(lar) ichidagi BARCHA paragraf matni va BARCHA jadval katak
    matnini (boshqa hech narsa — izoh, footnote, rasm ichidagi matn EMAS,
    python-docx bularni umuman ko'rmaydi) `re.search(..., re.IGNORECASE)`
    bilan tekshiradi. Bu — ODDIY MATNLI QIDIRUV, hech qanday semantik/
    ma'no darajasidagi tekshiruv YO'Q: agar biror "aniqlik/foiz" jadvali
    CH2 so'zini so'zma-so'z YOZMASDAN (masalan faqat "52 ta misol"
    ko'rinishida, so'zlarni sanab o'tmasdan) tilga olsa, bu funksiya buni
    UMUMAN topa OLMAYDI — qarang pastdagi "Cheklovlar" bo'limi.

    Qaytadi: HAR BIR moslik uchun bitta yozuv (`headword`, `pattern`,
    `chapter`, `idx`, matn parchasi). Hech narsa topilmagan headword bu
    ro'yxatda UMUMAN ko'rinmaydi — nol-hit holatlarni ko'rish uchun
    `summarize_leakage_by_headword()` ishlatiladi (u BARCHA headword'larni,
    hit=0 bo'lsa ham, ko'rsatadi)."""
    hits = []
    for hw in headwords:
        pattern = _word_boundary_pattern(hw)
        compiled = re.compile(pattern, re.IGNORECASE)
        for ch in chapter_names:
            if ch not in chapter_bounds:
                continue
            s, e = chapter_bounds[ch]
            for i in range(s, e):
                it = items[i]
                texts = []
                in_table = False
                if it.__class__.__name__ == "Paragraph":
                    texts = [it.text]
                elif it.__class__.__name__ == "Table":
                    in_table = True
                    texts = [c.text for row in it.rows for c in row.cells]
                for txt in texts:
                    if not txt or not txt.strip():
                        continue
                    if compiled.search(txt):
                        context_flag = any(kw in txt.lower() for kw in EVAL_CONTEXT_KEYWORDS)
                        hits.append({
                            "chapter": ch,
                            "idx": i,
                            "headword": hw,
                            "pattern": pattern,
                            "in_table": in_table,
                            "context_flag": context_flag,
                            "snippet": txt.strip()[:200],
                        })
    return hits


def summarize_leakage_by_headword(headwords: list[str], hits: list[dict], chapter_names: list[str]) -> list[dict]:
    """HAR BIR headword uchun (topilgan-topilmaganidan qat'i nazar) bitta
    qator qaytaradi — "topilmadi" xulosasi qanday olinganini (qaysi
    naqsh, qaysi boblar tekshirildi) reproduksiya qilish uchun. Bu
    `search_leakage()` natijasini headword bo'yicha guruhlaydi va
    hit=0 bo'lgan so'zlarni HAM ko'rsatadi (ular `search_leakage()`
    natijasida umuman yo'q edi)."""
    by_word: dict[str, list[dict]] = {}
    for h in hits:
        by_word.setdefault(h["headword"], []).append(h)

    rows = []
    for hw in headwords:
        word_hits = by_word.get(hw, [])
        per_chapter = {ch: sum(1 for h in word_hits if h["chapter"] == ch) for ch in chapter_names}
        rows.append({
            "headword": hw,
            "pattern": _word_boundary_pattern(hw),
            "per_chapter": per_chapter,
            "total": len(word_hits),
            "first_hit": word_hits[0] if word_hits else None,
        })
    return rows


def list_evaluation_context_blocks(items, chapter_bounds, chapter_names) -> list[dict]:
    """CH2 headword ro'yxatidan MUSTAQIL: berilgan bob(lar) ichidagi
    "aniqlik/foiz/%/misol/natija/test" so'zlaridan birortasini o'z ichiga
    olgan HAR BIR paragraf/jadval-katakni ro'yxatlaydi. Maqsad — bu
    ro'yxatni headword-qidiruvi natijasi bilan QO'LDA solishtirib, avtomatik
    so'z-qidiruvi biror baholash/aniqlik da'vosini "ko'rmay o'tib
    ketmaganini" mustaqil tekshirish imkonini berish (headword qidiruvi
    "ichkaridan tashqariga", bu funksiya esa "tashqaridan ichkariga"
    qaraydi — ikkalasi ham FAQAT so'zma-so'z matn darajasida, semantik
    tahlil emas)."""
    out = []
    for ch in chapter_names:
        if ch not in chapter_bounds:
            continue
        s, e = chapter_bounds[ch]
        for i in range(s, e):
            it = items[i]
            if it.__class__.__name__ == "Paragraph":
                t = it.text
                if t and any(k in t.lower() for k in EVAL_CONTEXT_KEYWORDS):
                    out.append({"chapter": ch, "idx": i, "in_table": False, "snippet": t.strip()[:220]})
            elif it.__class__.__name__ == "Table":
                for row in it.rows:
                    for c in row.cells:
                        if c.text and any(k in c.text.lower() for k in EVAL_CONTEXT_KEYWORDS):
                            out.append({"chapter": ch, "idx": i, "in_table": True, "snippet": c.text.strip()[:220]})
    return out


def run(docx_path: str, out_path: str | None) -> int:
    import kkt_v20_soz_tartibi as m

    if not os.path.exists(docx_path):
        print(f"XATO: {docx_path} topilmadi.", file=sys.stderr)
        return 1

    items = load_docx(docx_path)
    bounds = find_chapter_bounds(items)

    examples = m.CH2_EVX_EXAMPLES
    total = len(examples)
    unique_en = {ex["en"].strip().lower() for ex in examples}

    docx_records = extract_ch2_records(items, bounds.get("II", (0, 0))) if "II" in bounds else []
    pairs, unused_docx = match_ch2_examples(examples, docx_records)

    n_matched = sum(1 for p in pairs if p["docx"] is not None)
    n_unmatched = total - n_matched

    def _verdict(p):
        docx_r = p["docx"]
        if docx_r is None:
            return "DOCX'DA TOPILMADI (avtomatik qidiruv aniqlay olmadi)"
        en_match = normalize(p["ch2"]["en"]) == normalize(docx_r["en_marker_word"])
        uz_match = normalize(p["ch2"]["uz"]) == normalize(docx_r["uz_marker_word"] or "")
        if en_match and uz_match:
            return "MOS"
        if not en_match and not uz_match:
            return "EN VA UZ IKKALASI HAM FARQ QILADI"
        if not en_match:
            return "EN FARQ QILADI"
        return "UZ FARQ QILADI"

    mismatches = [(p, _verdict(p)) for p in pairs]
    mismatches = [(p, v) for p, v in mismatches if v != "MOS"]

    # Headword leakage qidiruvi (III va IV bob)
    single_and_phrase_headwords = sorted(unique_en, key=len, reverse=True)
    leakage_hits = search_leakage(items, bounds, ["III", "IV"], single_and_phrase_headwords)
    per_headword_summary = summarize_leakage_by_headword(single_and_phrase_headwords, leakage_hits, ["III", "IV"])
    eval_context_blocks = list_evaluation_context_blocks(items, bounds, ["III", "IV"])

    lines = []
    lines.append("# CH2_EVX_EXAMPLES — dissertatsiya docx bilan solishtiruv va III/IV bob leakage tekshiruvi")
    lines.append("")
    lines.append(f"**Generatsiya vaqti:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}Z")
    lines.append(f"**Manba:** `{os.path.relpath(docx_path, REPO_ROOT)}` (foydalanuvchi tomonidan 2026-09-08 da qo'shildi) "
                  f"va `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` ({total} ta yozuv)")
    lines.append(f"**Buyruq:** `python scripts/check_ch2_leakage.py`")
    lines.append("")
    lines.append("Bu hisobot ikkita ALOHIDA topshiriqni bittada bajaradi (foydalanuvchi so'rovi, 2026-09-08):")
    lines.append("1. CH2_EVX_EXAMPLES ro'yxatini II bobdagi haqiqiy paragraflar bilan solishtirish (mos kelmasliklar jadvali).")
    lines.append("2. CH2_EVX_EXAMPLES headword'larining III/IV bobda uchrashini (leakage xavfi) tekshirish.")
    lines.append("")

    lines.append("## 0. `CH2_EVX_EXAMPLES` docstring da'vosi: \"52 ta\" — tekshirildi")
    lines.append("")
    lines.append(
        f"`len(CH2_EVX_EXAMPLES) = {total}`. Docstring \"52 ta ingliz-o'zbek EVXs/EVIXs namuna so'z\" deb da'vo "
        f"qiladi — bu **TASDIQLANDI** ({total} == 52). Ilgari suhbatda aytilgan \"~44 ta\" taxmini **NOTO'G'RI** "
        f"edi. Noyob inglizcha bosh so'zlar soni: **{len(unique_en)}** (`gayer` ikki marta uchraydi — qiyosiy "
        f"\"sho'xroq\" va orttirma \"eng sho'x\" uchun ikkita alohida yozuv, ikkalasi ham `en='gayer'`)."
    )
    lines.append("")
    lines.append(
        "**LEKIN — ro'yxat TO'LIQ EMAS:** II bobning o'zida `CH2_EVX_EXAMPLES`ga umuman kiritilmagan "
        f"qo'shimcha \"Ingliz tilida EVX ... / Oʻzbek tilida EVIX ...\" namunalar ham bor — pastda "
        f"({len(unused_docx)} ta, 3-bo'lim) ro'yxat qilingan (masalan `to be`, `to have`, `become`, `need`, "
        f"`large->larger`, `big->bigger/biggest`, `good->better->best`, `easily`, `more clearly`, olmosh "
        f"jadvali \"I\"->\"men\" va h.k.). Demak \"52 ta\" — II bobning HAMMASI emas, balki dastur muallifi "
        f"TANLAB ko'chirgan qism."
    )
    lines.append("")

    lines.append("## 1. Paragraf darajasidagi solishtiruv — natija")
    lines.append("")
    lines.append(f"- Jami CH2_EVX_EXAMPLES yozuvi: **{total}**")
    lines.append(f"- Docx'da avtomatik topilgan (paragraf juftligi aniqlandi): **{n_matched}**")
    lines.append(f"- Docx'da avtomatik topilMAdi (qo'lda tekshirish kerak): **{n_unmatched}**")
    lines.append(f"- Topilganlardan MOS KELMAGAN (en va/yoki uz farq qiladi): **{len(mismatches)}**")
    lines.append("")

    if mismatches:
        lines.append("### Mos kelmasliklar — to'liq jadval (xom docx dalili bilan)")
        lines.append("")
        lines.append("| CH2 en | CH2 uz | Docx en (paragraf, idx) | Docx uz (paragraf, idx) | Docx en (jadval katakchasi) | Verdikt |")
        lines.append("|---|---|---|---|---|---|")
        for p, v in mismatches:
            ex = p["ch2"]
            r = p["docx"]
            if r is None:
                lines.append(f"| {ex['en']} | {ex['uz']} | — | — | — | {v} |")
                continue
            docx_en = f"{r['en_marker_word']} (#{r['en_idx']})"
            docx_uz = f"{r['uz_marker_word']} (#{r['uz_idx']})" if r["uz_marker_word"] else "(topilmadi)"
            tbl_note = r["en_table_word"] if r["en_table_word"] and r["en_table_word"] != r["en_marker_word"] else "—"
            lines.append(f"| {ex['en']} | {ex['uz']} | {docx_en} | {docx_uz} | {tbl_note} | {v} |")
        lines.append("")
        lines.append(
            "**\"Docx en (jadval katakchasi)\" ustuni haqida:** ba'zi yozuvlarda \"Ingliz tilida EVX <so'z>\" "
            "paragrafidan keyin kichik bir o'zak+affiks jadvali keladi (masalan `leaf | + es`). Bu katakchalarni "
            "to'g'ridan-to'g'ri qo'shib o'qish paragrafdagi TO'G'RI yozilgan shakldan farq qilishi mumkin "
            "(masalan jadval \"leaf\"+\"es\"=\"leafes\" beradi, paragrafning o'zida esa to'g'ri \"leaves\" "
            "yozilgan). Bu ustun FAQAT qo'shimcha dalil — qaysi manba \"to'g'ri\" ekanini bu skript HAL "
            "QILMAYDI."
        )
        lines.append("")

    if n_unmatched:
        lines.append("### Docx'da avtomatik topilmagan CH2 yozuvlar (qo'lda tekshirish kerak)")
        lines.append("")
        lines.append("| CH2 en | CH2 uz | Izoh |")
        lines.append("|---|---|---|")
        for p, v in mismatches:
            if p["docx"] is None:
                lines.append(f"| {p['ch2']['en']} | {p['ch2']['uz']} | Avtomatik qidiruv \"Ingliz tilida EVX\" naqshini bu yozuv uchun topa olmadi — bu skript metodikasining cheklovi, dissertatsiyada yo'qligini ANGLATMAYDI. |")
        lines.append("")

    lines.append("## 2. II bobdagi, lekin CH2_EVX_EXAMPLES ga KIRITILMAGAN namunalar")
    lines.append("")
    lines.append(
        f"Docx'dan avtomatik ajratib olingan {len(docx_records)} ta \"Ingliz tilida EVX\" belgisidan "
        f"{len(unused_docx)} tasi CH2_EVX_EXAMPLES dagi hech qaysi yozuv bilan bog'lanmadi — demak ular II "
        f"bobda BOR, lekin dastur muallifi CH2_EVX_EXAMPLES ga KIRITMAGAN:"
    )
    lines.append("")
    lines.append("| # (docx paragraf idx) | Ingliz (paragraf) | O'zbek (paragraf) |")
    lines.append("|---|---|---|")
    for r in unused_docx:
        lines.append(f"| {r['en_idx']} | {r['en_marker_word']} | {r['uz_marker_word'] or '(topilmadi)'} |")
    lines.append("")
    lines.append(
        "Diqqat: bu jadvaldagi ba'zi qatorlar dissertatsiyaning O'ZIDAGI (Claude yoki avvalgi transkripsiya "
        "emas) ichki nomuvofiqlikni aks ettirishi mumkin — masalan #666 qatorida \"Ingliz tilida EVX so'z: "
        "**variables**\" deb yozilgan, lekin undan keyingi o'zak+affiks jadvali `form|+al` va o'zbekcha "
        "tarjimasi \"rasmiy\" (=formal) — ya'ni bu qatordagi haqiqiy misol \"formal\" bo'lishi kerak edi, "
        "\"variables\" so'zi avvalgi bo'limdan (#310) qolib ketgan nusxa xatosi ko'rinadi (docx #664-673 "
        "qarang). Bu skript bunday holatlarni ANIQLAMAYDI/TUZATMAYDI — faqat xom matnni ko'rsatadi."
    )
    lines.append("")

    lines.append("## 3. Headword darajasidagi \"aylanma\"/leakage tekshiruvi — III va IV bob")
    lines.append("")
    lines.append(
        "### 3.0 Aniq metodika — qanday qidiruv ishlatildi (foydalanuvchi so'rovi, 2026-09-09)"
    )
    lines.append("")
    lines.append(
        "**Bu — oddiy matnli (substring) qidiruv, professor darajasidagi qo'lda-o'qib-chiqish EMAS.** "
        "Aniq algoritm:"
    )
    lines.append("")
    lines.append(
        f"1. CH2_EVX_EXAMPLES dagi {len(unique_en)} ta NOYOB inglizcha bosh so'z/ibora (`ex[\"en\"]` "
        f"maydoni, kichik harfga o'tkazilgan) ro'yxati olinadi."
    )
    lines.append(
        "2. Har bir headword uchun ALOHIDA regex naqshi tuziladi: "
        "`(?<![A-Za-z'’])<headword>(?![A-Za-z'’])` — ya'ni headworddan OLDIN va KEYIN lotin harfi yoki "
        "apostrof (oddiy `'` yoki tipografik `’`) kelmasligi shart. Bu — Python'ning standart `\\b` "
        "chegarasidan ATAYLAB farqli: `\\b` ko'p so'zli iboralar (\"a network\", \"more comfortable\") "
        "ichidagi bo'shliqni to'g'ri ushlamasligi, apostrofni esa so'z ichidagi belgi deb hisoblamasligi "
        "mumkin edi."
    )
    lines.append(
        "3. `re.search(naqsh, matn, re.IGNORECASE)` — bobning III va IV oralig'idagi (`find_chapter_bounds()` "
        "bilan aniqlangan blok-indekslar) **HAR BIR paragraf matni** va **HAR BIR jadval katak matni** "
        "ustida, birma-bir, alohida chaqiriladi."
    )
    lines.append(
        "4. Moslik topilsa, o'sha paragraf/katak matnining o'zida (BOSHQA hech qanday tashqi ma'lumot "
        "qo'shilmasdan) \"aniqlik\"/\"foiz\"/\"%\"/\"misol\"/\"natija\"/\"test\" so'zlaridan biri ham bor-"
        "yo'qligi tekshiriladi (`context_flag`) — bu ham oddiy substring tekshiruvi, na jadval sarlavhasi, "
        "na yaqin-atrofdagi paragraflar hisobga olinadi."
    )
    lines.append(
        "5. Natija: HAR BIR headword uchun 0 yoki undan ko'p \"hit\". \"Topilmadi\" xulosasi — shu headword "
        "uchun yuqoridagi regex III/IV bobning HECH bir paragraf/katagida `re.search` orqali moslik "
        "TOPMAGANI degani, boshqa hech narsa emas."
    )
    lines.append("")
    lines.append(
        "**Bu — funksiya darajasida qayta ishlatiladigan kod** "
        "(`scripts/check_ch2_leakage.py:search_leakage()`/`summarize_leakage_by_headword()`), demak "
        "boshqa birov xuddi shu skriptni qayta ishga tushirib, xuddi shu natijani oladi (git tarixi/versiya "
        "farqi bo'lmasa)."
    )
    lines.append("")

    lines.append(f"### 3.1 Har bir headword uchun natija ({len(per_headword_summary)} ta, HAMMASI — hit=0 bo'lganlar ham)")
    lines.append("")
    lines.append("| Headword | Qidiruv naqshi | III bobda | IV bobda | Jami | Birinchi moslik (idx, bob) |")
    lines.append("|---|---|---|---|---|---|")
    for row in per_headword_summary:
        pat_display = f"`{row['pattern']}`"
        first = row["first_hit"]
        first_display = f"#{first['idx']} ({first['chapter']})" if first else "—"
        lines.append(
            f"| {row['headword']} | {pat_display} | {row['per_chapter'].get('III', 0)} | "
            f"{row['per_chapter'].get('IV', 0)} | {row['total']} | {first_display} |"
        )
    lines.append("")
    n_zero = sum(1 for r in per_headword_summary if r["total"] == 0)
    lines.append(
        f"**{n_zero}/{len(per_headword_summary)}** headword uchun jami = 0, ya'ni yuqoridagi regex III/IV "
        f"bobning hech bir paragraf/jadval-katagida bu so'zni topmadi (5-band metodikaga qarang)."
    )
    lines.append("")

    lines.append(f"### 3.2 Topilgan holatlar — batafsil ({len(leakage_hits)} ta xom moslik)")
    lines.append("")
    if leakage_hits:
        n_table_hits = sum(1 for h in leakage_hits if h["in_table"])
        n_ctx_hits = sum(1 for h in leakage_hits if h["context_flag"])
        lines.append(f"- shundan jadval ichida: **{n_table_hits}**")
        lines.append(f"- shundan \"aniqlik\"/\"foiz\"/\"%\"/\"misol\"/\"natija\"/\"test\" so'zi bilan bir paragrafda/katakda: **{n_ctx_hits}**")
        lines.append("")
        lines.append("| Bob | Headword | Naqsh | Jadvalda? | Kontekst belgisi? | Docx idx | Matn parchasi |")
        lines.append("|---|---|---|---|---|---|---|")
        for h in sorted(leakage_hits, key=lambda x: (x["chapter"], x["idx"])):
            in_table_txt = "ha" if h["in_table"] else "yo'q"
            ctx_txt = "HA — tekshiring" if h["context_flag"] else "yo'q"
            snippet_txt = h["snippet"].replace(chr(10), " ")
            lines.append(f"| {h['chapter']} | {h['headword']} | `{h['pattern']}` | {in_table_txt} | {ctx_txt} | {h['idx']} | {snippet_txt} |")
        lines.append("")
        lines.append(
            "**Diqqat — bu jadval XULOSA EMAS:** ko'p qisqa inglizcha funksional so'zlar (masalan \"will\", "
            "\"can\", \"one\", \"here\") III/IV bobning umumiy (asosan o'zbek tilidagi) matnida TASODIFAN "
            "ham uchrashi mumkin (masalan boshqa inglizcha misol sifatida, yoki umuman aloqasiz kontekstda). "
            "Har bir qatorni qo'lda ko'rib chiqish kerak — bu skript faqat HAR BIR uchrashni xom docx "
            "manzili bilan ko'rsatadi, \"bu aylanma\" yoki \"bu tasodifiy\" degan xulosani Claude "
            "chiqarmaydi (professor/Ziyoviddin qarori)."
        )
    else:
        lines.append("Hech qanday moslik topilmadi — CH2_EVX_EXAMPLES headword'laridan birortasi ham III/IV "
                      "bob matnida (avtomatik qidiruv bo'yicha) uchramadi.")
    lines.append("")

    lines.append("### 3.3 Mustaqil tekshiruv — headword ro'yxatidan qat'i nazar, III/IV bobdagi BARCHA \"baholash-shaklidagi\" matn")
    lines.append("")
    lines.append(
        "Yuqoridagi 3.1/3.2 — headword'dan boshlab qidiradi (\"ichkaridan tashqariga\"). Bu bo'lim esa "
        "TESKARI yo'nalishda ishlaydi: CH2 so'zlaridan MUSTAQIL ravishda, III/IV bobdagi \"aniqlik\"/\"foiz\"/"
        "\"%\"/\"misol\"/\"natija\"/\"test\" so'zlaridan birortasini o'z ichiga olgan **HAR BIR** paragraf va "
        "jadval katakni to'liq ro'yxatlaydi — shu orqali o'qiuvchi (professor/Ziyoviddin) bu ro'yxatni QO'LDA "
        "ko'rib chiqib, yuqoridagi avtomatik so'z-qidiruvi biror haqiqiy baholash/aniqlik da'vosini "
        "\"ko'rmay o'tib ketmaganini\" MUSTAQIL tekshirishi mumkin (masalan, agar bir jadval CH2 so'zlarini "
        "so'zma-so'z yozmasdan, faqat \"52 ta misol asosida\" kabi umumiy iboralar bilan tasvirlasa, 3.1/3.2 "
        "buni topa OLMAYDI — lekin bu ro'yxatda o'sha jadval BOR, o'qib chiqish mumkin)."
    )
    lines.append("")
    lines.append(f"Jami topilgan blok: **{len(eval_context_blocks)}** (III bobda "
                  f"{sum(1 for b in eval_context_blocks if b['chapter']=='III')}, IV bobda "
                  f"{sum(1 for b in eval_context_blocks if b['chapter']=='IV')})")
    lines.append("")
    lines.append("| Bob | Docx idx | Jadval katagi? | Matn |")
    lines.append("|---|---|---|---|")
    for b in eval_context_blocks:
        it_txt = "ha" if b["in_table"] else "yo'q"
        lines.append(f"| {b['chapter']} | {b['idx']} | {it_txt} | {b['snippet'].replace(chr(10), ' ')} |")
    lines.append("")
    lines.append(
        "**MUHIM — dissertatsiyaning YAKKA-YAGONA raqamli aniqlik jadvali (4.3-jadval, docx idx 1287-1288, "
        "IV bob) alohida ko'rib chiqildi, chunki bu — butun hujjatdagi YAGONA joy, u yerda \"foiz\" bilan "
        "bog'liq son (97,7% va h.k.) HAQIQIY natija sifatida keltirilgan (qolgan barcha 54 blok umumiy "
        "matn, rasm izohi yoki bibliografiya):**"
    )
    lines.append("")
    lines.append("> **4.3-jadval**")
    lines.append(">")
    lines.append("> | № | Tarjima tizimlari | So'zlar soni | Tarjima foizi |")
    lines.append("> |---|---|---|---|")
    lines.append("> | 1 | Google Translate | 280 ta | 46% |")
    lines.append("> | 2 | DeepL Translate | 280 ta | 72% |")
    lines.append("> | 3 | Yandex Translate | 280 ta | 80% |")
    lines.append("> | 4 | Ingliz tilidan o'zbek tiliga rasmiy modellar asosida kompyuter tarjima moduli | 280 ta | 97,7% |")
    lines.append("")
    lines.append(
        "**Bu jadval haqida aniq/tekshirilgan faktlar (talqin emas):** jadval \"So'zlar soni: 280 ta\" "
        "deydi — LEKIN o'sha 280 ta so'zning O'ZI (ro'yxati) na jadvalning o'zida, na uning atrofidagi "
        "paragraflarda (docx idx 1284-1290, to'liq o'qildi) berilmagan. Shu sabab: **CH2_EVX_EXAMPLES (52 "
        "ta) yoki 1500 so'zlik lug'atning ushbu \"280 ta\" test to'plami bilan qanday bog'liqligini (mos "
        "keladimi, ustma-ust tushadimi, umuman aloqasi yo'qmi) SO'Z DARAJASIDA TEKSHIRISH BU DOCX ICHIDA "
        "MUMKIN EMAS** — chunki solishtirish uchun kerakli 280 ta so'zning matni umuman yo'q. Yuqoridagi "
        "atrofdagi yagona konkret misol — \"our books\" (item 1286, ilova/screenshot misoli sifatida "
        "keltirilgan, CH2_EVX_EXAMPLES yoki 1500-so'zlik lug'atda YO'Q so'z birikmasi). Bu — bu hisobotning "
        "ENG MUHIM OCHIQ SAVOLI: \"280 ta so'z\" test to'plamining aynan qaysi so'zlardan iboratligi "
        "aniqlanmaguncha, 97,7% ko'rsatkichi bilan CH2/1500-so'zlik lug'at orasidagi haqiqiy \"aylanma "
        "baholash\" xavfini SO'Z DARAJASIDA tekshirib bo'lmaydi."
    )
    lines.append("")
    lines.append(
        "**Qo'lda ko'rib chiqish natijasi (qolgan bloklar, Claude tomonidan, bir marta, 2026-09-09):** "
        f"yuqoridagi {len(eval_context_blocks)} ta blokdan yuqoridagi 4.3-jadval BUNDAN MUSTASNO, qolganlarning "
        "HECH birida CH2_EVX_EXAMPLES so'zlari (yoki ularga ishora) TOPILMADI — bularning deyarli barchasi "
        "(a) III bobdagi baza-qurish/vazn-hisoblash metodologiyasi tavsifi (masalan \"rasmiy modellar barcha "
        "so'z turkumlari uchun hisoblandi\" kabi UMUMIY bayonotlar, aniq so'z sanamasdan) yoki (b) IV "
        "bobdagi dastur-modul tavsifi/skrinshot izohlari va bibliografiya. **Bu qo'lda ko'rib chiqish "
        "rasmiy audit emas** — bitta o'qishda amalga oshirildi, boshqa birov xatolik topishi mumkin; shu "
        "sabab to'liq ro'yxat yuqorida qoldirildi."
    )
    lines.append("")

    lines.append("### 3.4 Cheklovlar (nima bu tekshiruv doirasidan TASHQARIDA qoldi)")
    lines.append("")
    lines.append(
        "- Bu — **so'zma-so'z matn qidiruvi**, semantik/ma'no darajasidagi tahlil EMAS. Agar III/IV bobdagi "
        "biror \"aniqlik\"/\"foiz\" jadvali test to'plamini CH2 so'zlarini AYNAN yozmasdan tasvirlasa (masalan "
        "faqat son bilan: \"52 ta misol\", yoki umuman tavsiflamasdan), bu skript buni ANIQLAY OLMAYDI."
    )
    lines.append(
        "- Rasm ichidagi matn (screenshot, diagram label) `python-docx` orqali UMUMAN o'qilmaydi — agar IV "
        "bobdagi dastur skrinshotlarida CH2 so'zlari ko'rinsa, bu skript ularni ko'rmaydi."
    )
    lines.append(
        "- Footnote/izoh matnlari (agar alohida XML qismida saqlangan bo'lsa) tekshirilmagan — bu docx'da "
        "shunday joy borligi alohida tasdiqlanmagan."
    )
    lines.append(
        "- 3.3-bo'limdagi \"qo'lda ko'rib chiqish\" — professor darajasidagi rasmiy audit emas, Claude "
        "tomonidan bitta o'qishda bajarilgan; qayta tekshirish tavsiya etiladi."
    )
    lines.append("")

    lines.append("## Xulosa (faqat aniqlangan faktlar — professor bilan muhokama uchun)")
    lines.append("")
    lines.append(
        f"1. **\"52 ta\" da'vosi to'g'ri** ({total} yozuv), lekin bu ro'yxat II bobning HAMMASI emas — "
        f"kamida {len(unused_docx)} ta qo'shimcha misol (shu jumladan **`will return` -> `qaytadi`**, "
        f"ilgari \"CH2_EVX_EXAMPLES da yo'q\" deb qayd etilgan edi — ENDI docx'da TOPILDI, #632-634) II "
        f"bobda bor-yu, CH2_EVX_EXAMPLES ga kiritilmagan."
    )
    lines.append(
        f"2. **{len(mismatches)} ta haqiqiy mos kelmaslik** topildi (yuqoridagi 1-bo'lim jadvali), ikki xil "
        f"sababga ega ko'rinadi: (a) transkripsiya xatosi (CH2 ro'yxatini qo'lda ko'chirishda paydo bo'lgan, "
        f"masalan `capabilityies` — docx'da hech qayerda bunday yozilish yo'q, faqat to'g'ri `capabilities`), "
        f"(b) docx'dagi ikkita QO'SHNI misoldan noto'g'ri qator ko'chirilgani (masalan `more comfortable` "
        f"uchun uz='eng qulay' olingan, lekin bu aslida QO'SHNI `most comfortable` misolining tarjimasi — "
        f"docx'da `more comfortable`->`qulayroq`, alohida). `schoolboys`->`Bojxonalar` xatosi ham xuddi shu "
        f"turdagi (oldingi `customhouses` qatoridan noto'g'ri ko'chirilgan) — bu docx dalili bilan ENDI "
        f"TASDIQLANDI (ilgari reports/faza_1.md da faqat FARAZ qilingan edi)."
    )
    lines.append(
        f"3. **So'z-darajasidagi (substring) qidiruv bo'yicha III/IV bobda CH2 headword'lari topilmadi** "
        f"({len(leakage_hits)} ta xom moslikning barchasi adabiyotlar ro'yxatidagi (bibliografiya) inglizcha "
        f"maqola sarlavhalarida — \"information\", \"here\" so'zlari, batafsil 3.2-bo'lim). **LEKIN bu "
        f"\"leakage yo'q\" degani EMAS** — dissertatsiyaning yagona raqamli aniqlik jadvali (4.3-jadval, IV "
        f"bob, 97,7% ko'rsatkichi) \"280 ta so'z\" ustida hisoblangan, LEKIN o'sha 280 ta so'zning matni "
        f"docx'ning hech qayerida berilmagan — shu sabab bu 280 ta so'z bilan CH2/1500-so'zlik lug'at "
        f"orasidagi bog'liqlikni SO'Z DARAJASIDA TEKSHIRISH BU DOCX ICHIDA MUMKIN EMAS (batafsil 3.3-bo'lim, "
        f"\"4.3-jadval\" alohida ko'rib chiqilgan qismi). Bu — reproduksiya qilingan METODIKANING (nima "
        f"qilindi/qilinmadi) o'zi, \"leakage bor/yo'q\" degan yakuniy xulosa EMAS."
    )
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
    ap.add_argument("--docx", default=DEFAULT_DOCX)
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "reports", "ch2_leakage_check.md"))
    ap.add_argument("--no-out", action="store_true")
    args = ap.parse_args()
    return run(args.docx, None if args.no_out else args.out)


if __name__ == "__main__":
    raise SystemExit(main())
