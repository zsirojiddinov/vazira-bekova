"""
tests/test_readonly_mode.py
============================
`readonly_mode()` / `translate_phrase(text, allow_write=False)` uchun
testlar. Foydalanuvchi so'rovi bo'yicha (Faza 0 dan keyingi qo'shimcha):
o'lchov/audit skriptlari tarjima chaqirganda .db fayllarga yozmasligini
KAFOLATLAYDI, lekin keshlash MANTIG'INI (vazn/kkt_symbol hisoblash) EMAS —
shu sabab tarjima natijasi (matn) ikkala holatda ham bir xil bo'lishi
alohida tekshiriladi.

Har bir test o'zining ALOHIDA izolyatsiyalangan nusxasida ishlaydi (repo
ildizidagi haqiqiy .db fayllarga tegmaydi — sabab: reports/faza_0.md).
"""
from __future__ import annotations

import sqlite3
import sys

import pytest

from conftest import _build_databases, _make_isolated_copy

TEXT = "from our books"  # Faza 0'da aynan shu matn db_insert("books","kitoblar","Ot","auto")
                          # yon ta'sirini yuzaga chiqargani empirik tasdiqlangan.


def _import_fresh(dest):
    """Berilgan (allaqachon _make_isolated_copy bilan to'ldirilgan) papkadan
    modulni TOZA holda import qiladi va bazani noldan quradi."""
    for name in list(sys.modules):
        if name in ("kkt_v20_soz_tartibi", "data_loader"):
            del sys.modules[name]
    sys.path.insert(0, str(dest))
    import kkt_v20_soz_tartibi as m
    assert m.SCRIPT_DIR == str(dest), "izolyatsiya buzilgan"
    _build_databases(m)
    return m


def _cleanup_module():
    for name in list(sys.modules):
        if name in ("kkt_v20_soz_tartibi", "data_loader"):
            del sys.modules[name]


def _counts(m):
    """(so'zlar soni UB_en_w'da, affikslar soni QM_en_w'da) — yozuv
    yon ta'sirini kuzatish uchun."""
    con = sqlite3.connect(m.DB_UB_EN)
    n_words = con.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    con.close()
    con = sqlite3.connect(m.DB_QM_EN)
    n_aff = con.execute("SELECT COUNT(*) FROM affixes").fetchone()[0]
    con.close()
    return (n_words, n_aff)


@pytest.fixture()
def fresh_module_factory(tmp_path):
    """Har chaqirilganda YANGI, mustaqil izolyatsiyalangan modul nusxasini
    beradi (bir testda bir nechta mustaqil "muhit" kerak bo'lganda)."""
    counter = {"n": 0}

    def _make():
        counter["n"] += 1
        dest = tmp_path / f"env_{counter['n']}"
        dest.mkdir()
        _make_isolated_copy(str(dest))
        return _import_fresh(dest)

    yield _make
    _cleanup_module()


def test_normal_mode_writes_to_db(fresh_module_factory):
    """Baseline/regression tekshiruvi: readonly qo'shilgach ham ODDIY
    (yozishga ruxsat berilgan) rejimda keshlash ISHLASHDA DAVOM ETISHI
    kerak — aks holda bu funksionallik kutilmasdan o'chib qolgan bo'ladi."""
    m = fresh_module_factory()
    before = _counts(m)
    m.translate_phrase(TEXT)
    after = _counts(m)
    assert after != before, (
        "Normal rejimda ham baza o'zgarmadi — yoki bu inputning yon ta'sir "
        "xatti-harakati o'zgargan, yoki readonly himoyasi normal rejimda ham "
        "yozishni bloklab qo'yayapti (regressiya)."
    )


def test_readonly_mode_blocks_writes(fresh_module_factory):
    m = fresh_module_factory()
    before = _counts(m)
    with m.readonly_mode():
        m.translate_phrase(TEXT)
    after = _counts(m)
    assert after == before, "readonly_mode() ichida baza baribir o'zgardi!"


def test_readonly_mode_preserves_translation_output(fresh_module_factory):
    """Eng muhim tekshiruv: yozish yoqilgan/o'chirilganidan qat'i nazar
    TARJIMA NATIJASI bir xil bo'lishi kerak (readonly faqat yon ta'sirni
    o'chiradi, algoritm natijasini emas). Ikki MUSTAQIL (bir-biriga
    ta'sir qilmaydigan) muhitda solishtiriladi."""
    m_rw = fresh_module_factory()
    result_rw = m_rw.translate_phrase(TEXT)

    m_ro = fresh_module_factory()
    with m_ro.readonly_mode():
        result_ro = m_ro.translate_phrase(TEXT)

    assert result_rw is not None and result_ro is not None
    assert result_rw == result_ro, (
        "readonly_mode() tarjima NATIJASINI o'zgartirib qo'ydi — bu faqat "
        "yon ta'sirni (bazaga yozishni) o'chirishi kerak edi."
    )


def test_translate_phrase_allow_write_false_matches_readonly_mode(fresh_module_factory):
    """translate_phrase(text, allow_write=False) — readonly_mode() ning
    qulay yorlig'i — bir xil natija berishi kerak."""
    m1 = fresh_module_factory()
    with m1.readonly_mode():
        expected = m1.translate_phrase(TEXT)

    m2 = fresh_module_factory()
    before = _counts(m2)
    actual = m2.translate_phrase(TEXT, allow_write=False)
    after = _counts(m2)

    assert after == before, "allow_write=False bo'lsa ham baza o'zgardi!"
    assert actual == expected


def test_readonly_mode_nesting_and_recovery(fresh_module_factory):
    """Ichma-ich (nested) readonly_mode() chaqiruvlari xavfsiz, va tashqi
    blokdan chiqilgach yozish rejimi ODDIY holatga qaytadi (bloklanib
    qolmaydi)."""
    m = fresh_module_factory()
    assert m.is_readonly() is False

    with m.readonly_mode():
        assert m.is_readonly() is True
        with m.readonly_mode():
            assert m.is_readonly() is True
        assert m.is_readonly() is True  # ichki blok tugagach ham tashqisi davom etadi

    assert m.is_readonly() is False

    # readonly blokidan chiqqandan keyin oddiy yozish ISHLASHI kerak
    # (readonly holati "yopishib qolmagan" ekanini tasdiqlaydi)
    with m.readonly_mode():
        pass  # depth 0 ga qaytadi
    before = _counts(m)
    m.translate_phrase(TEXT)
    after = _counts(m)
    assert after != before, "readonly_mode() dan chiqqandan keyin ham yozish bloklanib qoldi!"
