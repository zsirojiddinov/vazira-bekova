# Baza qayta ishlab chiqarilishi (reproducibility) tekshiruvi

**Sana:** 2026-09-08
**Maqsad:** git'ga commit qilingan 9 ta `.db` faylni tracking'dan chiqarishdan oldin, ular
`data/` dagi manba fayllardan **noldan, xato-siz** qayta qurilishini isbotlash
(foydalanuvchi talabi).

## Uslub — ANIQLASHTIRISH (foydalanuvchi savoli bo'yicha)

**Asosiy tekshiruv usuli — fayl md5'i EMAS, jadval KONTENTINI qator-ma-qator
solishtirish edi.** Sabab: ikkita SQLite fayli bir xil MANTIQIY kontentga ega
bo'lsa ham (bir xil jadvallar, bir xil qatorlar), **bayt darajasida farq
qilishi mumkin** — sahifa (page) joylashuvi, ichki freelist holati, yozish
tartibi kabi omillarga bog'liq. Shuning uchun md5 solishtiruvi **noto'g'ri
salbiy natija** (false negative — kontent bir xil bo'lsa ham "farq bor" deb
ko'rsatishi) berishi mumkin edi. To'g'ri usul — SQL orqali o'qib, KONTENTni
solishtirish, va aynan shu ishlatildi:

1. `kkt_v20_soz_tartibi.py`, `data_loader.py` va butun `data/` papkasi izolyatsiya qilingan
   vaqtinchalik papkaga nusxalandi (repo ildizidagi haqiqiy `.db` fayllarga tegilmadi).
2. O'sha vaqtinchalik papkada `main()` dagi baza-to'ldirish ketma-ketligi (GUI ochilishisiz)
   qayta ishga tushirildi: `init_all_databases → setup_database → load_xlsx_affixes →
   find_bazalar_docx/load_bazalar_docx → seed_core_demo_data →
   find_bazalar_affixes_docx/load_bazalar_affixes_docx → load_pdf_kkt_bazalar →
   load_ch2_evx_examples → resync_all_ids → mdb_seed_if_empty`.
3. Har bir `.db` fayl uchun: sxema (`SELECT name,sql FROM sqlite_master`), jadval ro'yxati,
   har jadvaldagi yozuvlar soni va **hamma qatorning to'liq kontenti**
   (`SELECT * FROM <jadval>`, barqaror solishtirish uchun qator-mazmuniga qarab saralangan,
   Python tuple sifatida) git'dagi nusxa bilan solishtirildi — **fayl baytlari emas,
   Python obyektlari (tuple/list) taqqoslandi**.

Skript: `scripts/build_db.py` (Faza 0 bilan birga qo'shiladi) + vaqtinchalik solishtiruv
skripti (`compare_db.py`, faqat shu tekshiruv uchun, repoga kirmaydi, kodi pastda).

<details>
<summary>compare_db.py — kontent-solishtiruv yadrosi (arxiv uchun)</summary>

```python
def dump(path):
    con = sqlite3.connect(path); cur = con.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name")
    schema = cur.fetchall()
    tables = {}
    for name, sql in schema:
        cur.execute(f'SELECT * FROM "{name}"')
        rows = sorted(cur.fetchall(), key=lambda r: [(x is None, x) for x in r])
        tables[name] = rows
    con.close()
    return schema, tables

# ... git'dagi va qayta qurilgan nusxa uchun dump() natijalari (schema, tables)
# Python == bilan solishtirildi (fayl baytlari EMAS).
```
</details>

### Qo'shimcha (keyinroq, foydalanuvchi savoli bo'yicha) tekshirilgan: md5 ham mos keldimi?

Yuqoridagi asosiy (kontent-darajasidagi) tekshiruvdan keyin, qiziqish
uchun md5 checksumlari ham solishtirildi (izolyatsiyalangan qayta qurilgan
nusxa vs git'dagi haqiqiy fayl):

| Baza | md5 bir xilmi | Kontent bir xilmi |
|---|---|---|
| BM_en_w.db / BM_uz_w.db / MDB_uz_w.db / PSB_en_w.db / PSB_uz_w.db / QM_en_w.db / QM_uz_w.db / UB_en_w.db / UB_uz_w.db | **Ha (barchasi)** | **Ha (barchasi)** |

Bu holatda md5 HAM mos chiqdi (SQLite yozish tartibi shu muhitda
deterministik bo'lib chiqdi). **Lekin bu tasodifiy/qo'shimcha natija —
metodologiya md5'ga TAYANMAYDI**, chunki: (a) turli SQLite versiyalari,
(b) VACUUM/ANALYZE ishga tushirilgan-tushirilmaganligi, (c) qatorlarni
qo'shish tartibidagi kichik farqlar — bularning har biri kontentni
o'zgartirmasdan baytlarni o'zgartirishi mumkin. Keyingi (Faza 1+) qayta
tekshiruvlar HAM kontent-darajasidagi solishtiruvga tayanishi kerak, md5'ga
emas.

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

Kontent darajasida (sxema + har bir qator) farq topilmadi → foydalanuvchi ko'rsatmasiga
ko'ra, `.db` fayllarni `git rm --cached` bilan tracking'dan chiqarish va `.gitignore` ga
`*.db` qo'shish **xavfsiz**: keyingi `make db` buyrug'i git tarixidan olib tashlangan
fayllarni kontent jihatidan bir xil tiklaydi (bu muhitda qo'shimcha tekshiruv shuni ham
ko'rsatdiki, hatto bayt darajasida — md5 — ham bir xil chiqdi, lekin bu kafolat emas,
yuqoridagi ogohlantirishga qarang).

## Qo'shimcha savol: git'dagi asl bazalarda `source='auto'` nechta?

`SELECT COUNT(*) FROM words WHERE source='auto'` — **0** (ikkalasida ham: `UB_en_w.db`
va `UB_uz_w.db`). To'liq `source` taqsimoti (1596 ta yozuvning hammasi): `json`(1513),
`chapter2_evx`(52), `docx`(31) — uchtasi ham qayta ishlab chiqariladigan, kod/data
manbali kategoriyalar; `auto` yoki `user` kategoriyali (ya'ni ishga tushirish vaqtida
qo'shilgan) yozuv git HEAD'da **yo'q**. Batafsil izoh va bu savolning nima uchun
so'ralgani: `reports/faza_0.md`, "Ikkita savolga javob" bo'limi.
