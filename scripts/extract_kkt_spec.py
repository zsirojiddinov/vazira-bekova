#!/usr/bin/env python3
"""
scripts/extract_kkt_spec.py
==============================
`data/kkt_qoidalari.docx` (KKT formalizmining rasmiy qoidalar to'plami —
foydalanuvchi 2026-09-11 da qo'shdi) dan strukturaviy spesifikatsiyani
ajratib, `data/kkt_spec.json` ga yozadi.

Bu — MA'LUMOT EMAS, SPESIFIKATSIYA. Shu sabab:

- Har bir matn maydoni (`tavsif`, `en_misol`, `uz_misol`, operator `mano`
  va h.k.) docx katagidan AYNAN ko'chiriladi — tipografik apostroflar
  (‘ ’), "–" tire, "→" strelka, "…" va bosh harflar ham o'zgartirilmaydi.
  Hech narsa "tuzatilmaydi".
- Docx'da xato/nomuvofiq ko'ringan joylar original holicha qoladi va
  ALOHIDA `izoh` maydonida qayd etiladi. `izoh`lar ikki xil:
  (a) AVTOMATIK — "A + B = C" ko'rinishidagi katakda "+" bilan ajratilgan
      komponentlar qo'shilganda C hosil bo'lmasa (`_concat_izoh()`);
  (b) QO'LDA — `_QOLDA_IZOHLAR` lug'atida, har biri faqat katakning o'zida
      ko'rinib turgan faktni aytadi (lingvistik hukm chiqarmaydi).
- Yagona "tarjima" qatlami — kod bilan solishtirish uchun kerak bo'lgan
  KALITLAR: bo'lim sarlavhasi "1. OT (Noun) ..." -> `pos: "Ot"`, vazn
  paragrafidagi "Fe’l" -> `"Fe'l"` (kodning `POS_V2` kalitlari ASCII
  apostrofli). Asl yozilish `bolim` va `pos_weights_manba[].docx_matn`
  maydonlarida saqlanadi.

Docx tuzilishi o'zgarsa (jadval/bo'lim soni boshqacha bo'lsa) skript
jimgina "moslashmaydi" — xato bilan to'xtaydi (`SpecStructureError`).

Ishlatish:
    python scripts/extract_kkt_spec.py
    python scripts/extract_kkt_spec.py --check   # JSON docx bilan sinxronmi (CI uchun)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

DEFAULT_DOCX = os.path.join(REPO_ROOT, "data", "kkt_qoidalari.docx")
DEFAULT_JSON = os.path.join(REPO_ROOT, "data", "kkt_spec.json")


class SpecStructureError(RuntimeError):
    """Docx kutilgan tuzilishga (1 operator jadvali + 6 bo'lim jadvali) mos emas."""


# Bo'lim sarlavhasidagi (masalan "3. FE’L (Verb) so‘z turkumi qoidalari")
# katta harfli nom -> kodning POS kaliti (kkt_v20_soz_tartibi.py:POS_KKT).
_HEADING_TO_POS = {
    "OT": "Ot", "SIFAT": "Sifat", "FE'L": "Fe'l",
    "RAVISH": "Ravish", "SON": "Son", "OLMOSH": "Olmosh",
}
_HEADING_RE = re.compile(r"^\s*(\d+)\.\s+(.+?)\s+\(([A-Za-z]+)\)\s+so.z turkumi qoidalari\s*$")

# Vazn paragrafidagi nom -> POS_V2 kaliti. Faqat apostrof normallashtiriladi
# va "Yordamchi so'z turkumlari" qisqartiriladi (kodda bunday kalit yo'q —
# topshiriq matnidagi "Yordamchi=0.07" nomi ishlatildi).
_WEIGHT_NAME_TO_KEY = {
    "Ot": "Ot", "Sifat": "Sifat", "Fe'l": "Fe'l", "Ravish": "Ravish",
    "Olmosh": "Olmosh", "Son": "Son", "Bog'lovchi": "Bog'lovchi",
    "Predlog": "Predlog", "Yordamchi so'z turkumlari": "Yordamchi",
}
_WEIGHT_ITEM_RE = re.compile(r"^(.*?)\s*\(([^)]*)\)\s*[–-]\s*([0-9]+(?:\.[0-9]+)?)\.?$")

_APOS_RE = re.compile("[‘’ʻʼ`]")

# Qo'lda qayd etilgan izohlar — FAQAT katakning o'zida ko'rinadigan fakt.
# Kalit — `uid`. Bu yerda hech qanday "to'g'ri javob" taklif qilinmaydi.
_QOLDA_IZOHLAR = {
    "2.11": "Tavsifda \"chiziqcha (defis) bilan ajratib yoziladigan\" deyilgan, lekin ingliz misolida "
            "(\"custom + houses = customhouses\") defis yo'q — natija qo'shib yozilgan.",
    "2.13": "O'zbek misoli katagida izoh qavs ichida berilgan: \"axborot (affikssiz)\" — natija so'zi "
            "\"axborot\", \"(affikssiz)\" misolning bir qismi emas.",
    "2.20": "Ingliz misolida natija shakli berilmagan (\"high-dimension + al\" — \"=\" yo'q); o'zbek "
            "misolida ham (\"ko‘p o‘lchov + li\").",
    "3.2": "Ingliz misoli boshqa qatorlardan teskari tartibda yozilgan: natija chapda "
           "(\"easi(ly) = easy + ly\"), boshqa qatorlarda \"asos + affiks = natija\".",
    "3.12": "O'zbek katagida \"(affikssiz, qo‘shib yoziladi)\" deyilgan, lekin misolning o'zi "
            "bo'shliq bilan yozilgan: \"o‘n besh\".",
    "3.19": "O'zbek misolida natija shakli berilmagan (\"bir yuz yigirma bir + inchi\" — \"=\" yo'q).",
    "3.25": "4 ta inglizcha shaklga 4 ta o'zbekcha mos keladi, lekin faqat birinchisi \"+ niki\" "
            "(\"men + niki\"), qolgan uchtasi \"+ ning\" bilan berilgan — 3.24-qoidadagi (egalik "
            "olmosh-sifat) bilan bir xil. Nomuvofiqlik bo'lishi mumkin — Claude hal qilmaydi.",
    "3.27": "Ikkala misol ro'yxati \"…\" bilan tugaydi — to'liq ro'yxat emas.",
    "3.28": "Ikkala misol ro'yxati \"…\" bilan tugaydi — to'liq ro'yxat emas.",
}


def _norm_apos(s: str) -> str:
    return _APOS_RE.sub("'", s)


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_blocks(doc):
    """Paragraf va jadvallarni hujjatdagi HAQIQIY tartibda qaytaradi."""
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    for child in doc.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, doc)
        elif child.tag.endswith("}tbl"):
            yield Table(child, doc)


