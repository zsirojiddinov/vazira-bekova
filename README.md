# KKT tarjima tizimi (ingliz → o'zbek)

05.01.04 ixtisosligi bo'yicha dissertatsiyaning dasturiy qismi. Kengayuvchi
kirish tili (KKT — kompyuter kelishuvi tili) asosidagi formal modellarga
tayangan mashina tarjimasi prototipi (faqat EN → UZ yo'nalishi).

Bu README **infratuzilma** (Faza 0) hujjati: muhitni qanday tiklash, bazani
qanday qurish, testlarni qanday ishga tushirish. Loyihaning ilmiy holati,
ma'lum kamchiliklar va reja uchun `reports/` papkasiga qarang.

## Muhit (tekshirilgan konfiguratsiya)

| | |
|---|---|
| Python | **3.14.0** (CPython, framework build) |
| SQLite | **3.51.0** (2025-06-12) |
| OT | macOS (Darwin 25.4.0), arm64 |
| GUI | Tkinter (ixtiyoriy — pastga qarang) |

Boshqa Python/SQLite versiyalarida ishlashi mumkin, lekin tekshirilmagan.
Aniq kutubxona versiyalari — `requirements.txt`.

## O'rnatish

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Loyiha tarkibi

```
kkt_v20_soz_tartibi.py   — tarjima mantig'i + Tkinter GUI (bitta faylda)
data_loader.py           — data/*.json fayllarni Python obyektlariga o'qiydi
data/                    — manba hujjatlar (docx/xlsx) va ulardan olingan json
scripts/build_db.py      — 9 ta .db bazani GUI'siz, buyruq qatoridan quradi
tests/                   — pytest testlari (izolyatsiyalangan muhitda ishlaydi)
reports/                 — har faza bo'yicha hisobotlar, o'lchov natijalari
```

### Kerakli manba fayllar (`data/`)

Bazani qurish uchun quyidagi fayllar `data/` papkasida bo'lishi kerak
(fayl nomlari **aynan shunday**, bo'sh joy/nuqta joylashuvi muhim —
`kkt_v20_soz_tartibi.py` ichidagi qidiruv patterni qat'iy):

| Fayl | Ishlatilishi |
|---|---|
| `1500_EN_UZ_6_POS_sorted.20.docx` (+ mos `.json`) | Asosiy EN-UZ so'z jufti lug'ati (1417+ juft, 6 POS) |
| `Table_English 1-7 Vazn Type 2 14.02.2024.xlsx` (+ `.json`) | Ingliz affikslari va vaznlari |
| `Lotinda Table_Uzbek 1-7 Vazn 11.02.2025.xlsx` (+ `.json`) | O'zbek affikslari |
| `100_soz.docx` (+ `.json`) | 100 ta etalon juftlik (gold-test, `scripts/check_100_soz.py`). Faylning o'zini kod o'qimaydi, **LEKIN xuddi shu 100 juft 1500-JSON ichidagi "100 SOZ" kategoriyasi orqali lug'atga yuklanadi** — natijaga ta'siri 0 ekani o'lchangan (`reports/faza_2_lexicon_sources.md`). Yangi gold to'plamlar uchun qoida: `CLAUDE.md` |
| `KKT_Terminologik_Lugat.docx` (+ `.json`) | KKT terminologik lug'at — **kod tomonidan hozircha ishlatilmaydi** |

`.json` fayllar tegishli `.docx`/`.xlsx` fayllardan oldindan konvertatsiya
qilingan (`data_loader.py` shularni o'qiydi). Agar `data_loader.py` topilmasa
yoki `.json` fayl yo'q bo'lsa, `kkt_v20_soz_tartibi.py` **jimgina** to'g'ridan-
to'g'ri `.docx`/`.xlsx` o'qishga o'tadi — bu holda natija sonlari FARQ
QILISHI mumkin (batafsil: `reports/db_reproducibility.md`). Shuning uchun
`data_loader.py` har doim `kkt_v20_soz_tartibi.py` bilan bir papkada
bo'lishi shart.

Ixtiyoriy (hozircha repoda yo'q, mavjud bo'lsa qo'shimcha ma'lumot yuklaydi):
`bazalar_ma_lumot_09.docx`, `bazalar_ma_lumot_09_07.docx`, `so_zlar_bazasi_un.docx`.

## Bazani qurish

9 ta SQLite bazasi (`UB_en_w.db`, `UB_uz_w.db`, `QM_en_w.db`, `QM_uz_w.db`,
`BM_en_w.db`, `BM_uz_w.db`, `PSB_en_w.db`, `PSB_uz_w.db`, `MDB_uz_w.db`)
**generatsiya qilinadigan artefakt** — git'da saqlanmaydi (`.gitignore`),
har doim `data/` dan qayta quriladi:

```bash
make db
# yoki
python3 scripts/build_db.py
```

Bu GUI ochmaydi — faqat bazani to'ldiradi va konsolga statistika chiqaradi.
Qayta ishlab chiqarilishi (git'dagi versiyalar bilan kontent darajasida —
sxema + har bir qator — solishtirib, md5 EMAS) tasdiqlangan:
`reports/db_reproducibility.md`.

## Ishga tushirish (GUI)

```bash
python3 kkt_v20_soz_tartibi.py
```

Birinchi marta ishga tushirilganda bazalar avtomatik quriladi (agar hali
qurilmagan bo'lsa). Tkinter kerak (pastga qarang).

## Tarjima mantig'ini GUI'siz ishlatish

`translate_phrase()` va uning bog'liqliklari (`smart_parse`, `uz_stem`,
`translate_phrase_kkt`, `translate_phrase_general` va h.k.) **tkinter
o'rnatilmagan muhitda ham** import va ishlaydi (`HAS_TK=False` — GUI
qismi shunchaki ishlamaydi, xatoga chiqmaydi):

```python
import kkt_v20_soz_tartibi as m
print(m.translate_phrase("The student reads the book"))
```

⚠️ **Yon ta'sir haqida ogohlantirish:** `translate_phrase()`/`smart_parse()`
noma'lum ko'plik shakllarini avtomatik xulosa chiqarib, natijani
**to'g'ridan-to'g'ri `.db` fayllarga yozib qo'yadi** (`source="auto"`
keshlash). Bu ishlab chiqarish/tekshiruv skriptlarini yozayotganda hisobga
olinishi kerak — testlar buni izolyatsiyalangan nusxada ishlatadi (pastga
qarang), lekin qo'lda ishga tushirilganda repo ildizidagi haqiqiy `.db`
fayllar o'zgarishi mumkin.

## Testlar

```bash
make test
# yoki
python3 -m pytest tests/ -v
```

Testlar **repo ildizidagi haqiqiy `.db` fayllarga hech qachon tegmaydi** —
har bir test sessiyasi `kkt_v20_soz_tartibi.py` + `data_loader.py` + `data/`
ni vaqtinchalik izolyatsiyalangan papkaga nusxalab, bazani o'sha yerda
noldan quradi (`tests/conftest.py`). Sabab: yuqoridagi yon ta'sir — birinchi
marta bu izolyatsiya bo'lmagan holda test yozilganda repo bazalari
tasodifan ifloslangan edi (voqea: `reports/faza_0.md`).

Faza 0 da faqat infratuzilma testlari bor edi. Faza 1'dan boshlab tarjima
mantig'ining o'zi (uz_stem, make_uzbek, MORPH_RULES, smart_parse,
translate_phrase_kkt/general) uchun ham regression testlar bor — barchasi
xuddi shu izolyatsiya qoidasiga bo'ysunadi va DB'ga yozadigan chaqiruvlar
`readonly_mode()` orqali ishlaydi. CI (`.github/workflows/tests.yml`) har
push/PR'da `pytest tests/`ni ishga tushiradi.

### Read-only rejim (audit/o'lchov skriptlari uchun)

`translate_phrase()`/`smart_parse()` — yon ta'sirga ega (yuqoriga qarang).
Bazani o'zgartirmasdan ko'p marta tarjima qilish kerak bo'lganda:

```python
from kkt_v20_soz_tartibi import translate_phrase, readonly_mode

with readonly_mode():
    natija = translate_phrase(matn)
# yoki qulay yorliq:
natija = translate_phrase(matn, allow_write=False)
```

### Gold-set va audit skriptlari (Faza 1)

- `python scripts/check_100_soz.py` — `data/100_soz.docx` dagi 100 ta
  INSON tayyorlagan etalon juftlikni to'g'ridan-to'g'ri docx'dan o'qib,
  `translate_phrase(..., allow_write=False)` bilan solishtiradi (apostrof+
  bosh harf normalizatsiyasi bilan). Natija: `reports/faza_1_100soz_baseline.md`.
- `python scripts/audit_examples.py` — dissertatsiya II bobidan
  `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` ga qo'lda ko'chirilgan 52 ta
  misolni tekshiradi (xom `so_zlar_bazasi_un.docx` repoda yo'q — mazmuni
  literal ro'yxat sifatida allaqachon bor). Natija:
  `reports/faza_1_audit_examples.md` — jumladan **aylanma (circular)
  tekshiruv** ogohlantirishi (bitta-so'zli misollar shu jadvaldan
  to'g'ridan-to'g'ri o'qilgani uchun "mos kelishi" ko'pincha morfologik
  ishlaganini ISBOTLAMAYDI).

Ikkalasi ham hech qanday raqamni qo'lda kiritmaydi — har safar joriy kod
va joriy bazadan qayta hisoblaydi.

## Ma'lum holat va cheklovlar

Loyihaning to'liq holati, ma'lum kamchiliklar, o'lchov natijalari va
qaysi taqriz bandlari qanday yopilgani — `reports/` papkasidagi har-faza
hisobotlarida (`reports/faza_0.md`, ...).
