"""
tests/conftest.py
==================
pytest umumiy sozlamalari.

MUHIM (reports/faza_0.md dagi hodisaga qarang): `translate_phrase()` /
`smart_parse()` mantig'i **yon ta'sirga ega** — noma'lum ko'plik shakllarini
(masalan "books") avtomatik xulosa chiqarib, natijani `db_insert(..., "auto")`
orqali TO'G'RIDAN-TO'G'RI `.db` fayllarga YOZIB QO'YADI. Birinchi marta test
yozilganda aynan shu sabab bilan repo ildizidagi HAQIQIY `.db` fayllar bir
marta pytest ishga tushirilganda "ifloslangan" edi (git tarixi bilan solishtirib
aniqlangan, keyin `git checkout` bilan tuzatilgan — qarang reports/faza_0.md).

Shuning uchun testlar HECH QACHON repo ildizidagi `.db` fayllarga bevosita
tegmaydi: har bir test sessiyasi uchun `kkt_v20_soz_tartibi.py`, `data_loader.py`
va `data/` papkasi **vaqtinchalik, izolyatsiyalangan papkaga** nusxalanadi,
bazalar o'sha yerda noldan quriladi va modul O'SHA nusxadan import qilinadi
(`SCRIPT_DIR` — modul joylashgan papka bo'lgani uchun, izolyatsiya avtomatik
ta'minlanadi). Repo ildizidagi haqiqiy `.db` fayllar testlar davomida umuman
ochilmaydi.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_COPY_ITEMS = ["kkt_v20_soz_tartibi.py", "data_loader.py", "data"]


def _make_isolated_copy(dest: str) -> None:
    for item in _COPY_ITEMS:
        src = os.path.join(REPO_ROOT, item)
        dst = os.path.join(dest, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def _build_databases(m) -> None:
    """`scripts/build_db.py` bilan bir xil ketma-ketlik (GUI'siz) — izolyatsiya
    qilingan modul nusxasi ustida ishlaydi. Ketma-ketlik main()'dagi bilan
    aynan mos kelishi kerak (Faza 1 da ikkalasi bitta yordamchi funksiyaga
    birlashtirilishi mumkin)."""
    m._safe_step("init_all_databases", m.init_all_databases)
    docx_path = m._safe_step("find_docx", m.find_docx) if m.HAS_DOCX else None
    m._safe_step("setup_database", m.setup_database, docx_path)
    m._safe_step("load_xlsx_affixes", m.load_xlsx_affixes)
    bz_path = m._safe_step("find_bazalar_docx", m.find_bazalar_docx)
    if bz_path:
        m._safe_step("load_bazalar_docx", m.load_bazalar_docx, bz_path)
    m._safe_step("seed_core_demo_data", m.seed_core_demo_data)
    bazalar2_path = m._safe_step("find_bazalar_affixes_docx", m.find_bazalar_affixes_docx)
    if bazalar2_path:
        m._safe_step("load_bazalar_affixes_docx", m.load_bazalar_affixes_docx, bazalar2_path)
    m._safe_step("load_pdf_kkt_bazalar", m.load_pdf_kkt_bazalar)
    m._safe_step("load_ch2_evx_examples", m.load_ch2_evx_examples)
    m._safe_step("resync_all_ids", m.resync_all_ids)
    m._safe_step("mdb_seed_if_empty", m.mdb_seed_if_empty)


@pytest.fixture(scope="session")
def isolated_kkt_module():
    """Butun test sessiyasi uchun BITTA marta: izolyatsiyalangan nusxa
    yaratadi, bazalarni o'sha yerda noldan quradi va modulni o'sha nusxadan
    import qilib qaytaradi. Repo ildizidagi haqiqiy `.db` fayllarga hech qanday
    yozuv bo'lmaydi."""
    tmp_dir = tempfile.mkdtemp(prefix="kkt_test_isolated_")
    _make_isolated_copy(tmp_dir)

    # Modul va tkinter keshini tozalab, izolyatsiyalangan papkani sys.path
    # boshiga qo'yamiz — shunda `import kkt_v20_soz_tartibi` aynan shu
    # nusxadan import bo'ladi (REPO_ROOT dagi asl fayldan emas).
    for name in list(sys.modules):
        if name in ("kkt_v20_soz_tartibi", "data_loader"):
            del sys.modules[name]
    sys.path.insert(0, tmp_dir)

    import kkt_v20_soz_tartibi as m

    assert m.SCRIPT_DIR == tmp_dir, (
        "Modul SCRIPT_DIR izolyatsiyalangan nusxaga emas, repo ildiziga "
        "ishora qilyapti — testlar haqiqiy .db fayllarni buzishi mumkin edi!"
    )

    _build_databases(m)

    yield m

    sys.path.remove(tmp_dir)
    for name in list(sys.modules):
        if name in ("kkt_v20_soz_tartibi", "data_loader", "build_db_for_tests"):
            del sys.modules[name]
    shutil.rmtree(tmp_dir, ignore_errors=True)