def _concat_izoh(cell: str) -> str | None:
    """"A + B = C" (bitta "=") ko'rinishidagi katak uchun: "+" bilan
    ajratilgan komponentlar (atrofidagi bo'shliqlarsiz) qo'shilganda C
    hosil bo'lmasa, shu faktni qaytaradi. "→" bor bo'lsa, faqat oxirgi
    "→" dan keyingi qism tekshiriladi ("large → larg + er = larger")."""
    if cell.count("=") != 1 or "+" not in cell:
        return None
    lhs, rhs = (p.strip() for p in cell.split("="))
    lhs = lhs.split("→")[-1].strip()
    if "+" not in lhs:
        return None
    joined = re.sub(r"\s*\+\s*", "", lhs)
    if joined == rhs:
        return None
    return (f"\"{cell}\": \"+\" bilan ajratilgan komponentlar qo'shilganda \"{joined}\" hosil bo'ladi, "
            f"natija sifatida esa \"{rhs}\" yozilgan.")


def _missing_ids(rules: list[dict]) -> list[str]:
    """"2.N"/"3.N" raqamlari orasidagi bo'shliqlar (har bir prefiks uchun
    eng kichik va eng katta N oralig'ida). "2.55a"/"2.55b" -> 55."""
    by_prefix: dict[str, set[int]] = {}
    for r in rules:
        m = re.match(r"^(\d+)\.(\d+)[a-z]?$", r["id"])
        if m:
            by_prefix.setdefault(m.group(1), set()).add(int(m.group(2)))
    out = []
    for prefix in sorted(by_prefix, key=int):
        nums = by_prefix[prefix]
        out += [f"{prefix}.{n}" for n in range(min(nums), max(nums) + 1) if n not in nums]
    return out


