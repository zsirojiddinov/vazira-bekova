#!/usr/bin/env python3
"""
scripts/build_db.py
====================
`kkt_v20_soz_tartibi.py` ichidagi baza-to'ldirish funksiyalarini GUI (Tkinter
mainloop) ochmasdan, buyruq qatoridan ishga tushiradi — `make db` shu skriptni
chaqiradi.

Bu skript `main()` dagi bazani to'ldirish ketma-ketligini AYNAN takrorlaydi
(faqat oxiridagi `MTSystem().mainloop()` chaqiruvi olib tashlangan) — birorta
ham tarjima/baza mantig'i bu yerda qayta yozilmagan, faqat mavjud funksiyalar
chaqiriladi.

DIQQAT (reports/db_reproducibility.md): `data_loader.py` skript bilan bir xil
papkada (repo ildizida) bo'lishi SHART — bo'lmasa `setup_database()` va
`load_xlsx_affixes()` jimgina docx/xlsx zaxira yo'liga tushib, BOSHQA sonlar
beradi (bu haqda ogohlantirish konsolga chiqariladi, lekin dastur to'xtamaydi).

Ishlatish:
    python scripts/build_db.py
    # yoki
    make db
"""
from __future__ import annotations

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, REPO_ROOT)


def main() -> int:
    if not os.path.exists(os.path.join(REPO_ROOT, "data_loader.py")):
        print("  [OGOHLANTIRISH] data_loader.py repo ildizida topilmadi — "
              "so'z/affiks yuklash docx/xlsx zaxira yo'liga o'tadi va "
              "natijalar git'dagi .db fayllardan FARQ QILISHI mumkin "
              "(qarang: reports/db_reproducibility.md).")

    import kkt_v20_soz_tartibi as m

    print("=" * 65)
    print("  Baza qurish (GUI'siz) — scripts/build_db.py")
    print("  Skript papkasi (bazalar shu yerga yoziladi):", m.SCRIPT_DIR)
    print("=" * 65)

    m._safe_step("Bazalarni ishga tushirish (init_all_databases)", m.init_all_databases)

    need_rebuild = not all(
        os.path.exists(p) for p in (m.DB_UB_EN, m.DB_UB_UZ, m.DB_QM_EN, m.DB_QM_UZ)
    )
    if not need_rebuild:
        s = m._safe_step("Baza statistikasi (db_stats)", m.db_stats) or {"total": 0}
        if s.get("total", 0) == 0:
            need_rebuild = True
        else:
            print(f"  UB_en_w/UB_uz_w: {s['total']} so'z | "
                  f"QM_en_w:{s['aff_en']} QM_uz_w:{s['aff_uz']}")

    if need_rebuild:
        docx_path = m._safe_step("DOCX qidirish (find_docx)", m.find_docx) if m.HAS_DOCX else None
        if docx_path:
            print("  Topildi: " + os.path.basename(docx_path))
        else:
            print(f"  DIQQAT: {m.DOCX_CANDIDATES[0]} topilmadi.")
        n = m._safe_step("Baza to'ldirish (setup_database)", m.setup_database, docx_path) or 0
        if n > 0:
            print(f"  {n} ta so'z UB_en_w/UB_uz_w ga yuklandi.")
        n2 = m._safe_step("Excel/JSON affikslari (load_xlsx_affixes)", m.load_xlsx_affixes) or 0
        print(f"  {n2} ta affiks QM_en_w ga yuklandi.")

    bz_path = m._safe_step("bazalar_ma_lumot_09.docx qidirish", m.find_bazalar_docx)
    if bz_path:
        r = m._safe_step("bazalar_ma_lumot_09.docx yuklash", m.load_bazalar_docx, bz_path)
        if r:
            print(f"  BM belgilar:+{r['symbols']}  QM_en_w:+{r['aff_en']}  "
                  f"QM_uz_w:+{r['aff_uz']}  UB so'zlar:+{r['words']}")

    n3 = m._safe_step("Zaxira lug'at (seed_core_demo_data)", m.seed_core_demo_data) or 0
    if n3:
        print(f"  Zaxira lug'at: {n3} ta asosiy so'z qo'shildi.")

    bazalar2_path = m._safe_step("bazalar_ma_lumot_09_07.docx qidirish", m.find_bazalar_affixes_docx)
    if bazalar2_path:
        m._safe_step("bazalar_ma_lumot_09_07.docx yuklash", m.load_bazalar_affixes_docx, bazalar2_path)

    pdf_r = m._safe_step("PDF manba (load_pdf_kkt_bazalar)", m.load_pdf_kkt_bazalar)
    if pdf_r:
        print(f"  KKT belgilar +{pdf_r['symbols']}, QM_en_w affikslar +{pdf_r['affixes_en']}")

    ch2_r = m._safe_step("II bob namunalari (load_ch2_evx_examples)", m.load_ch2_evx_examples)
    if ch2_r:
        print(f"  UB so'zlar +{ch2_r['words']}, BM formal modellar +{ch2_r['models']}, "
              f"grammatik qoidalar +{ch2_r['rules']}")

    rr = m._safe_step("ID sinxronlash (resync_all_ids)", m.resync_all_ids)
    if rr:
        print(f"  ID sinxronlandi — so'zlar EN:{rr['words_en']} UZ:{rr['words_uz']} | "
              f"qo'shimchalar EN:{rr['aff_en']} UZ:{rr['aff_uz']}")

    mdb_added = m._safe_step("MDB_uz_w to'ldirish (mdb_seed_if_empty)", m.mdb_seed_if_empty) or 0
    if mdb_added:
        print(f"  MDB_uz_w: {mdb_added} ta nomzod qo'shildi.")

    s = m._safe_step("Yakuniy baza statistikasi (db_stats)", m.db_stats) or {}
    print("=" * 65)
    print("  Yakuniy statistika:", s)
    print("  Tayyor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
