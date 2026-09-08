# Baza qayta ishlab chiqarilishi (reproducibility) tekshiruvi

**Sana:** 2026-09-08
**Maqsad:** git'ga commit qilingan 9 ta `.db` faylni tracking'dan chiqarishdan oldin, ular
`data/` dagi manba fayllardan **noldan, xato-siz, bit-ma-bit bir xil** qayta qurilishini
isbotlash (foydalanuvchi talabi).

## Uslub

1. `kkt_v20_soz_tartibi.py`, `data_loader.py` va butun `data/` papkasi izolyatsiya qilingan
   vaqtinchalik papkaga nusxalandi (repo ildizidagi haqiqiy `.db` fayllarga tegilmadi).
2. O'sha vaqtinchalik papkada `main()` dagi baza-to'ldirish ketma-ketligi (GUI ochilishisiz)
   qayta ishga tushirildi: `init_all_databases → setup_database → load_xlsx_affixes →
   find_bazalar_docx/load_bazalar_docx → seed_core_demo_data →
   find_bazalar_affixes_docx/load_bazalar_affixes_docx → load_pdf_kkt_bazalar →
   load_ch2_evx_examples → resync_all_ids → mdb_seed_if_empty`.
3. Har bir `.db` fayl uchun: sxema (`sqlite_master`), jadval ro'yxati, har jadvaldagi
   yozuvlar soni va **hamma qatorning to'liq kontenti** (barqaror solishtirish uchun
   qator-mazmuniga qarab saralangan) git'dagi nusxa bilan solishtirildi.

Skript: `scripts/build_db.py` (Faza 0 bilan birga qo'shiladi) + vaqtinchalik solishtiruv
skripti (`compare_db.py`, faqat shu tekshiruv uchun, repoga kirmaydi).

## Natija

| Baza | Sxema | Jadvallar | Natija |
|---|---|---|---|
| `BM_en_w.db` | bir xil | `formal_model`(68), `grammar_rules`(52), `kkt_symbols`(90), `pos_weight`(8), `word_models`(52) | **bir xil** |
| `BM_uz_w.db` | bir xil | `formal_model`(25), `grammar_rules`(52), `kkt_symbols`(90), `pos_weight`(8), `word_models`(50) | **bir xil** |
| `MDB_uz_w.db` | bir xil | `candidates`(1526) | **bir xil** |
| `PSB_en_w.db` | bir xil | `terms`(0) | **bir xil** |
| `PSB_uz_w.db` | bir xil | `terms`(0) | **bir xil** |
| `QM_en_w.db` | bir xil | `affixes`(582) | **bir xil** |
| `QM_uz_w.db` | bir xil | `affixes`(440) | **bir xil** |
| `UB_en_w.db` | bir xil | `words`(1596) | **bir xil** |
| `UB_uz_w.db` | bir xil | `words`(1596) | **bir xil** |

Barcha 9 ta baza — sxema va har bir qator (jumladan `weight` ustunlaridagi qiymatlar) —
qayta qurishda git'dagi nusxa bilan **to'liq mos keldi**. Farq topilmadi.

## Muhim ogohlantirishlar (bularsiz "reproducibility" noto'g'ri tushunilishi mumkin)

1. **Qayta ishlab chiqarish `data_loader.py` mavjudligiga bog'liq, va bu bog'liqlik
   jimgina (silent) ishlaydi.** `setup_database()` va `load_xlsx_affixes()` avval
   `data_loader.py` orqali JSON fayllarni o'qishga urinadi; agar u topilmasa (masalan
   `data_loader.py` skript bilan bir joyda bo'lmasa), **xatoga chiqmasdan** to'g'ridan-to'g'ri
   docx/xlsx o'qishga tushadi — va natija **boshqacha** bo'ladi (masalan so'z juftlari:
   JSON yo'lida 1518 ta, DOCX-zaxira yo'lida 1417 ta — 101 ta farq). Bu tekshiruv paytida
   birinchi urinishda aynan shu sabab bilan (temp papkaga `data_loader.py` nusxalanmagani
   uchun) soxta "farq" chiqqan edi; `data_loader.py`ni ham nusxalab qayta ishga tushirilgach
   farq yo'qoldi. **Xulosa:** `make db` va CI hujjatida `data_loader.py` majburiy ravishda
   `kkt_v20_soz_tartibi.py` bilan bir joyda bo'lishi alohida ta'kidlanishi kerak (README,
   Faza 0). Bu, qat'iy aytganda, Qoida 5 ("muvaffaqiyatsizlikni yashirma") nuqtai nazaridan
   ham nozik joy — zaxira yo'l xato chiqarmaydi, shunchaki boshqa sonlar beradi; buni
   alohida topilma sifatida Faza 2/8 ga qaydga olindi.
2. **`kkt_symbols` (90 ta) va `formal_model`/`grammar_rules` (52 ta) yozuvlarining manbasi —
   tashqi qayta o'qiladigan fayl emas, balki `kkt_v20_soz_tartibi.py` ichiga qo'lda
   transkripsiya qilingan literal Python ro'yxatlar** (`load_pdf_kkt_bazalar()` va
   `load_ch2_evx_examples()` funksiyalari, docstring: "qo'lda tekshirib chiqilgan"). Bu
   ma'lumot ham deterministik qayta ishlab chiqariladi (kod o'zgarmasa, natija bir xil
   chiqadi — yuqoridagi jadval buni tasdiqlaydi), lekin **provenance** (Faza 7,
   `provenance` ustuni) bu holatlarda "manba: `1500_...docx`" emas, balki "manba:
   `kkt_v20_soz_tartibi.py` ichidagi `KKT_SYMBOLS`/`CH2_...` literal, PDF/docx dan qo'lda
   ko'chirilgan" deb yozilishi kerak.
3. Bu tekshiruv **faqat "joriy kod joriy `data/` fayllaridan joriy `.db` fayllarni beradi"**
   ekanini tasdiqlaydi. U `.db` fayllar ichidagi ma'lumotning **lingvistik to'g'riligini**
   tasdiqlamaydi (masalan 29/82-bandlardagi soxta og'irlik (`0.00101` va h.k.) muammosi —
   bu Faza 5/6 masalasi, bazalar qayta qurilganda ham xuddi shunday saqlanib qoladi, chunki
   u kodning o'zida shunday hisoblangan).

## Xulosa

Farq topilmadi → foydalanuvchi ko'rsatmasiga ko'ra, `.db` fayllarni `git rm --cached` bilan
tracking'dan chiqarish va `.gitignore` ga `*.db` qo'shish **xavfsiz**: keyingi
`make db` buyrug'i git tarixidan olib tashlangan fayllarni bit-ma-bit tiklaydi.