def _parse_weights(text: str) -> tuple[dict, list]:
    body = text.split(":", 1)[1] if ":" in text else text
    weights: dict[str, float] = {}
    manba: list[dict] = []
    for raw in (p.strip() for p in body.split(";")):
        if not raw:
            continue
        m = _WEIGHT_ITEM_RE.match(raw)
        if not m:
            raise SpecStructureError(f"Vazn bandini o'qib bo'lmadi: {raw!r}")
        name, symbol, value = m.group(1).strip(), m.group(2).strip(), m.group(3)
        key = _WEIGHT_NAME_TO_KEY.get(_norm_apos(name))
        if key is None:
            raise SpecStructureError(f"Noma'lum so'z turkumi nomi vazn paragrafida: {name!r}")
        weights[key] = float(value)
        manba.append({"kalit": key, "docx_matn": raw.rstrip("."), "nomi": name,
                      "belgi": symbol, "vazn": float(value)})
    return weights, manba


def extract(docx_path: str) -> dict:
    from docx import Document

    doc = Document(docx_path)
    blocks = list(_iter_blocks(doc))

    paragraphs = [b.text for b in blocks if b.__class__.__name__ == "Paragraph"]
    title = [t for t in paragraphs[:2] if t.strip()]

    operators: list[dict] = []
    alifbo = None
    weights = weights_manba = None
    rules: list[dict] = []
    table_rows: dict[str, int] = {}
    current = None  # (pos, bolim_matni)
    table_no = 0

    for b in blocks:
        if b.__class__.__name__ == "Paragraph":
            t = b.text.strip()
            if not t:
                continue
            if t.startswith("KKT (") and "alifbosi" in t:
                alifbo = t
            if "raqamli vazn qiymatlari" in t:
                weights, weights_manba = _parse_weights(t)
            m = _HEADING_RE.match(t)
            if m:
                pos = _HEADING_TO_POS.get(_norm_apos(m.group(2)).upper())
                if pos is None:
                    raise SpecStructureError(f"Noma'lum bo'lim sarlavhasi: {t!r}")
                current = (pos, t)
            continue

        table_no += 1
        rows = [[c.text for c in r.cells] for r in b.rows]
        header = [_norm_apos(h).strip() for h in rows[0]]
        if header[:2] == ["Belgi", "Ma'nosi"]:
            operators = [{"belgi": r[0], "mano": r[1]} for r in rows[1:]]
            continue
        if header != ["№", "Qoida tavsifi", "Ingliz tilida misol", "O'zbek tilida misol"]:
            raise SpecStructureError(f"{table_no}-jadval sarlavhasi kutilmagan: {rows[0]!r}")
        if current is None:
            raise SpecStructureError(f"{table_no}-jadvaldan oldin bo'lim sarlavhasi topilmadi")
        pos, bolim = current
        table_rows[pos] = len(rows)
        for qator, r in enumerate(rows[1:], start=1):
            rid, tavsif, en, uz = r
            uid = rid if rid != "–" else f"–({pos})"
            rule = {"id": rid, "uid": uid, "pos": pos, "tavsif": tavsif,
                    "en_misol": en, "uz_misol": uz,
                    "bolim": bolim, "jadval": table_no, "qator": qator}
            izohlar = [x for x in (_concat_izoh(en), _concat_izoh(uz)) if x]
            if uid in _QOLDA_IZOHLAR:
                izohlar.append(_QOLDA_IZOHLAR[uid])
            if izohlar:
                rule["izoh"] = " | ".join(izohlar)
            rules.append(rule)
        current = None

    if len(operators) != 4:
        raise SpecStructureError(f"4 ta operator kutilgan edi, {len(operators)} ta topildi")
    if weights is None:
        raise SpecStructureError("Vazn paragrafi topilmadi")
    if sorted(table_rows) != sorted(_HEADING_TO_POS.values()):
        raise SpecStructureError(f"6 ta bo'lim jadvali kutilgan edi, topildi: {sorted(table_rows)}")
    uids = [r["uid"] for r in rules]
    if len(uids) != len(set(uids)):
        raise SpecStructureError("uid takrorlanmoqda")

    per_pos = {p: sum(1 for r in rules if r["pos"] == p) for p in table_rows}
    hujjat_izohlari = [
        f"Qoidalar soni: jami {len(rules)} ta ("
        + ", ".join(f"{p} {n}" for p, n in per_pos.items())
        + "). Jadvallarning SARLAVHA qatori bilan birga olingan qator soni esa "
        + ", ".join(f"{p} {n}" for p, n in table_rows.items())
        + f" = {sum(table_rows.values())} — ya'ni \"93 ta qoida\" soni sarlavha qatorlarini ham "
          "qo'shib sanalgan ko'rinadi.",
        "2 ta qatorda raqam o'rniga \"–\" turadi (Sifat va Ravish bo'limlarining birinchi qatori: "
        "\"Oddiy sifat\", \"Sodda ravish\"). Ular uchun `uid` = \"–(Sifat)\" / \"–(Ravish)\".",
        "Raqamlash uzluksiz emas: " + ", ".join(_missing_ids(rules)) + " raqamlari hujjatda yo'q.",
        "Fe'l bo'limida \"2.55a\" (need) va \"2.55b\" (gerund) — ikkita alohida qoida, \"2.55b\" "
        "jadvalda \"2.56\" dan KEYIN turadi.",
        "Vazn paragrafida Yordamchi so'z turkumlari uchun belgi \"U, L\" (ikkita) — bitta vazn (0.07).",
    ]

    return {
        "manba": {
            "fayl": os.path.relpath(docx_path, REPO_ROOT),
            "sha256": _sha256(docx_path),
            "hajm_bayt": os.path.getsize(docx_path),
            "repoda": False,
            "provenance": "Manba docx foydalanuvchi tomonidan 2026-09-11 da taqdim etilgan (asl nomi "
                          "KKT_qoidalari.docx). U dissertatsiya fayli kabi .gitignore'da — repoga "
                          "JOYLASHTIRILMAYDI; bu JSON undan ajratilgan nusxa. Mahalliy docx aynan shu "
                          "manba ekanini tekshirish: `shasum -a 256 data/kkt_qoidalari.docx` natijasi "
                          "yuqoridagi sha256 ga teng bo'lishi va `python scripts/extract_kkt_spec.py "
                          "--check` \"SINXRON\" berishi kerak.",
            "sarlavha": title,
            "izoh": "Docx'dan scripts/extract_kkt_spec.py bilan avtomatik ajratilgan. Matn maydonlari "
                    "aynan ko'chirilgan; `pos`, `uid` va `pos_weights` kalitlari — kod bilan solishtirish "
                    "uchun qo'shilgan kalitlar.",
        },
        "alifbo_tavsifi": alifbo,
        "operators": operators,
        "pos_weights": weights,
        "pos_weights_manba": weights_manba,
        "rules": rules,
        "sonlar": {
            "jami_qoida": len(rules),
            "pos_boyicha": per_pos,
            "jadval_qatorlari_sarlavha_bilan": table_rows,
        },
        "hujjat_izohlari": hujjat_izohlari,
    }


def dumps(spec: dict) -> str:
    return json.dumps(spec, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docx", default=DEFAULT_DOCX)
    ap.add_argument("--out", default=DEFAULT_JSON)
    ap.add_argument("--check", action="store_true",
                    help="Yozmaydi — mavjud JSON docx'dan qayta ajratilgan natija bilan bir xilmi, tekshiradi")
    args = ap.parse_args()

    if not os.path.exists(args.docx):
        print(f"XATO: {args.docx} topilmadi.", file=sys.stderr)
        return 1
    text = dumps(extract(args.docx))

    if args.check:
        with open(args.out, encoding="utf-8") as f:
            same = f.read() == text
        print("SINXRON" if same else f"FARQ BOR: {args.out} docx bilan mos emas — qayta ishga tushiring.")
        return 0 if same else 1

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    spec = json.loads(text)
    print(f"[yozildi: {args.out}] — {spec['sonlar']['jami_qoida']} qoida, "
          f"{len(spec['operators'])} operator, {len(spec['pos_weights'])} vazn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
