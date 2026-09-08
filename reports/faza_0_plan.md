# Faza 0 — reja (kod yozilishidan oldin)

## 1. Repozitoriyani o'qishdan chiqqan aniqliklar (taqriz vazifasidagi tavsifdan farqlar)

Ishga tushirishdan oldin quyidagilar tasdiqlanishi/eslatilishi kerak, chunki topshiriqdagi
tavsif bilan haqiqiy holat bir necha joyda farq qiladi:

- `kkt_v20_soz_tartibi.py` — haqiqiy uzunligi **3532 qator** (topshiriqda 3329 deyilgan).
  Aniqlangan `def` soni: **91** — bu mos keladi.
- Manba fayllar nomi topshiriqdagidan farqli:
  - `1500_EN_UZ_6_POS_sorted.20.docx` (topshiriqda `..._sorted_20.docx` — pastki chiziq/nuqta farqi)
  - `100_soz.docx` (topshiriqda `100_ta_lug_at.docx`)
  - Qo'shimcha: `data/KKT_Terminologik_Lugat.docx` — bu ham mavjud, topshiriqda tilga olingan
    "KKT terminologik lug'at" shu bo'lsa kerak.
- `data/` papkasida docx fayllarning tayyor **JSON konvertatsiyalari** allaqachon bor
  (`data_loader.py` shularni o'qiydi) — ya'ni docx → JSON konvertatsiya avval qo'lda/skript bilan
  qilingan. `kkt_v20_soz_tartibi.py` ning o'zi esa **docx fayllarni to'g'ridan-to'g'ri** o'qiydi
  (`load_bazalar_docx`, `_load_words_from_docx` va h.k.) — ikkita mustaqil yo'l bor: `data_loader.py`
  (JSON asosida, alohida, hozircha asosiy dastur uni chaqirmaydi) va `kkt_v20_soz_tartibi.py`
  ichidagi docx-o'qish. Bu ikkalasi hozircha bog'lanmagan — Faza 0 bu holatni **o'zgartirmaydi**,
  faqat hujjatlashtiradi (README'da).
- 9 ta `.db` fayl **hozir git'ga commit qilingan** (`git ls-files` tasdiqlaydi). Qoidaga ko'ra
  (`*.db generatsiya qilinadi, saqlanmaydi`) bularni `.gitignore` ga qo'shib, `git rm --cached`
  bilan repodan chiqarish kerak — lokal fayllar diskda qoladi, faqat git tracking to'xtaydi.
- Muhit: Python **3.14.0** (`.venv`, framework build), SQLite **3.51.0** (2025-06-12), macOS
  Darwin 25.4.0 arm64. O'rnatilgan paketlar (`pip list`): `python-docx 1.2.0`, `openpyxl 3.1.5`,
  `nltk 3.10.3`, `lxml 6.1.3`, `regex`, `click`, `joblib`, `tqdm`, `defusedxml`, `et_xmlfile`,
  `typing_extensions`, `cloudpickle`. **`pytest` o'rnatilmagan** — Faza 0 da qo'shiladi.
- `tkinter` import qilinganda xato bermaydi (mahalliy muhitda mavjud) — lekin butun fayl
  modul darajasida `import tkinter as tk` va `from tkinter import ttk, filedialog, messagebox`
  qiladi. Tekshirilgan natija: GUI klassi (`MTSystem`, 3102-qatordan) va `main()` dan tashqarida,
  ya'ni tarjima mantig'i funksiyalarida (`translate_phrase*`, `smart_parse`, `uz_stem`,
  `_chunk_phrase` va h.k.) `tk.`/`messagebox.`/`ttk.` ga to'g'ridan-to'g'ri chaqiruv **yo'q**.
  Yagona bog'liqlik — modul yuklanayotganda tkinter **import qilinishining o'zi** (agar CI
  konteynerida Tk kutubxonasi bo'lmasa, `import tkinter` xato beradi va butun fayl, demak
  tarjima funksiyalari ham, yuklanmay qoladi). Demak minimal, xavfsiz tuzatish: tkinter
  importini **ixtiyoriy** qilish (xuddi nltk importi try/except bilan o'ralganidek), `MTSystem`
  klassini va GUI-bog'liq kodni faqat tk mavjud bo'lganda ishlatish. Bu **mantiqni qayta yozish
  emas** — faqat import chegarasini qattiqlashtiradi, shuning uchun Qoida 6 ga zid emas.
- `nltk` wordnet korpusi mahalliy diskda hali yuklanmagan (`~/nltk_data` bo'sh) — birinchi
  ishga tushirishda tarmoqqa 3 soniyalik urinish bo'ladi (mavjud kod shuni allaqachon vaqt
  chegarasi bilan himoya qilgan, `USE_LEMMA=False` fallback bilan). CI da tarmoq yo'q bo'lsa
  ham dastur ishlashi kerak — buni testda tekshiramiz (Faza 1), Faza 0 da faqat hujjatlashtiramiz.

## 2. Faza 0 doirasida qilinadigan ishlar (aniq fayllar)

1. **`requirements.txt`** — hozirgi `.venv` dagi aniq versiyalar bilan (`python-docx==1.2.0`,
   `openpyxl==3.1.5`, `nltk==3.10.3`, `lxml==6.1.3`) + test uchun `pytest` (yangi qo'shiladi,
   versiyasi o'rnatilgandan keyin pin qilinadi).
2. **`README.md`** — bo'limlar: talab qilinadigan Python versiyasi (3.14, framework build —
   tkinter shu bilan keladi), kutubxonalar ro'yxati, SQLite versiyasi, sinovdan o'tgan OT
   (macOS 15/Darwin 25.4, arm64), ishga tushirish tartibi (`python kkt_v20_soz_tartibi.py`),
   qaysi manba fayllar `data/` da kerakligi (aniq fayl nomlari, docx **va** mos json juftlari),
   `make db` bilan bazani noldan qurish, testlarni ishga tushirish (`pytest`).
3. **`.gitignore`** — `*.db` qo'shiladi; 9 ta hozirgi `.db` fayl `git rm --cached` bilan
   tracking'dan chiqariladi (disk fayllari qoladi). `__pycache__/`, `.venv/`, `.idea/`, `.DS_Store`
   allaqachon bor.
4. **`Makefile`** — `make db` maqsadi: `scripts/build_db.py` ni chaqiradi (GUI ochmasdan,
   `init_all_databases` + `setup_database` + `load_xlsx_affixes` + boshqa yuklovchilarni
   `kkt_v20_soz_tartibi.py`'dan import qilib ishga tushiradi). `make test` → `pytest`.
5. **`scripts/build_db.py`** — `main()` dagi bazani to'ldirish qismini (GUI ochilishisiz)
   qayta ishlatadigan kichik skript. Mavjud funksiyalarni **chaqiradi**, ularning mantig'ini
   nusxalamaydi yoki o'zgartirmaydi.
6. **`kkt_v20_soz_tartibi.py` — bitta minimal, alohida commit bo'ladigan tuzatish**:
   tkinter importini try/except bilan o'rab, `HAS_TK` flag qo'shish; `MTSystem` klassi va
   `main()` ichidagi GUI chaqiruvi faqat `HAS_TK=True` bo'lganda ishlaydi (aks holda aniq xato
   xabari bilan to'xtaydi). `show_error_dialog` allaqachon `tk._default_root` orqali himoyalangan
   — uni `HAS_TK` bilan mos ravishda kengaytiramiz. Boshqa hech qanday funksiya qatori
   o'zgarmaydi.
7. **`tests/` skeleti** — `tests/conftest.py`, `tests/test_smoke.py`: modul `tkinter`siz
   muhitda import qilinishini simulyatsiya qiladigan test (masalan `sys.modules["tkinter"]=None`
   trick bilan ImportError'ni sun'iy chaqirib, `HAS_TK=False` yo'lini tekshiradi) + oddiy
   "`translate_phrase` mavjud va chaqiriladigan" smoke test. Haqiqiy tarjima to'g'riligini
   tekshiruvchi testlar Faza 1 da yoziladi — bu yerda faqat infratuzilma.
8. **`reports/faza_0.md`** — yakuniy hisobot: nima qilindi, qaysi bandlar yopildi (50, 51),
   nima ishlamadi/qoldi.

## 3. Commit bo'linishi (Qoida 6: har tuzatish alohida commit)

1. `chore: requirements.txt, README.md, .gitignore, Makefile qo'shildi`
2. `chore: .db fayllarni git tracking'dan chiqarish (*.db .gitignore ga qo'shildi)`
3. `refactor: tkinter importini ixtiyoriy qilish (HAS_TK), GUI'ni mantiqdan ajratish`
4. `test: pytest skeleti va tkinter'siz import smoke testi`
5. `docs: reports/faza_0.md hisoboti`

## 4. Yopiladigan taqriz bandlari

- **51-band** (fayl nomi/versiya nomuvofiqligi, ishga tushirish tartibi hujjatlashmagan) —
  README + `__version__` masalasi qisman shu yerda boshlanadi, to'liq yopilishi Faza 2 da
  (fayl nomi/versiya birxillashtirilganda).
- **50-band** (test yo'qligi, reproducibility) — to'liq yopilishi Faza 1 da, Faza 0 faqat
  infratuzilmani (pytest, CI skeleti) tayyorlaydi.

## 5. Qoidalarga muvofiqlik tekshiruvi

- Hech qanday eksperimental raqam/natija ishlab chiqarilmaydi — bu faza faqat infratuzilma.
- Vazn qiymatlariga tegilmaydi.
- Gold test to'plami hali yo'q — kodni testga moslab tuzatish xavfi yo'q.
- `kkt_v20_soz_tartibi.py` dagi yagona o'zgarish (tkinter ixtiyoriy qilish) **funksional
  natijani o'zgartirmaydi** — faqat import xatosini oldini oladi. Alohida commit, keyingi
  bosqichda test bilan tekshiriladi.

---

**Tasdiqlashni kutyapman**: yuqoridagi reja bo'yicha davom etaymi, yoki biror band bo'yicha
yo'nalishni o'zgartirishim kerakmi (masalan `.db` fayllarni git tarixidan olib tashlashning
kerak emasligi, yoki `data_loader.py` bilan `kkt_v20_soz_tartibi.py` docx-o'qish yo'lini
birlashtirish Faza 0 ga kiritilishi kerakligi)?
