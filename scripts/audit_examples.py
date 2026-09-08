#!/usr/bin/env python3
"""
scripts/audit_examples.py
============================
Dissertatsiyaning II bobidagi HAR BIR misolni topib, dasturdan o'tkazib,
kirish/chiqish mosligini tekshiradi.

MANBA HAQIDA MUHIM ESLATMA:
  Topshiriq "II bob misollarini docx dan ajratib olish" deydi. Bu repoda
  o'sha xom docx ("so_zlar_bazasi_un.docx") HOZIRCHA YO'Q — lekin uning
  MAZMUNI allaqachon `kkt_v20_soz_tartibi.py` ichida `CH2_EVX_EXAMPLES`
  nomli literal Python ro'yxati sifatida bor: funksiya docstringi ("52 ta
  ingliz-o'zbek EVXs/EVIXs namuna so'z ... so_zlar_bazasi_un.docx'dan
  ajratib olingan") buni tasdiqlaydi — bu ro'yxat DISSERTATSIYA MATNIDAN
  QO'LDA (dastur muallifi tomonidan, Claude tomonidan EMAS) ko'chirilgan.
  Shu sabab bu skript ASOSIY manba sifatida O'SHA ro'yxatni ishlatadi —
  qayta to'qimaydi, faqat MAVJUDINI o'qiydi va tekshiradi (Qoida 1).

  Agar kelajakda haqiqiy "so_zlar_bazasi_un.docx" fayli repoga qo'shilsa
  (`--docx` bilan yoki find_ch2_examples_docx() orqali avtomatik topilsa),
  skript buni ALOHIDA hujjatlaydi (qarang --docx bo'limi pastda) — lekin
  xom docx JADVAL TUZILISHINI hozircha tekshirish imkoni yo'q (fayl yo'q),
  shuning uchun undan avtomatik qayta-ajratib-olish BU FAZADA amalga
  oshirilmagan (ochiq qoldirilgan, Faza 1 hisobotida qayd etiladi).

Ishlatish:
    python scripts/audit_examples.py
    python scripts/audit_examples.py --out reports/faza_1_audit_examples.md
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

from _common import normalize  # noqa: E402

# Topshiriqda ANIQ nomlab o'tilgan, avval qo'lda topilgan muammoli
# misollar — shu ro'yxatda albatta topilishi (va joriy holatda ko'pincha
# mos kelmasligi) kutiladi. Bu FAQAT tekshiruv uchun eslatma, gold qiymat
# emas (gold qiymat — CH2_EVX_EXAMPLES ichidagi "uz" maydoni, o'zi).
NAMED_IN_TASK = {"capabilityies", "leafes", "schoolboys", "more comfortable"}


def run(out_path: str | None) -> int:
    import kkt_v20_soz_tartibi as m

    examples = m.CH2_EVX_EXAMPLES
    total = len(examples)

    docx_path = m._safe_step("so_zlar_bazasi_un.docx qidirish", m.find_ch2_examples_docx)
    docx_note = (
        f"Topildi: `{os.path.relpath(docx_path, REPO_ROOT)}` — LEKIN bu skript hozircha "
        f"undan avtomatik qayta ajratib olmaydi (jadval tuzilishi tasdiqlanmagan, qo'lda "
        f"tekshirish talab qilinadi, Faza 1 doirasidan tashqarida)."
        if docx_path else
        "Topilmadi (`so_zlar_bazasi_un.docx` repoda yo'q) — quyidagi natija to'liq "
        "`kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` literal ro'yxatiga asoslangan."
    )

    results = []
    for ex in examples:
        en = ex["en"]
        ref = ex["uz"]
        with m.readonly_mode():
            r = m.translate_phrase(en, allow_write=False)
            sp = m.smart_parse(en)
        hyp = r["natija"] if r else None
        # MUHIM METODOLOGIK OGOHLANTIRISH: load_ch2_evx_examples() bu
        # ro'yxatning HAR BIR "en" so'zini UB_en_w'ga TO'G'RIDAN-TO'G'RI
        # headword sifatida (source='chapter2_evx') YOZIB QO'YGAN. Shu
        # sabab BITTA-SO'ZLI misollar uchun translate_phrase() "to'g'ri"
        # javob bersa ham, bu ko'pincha MORFOLOGIK DERIVATSIYA emas — bu
        # xuddi shu jadvaldan TO'G'RIDAN-TO'G'RI o'qib qaytarish (aylanma/
        # circular tekshiruv). Haqiqiy derivatsiya bo'lgan-bo'lmaganini
        # smart_parse().method orqali bilib olamiz.
        is_direct_seed_hit = sp.get("method") == "UB_en_w[ID]→UB_uz_w[ID]"
        results.append({
            **ex,
            "hypothesis": hyp,
            "is_direct_seed_hit": is_direct_seed_hit,
            "match_raw": hyp == ref,
            "match_normalized": hyp is not None and normalize(hyp) == normalize(ref),
        })

    n_match = sum(1 for r in results if r["match_normalized"])
    n_match_direct = sum(1 for r in results if r["match_normalized"] and r["is_direct_seed_hit"])
    n_match_derived = n_match - n_match_direct
    n_none = sum(1 for r in results if r["hypothesis"] is None)
    n_wrong = total - n_match - n_none

    found_named = {r["en"] for r in results if r["en"] in NAMED_IN_TASK}
    missing_named = NAMED_IN_TASK - found_named

    lines = []
    lines.append("# II bob misollari auditi (CH2_EVX_EXAMPLES)")
    lines.append("")
    lines.append(f"**Generatsiya vaqti:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}Z")
    lines.append(f"**Manba:** `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` ({total} ta misol)")
    lines.append(f"**Buyruq:** `python scripts/audit_examples.py`")
    lines.append("**Rejim:** `translate_phrase(text, allow_write=False)` — bazaga yozilmagan.")
    lines.append("")
    lines.append(f"**so_zlar_bazasi_un.docx qidiruvi:** {docx_note}")
    lines.append("")
    lines.append("## MUHIM METODOLOGIK OGOHLANTIRISH — aylanma (circular) tekshiruv xavfi")
    lines.append("")
    lines.append(
        "`load_ch2_evx_examples()` shu RO'YXATNING HAR BIR so'zini `UB_en_w`ga "
        "TO'G'RIDAN-TO'G'RI headword sifatida (`source='chapter2_evx'`) yozib qo'yadi. "
        "Shu sabab BITTA-SO'ZLI misol uchun `translate_phrase()` \"to'g'ri\" javob bersa "
        "ham, bu ko'pincha morfologik DERIVATSIYA emas — tizim shu jadvaldan "
        "TO'G'RIDAN-TO'G'RI o'qib qaytaryapti (aylanma tekshiruv: ma'lumot qayerdan "
        "kelgan bo'lsa, o'sha yerga solishtirilyapti). Har bir moslik pastda ikkiga "
        "ajratilgan: **to'g'ridan (aylanma, past ishonchli)** va **derivatsiya orqali "
        "(haqiqiy morfologik test)**."
    )
    lines.append("")
    lines.append("## Umumiy natija")
    lines.append("")
    lines.append(f"- Jami: **{total}**")
    lines.append(f"- Aniq mos (normalizatsiya bilan): **{n_match}/{total}**")
    lines.append(f"  - shundan to'g'ridan (aylanma, CH2_EVX_EXAMPLES headword sifatida "
                  f"o'zi ham bor): **{n_match_direct}**")
    lines.append(f"  - shundan HAQIQIY derivatsiya orqali (affiks/o'zak ajratish ishlagan): "
                  f"**{n_match_derived}**")
    lines.append(f"- `None` qaytardi: **{n_none}/{total}**")
    lines.append(f"- Natija qaytardi, lekin matn mos emas: **{n_wrong}/{total}**")
    lines.append("")
    lines.append("## Topshiriqda nomlab o'tilgan misollar")
    lines.append("")
    lines.append(
        "Topshiriq matni: *\"capabilityies, leafes, schoolboys, more comfortable, will "
        "return shu yo'l bilan topilishi kerak edi\"*. Tekshiruv:"
    )
    lines.append("")
    for en in sorted(NAMED_IN_TASK):
        if en not in found_named:
            lines.append(f"- `{en}` — CH2_EVX_EXAMPLES da TOPILMADI (bu 4 tadan tashqarida).")
            continue
        r = next(x for x in results if x["en"] == en)
        if r["match_normalized"] and r["is_direct_seed_hit"]:
            status = "MOS KELDI, LEKIN AYLANMA (to'g'ridan bazadan, morfologik derivatsiya EMAS)"
        elif r["match_normalized"]:
            status = "MOS KELDI, HAQIQIY DERIVATSIYA ORQALI"
        else:
            status = "MOS EMAS (kutilgan edi)"
        lines.append(f"- `{en}` -> etalon `{r['uz']!r}`, joriy chiqish `{r['hypothesis']!r}` — **{status}**")
    if missing_named:
        lines.append("")
        lines.append(f"DIQQAT: `will return` CH2_EVX_EXAMPLES da yo'q (faqat modal fe'l "
                      f"\"will\" alohida bor, \"will return\" ibora sifatida emas) — bu "
                      f"topshiriqdagi tavsif bilan bevosita mos kelmaydi, alohida "
                      f"tests/test_translate_phrase_general.py::test_will_return_modal_verb_returns_none "
                      f"da tekshirilgan.")
    lines.append("")
    lines.append("## Mos kelmagan barcha qatorlar")
    lines.append("")
    lines.append("| Ingliz | Etalon (uz) | Chiqish | POS |")
    lines.append("|---|---|---|---|")
    for r in results:
        if r["match_normalized"]:
            continue
        lines.append(f"| {r['en']} | {r['uz']} | {r['hypothesis']!r} | {r['pos']} |")
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
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "reports", "faza_1_audit_examples.md"))
    ap.add_argument("--no-out", action="store_true")
    args = ap.parse_args()
    return run(None if args.no_out else args.out)


if __name__ == "__main__":
    raise SystemExit(main())
