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

**ENG MUHIM TOPILMA (metodologik):** 26 ta "mos" natijaning **26 tasi
ham aylanma (circular)** — hech biri haqiqiy morfologik derivatsiya orqali
emas. Sabab: `load_ch2_evx_examples()` shu ro'yxatning har bir so'zini
UB_en_w'ga to'g'ridan-to'g'ri headword sifatida yozib qo'yadi; bitta so'zli
kirish uchun tizim shu YOZUVNI o'qib qaytaradi, morfologiya ishlamaydi.
Bu `smart_parse().method` orqali aniq ajratildi
(`is_direct_seed_hit`/`n_match_derived=0`). **Xulosa: II bob "namunalari"
hozircha algoritmning morfologik qobiliyatini umuman SINAMAYDI** — bu
audit_examples.py ning eng qimmatli natijasi, chunki u tashqi ko'rinishda
"52 tadan 26 tasi ishlaydi" degan noto'g'ri taassurotni fosh qiladi.

Topshiriqda nomlab o'tilgan 4 ta misol:
- `capabilityies`, `leafes`, `schoolboys` — CH2_EVX_EXAMPLES da topildi,
  "mos keldi" — LEKIN yuqoridagi aylanma sabab bilan.
- `more comfortable` — CH2_EVX_EXAMPLES da bor, `translate_phrase` `None`
  qaytaradi (haqiqiy, kutilgan muvaffaqiyatsizlik — "more X" analitik
  qiyosiy shakl qo'llab-quvvatlanmaydi).
- `will return` — CH2_EVX_EXAMPLES da YO'Q (faqat "will" alohida bor).

To'liq jadval: `reports/faza_1_audit_examples.md`.

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
3. **II bob "namunalari" morfologik testni sinamaydi** (aylanma tekshiruv
   muammosi, yuqoriga qarang) — `scripts/audit_examples.py` ning asosiy
   topilmasi.
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
