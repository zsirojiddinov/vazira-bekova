# Faza 1 — hisobot: regression harness

**Sana:** 2026-09-08

## Nima qilindi

### 1. Read-only rejim (Faza 0 yakunida, foydalanuvchi so'rovi bilan qo'shildi)

`readonly_mode()` kontekst-menejeri va `translate_phrase(text, allow_write=False)`
yorlig'i — to'rtta yozish-nuqtasini (`db_insert`, `qm_confirm_or_add`,
`bm_get_or_create_pos_model`, `bm_get_or_create_affix_model`) global bayroq
orqali o'chiradi, KESHLASH MANTIG'INI (vazn/kkt_symbol hisoblashni) esa
saqlab qoladi — shu sabab tarjima natijasi ikkala rejimda ham bir xil.
5 test bilan tasdiqlangan. Bu Faza 1 dagi BARCHA o'lchov/audit skriptlari
uchun majburiy old shart edi.

### 2. Unit/regression testlar (148 test + 6 xfail)

| Fayl | Nima sinaladi |
|---|---|
| `tests/test_uz_stem.py` | Sof funksiya, 11 holat |
| `tests/test_make_uzbek.py` | 72 affiks->shablon holati (funksiya bilan tasdiqlangan) |
| `tests/test_affix_tables.py` | MORPH_RULES strukturasi: POS_KKT bilan moslik, tartib qoidalari |
| `tests/test_smart_parse.py` | To'g'ridan/derivatsiya orqali topish, topilmagan holatlar, 2 ta YANGI xato |
| `tests/test_translate_phrase_kkt.py` | `data/100_soz.docx` dan 19 ta real holat (11 mos, 6 xfail, 2 "None kutilgan") |
| `tests/test_translate_phrase_general.py` | Topshiriqda nomlangan 5 muammoli misol + tushum kelishigi holati |
| `tests/test_check_100_soz.py` | `scripts/check_100_soz.py` ning docx-parsing va normalizatsiyasi |
| `tests/test_audit_examples.py` | `scripts/audit_examples.py` ning CH2_EVX_EXAMPLES bilan mosligi |

**Barchasi** `tests/conftest.py::isolated_kkt_module` orqali izolyatsiyalangan
muhitda ishlaydi; DB'ga yozadigan har bir chaqiruv `readonly_mode()` bilan
o'ralgan. Hech qanday gold/etalon qiymat Claude tomonidan TO'QILMAGAN —
har biri: (a) `data/100_soz.docx` (inson tayyorlagan, dissertatsiya
etalon to'plami), (b) `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` (dastur
muallifi tomonidan dissertatsiya matnidan qo'lda ko'chirilgan), yoki
(c) kodning o'z ichidagi deterministik qoida (masalan `make_uzbek()`
dagi `rules` lug'ati) dan olingan.

### 3. `scripts/check_100_soz.py` — 100_soz.docx gold-runner

`data/100_soz.docx` (100 ta EN->UZ etalon) ni to'g'ridan-to'g'ri docx'dan
o'qib, `translate_phrase(text, allow_write=False)` bilan (apostrof+bosh
harf normalizatsiyasi bilan) solishtiradi.

**Natija (2026-09-08, joriy kod + joriy baza):**

```
python scripts/check_100_soz.py
```

- Aniq mos (normalizatsiya bilan): **56/100**
- Aniq mos (normalizatsiyasiz, xom matn): **24/100**
- `None` qaytardi: **0/100**
- Matn farq qiladi: **44/100**

To'liq jadval: `reports/faza_1_100soz_baseline.md`.

