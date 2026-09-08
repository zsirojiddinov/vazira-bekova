"""
tests/test_smoke.py
====================
Faza 0 infratuzilma testlari. Bu yerda tarjima SIFATI tekshirilmaydi (buni
Faza 1 dagi to'liq regression harness qiladi) — faqat:
  1) modul odatdagi (tkinter mavjud) muhitda import bo'lishi va asosiy
     funksiyalar mavjudligi;
  2) modul tkinter MAVJUD BO'LMAGAN muhitda ham (HAS_TK=False) importda
     yiqilmasligi va translate_phrase() baribir ishlashi
     ("GUI ni mantiqdan ajratish" talabi — Faza 0, 50/51-bandlar).

DIQQAT: `translate_phrase()`/`smart_parse()` NOMA'LUM SO'ZLARNI (masalan
ko'plik shakllarini) avtomatik xulosa chiqarib bazaga YOZIB QO'YADI
(`db_insert(..., "auto")` — yon ta'sir). Shu sabab HECH BIR test repo
ildizidagi haqiqiy `.db` fayllarga bevosita tegmaydi — hammasi
`conftest.py`dagi `isolated_kkt_module` orqali izolyatsiyalangan nusxada
ishlaydi (qarang: reports/faza_0.md, "tests repo db fayllarini ifloslagan
edi" hodisasi).
"""
from __future__ import annotations

import builtins
import os
import sys

from conftest import REPO_ROOT, _build_databases, _make_isolated_copy


def test_module_imports_normally(isolated_kkt_module):
    m = isolated_kkt_module
    assert callable(m.translate_phrase)
    assert callable(m.smart_parse)
    assert callable(m.uz_stem)
    assert callable(m.translate_phrase_kkt)
    assert callable(m.translate_phrase_general)
    assert m.HAS_TK is True  # bu muhitda tkinter mavjud


def test_translate_phrase_runs_in_isolation(isolated_kkt_module, tmp_path):
    """translate_phrase() chaqirilganda repo ildizidagi haqiqiy .db fayllar
    o'zgarmasligini alohida tekshiradi (izolyatsiya kafolati)."""
    real_db_before = {
        f: os.path.getmtime(os.path.join(REPO_ROOT, f))
        for f in ("UB_en_w.db", "UB_uz_w.db")
        if os.path.exists(os.path.join(REPO_ROOT, f))
    }

    m = isolated_kkt_module
    result = m.translate_phrase("from our books")
    assert result is not None

    real_db_after = {
        f: os.path.getmtime(os.path.join(REPO_ROOT, f))
        for f in ("UB_en_w.db", "UB_uz_w.db")
        if os.path.exists(os.path.join(REPO_ROOT, f))
    }
    assert real_db_before == real_db_after, (
        "translate_phrase() repo ildizidagi HAQIQIY .db fayllarga tegdi — "
        "izolyatsiya buzilgan!"
    )


def test_module_imports_and_translates_without_tkinter(tmp_path, monkeypatch):
    """tkinter o'rnatilmagan/mavjud bo'lmagan muhitni simulyatsiya qiladi
    (masalan Tk kutubxonasi bo'lmagan CI konteyneri) va tarjima mantig'i
    baribir ishlashini tasdiqlaydi. Bu ham OʻZ ALOHIDA izolyatsiyalangan
    nusxasida ishlaydi — repo ildiziga tegmaydi."""
    dest = tmp_path / "isolated_no_tk"
    dest.mkdir()
    _make_isolated_copy(str(dest))

    for name in list(sys.modules):
        if name in ("kkt_v20_soz_tartibi", "data_loader") or name == "tkinter" or name.startswith("tkinter."):
            monkeypatch.delitem(sys.modules, name, raising=False)

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "tkinter" or name.startswith("tkinter."):
            raise ImportError("tkinter yo'q (test simulyatsiyasi)")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.syspath_prepend(str(dest))

    import kkt_v20_soz_tartibi as m

    assert m.HAS_TK is False, "tkinter yo'q holatda HAS_TK True bo'lib qoldi"
    assert m.SCRIPT_DIR == str(dest), "izolyatsiya buzilgan — repo ildizi ishlatildi"

    _build_databases(m)

    result = m.translate_phrase("from our books")
    assert result is not None
    assert "natija" in result

    # main() tkinter yo'qligida xato bilan yiqilmasdan, aniq xabar bilan
    # to'xtashi kerak (GUI ochilmaydi, lekin dastur qulamaydi).
    monkeypatch.setattr(m, "_safe_step", lambda label, fn, *a, **kw: None)
    m.main()  # exception chiqarmasligi kerak

    for name in list(sys.modules):
        if name in ("kkt_v20_soz_tartibi", "data_loader") or name == "tkinter" or name.startswith("tkinter."):
            monkeypatch.delitem(sys.modules, name, raising=False)