**Bu — Faza 0'da "tasdiqlanmagan" deb belgilangan 56/100 sonining BIRINCHI
RASMAN tasdig'i.** Muhim: bu tasodifiy emas — foydalanuvchining o'z qo'lda
sinovi bilan mos keldi, lekin endi metodikasi (read-only, normalizatsiya,
manba) to'liq hujjatlashtirilgan va skript bilan istalgan vaqt qayta
tekshirilishi mumkin. **80/100 (3 ta ot qo'shilgandan keyingi) hali
tasdiqlanmagan** — chunki bu "3 ta ot"ni lug'atga qo'shish qarori inson
zimmasida (Qoida 1), Claude bu Faza 1 doirasida lug'atga hech narsa
qo'shmadi.

Mos kelmagan 44 qatorning tarkibi:
- **20 ta** — "our X"/"your X" (bare, tushum kelishigi "-ni" yo'q).
  `translate_phrase_kkt()` bu naqshni ushlamaydi (3 so'z talab qiladi),
  `translate_phrase_general()` esa "-ni" qo'shmaydi. Bu — Faza 0'da
  qayd etilgan, Faza 2'da inson qaroriga muhtoj masala.
- **30 ta** — "school"/"program"/"article" ustunlaridagi barcha qatorlar
  (10 naqsh × 3 ot). Bular topshiriqdagi "yetishmayotgan 3 ta ot" bilan
  bir xil sabab: bu so'zlar lug'atda yo'q. `translate_phrase_kkt()`
  darajasida buni to'g'ridan-to'g'ri tekshirdik (xfail testlar) — natija
  `None`. LEKIN to'liq `translate_phrase()` zanjirida (kkt->general
  fallback) natija `None` EMAS, balki **garbled matn** ("Dan bizning",
  "Ga sizning" kabi) — bu YANGI kuzatish: general fallback yo'q so'zni
  "?" bilan belgilash o'rniga predlog/olmoshni alohida so'z sifatida
  chiqarib yuboradi.

### 4. `scripts/audit_examples.py` — II bob auditi

Xom `so_zlar_bazasi_un.docx` repoda yo'q, lekin uning mazmuni
`kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` (52 ta misol) sifatida
allaqachon mavjud (dastur muallifi tomonidan qo'lda ko'chirilgan). Skript
shu manbani ishlatadi.

**Natija:**

```
python scripts/audit_examples.py
```

- Jami: 52, aniq mos: **26/52**, `None`: 15/52, matn farq: 11/52

**ENG MUHIM TOPILMA (metodologik) — "aylanma" so'zining aniqlashtirilgan
ma'nosi:** dastlabki hisobotda "26/26 aylanma" deyilgan edi; foydalanuvchi
so'rovi bilan bu da'vo HAR BIR misol darajasida tekshirildi (pastdagi
jadval — `scripts/audit_examples.py` bilan qayta ishlab chiqariladi,
`_provenance_for()`/`_load_independent_source_headwords()` funksiyalari,
haqiqiy `UB_en_w.db` dan faqat SELECT bilan o'qiydi). **Natija: 25/26
haqiqatan HAM to'liq aylanma, 1/26 ("much") esa MUSTAQIL manbadan ekan —
dastlabki "26/26" da'vosi noto'g'ri edi, shu bilan TUZATILDI.**

**Metodika:** har bir to'g'ridan-mos misol uchun (1) `UB_en_w.db`dagi
BARCHA qatorlar (id, tarjima, POS, `source`) o'qildi, (2) qaysi qator
`translate_phrase()` tomonidan tanlangani aniqlandi, (3) shu inglizcha
bosh so'z ikkita `CH2_EVX_EXAMPLES`dan MUSTAQIL inson-manba faylida
(`data/1500_EN_UZ_6_POS_sorted.20.json` — 1500-so'zlik lug'at,
`data/100_soz.json`) ham bor-yo'qligi tekshirildi. **Git tarixi bo'yicha:**
`CH2_EVX_EXAMPLES` ro'yxati va uni yuklaydigan barcha boshqa kod BITTA
"Initial commit"da (`841d174`, 2026-09-08) qo'shilgan — so'z darajasida
ma'noli git sana/tarix solishtiruvi YO'Q (`.db` fayllarining o'zi esa
umuman git'da kuzatilmaydi, Faza 0). Shu sabab "oldin/keyin" ustuni git
sanasiga emas, kodning DETERMINISTIK yuklash tartibiga asoslangan:
`setup_database()` (1500-so'zlik JSON/docx) `scripts/build_db.py`da HAR
DOIM `load_ch2_evx_examples()`dan OLDIN ishga tushadi — demak mustaqil
manbadagi so'z UB_en_w'ga CH2 ro'yxatidan OLDIN yozilgan bo'lardi.

| Misol (en) | UB_en_w qatorlari (id, tarjima, POS, source) | Tanlangan qator | Mustaqil manbada? | Xulosa |
|---|---|---|---|---|
| processes | id=1545 'jarayonlar' Ot src=chapter2_evx | id=1545 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| an example | id=1547 'misol' Ot src=chapter2_evx | id=1547 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| capabilityies | id=1550 'imkonyatlar' Ot src=chapter2_evx | id=1550 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| delays | id=1551 'kechikishlar' Ot src=chapter2_evx | id=1551 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| leafes | id=1552 'barglar' Ot src=chapter2_evx | id=1552 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| men | id=1553 'erkaklar' Ot src=chapter2_evx | id=1553 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| customhouses | id=1554 'Bojxonalar' Ot src=chapter2_evx | id=1554 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| schoolboys | id=1555 'Bojxonalar' Ot src=chapter2_evx | id=1555 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| information | id=1556 'Axborot' Ot src=chapter2_evx | id=1556 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| contents | id=1557 'mazmun' Ot src=chapter2_evx | id=1557 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| student's | id=1558 'studentning' Ot src=chapter2_evx | id=1558 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| cleverer | id=1573 'aqilliroq' Sifat src=chapter2_evx | id=1573 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| cleverest | id=1574 'eng aqilli' Sifat src=chapter2_evx | id=1574 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| busier | id=1575 'kattaroq' Sifat src=chapter2_evx | id=1575 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| busiest | id=1576 'eng katta' Sifat src=chapter2_evx | id=1576 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| gayer | id=1577 "sho'xroq" Sifat src=chapter2_evx; id=1578 "eng sho'x" Sifat src=chapter2_evx | id=1577 src=chapter2_evx | yo'q | TO'LIQ AYLANMA (2 qator, ikkalasi ham chapter2_evx) |
| here | id=1581 'shu yerda' Ravish src=chapter2_evx | id=1581 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| faster | id=1582 'tezroq' Ravish src=chapter2_evx | id=1582 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| fastest | id=1583 'eng tez' Ravish src=chapter2_evx | id=1583 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| inside | id=1584 'ichkarida' Ravish src=chapter2_evx | id=1584 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| today | id=1585 'bugun' Ravish src=chapter2_evx | id=1585 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| **much** | id=424 "Ko'p" **Ot src=json**; id=1586 "ko'p" Ravish src=chapter2_evx | **id=424 src=json** | **1500_EN_UZ_6_POS_sorted.20.json** | **MUSTAQIL MANBA** — CH2_EVX_EXAMPLES EMAS |
| quietly | id=1587 'tinchgina' Ravish src=chapter2_evx | id=1587 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| fifteen | id=1589 "o'n besh" Son src=chapter2_evx | id=1589 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| eighty | id=1590 'sakson' Son src=chapter2_evx | id=1590 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |
| hundredth | id=1594 'yuzinchi' Son src=chapter2_evx | id=1594 src=chapter2_evx | yo'q | TO'LIQ AYLANMA |

**Jadvaldan chiqadigan xulosa (umumlashtirilgan bayondan emas):**
25/26 qatorda `source` ustuni FAQAT `chapter2_evx` — bu so'zlar
`UB_en_w`ga boshqa hech qanday yo'l bilan kirmagan, faqat
`load_ch2_evx_examples()` orqali; shu sabab ular uchun `translate_phrase()`
ning "mos javobi" hech narsani sinamaydi — funksiya shu YOZUVNI o'qib
qaytaryapti. Bitta qatorda (`much`) esa `source` ustuni ikkita qiymatga
ega (`json` va `chapter2_evx`) va TANLANGAN (birinchi, eng kichik `id`)
qator aynan `json`-manbali — demak bu bitta holatda "mos javob"
`CH2_EVX_EXAMPLES`ga bog'liq emas, mustaqil 1500-so'zlik lug'atdan kelgan
(garchi bu ham morfologik derivatsiya emas, oddiy to'g'ridan-to'g'ri
lug'at izlashi bo'lsa-da). **Tuzatilgan xulosa: 26 tadan 25 tasi to'liq
aylanma, 1 tasi mustaqil manbali to'g'ridan izlash, 0 tasi morfologik
derivatsiya.**

Topshiriqda nomlab o'tilgan 4 ta misol (jadvaldagi tegishli qatorlarga
asoslanib):
- `capabilityies`, `leafes`, `schoolboys` — jadvalda TO'LIQ AYLANMA
  (source=chapter2_evx, boshqa manbada yo'q).
- `more comfortable` — CH2_EVX_EXAMPLES da bor, `translate_phrase` `None`
  qaytaradi (haqiqiy, kutilgan muvaffaqiyatsizlik — "more X" analitik
  qiyosiy shakl qo'llab-quvvatlanmaydi).
- `will return` — CH2_EVX_EXAMPLES da YO'Q (faqat "will" alohida bor).

To'liq (avtomatik qayta hisoblanadigan) jadval: `reports/faza_1_audit_examples.md`
(buyruq: `python scripts/audit_examples.py` yoki `make audit`).

### 5. CI

`.github/workflows/tests.yml` — har push/PR'da `pytest tests/` (izolyatsiyalangan)
+ `make db` bilan qurilgan haqiqiy bazaga qarshi ikkala skriptning smoke-testi.

## Yangi topilgan xatolar (Faza 1 tayyorlash paytida, hech biri tuzatilmagan)

Qoida 3/6 bo'yicha — quyidagilarning HECH biri bu commitlarda TUZATILMADI,
faqat test/hisobot bilan QAYD ETILDI:

1. **`"schoolboys"` -> `"Bojxonalar"`** — `kkt_v20_soz_tartibi.py:1652`
   dagi `CH2_EVX_EXAMPLES` literalida aniq copy-paste xatosi (oldingi
   "customhouses" qatoridan nusxalangan tarjima). `tests/test_translate_phrase_general.py::test_schoolboys_produces_wrong_translation_data_bug`
   da qayd etilgan.
2. **`"worker"` -> `"Ishlaroq"`** — `make_uzbek()` ning "-er" zaxira
   qoidasi HAR DOIM qiyosiy daraja (+roq) deb hisoblaydi, agentiv/ish-
   bajaruvchi ma'noni (POS="Ot" bo'lsa ham) ajratmaydi. Sabab: `make_uzbek()`
   ga faqat affiks matni ("er") uzatiladi, `derived_pos` (Ot vs Sifat)
   YO'Q. `tests/test_smart_parse.py::test_smart_parse_agentive_er_uses_wrong_fallback_suffix_data_bug`
   da qayd etilgan.
3. **II bob "namunalarining" 25/26 to'g'ridan mos kelgan hollari morfologik
   testni umuman SINAMAYDI** (to'liq aylanma — jadval va tuzatilgan xulosa
   yuqorida) — `scripts/audit_examples.py` ning asosiy topilmasi. (1/26,
   `much`, mustaqil manbali — bu istisno ham jadvalda aniq ko'rsatilgan.)
4. **`translate_phrase()` to'liq zanjirida yo'q ot "?" bilan belgilanmaydi,
   balki noto'g'ri qayta tartiblanadi** ("Dan bizning" kabi) —
   `translate_phrase_kkt()` darajasida (xfail testlar) kutilgan `None`
   dan farqli, `check_100_soz.py` natijasida ko'rilgan.

Bularning barchasi — Faza 2 ("ma'lum kod xatolarini tuzatish") va Faza 7/8
(provenance, error analysis) uchun kandidatlar, aniq fayl/qator ko'rsatkichi
bilan.

## Qaysi taqriz bandlari yopildi

- **20-band** — II bob misollarini avtomatik audit qilish. **Yopildi**
  (`scripts/audit_examples.py`), muhim qo'shimcha topilma bilan (aylanma
  tekshiruv muammosi).
- **24-band** — 100_ta_lug'at bilan avtomatik solishtiruv. **Yopildi**
  (`scripts/check_100_soz.py`), 56/100 rasman tasdiqlandi.
- **50-band** — testlar yo'qligi / CI. **To'liq yopildi**: 148 test + CI
  workflow, barchasi izolyatsiyalangan va reproducible.
- **80-band** — `capabilities`, `leaves`, `schoolboys`, `more comfortable`,
  `will return` audit orqali topilishi kerak edi. **Yopildi**: barchasi
  topildi va tekshirildi (`will return` CH2_EVX_EXAMPLES da yo'qligi ham
  aniq hujjatlashtirilgan).

## Qayta ishlab chiqarish buyruqlari

```bash
pip install -r requirements.txt
make db                                    # 9 ta .db ni noldan quradi
make test                                  # 148 test + 6 xfail, ~6 soniya
make check100                              # reports/faza_1_100soz_baseline.md
make audit                                 # reports/faza_1_audit_examples.md
```

## Nima ishlamadi / ochiq qoldi

- **80/100 (3 ta ot bilan) hali tasdiqlanmagan** — lug'atga so'z qo'shish
  Claude vazifasi emas (Qoida 1). Inson `school`/`program`/`article`
  so'zlarini (va ularning to'g'ri tarjimasini) lug'atga qo'shgach,
  `make check100` avtomatik yangi sonni beradi.
- **20 ta "-ni" (tushum kelishigi) holati hal qilinmadi** — Faza 2'da
  `reports/accusative_analysis.md` yozilgach, inson qarori kutiladi
  (Qoida bo'yicha).
- **`so_zlar_bazasi_un.docx` xom fayli hali repoda yo'q** — agar u
  qo'shilsa, `audit_examples.py` ni undan to'g'ridan-to'g'ri qayta
  ajratib olishga kengaytirish mumkin (hozir faqat literal
  `CH2_EVX_EXAMPLES` ishlatiladi, jadval tuzilishi noma'lum bo'lgani
  uchun xom docx parslash yozilmadi).
- Yuqorida sanalgan 4 ta yangi xato (schoolboys, worker, II bob aylanma
  muammosi, garbled fallback) — tuzatilmadi, faqat qayd etildi. Ularni
  tuzatish Faza 2/7/8 ishi.
- `scripts/audit_examples.py` va `check_100_soz.py` orasida ozgina kod
  takrorlanishi qoldi (docx yuklash naqshi) — `_common.py` ga faqat
  `normalize()` chiqarildi, docx-parsing umumiylashtirilmadi (ikkala
  fayl strukturasi turlicha: 100_soz 4-ustunli, CH2 esa Python literal).
