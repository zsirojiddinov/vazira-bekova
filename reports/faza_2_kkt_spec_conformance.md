# Faza 2 — KKT rasmiy spesifikatsiyasiga moslik auditi (conformance matrix)

**Generatsiya vaqti:** 2026-09-11T11:37:38+00:00
**Buyruq:** `python scripts/audit_kkt_spec_conformance.py`
**Spesifikatsiya:** `data/kkt_spec.json` ← `data/kkt_qoidalari.docx` (sha256 `4954c528bc7eec3d…`)
**Kod:** `kkt_v20_soz_tartibi.py` (bazalar data/ dan izolyatsiyalangan papkada noldan qurilgan, `readonly_mode`; NLTK lemmatizer: `USE_LEMMA=True`)

## 0. Asosiy natija

Spesifikatsiyadagi **87 ta qoida** kod bilan solishtirildi. **28 ta to'liq mos (23 tasi mustaqil hisoblangan, 5 tasi aylanma — hammasi CH2_EVX_EXAMPLES orqali)**, 33 ta qisman mos, 21 ta yo'q, 5 ta zid.

| Holat | Soni | Ulushi |
|---|---|---|
| **TO'LIQ MOS** | **28** (23 mustaqil / 5 aylanma) | 32.2% |
| **QISMAN MOS** | **33** | 37.9% |
| **YO'Q** | **21** | 24.1% |
| **ZID** | **5** | 5.7% |
| Jami | 87 | 100% |

### 0.1 28 ta TO'LIQ MOS — haqiqiy tarkibi

- **mustaqil hisoblangan** — natijani kod o'zi hisobladi: M/N/S turida kodga FAQAT docx'dagi o'zak berildi (stub, real lug'at yashirilgan), L turida natija CH2_EVX_EXAMPLES'dan mustaqil lug'at yozuvidan (1500-lug'at yoki kod ichidagi SEED_WORDS) keldi.
- **CH2_EVX_EXAMPLES orqali aylanma** — natija dissertatsiya II bob misollarining lug'atga yozilgan nusxasidan (`source='chapter2_evx'`) o'qib qaytarildi; docx misoli ham shu manbadan — mustaqil dalil emas.
- Oxirgi ustun — xuddi shu misol HAQIQIY lug'at bilan qanday yo'l orqali chiqishi (M/N/S uchun holatga ta'sir qilmaydi, lekin amaliyotda ko'p misol baribir CH2 dan qaytishini ko'rsatadi).

| qoida_id | POS | tur | belgi | qanday aniqlandi | haqiqiy lug'at bilan yo'l |
|---|---|---|---|---|---|
| 2.1 | Ot | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | variables: qoida -s (o'zak variable, Ot) |
| 2.4 | Ot | S | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | the: topilmadi; progress: topilmadi |
| 2.6 | Ot | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | processes: lug'at[chapter2_evx] |
| 2.7 | Ot | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | capabilities: topilmadi |
| 2.8 | Ot | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | delays: lug'at[chapter2_evx] |
| 2.9 | Ot | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | leaves: topilmadi |
| 2.11 | Ot | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | customhouses: lug'at[chapter2_evx] |
| 2.16 | Ot | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | student's: lug'at[chapter2_evx] |
| 2.22 | Sifat | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | cleverest: lug'at[chapter2_evx] |
| 2.23 | Sifat | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | larger: topilmadi |
| 2.24 | Sifat | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | largest: topilmadi |
| 2.25 | Sifat | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | bigger: topilmadi |
| 2.26 | Sifat | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | biggest: topilmadi |
| 2.27 | Sifat | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | busier: lug'at[chapter2_evx] |
| 2.29 | Sifat | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | gayer: lug'at[chapter2_evx] |
| 2.30 | Sifat | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | gayest: topilmadi |
| 2.46 | Fe'l | L | **CH2_EVX_EXAMPLES orqali aylanma** | haqiqiy lug'at: natija FAQAT CH2_EVX_EXAMPLES yozuvidan (docx misoli bilan bir manba) | will: lug'at[chapter2_evx] |
| 2.49 | Fe'l | L | **CH2_EVX_EXAMPLES orqali aylanma** | haqiqiy lug'at: natija FAQAT CH2_EVX_EXAMPLES yozuvidan (docx misoli bilan bir manba) | can: lug'at[chapter2_evx] |
| 2.61 | Fe'l | L | **mustaqil hisoblangan** | haqiqiy lug'at: 1500-lug'at yozuvi | understand: lug'at[json] |
| 3.1 | Ravish | L | **CH2_EVX_EXAMPLES orqali aylanma** | haqiqiy lug'at: natija FAQAT CH2_EVX_EXAMPLES yozuvidan (docx misoli bilan bir manba) | here: lug'at[chapter2_evx] |
| 3.6 | Ravish | L | **CH2_EVX_EXAMPLES orqali aylanma** | haqiqiy lug'at: natija FAQAT CH2_EVX_EXAMPLES yozuvidan (docx misoli bilan bir manba) | inside: lug'at[chapter2_evx] |
| 3.7 | Ravish | L | **CH2_EVX_EXAMPLES orqali aylanma** | haqiqiy lug'at: natija FAQAT CH2_EVX_EXAMPLES yozuvidan (docx misoli bilan bir manba) | today: lug'at[chapter2_evx] |
| 3.8 | Ravish | L | **mustaqil hisoblangan** | haqiqiy lug'at: 1500-lug'at yozuvi | much: lug'at[json] |
| 3.12 | Son | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | fifteen: lug'at[chapter2_evx] |
| 3.14 | Son | S | **mustaqil hisoblangan** | stub; maxsus qoida yo'q — so'zma-so'z birikma | eighty: lug'at[chapter2_evx]; five: topilmadi |
| 3.15 | Son | S | **mustaqil hisoblangan** | stub; maxsus qoida yo'q — so'zma-so'z birikma | one: lug'at[json]; hundred: topilmadi |
| 3.16 | Son | S | **mustaqil hisoblangan** | stub; maxsus qoida yo'q — so'zma-so'z birikma | four: topilmadi; million: topilmadi |
| 3.18 | Son | M | **mustaqil hisoblangan** | stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi | hundredth: lug'at[chapter2_evx] |

**"93 ta qoida" haqida — tuzatish:** docx jadvallarida **87 ta** qoida bor. "93" soni (Ot 16, Sifat 18, Fe'l 29, Ravish 11, Son 11, Olmosh 8) har bir jadvalning SARLAVHA qatorini ham qo'shib sanalgan (16−1 + 18−1 + 29−1 + 11−1 + 11−1 + 8−1 = 87). Tekshiruv: `data/kkt_spec.json` → `sonlar`.

### Turkum bo'yicha

| POS | TO'LIQ MOS | QISMAN MOS | YO'Q | ZID | Jami |
|---|---|---|---|---|---|
| Ot | 8 | 4 | 1 | 2 | 15 |
| Sifat | 8 | 5 | 4 | 0 | 17 |
| Fe'l | 3 | 11 | 11 | 3 | 28 |
| Ravish | 4 | 4 | 2 | 0 | 10 |
| Son | 5 | 2 | 3 | 0 | 10 |
| Olmosh | 0 | 7 | 0 | 0 | 7 |

### Qoida turi bo'yicha

| Tur | TO'LIQ MOS | QISMAN MOS | YO'Q | ZID | Jami |
|---|---|---|---|---|---|
| M — morfologik (affiks) | 17 | 17 | 0 | 1 | 35 |
| N — noqoida (o'zak o'zgarishi) | 0 | 3 | 1 | 0 | 4 |
| S — ibora (so'z tartibi / funksional so'z) | 4 | 0 | 8 | 4 | 16 |
| L — leksik moslik | 7 | 13 | 12 | 0 | 32 |

### TO'LIQ MOS natijalarini qanday o'qish kerak (halol baho)

- M/N/S turidagi TO'LIQ MOS (21 ta) — **lug'atdan mustaqil** tekshirilgan: kodga faqat docx'dagi o'zak berilgan (stub), qolgani haqiqiy qoida zanjiri. Bu — formal qoidaning o'zi ishlashining dalili. Lekin real lug'atda o'sha o'zak bo'lmasa, amaliy tarjima baribir chiqmaydi (quyidagi batafsil jadvaldagi "real lug'at" qatori).
- L turidagi TO'LIQ MOS (7 ta) — HAQIQIY lug'at bilan. Shundan **5 tasi natijani FAQAT `CH2_EVX_EXAMPLES` (dissertatsiya II bob misollari, `source='chapter2_evx'`) yozuvidan oladi** — ya'ni docx misoli bilan bir xil manbadan ko'chirilgan so'z qaytyapti (aylanma; mustaqil dalil emas): 2.46, 2.49, 3.1, 3.6, 3.7.
- S turidagi TO'LIQ MOS ichida **3 tasi** uchun kodda maxsus qoida YO'Q — natija oddiy so'zma-so'z birikmadan to'g'ri chiqib qolgan (masalan son birikmalari): 3.14, 3.15, 3.16.
- **Muhitga bog'liq holatlar** (NLTK wordnet lemmatizer bor/yo'qligiga qarab o'zgaradi — hisobot `USE_LEMMA=True` bilan): 2.33: QISMAN MOS → wordnet'siz YO'Q; 2.65: QISMAN MOS → wordnet'siz YO'Q.
- **Docx ichki nomuvofiqligi tufayli QISMAN** (1 ta): kod natijasi docx katagidagi "+" qismlarining yig'indisiga teng, lekin docx natija katagida boshqacha yozilgan (`data/kkt_spec.json` → `izoh`). Holat docx matni bo'yicha (tuzatilmagan) qoldirildi: 2.21.

## 1. Metodika

1. **Spesifikatsiya** — `scripts/extract_kkt_spec.py` docx'dan avtomatik ajratadi (matn aynan ko'chirilgan, `--check` rejimi JSON docx bilan sinxronligini tekshiradi).
2. **Har bir qoida uchun tekshiruv** — `PROBES` (skript ichida): docx katagidagi misoldan olingan kirish/kutilgan juftlar. Har bir qiymat docx katagidan kelib chiqishi test bilan tekshiriladi (`tests/test_kkt_spec_conformance.py::test_probe_values_trace_to_docx_cells`). Kirishdagi tipografik apostrof (’) ASCII (') ga almashtirilgan — kod tokenizatori (`[A-Za-z']+`) faqat ASCII ni taniydi.
3. **Solishtiruv** — `scripts/_common.normalize()` (NFC, kichik harf, apostroflar bir xil, bo'shliqlar siqilgan); kutilgan qiymatdan qavs ichidagi izoh (masalan "(affikssiz)") va "…" olib tashlanadi. Bitta so'zli kirishda lug'at yozuvining " / " variantlaridan biri ham qabul qilinadi ("variant" belgisi bilan ko'rsatiladi).
4. **Tizim chiqishi** — GUI'dagi kabi: `translate_phrase(..., allow_write=False)` natija bersa — o'sha, aks holda `parse_sentence()` so'zma-so'z natijasi (topilmagan so'z `[so'z?]`).
5. **Holat mantig'i** (tur bo'yicha, `evaluate_rule()`):
   - **M**: stub bilan — affiks va o'zak tanildi + turkum spec bilan bir xil + natija mos → TO'LIQ MOS; tanildi, turkum bir xil, natija farq → QISMAN; tanildi, lekin kod uni BOSHQA turkumga qo'yadi: natija mos → QISMAN, farq → ZID; tanilmadi, lekin kodda shu affiks uchun qoida BOR (ishlamadi — dalilda o'zak-tiklash nomzodlari ko'rsatilgan) → QISMAN; affiks uchun qoida umuman yo'q → YO'Q.
   - Stub'dagi `⟨...⟩` qiymat — ma'lumot emas, BELGI: docx o'zakning o'zbekchasini bermagan joyda (2.13, 3.13) kod o'zbek tomonini qanday qurishini ko'rsatadi.
   - **N**: hamma juft mos → TO'LIQ MOS; noqoida shakldan asosiy o'zak tanildi (masalan lemmatizer orqali), natija farq → QISMAN; tanilmadi → YO'Q.
   - **S**: stub bilan natija mos → TO'LIQ MOS; mos emas va kodda AYNAN shu hodisa uchun alohida qoida bor (`mex` — masalan `_DETERMINERS`, `PREP_UZ_X3`) → ZID; bunday qoida yo'q → YO'Q.
   - **L**: haqiqiy lug'at bilan — hamma juft mos → TO'LIQ MOS; qisman mos yoki bosh so'z topildi-yu natija farq → QISMAN; bosh so'z(lar) umuman topilmadi → YO'Q.
6. **Chegara** — bu audit formal qoidaning TO'G'RI IMPLEMENT QILINGANINI tekshiradi, tarjima sifatini emas. Gold to'plamlar (`100_soz`, `1500_...`) bu yerda ishlatilmaydi — 1500-lug'at faqat 4-bo'limdagi ustuvorlik hisobida (qamrov soni) ishlatiladi.

## 2. Moslik jadvali (87 qoida)

| qoida_id | POS | holat | dalil (kod qatori yoki test natijasi) |
|---|---|---|---|
| 2.1 | Ot | **TO'LIQ MOS** | [M] MORPH_RULES:511, make_uzbek:544; stub: tahlil: -s + variable → Ot — stub: `variables` → «O‘zgaruvchilar» (kutilgan «o‘zgaruvchilar») ✓ |
| 2.2 | Ot | **ZID** | [S] _DETERMINERS:2194 — artikllarni (the/a/an ...) iboradan butunlay olib tashlaydi — stub: `a network` → «Tarmoq» (kutilgan «bitta tarmoq») ✗ |
| 2.3 | Ot | **ZID** | [S] _DETERMINERS:2194 — artikllarni (the/a/an ...) iboradan butunlay olib tashlaydi — stub: `an example` → «Misol» (kutilgan «bitta misol») ✗ |
| 2.4 | Ot | **TO'LIQ MOS** | [S] _DETERMINERS:2194 — artikllarni (the/a/an ...) iboradan butunlay olib tashlaydi — stub: `the progress` → «Taraqqiyot» (kutilgan «taraqqiyot») ✓ |
| 2.5 | Ot | **QISMAN MOS** | [M] MORPH_RULES:511, make_uzbek:544; stub: tahlil: -s + germany → Ot — stub: `The Germanys` → «Germaniyalar» (kutilgan «Germaniyaliklar») ✗ |
| 2.6 | Ot | **TO'LIQ MOS** | [M] MORPH_RULES:509, make_uzbek:544; stub: tahlil: -es + process → Ot — stub: `processes` → «Jarayonlar» (kutilgan «jarayonlar») ✓ |
| 2.7 | Ot | **TO'LIQ MOS** | [M] MORPH_RULES:506, make_uzbek:545; stub: tahlil: -ies + capability → Ot — stub: `capabilities` → «Imkoniyatlar» (kutilgan «imkoniyatlar») ✓ |
| 2.8 | Ot | **TO'LIQ MOS** | [M] MORPH_RULES:511, make_uzbek:544; stub: tahlil: -s + delay → Ot — stub: `delays` → «Kechikishlar» (kutilgan «kechikishlar») ✓ |
| 2.9 | Ot | **TO'LIQ MOS** | [M] MORPH_RULES:507, make_uzbek:545; stub: tahlil: -ves + leaf → Ot — stub: `leaves` → «Barglar» (kutilgan «barglar») ✓ |
| 2.10 | Ot | **YO'Q** | [N] o'zak tanildi: yo‘q (USE_LEMMA=True) — stub: `men` → «[men?]» (kutilgan «erkaklar») ✗ |
| 2.11 | Ot | **TO'LIQ MOS** | [M] MORPH_RULES:511, make_uzbek:544; stub: tahlil: -s + customhouse → Ot — stub: `customhouses` → «Bojxonalar» (kutilgan «bojxonalar») ✓ |
| 2.12 | Ot | **QISMAN MOS** | [M] MORPH_RULES:511, make_uzbek:544; stub: tahlil: -s + schoolboy → Ot — stub: `schoolboys` → «Maktab bolalar» (kutilgan «maktab bolalari») ✗ |
| 2.13 | Ot | **QISMAN MOS** | [M] MORPH_RULES:443, make_uzbek:569; stub: tahlil: -ation + inform → Ot — stub: `information` → «⟨inform⟩ish» (kutilgan «axborot») ✗ |
| 2.15 | Ot | **QISMAN MOS** | [M] MORPH_RULES:511, make_uzbek:544; stub: tahlil: -s + content → Ot — stub: `contents` → «Mundarijalar» (kutilgan «mundarija») ✗ |
| 2.16 | Ot | **TO'LIQ MOS** | [M] _smart_parse_core:2987 (alohida tarmoq); stub: tahlil: -'s + student → Ot — stub: `student's` → «Studentning» (kutilgan «studentning») ✓ |
| –(Sifat) | Sifat | **YO'Q** | [L] real lug'at: `big` → «[big?]» (kutilgan «katta») ✗ — yo'l: big: topilmadi |
| 2.19 | Sifat | **QISMAN MOS** | [M] MORPH_RULES:432, make_uzbek:565; stub: tahlil: -al + form → Sifat — stub: `formal` → «Rasmga oid» (kutilgan «rasmiy») ✗ |
| 2.20 | Sifat | **QISMAN MOS** | [M] MORPH_RULES:432, make_uzbek:565; stub: tahlil: -al + dimension → Sifat — stub: `high-dimensional` → «Ko‘p o‘lchovga oid» (kutilgan «ko‘p o‘lchovli») ✗ |
| 2.21 | Sifat | **QISMAN MOS** | [M] MORPH_RULES:396,413, make_uzbek:552; stub: tahlil: -er + clever → Sifat — stub: `cleverer` → «Aqilliroq» (kutilgan «aqillroq») ✗ ⚠ natija docx katagining "+" qismlari yig'indisiga («aqilliroq») teng |
| 2.22 | Sifat | **TO'LIQ MOS** | [M] MORPH_RULES:411, make_uzbek:541; stub: tahlil: -est + clever → Sifat — stub: `cleverest` → «Eng aqilli» (kutilgan «eng aqilli») ✓ |
| 2.23 | Sifat | **TO'LIQ MOS** | [M] MORPH_RULES:396,413, make_uzbek:552; stub: tahlil: -er + large → Sifat — stub: `larger` → «Kattaroq» (kutilgan «kattaroq») ✓ |
| 2.24 | Sifat | **TO'LIQ MOS** | [M] MORPH_RULES:411, make_uzbek:541; stub: tahlil: -est + large → Sifat — stub: `largest` → «Eng katta» (kutilgan «eng katta») ✓ |
| 2.25 | Sifat | **TO'LIQ MOS** | [M] MORPH_RULES:396,413, make_uzbek:552; stub: tahlil: -er + big → Sifat — stub: `bigger` → «Kattaroq» (kutilgan «kattaroq») ✓ |
| 2.26 | Sifat | **TO'LIQ MOS** | [M] MORPH_RULES:411, make_uzbek:541; stub: tahlil: -est + big → Sifat — stub: `biggest` → «Eng katta» (kutilgan «eng katta») ✓ |
| 2.27 | Sifat | **TO'LIQ MOS** | [M] MORPH_RULES:410, make_uzbek:552; stub: tahlil: -ier + busy → Sifat — stub: `busier` → «Bandroq» (kutilgan «bandroq») ✓ |
| 2.28 | Sifat | **QISMAN MOS** | [M] MORPH_RULES:409, make_uzbek:541; stub: tahlil: -∅ + busy → Sifat; qoida BOR, lekin bu so'zni tanimadi — o'zak tiklash nomzodlari: busiy, busi (stub o'zagi: busy) — stub: `busiest` → «Band» (kutilgan «eng band») ✗ |
| 2.29 | Sifat | **TO'LIQ MOS** | [M] MORPH_RULES:396,413, make_uzbek:552; stub: tahlil: -er + gay → Sifat — stub: `gayer` → «Sho‘xroq» (kutilgan «sho‘xroq») ✓ |
| 2.30 | Sifat | **TO'LIQ MOS** | [M] MORPH_RULES:411, make_uzbek:541; stub: tahlil: -est + gay → Sifat — stub: `gayest` → «Eng sho‘x» (kutilgan «eng sho‘x») ✓ |
| 2.31 | Sifat | **YO'Q** | [S] stub: `more comfortable` → «Qulay» (kutilgan «qulayroq») ✗ |
| 2.32 | Sifat | **YO'Q** | [S] stub: `most comfortable` → «Qulay» (kutilgan «eng qulay») ✗ |
| 2.33 | Sifat | **QISMAN MOS** | [N] o'zak tanildi: ha (USE_LEMMA=True) — stub: `good` → «Yaxshi» (kutilgan «yaxshi») ✓; `better` → «Yaxshi» (kutilgan «yaxshiroq») ✗; `best` → «[best?]» (kutilgan «eng yaxshi») ✗ |
| 2.34 | Sifat | **YO'Q** | [S] stub: `less interesting` → «Qiziqarli» (kutilgan «kamroq qiziqarli») ✗ |
| 2.36 | Fe'l | **YO'Q** | [L] real lug'at: `read` → «[read?]» (kutilgan «o‘qimoq») ✗ — yo'l: read: topilmadi |
| 2.37 | Fe'l | **ZID** | [M] MORPH_RULES:511, make_uzbek:544; stub: tahlil: -s + speak → Ot — stub: `speaks` → «Gapirlar» (kutilgan «gapiradi») ✗ |
| 2.38 | Fe'l | **YO'Q** | [L] real lug'at: `to be` → «Ga» (kutilgan «bo‘lmoq») ✗ — yo'l: be: topilmadi |
| 2.39 | Fe'l | **YO'Q** | [L] real lug'at: `am` → «[am?]» (kutilgan «man») ✗ — yo'l: am: topilmadi |
| 2.41 | Fe'l | **YO'Q** | [L] real lug'at: `was` → «[was?]» (kutilgan «edi») ✗; `were` → «[were?]» (kutilgan «edi») ✗ — yo'l: was: topilmadi; were: topilmadi |
| 2.42 | Fe'l | **QISMAN MOS** | [N] o'zak tanildi: ha (USE_LEMMA=True) — stub: `been` → «bo‘ltir» (kutilgan «bo‘lgan») ✗ |
| 2.43 | Fe'l | **QISMAN MOS** | [M] MORPH_RULES:488, make_uzbek:547; stub: tahlil: -ing + be → Fe'l — stub: `being` → «bo‘ling» (kutilgan «bo‘layotgan») ✗ |
| 2.44 | Fe'l | **YO'Q** | [L] real lug'at: `to have` → «Ga» (kutilgan «bor bo‘lmoq») ✗ — yo'l: have: topilmadi |
| 2.45 | Fe'l | **YO'Q** | [L] real lug'at: `to do` → «Ga» (kutilgan «qilmoq») ✗ — yo'l: do: topilmadi |
| 2.46 | Fe'l | **TO'LIQ MOS** | [L] real lug'at: `will` → «keladi» (kutilgan «keladi») ✓ — yo'l: will: lug'at[chapter2_evx] |
| 2.47 | Fe'l | **QISMAN MOS** | [L] real lug'at: `would` → «keladi» (kutilgan «edi») ✗ — yo'l: would: lug'at[chapter2_evx] |
| 2.48 | Fe'l | **YO'Q** | [L] real lug'at: `become` → «[become?]» (kutilgan «bo‘lmoq») ✗ — yo'l: become: topilmadi |
| 2.49 | Fe'l | **TO'LIQ MOS** | [L] real lug'at: `can` → «qila  olmoq» (kutilgan «qila olmoq») ✓ — yo'l: can: lug'at[chapter2_evx] |
| 2.50 | Fe'l | **YO'Q** | [L] real lug'at: `could` → «[could?]» (kutilgan «olardi») ✗ — yo'l: could: topilmadi |
| 2.51 | Fe'l | **QISMAN MOS** | [L] real lug'at: `may` → «Ajratib ko'rsatmoq» (kutilgan «mumkin») ✗ — yo'l: may: lug'at[chapter2_evx] +MDB almashtirdi |
| 2.52 | Fe'l | **QISMAN MOS** | [L] real lug'at: `might` → «Ajratib ko'rsatmoq» (kutilgan «mumkin») ✗ — yo'l: might: lug'at[chapter2_evx] +MDB almashtirdi |
| 2.53 | Fe'l | **QISMAN MOS** | [L] real lug'at: `must` → «shart» (kutilgan «kerak») ✗ — yo'l: must: lug'at[chapter2_evx] |
| 2.54 | Fe'l | **QISMAN MOS** | [L] real lug'at: `ought to` → «Ga ajratib ko'rsatmoq» (kutilgan «zarur») ✗ — yo'l: ought: lug'at[chapter2_evx] +MDB almashtirdi |
| 2.55a | Fe'l | **YO'Q** | [L] real lug'at: `need` → «[need?]» (kutilgan «kerak») ✗ — yo'l: need: topilmadi |
| 2.56 | Fe'l | **ZID** | [S] PREP_UZ_X3:2077 — "to" -> "ga" (kelishik qo'shimchasi) sifatida ishlaydi — stub: `to ask` → «Ga so‘ramoq» (kutilgan «so‘ramoq») ✗ |
| 2.55b | Fe'l | **QISMAN MOS** | [M] MORPH_RULES:488, make_uzbek:547; stub: tahlil: -ing + read → Fe'l — stub: `reading` → «o‘qiing» (kutilgan «o‘qishni») ✗ |
| 2.58 | Fe'l | **YO'Q** | [L] real lug'at: `to follow` → «Ga» (kutilgan «kuzatmoq») ✗ — yo'l: follow: topilmadi |
| 2.59 | Fe'l | **ZID** | [S] PREP_UZ_X3:2077 — "to" -> "ga" (kelishik qo'shimchasi) sifatida ishlaydi — stub: `listen to me` → «Meniga tinglamoq» (kutilgan «meni tinglamoq») ✗ |
| 2.61 | Fe'l | **TO'LIQ MOS** | [L] real lug'at: `understand` → «Tushunmoq» (kutilgan «tushunmoq») ✓ — yo'l: understand: lug'at[json] |
| 2.62 | Fe'l | **YO'Q** | [S] stub: `will return` → «[will?] qaytmoq» (kutilgan «qaytmoq») ✗ |
| 2.63 | Fe'l | **QISMAN MOS** | [M] MORPH_RULES:490, make_uzbek:550; stub: tahlil: -ed + work → Fe'l — stub: `worked` → «ishlaaylik» (kutilgan «ishladi») ✗ |
| 2.64 | Fe'l | **QISMAN MOS** | [M] MORPH_RULES:487, make_uzbek:550; stub: tahlil: -ied + simplify → Fe'l — stub: `simplified` → «soddalashtirilgan» (kutilgan «soddalashtirildi») ✗ |
| 2.65 | Fe'l | **QISMAN MOS** | [N] o'zak tanildi: ha (USE_LEMMA=True) — stub: `send` → «yubormoq» (kutilgan «yubormoq») ✓; `sent` → «yubormoq» (kutilgan «yubordi») ✗; `sent` → «yubormoq» (kutilgan «yuborgan») ✗ |
| –(Ravish) | Ravish | **YO'Q** | [L] real lug'at: `very` → «[very?]» (kutilgan «juda») ✗ — yo'l: very: topilmadi |
| 3.1 | Ravish | **TO'LIQ MOS** | [L] real lug'at: `here` → «Shu yerda» (kutilgan «shu yerda») ✓ — yo'l: here: lug'at[chapter2_evx] |
| 3.2 | Ravish | **QISMAN MOS** | [M] MORPH_RULES:381, make_uzbek:555; stub: tahlil: -ily + easy → Ravish — stub: `easily` → «Oson tarzda» (kutilgan «osonlik bilan») ✗ |
| 3.3 | Ravish | **QISMAN MOS** | [M] MORPH_RULES:396,413, make_uzbek:552; stub: tahlil: -er + fast → Sifat — stub: `faster` → «Tezroq» (kutilgan «tezroq») ✓ |
| 3.4 | Ravish | **QISMAN MOS** | [M] MORPH_RULES:411, make_uzbek:541; stub: tahlil: -est + fast → Sifat — stub: `fastest` → «Eng tez» (kutilgan «eng tez») ✓ |
| 3.5 | Ravish | **YO'Q** | [S] stub: `more clearly` → «Aniq» (kutilgan «aniqroq») ✗ |
| 3.6 | Ravish | **TO'LIQ MOS** | [L] real lug'at: `inside` → «Ichkarida» (kutilgan «ichkarida») ✓ — yo'l: inside: lug'at[chapter2_evx] |
| 3.7 | Ravish | **TO'LIQ MOS** | [L] real lug'at: `today` → «Bugun» (kutilgan «bugun») ✓ — yo'l: today: lug'at[chapter2_evx] |
| 3.8 | Ravish | **TO'LIQ MOS** | [L] real lug'at: `much` → «Ko'p» (kutilgan «ko‘p») ✓ — yo'l: much: lug'at[json] |
| 3.9 | Ravish | **QISMAN MOS** | [M] MORPH_RULES:385, make_uzbek:554; stub: tahlil: -ly + quiet → Ravish — stub: `quietly` → «Tinch tarzda» (kutilgan «tinchgina») ✗ |
| 3.11 | Son | **QISMAN MOS** | [L] real lug'at: `one` → «Biri / Bitta» (kutilgan «bir») ✗ — yo'l: one: lug'at[json] |
| 3.12 | Son | **TO'LIQ MOS** | [M] MORPH_RULES:371, make_uzbek:588; stub: tahlil: -teen + fif → Son — stub: `fifteen` → «O'n besh» (kutilgan «o‘n besh») ✓ |
| 3.13 | Son | **QISMAN MOS** | [M] MORPH_RULES:373, make_uzbek:588; stub: tahlil: -ty + eigh → Son — stub: `eighty` → «⟨eigh⟩ o'nlik» (kutilgan «sakson») ✗ |
| 3.14 | Son | **TO'LIQ MOS** | [S] kodda bu hodisa uchun maxsus qoida yo'q — natija so'zma-so'z birikmadan kelib chiqdi — stub: `eighty-five` → «Sakson besh» (kutilgan «sakson besh») ✓ |
| 3.15 | Son | **TO'LIQ MOS** | [S] kodda bu hodisa uchun maxsus qoida yo'q — natija so'zma-so'z birikmadan kelib chiqdi — stub: `one hundred` → «Bir yuz» (kutilgan «bir yuz») ✓ |
| 3.16 | Son | **TO'LIQ MOS** | [S] kodda bu hodisa uchun maxsus qoida yo'q — natija so'zma-so'z birikmadan kelib chiqdi — stub: `four million` → «To‘rt million» (kutilgan «to‘rt million») ✓ |
| 3.17 | Son | **YO'Q** | [S] stub: `three hundred and five` → «Uch yuz va besh» (kutilgan «uch yuz besh») ✗ |
| 3.18 | Son | **TO'LIQ MOS** | [M] MORPH_RULES:372, make_uzbek:589; stub: tahlil: -th + hundred → Son — stub: `hundredth` → «Yuzinchi» (kutilgan «yuzinchi») ✓ |
| 3.19 | Son | **YO'Q** | [S] stub: `hundred and twenty-first` → «Yuz va yigirma» (kutilgan «bir yuz yigirma birinchi») ✗ |
| 3.20 | Son | **YO'Q** | [S] stub: `chapter five` → «Bob besh» (kutilgan «beshinchi bob») ✗ |
| 3.22 | Olmosh | **QISMAN MOS** | [L] real lug'at: `I` → «[i?]» (kutilgan «men») ✗ … (5/6 mos) — yo'l: i: topilmadi; he: lug'at[json]; we: lug'at[json]; me: lug'at[json]; him: lug'at[json]; us: lug'at[json] |
| 3.23 | Olmosh | **QISMAN MOS** | [L] real lug'at: `I` → «[i?]» (kutilgan «men») ✗ … (6/7 mos) — yo'l: i: topilmadi; he: lug'at[json]; she: lug'at[json]; it: lug'at[json]; we: lug'at[json]; you: lug'at[json]; they: lug'at[json] |
| 3.24 | Olmosh | **QISMAN MOS** | [L] real lug'at: `my` → «Mening» (kutilgan «menning») ✗ … (4/5 mos) — yo'l: my: lug'at[docx]; his: lug'at[docx]; our: lug'at[docx]; your: lug'at[docx]; their: lug'at[docx] |
| 3.25 | Olmosh | **QISMAN MOS** | [L] real lug'at: `mine` → «Meniki» (kutilgan «menniki») ✗; `ours` → «Bizniki» (kutilgan «bizning») ✗; `yours` → «Sizniki» (kutilgan «sizning») ✗ … (0/4 mos) — yo'l: mine: lug'at[json]; ours: lug'at[json]; yours: lug'at[json]; theirs: lug'at[json] |
| 3.26 | Olmosh | **QISMAN MOS** | [L] real lug'at: `who` → «[who?]» (kutilgan «kim») ✗; `which` → «Qaysi biri» (kutilgan «qaysi») ✗ … (3/5 mos) — yo'l: who: topilmadi; whom: lug'at[json]; whose: lug'at[json]; what: lug'at[json]; which: lug'at[json] |
| 3.27 | Olmosh | **QISMAN MOS** | [L] real lug'at: `no` → «[no?]» (kutilgan «yo‘q») ✗; `many` → «Ko'p» (kutilgan «ko‘pchilik») ✗; `each` → «Har biri» (kutilgan «har bir») ✗ … (5/8 mos) — yo'l: some: lug'at[json]; someone: lug'at[json]; any: lug'at[json]; no: topilmadi; much: lug'at[json]; many: lug'at[json]; all: lug'at[json]; each: lug'at[json] |
| 3.28 | Olmosh | **QISMAN MOS** | [L] real lug'at: `yourself` → «O'zingiz» (kutilgan «o‘zing») ✗ … (3/4 mos) — yo'l: myself: lug'at[json]; yourself: lug'at[json]; himself: lug'at[json]; ourselves: lug'at[json] |

### 2.1 Qo'shimcha: real lug'at bilan natija (M/N/S qoidalari, holatga ta'sir qilmaydi)

Stub tekshiruvi formal qoidani ajratib oladi; bu jadval o'sha misollar HAQIQIY lug'at bilan nima berishini ko'rsatadi — farq qilsa, sabab ko'pincha lug'at bo'shlig'i (o'zak yo'q) yoki misolning o'zi `CH2_EVX_EXAMPLES` dan to'g'ridan-to'g'ri qaytishi.

| qoida_id | holat (stub) | real lug'at natijasi | yo'l |
|---|---|---|---|
| 2.1 | TO'LIQ MOS | `variables` → «O'zgaruvchilar» ✓ | variables: qoida -s (o'zak variable, Ot) |
| 2.2 | ZID | `a network` → «[a?] Tarmoq» ✗ | a: topilmadi; network: lug'at[json] |
| 2.3 | ZID | `an example` → «Misol» ✗ | an: topilmadi; example: lug'at[json] |
| 2.4 | TO'LIQ MOS | `the progress` → «[the?] [progress?]» ✗ | the: topilmadi; progress: topilmadi |
| 2.5 | QISMAN MOS | `The Germanys` → «[the?] [germanys?]» ✗ | the: topilmadi; germanys: topilmadi |
| 2.6 | TO'LIQ MOS | `processes` → «Jarayonlar» ✓ | processes: lug'at[chapter2_evx] |
| 2.7 | TO'LIQ MOS | `capabilities` → «[capabilities?]» ✗ | capabilities: topilmadi |
| 2.8 | TO'LIQ MOS | `delays` → «Kechikishlar» ✓ | delays: lug'at[chapter2_evx] |
| 2.9 | TO'LIQ MOS | `leaves` → «[leaves?]» ✗ | leaves: topilmadi |
| 2.10 | YO'Q | `men` → «Erkaklar» ✓ | men: lug'at[chapter2_evx] |
| 2.11 | TO'LIQ MOS | `customhouses` → «Bojxonalar» ✓ | customhouses: lug'at[chapter2_evx] |
| 2.12 | QISMAN MOS | `schoolboys` → «Bojxonalar» ✗ | schoolboys: lug'at[chapter2_evx] |
| 2.13 | QISMAN MOS | `information` → «Axborot» ✓ | information: lug'at[chapter2_evx] |
| 2.15 | QISMAN MOS | `contents` → «Mazmun» ✗ | contents: lug'at[chapter2_evx] |
| 2.16 | TO'LIQ MOS | `student's` → «Studentning» ✓ | student's: lug'at[chapter2_evx] |
| 2.19 | QISMAN MOS | `formal` → «[formal?]» ✗ | formal: topilmadi |
| 2.20 | QISMAN MOS | `high-dimensional` → «O‘lchamli» ✗ | high: topilmadi; dimensional: lug'at[json] |
| 2.21 | QISMAN MOS | `cleverer` → «Aqilliroq» ✗ | cleverer: lug'at[chapter2_evx] |
| 2.22 | TO'LIQ MOS | `cleverest` → «Eng aqilli» ✓ | cleverest: lug'at[chapter2_evx] |
| 2.23 | TO'LIQ MOS | `larger` → «[larger?]» ✗ | larger: topilmadi |
| 2.24 | TO'LIQ MOS | `largest` → «[largest?]» ✗ | largest: topilmadi |
| 2.25 | TO'LIQ MOS | `bigger` → «[bigger?]» ✗ | bigger: topilmadi |
| 2.26 | TO'LIQ MOS | `biggest` → «[biggest?]» ✗ | biggest: topilmadi |
| 2.27 | TO'LIQ MOS | `busier` → «Kattaroq» ✗ | busier: lug'at[chapter2_evx] |
| 2.28 | QISMAN MOS | `busiest` → «Eng katta» ✗ | busiest: lug'at[chapter2_evx] |
| 2.29 | TO'LIQ MOS | `gayer` → «Sho'xroq» ✓ | gayer: lug'at[chapter2_evx] |
| 2.30 | TO'LIQ MOS | `gayest` → «[gayest?]» ✗ | gayest: topilmadi |
| 2.31 | YO'Q | `more comfortable` → «[more?] [comfortable?]» ✗ | more: topilmadi; comfortable: topilmadi |
| 2.32 | YO'Q | `most comfortable` → «Eng ko'p / Aksariyat» ✗ | most: lug'at[json]; comfortable: topilmadi |
| 2.33 | QISMAN MOS | `good` → «[good?]» ✗ | good: topilmadi |
| 2.33 | QISMAN MOS | `better` → «[better?]» ✗ | better: topilmadi |
| 2.33 | QISMAN MOS | `best` → «Eng yaxshi» ✓ | best: lug'at[json] |
| 2.34 | YO'Q | `less interesting` → «[less?] Qiziqishing» ✗ | less: topilmadi; interesting: qoida -ing (o'zak interest, Fe'l) |
| 2.37 | ZID | `speaks` → «[speaks?]» ✗ | speaks: topilmadi |
| 2.42 | QISMAN MOS | `been` → «[been?]» ✗ | been: topilmadi |
| 2.43 | QISMAN MOS | `being` → «[being?]» ✗ | being: topilmadi |
| 2.56 | ZID | `to ask` → «Ga ajratib ko'rsatmoq» ✗ | to: lug'at[docx]; ask: lug'at[json] +MDB almashtirdi |
| 2.55b | QISMAN MOS | `reading` → «o'qishni» ✓ | reading: lug'at[chapter2_evx] |
| 2.59 | ZID | `listen to me` → «Meniga» ✗ | listen: topilmadi; to: lug'at[docx]; me: lug'at[json] |
| 2.62 | YO'Q | `will return` → «keladi [return?]» ✗ | will: lug'at[chapter2_evx]; return: topilmadi |
| 2.63 | QISMAN MOS | `worked` → «Ishlaaylik» ✗ | worked: qoida -ed (o'zak work, Fe'l) |
| 2.64 | QISMAN MOS | `simplified` → «Oddiylashtirgan» ✗ | simplified: qoida -ify+ied (o'zak simple, Fe'l) |
| 2.65 | QISMAN MOS | `send` → «[send?]» ✗ | send: topilmadi |
| 2.65 | QISMAN MOS | `sent` → «yuborgan» ✗ | sent: lug'at[chapter2_evx] |
| 2.65 | QISMAN MOS | `sent` → «yuborgan» ✓ | sent: lug'at[chapter2_evx] |
| 3.2 | QISMAN MOS | `easily` → «Osonlikcha» ✗ | easily: lug'at[json] |
| 3.3 | QISMAN MOS | `faster` → «Tezroq» ✓ | faster: lug'at[chapter2_evx] |
| 3.4 | QISMAN MOS | `fastest` → «Eng tez» ✓ | fastest: lug'at[chapter2_evx] |
| 3.5 | YO'Q | `more clearly` → «Aniq / Ravshan» ✗ | more: topilmadi; clearly: lug'at[json] |
| 3.9 | QISMAN MOS | `quietly` → «Tinchgina» ✓ | quietly: lug'at[chapter2_evx] |
| 3.12 | TO'LIQ MOS | `fifteen` → «O'n besh» ✓ | fifteen: lug'at[chapter2_evx] |
| 3.13 | QISMAN MOS | `eighty` → «Sakson» ✓ | eighty: lug'at[chapter2_evx] |
| 3.14 | TO'LIQ MOS | `eighty-five` → «Sakson» ✗ | eighty: lug'at[chapter2_evx]; five: topilmadi |
| 3.15 | TO'LIQ MOS | `one hundred` → «Biri / Bitta» ✗ | one: lug'at[json]; hundred: topilmadi |
| 3.16 | TO'LIQ MOS | `four million` → «[four?] [million?]» ✗ | four: topilmadi; million: topilmadi |
| 3.17 | YO'Q | `three hundred and five` → «Va» ✗ | three: topilmadi; hundred: topilmadi; and: lug'at[docx,json]; five: topilmadi |
| 3.18 | TO'LIQ MOS | `hundredth` → «Yuzinchi» ✓ | hundredth: lug'at[chapter2_evx] |
| 3.19 | YO'Q | `hundred and twenty-first` → «Va» ✗ | hundred: topilmadi; and: lug'at[docx,json]; twenty: topilmadi; first: topilmadi |
| 3.20 | YO'Q | `chapter five` → «Bob» ✗ | chapter: lug'at[json]; five: topilmadi |

## 3. 87 qoidadan tashqari: vaznlar, turkum belgilari, operatorlar

`POS_V2` (`kkt_v20_soz_tartibi.py:211`) va `POS_KKT` (`:207`) spesifikatsiya bilan. "runtime" — tarjima paytida haqiqatda ishlatiladigan qiymat (`bm_get_or_create_pos_model(DB_BM_EN, pos)` — avval BM_en_w.pos_weight jadvaliga qaraydi):

| Spec (docx matni) | Spec vazni | `POS_V2` | runtime (BM_en_w) | Spec belgisi | `POS_KKT` | Xulosa |
|---|---|---|---|---|---|---|
| Ot (C) – 0.85 | 0.85 | 0.85 | 0.85 | C | C | bit-aniq mos |
| Sifat (P) – 0.6 | 0.6 | 0.6 | 0.6 | P | P | bit-aniq mos |
| Fe’l (G) – 0.9 | 0.9 | 0.9 | 0.9 | G | G | bit-aniq mos |
| Ravish (N) – 0.4 | 0.4 | 0.4 | 0.4 | N | N | bit-aniq mos |
| Olmosh (M) – 0.5 | 0.5 | 0.5 | 0.5 | M | M | bit-aniq mos |
| Son (F) – 0.5 | 0.5 | 0.5 | 0.5 | F | F | bit-aniq mos |
| Bog‘lovchi (Y) – 0.2 | 0.2 | 0.2 | 0.2 | Y | Y | bit-aniq mos |
| Predlog (D) – 0.4 | 0.4 | 0.4 | 0.4 | D | D | bit-aniq mos |
| Yordamchi so‘z turkumlari (U, L) – 0.07 | 0.07 | — | — | U, L | — | **kodda yo'q** (POS_V2/POS_KKT kaliti yo'q) |

- **Yordamchi so'z turkumlari (U, L) — 0.07:** `POS_V2`/`POS_KKT` da kalit yo'q. `0.07` qiymati kodda hisob-kitobda faqat bitta joyda qattiq yozilgan: `kkt_uz()` ichida o'zbekcha "eng" (orttirma, belgisi `P2_D`) uchun (`kkt_v20_soz_tartibi.py:645`) — ya'ni vazn qiymati mos, lekin spec'dagi U/L belgisi bilan emas, `P2_D` bilan bog'langan.
- Taqrizning 27-bandi ("vaznlar qayerdan olingan") uchun: 8 ta vazn kodda spec bilan bir xil. Bu — qiymatlarning MANBASINI ko'rsatadi, ularning ILMIY ASOSINI emas (28-band ochiq qoladi).

**Operatorlar** (spec 1-jadval) — kodda qanday ishlatilishi (faqat `grep`, bajarilmaydi):

| Belgi | Spec ma'nosi | Kodda |
|---|---|---|
| ⊕ | Biriktirish (konkatenatsiya) amali | Formal model satrlarida biriktirish sifatida (`kkt_en()` — `'⊕↓'.join(segs)`, `:624`); SSM segment ajratgichi (`_ssm_split_segments`, `:2663`). |
| V | “Yoki” amali | "Yoki" amali sifatida ISHLATILMAYDI. `KKT_SYMBOLS` da `("V","umumiy BB")` — boshqa ma'noda (umumiy baza) belgilangan. |
| ↓ (⇓) | “Ulanish” (qo‘shilish) yoki “ulanmaslik” (qo‘shilmaslik) amali | Faqat `⊕↓` juftligi ichida va SSM'da "ixtiyoriy segment" belgisi sifatida (`_ssm_split_segments`: `p.startswith("↓")`). `⇓` kodda yo'q. |
| $ | Tanlash amali: $[i, l-m] Pi ko‘rinishida yoziladi | Formal model satrlarida `$[i,1-h]Ci` ko'rinishida (matn sifatida) hosil qilinadi; tanlash amali sifatida hisoblanmaydi. |

**Teskari yo'nalish (kodda bor, spec misollarida tekshirilmagan affikslar)** — `MORPH_RULES` dagi 52 ta affiks hech bir spec qoidasining misoli bilan qamrab olinmagan: `-selves`, `-self`, `-ever`, `-thing`, `-fold`, `-ally`, `-ably`, `-ibly`, `-ward`, `-wards`, `-wise`, `-or`, `-ical`, `-able`, `-ible`, `-ful`, `-less`, `-ous`, `-ive`, `-ory`, `-ary`, `-ant`, `-ent`, `-ic`, `-ish`, `-like`, `-ization`, `-isation`, `-ition`, `-tion`, `-sion`, `-ment`, `-ness`, `-ity`, `-ance`, `-ence`, `-ism`, `-ist`, `-ship`, `-hood`, `-dom`, `-age`, `-ure`, `-ology`, `-logy`, `-ics`, `-izing`, `-ifying`, `-ize`, `-ise`, `-ify`, `-en`. Xususan `-er` (Ot←Fe'l, ish bajaruvchi, `MORPH_RULES:396`) — spesifikatsiyada umuman yo'q kategoriya (`reports/faza_2_er_gap.md` 6-bo'lim).

## 4. YO'Q va ZID qoidalar — ustuvorlik bo'yicha (Vazifa 4)

**Kod o'zgartirilmadi.** Bu ro'yxat — keyingi bosqich uchun. Tuzatish maqsadi faqat spesifikatsiyaga moslash (gold test natijasini yaxshilash emas).

Ustuvorlik o'lchovlari (ikkalasi ham `data/1500_EN_UZ_6_POS_sorted.20.json` 6 asosiy kategoriyasi bo'yicha, avtomatik hisoblangan):
- **Asos soni** — qoida qo'llanadigan kategoriyadagi yozuvlar soni (masalan fe'l qoidasi uchun VERBS). Qoida implement qilinsa, shuncha lug'at so'zi uchun yangi shakl hosil bo'la oladi.
- **Sirt soni** — lug'atda bosh so'zi AYNAN shu qoida shakliga mos yozuvlar (regex skriptdagi `sirt`); L turi uchun — bosh so'z(lar) lug'atda bor-yo'qligi.

| # | qoida_id | POS | holat | tur | asos soni (kategoriya) | sirt soni (misollar) | spec misoli |
|---|---|---|---|---|---|---|---|
| 1 | 2.2 | Ot | ZID | S | 630 (NOUNS (OTLAR)) | 0 | `a network` ⟹ `bitta tarmoq` |
| 2 | 2.3 | Ot | ZID | S | 630 (NOUNS (OTLAR)) | 0 | `an example` ⟹ `bitta misol` |
| 3 | 2.37 | Fe'l | ZID | M | 317 (VERBS (FE'LLAR)) | 0 | `speak + s = speaks` ⟹ `gapir + a + di = gapiradi` |
| 4 | 2.56 | Fe'l | ZID | S | 317 (VERBS (FE'LLAR)) | 0 | `to ask` ⟹ `so‘ramoq` |
| 5 | 2.59 | Fe'l | ZID | S | 317 (VERBS (FE'LLAR)) | 0 | `listen to me` ⟹ `meni tinglamoq` |
| 6 | 2.62 | Fe'l | YO'Q | S | 317 (VERBS (FE'LLAR)) | 0 | `will return` ⟹ `qaytmoq` |
| 7 | 2.31 | Sifat | YO'Q | S | 262 (ADJECTIVES (SIFATLAR)) | 0 | `more comfortable` ⟹ `qulay + roq = qulayroq` |
| 8 | 2.32 | Sifat | YO'Q | S | 262 (ADJECTIVES (SIFATLAR)) | 0 | `most comfortable` ⟹ `eng qulay` |
| 9 | 2.34 | Sifat | YO'Q | S | 262 (ADJECTIVES (SIFATLAR)) | 0 | `less interesting` ⟹ `kamroq qiziqarli` |
| 10 | 3.5 | Ravish | YO'Q | S | 168 (ADVERBS (RAVISHLAR)) | 156 (abruptly, absolutely, abstractly, accordingly, accurately) | `more clearly` ⟹ `aniq + roq = aniqroq` |
| 11 | 2.10 | Ot | YO'Q | N | — | 0 | `man → men` ⟹ `erkak → erkak + lar = erkaklar` |
| 12 | 2.36 | Fe'l | YO'Q | L | — | 0 | `read` ⟹ `o‘qimoq` |
| 13 | 2.38 | Fe'l | YO'Q | L | — | 0 | `to be` ⟹ `bo‘lmoq` |
| 14 | 2.39 | Fe'l | YO'Q | L | — | 0 | `am` ⟹ `man (1-shaxs birlik affiksi)` |
| 15 | 2.41 | Fe'l | YO'Q | L | — | 0 | `was, were` ⟹ `edi` |
| 16 | 2.44 | Fe'l | YO'Q | L | — | 0 | `to have` ⟹ `bor bo‘lmoq` |
| 17 | 2.45 | Fe'l | YO'Q | L | — | 0 | `to do` ⟹ `qilmoq` |
| 18 | 2.48 | Fe'l | YO'Q | L | — | 0 | `become` ⟹ `bo‘lmoq` |
| 19 | 2.50 | Fe'l | YO'Q | L | — | 0 | `could` ⟹ `ol + ar + di = olardi` |
| 20 | 2.55a | Fe'l | YO'Q | L | — | 0 | `need` ⟹ `kerak` |
| 21 | 2.58 | Fe'l | YO'Q | L | — | 0 | `to follow` ⟹ `kuzatmoq` |
| 22 | 3.17 | Son | YO'Q | S | — | 0 | `three hundred and five` ⟹ `uch yuz besh (bog‘lovchisiz)` |
| 23 | 3.19 | Son | YO'Q | S | — | 0 | `hundred and twenty-first` ⟹ `bir yuz yigirma bir + inchi` |
| 24 | 3.20 | Son | YO'Q | S | — | 0 | `chapter five` ⟹ `besh + inchi bob = beshinchi bob` |
| 25 | –(Ravish) | Ravish | YO'Q | L | — | 0 | `very` ⟹ `juda` |
| 26 | –(Sifat) | Sifat | YO'Q | L | — | 0 | `big` ⟹ `katta` |

Jami YO'Q: **21**, ZID: **5**.

## 5. `CH2_EVX_EXAMPLES` ↔ spesifikatsiya (lug'atdagi dissertatsiya nusxalari rasmiy qoidaga mosmi)

`load_ch2_evx_examples()` bu 52 ta yozuvni UB_en_w'ga headword sifatida yozadi — L turidagi ko'p natijalar aynan shu yerdan keladi. Inglizcha shakli spec misoli bilan bir xil bo'lgan 49 ta juftdan **13 tasida o'zbekcha tarjima spec'dan farq qiladi**:

| CH2 en | CH2 uz | spec qoidasi | spec kutilgan | izoh |
|---|---|---|---|---|
| a network | tarmoq | 2.2 | bitta tarmoq |  |
| an example | misol | 2.3 | bitta misol |  |
| schoolboys | Bojxonalar | 2.12 | maktab bolalari |  |
| contents | mazmun | 2.15 | mundarija |  |
| would | keladi | 2.47 | edi |  |
| must | shart | 2.53 | kerak |  |
| to follow | ergashmoq | 2.58 | kuzatmoq |  |
| cleverer | aqilliroq | 2.21 | aqillroq | CH2 docx katagining "+" qismlari yig'indisiga («aqilliroq») teng — docx ichki nomuvofiqligi |
| busier | kattaroq | 2.27 | bandroq |  |
| busiest | eng katta | 2.28 | eng band |  |
| gayer | eng sho'x | 2.29 | sho‘xroq |  |
| more comfortable | eng qulay | 2.31 | qulayroq |  |
| less interesting | so'z kamroq qiziqarli | 2.34 | kamroq qiziqarli |  |

Inglizcha shakli hech bir spec misoliga to'g'ri kelmagan CH2 yozuvlari (3 ta): `capabilityies`, `leafes`, `ought`. (Masalan `capabilityies`/`leafes` — `reports/ch2_leakage_check.md` dagi transkripsiya xatolari; spec'da to'g'ri `capabilities`/`leaves`.)

## 6. Batafsil — har bir qoida bo'yicha to'liq xom natija

### 2.1 — Ko‘plik oti – “-s” affiksi bilan yasaladi

- Spec: `variable + s = variables` → `o‘zgar + uv + chi + lar = o‘zgaruvchilar`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: variable→o‘zgaruvchi (Ot)
- stub: `variables` → «O‘zgaruvchilar» (kutilgan «o‘zgaruvchilar») ✓ — yo'l: translate_phrase; variables: qoida -s (o'zak variable, Ot)
- real lug'at: `variables` → «O'zgaruvchilar» (kutilgan «o‘zgaruvchilar») ✓ — yo'l: translate_phrase; variables: qoida -s (o'zak variable, Ot)

### 2.2 — Noaniq artikl “a” undosh tovush bilan boshlanuvchi otdan oldin qo‘llaniladi

- Spec: `a network` → `bitta tarmoq`
- Tur: **S**, holat: **ZID**
- Stub: network→tarmoq (Ot)
- stub: `a network` → «Tarmoq» (kutilgan «bitta tarmoq») ✗ — yo'l: translate_phrase; a: topilmadi; network: lug'at[stub]
- real lug'at: `a network` → «[a?] Tarmoq» (kutilgan «bitta tarmoq») ✗ — yo'l: so'zma-so'z; a: topilmadi; network: lug'at[json]

### 2.3 — Noaniq artikl “an” unli tovush bilan boshlanuvchi otdan oldin qo‘llaniladi

- Spec: `an example` → `bitta misol`
- Tur: **S**, holat: **ZID**
- Stub: example→misol (Ot)
- stub: `an example` → «Misol» (kutilgan «bitta misol») ✗ — yo'l: translate_phrase; an: topilmadi; example: lug'at[stub]
- real lug'at: `an example` → «Misol» (kutilgan «bitta misol») ✗ — yo'l: translate_phrase; an: topilmadi; example: lug'at[json]

### 2.4 — Aniq artikl “the” so‘zlovchi va tinglovchiga aniq bo‘lgan otdan oldin qo‘llaniladi

- Spec: `the progress` → `taraqqiyot`
- Tur: **S**, holat: **TO'LIQ MOS**
- Stub: progress→taraqqiyot (Ot)
- stub: `the progress` → «Taraqqiyot» (kutilgan «taraqqiyot») ✓ — yo'l: translate_phrase; the: topilmadi; progress: lug'at[stub]
- real lug'at: `the progress` → «[the?] [progress?]» (kutilgan «taraqqiyot») ✗ — yo'l: so'zma-so'z; the: topilmadi; progress: topilmadi

### 2.5 — Atoqli otlarga “-s” ko‘plik affiksi qo‘shilishi (o‘zbekchada so‘z yasovchi “-lik” + ko‘plik “-lar” bilan beriladi)

- Spec: `The Germanys` → `Germaniya + lik + lar = Germaniyaliklar`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: germany→Germaniya (Ot)
- stub: `The Germanys` → «Germaniyalar» (kutilgan «Germaniyaliklar») ✗ — yo'l: translate_phrase; the: topilmadi; germanys: qoida -s (o'zak germany, Ot)
- real lug'at: `The Germanys` → «[the?] [germanys?]» (kutilgan «Germaniyaliklar») ✗ — yo'l: so'zma-so'z; the: topilmadi; germanys: topilmadi

### 2.6 — Oxiri “-s, -ss, -x, -ch, -sh” bilan tugagan otlarga ko‘plik “-es” affiksi qo‘shiladi

- Spec: `process + es = processes` → `jarayon + lar = jarayonlar`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: process→jarayon (Ot)
- stub: `processes` → «Jarayonlar» (kutilgan «jarayonlar») ✓ — yo'l: translate_phrase; processes: qoida -es (o'zak process, Ot)
- real lug'at: `processes` → «Jarayonlar» (kutilgan «jarayonlar») ✓ — yo'l: translate_phrase; processes: lug'at[chapter2_evx]

### 2.7 — Undoshdan keyin “-y” bilan tugagan otlarda “-y” “-i” ga aylanib “-es” qo‘shiladi

- Spec: `capability + ies = capabilities` → `imkoniyat + lar = imkoniyatlar` — *docx izohi:* "capability + ies = capabilities": "+" bilan ajratilgan komponentlar qo'shilganda "capabilityies" hosil bo'ladi, natija sifatida esa "capabilities" yozilgan.
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: capability→imkoniyat (Ot)
- stub: `capabilities` → «Imkoniyatlar» (kutilgan «imkoniyatlar») ✓ — yo'l: translate_phrase; capabilities: qoida -ies (o'zak capability, Ot)
- real lug'at: `capabilities` → «[capabilities?]» (kutilgan «imkoniyatlar») ✗ — yo'l: so'zma-so'z; capabilities: topilmadi

### 2.8 — Unlidan keyin “-y” bilan tugagan otlarda “-y” o‘zgarmasdan “-s” qo‘shiladi

- Spec: `delay + s = delays` → `kechikish + lar = kechikishlar`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: delay→kechikish (Ot)
- stub: `delays` → «Kechikishlar» (kutilgan «kechikishlar») ✓ — yo'l: translate_phrase; delays: qoida -s (o'zak delay, Ot)
- real lug'at: `delays` → «Kechikishlar» (kutilgan «kechikishlar») ✓ — yo'l: translate_phrase; delays: lug'at[chapter2_evx]

### 2.9 — “-f, -fe” bilan tugagan otlarda “-f” “-v” ga aylanib “-s/-es” qo‘shiladi

- Spec: `leaf = lea + v + es = leaves` → `barg + lar = barglar`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: leaf→barg (Ot)
- stub: `leaves` → «Barglar» (kutilgan «barglar») ✓ — yo'l: translate_phrase; leaves: qoida -ves (o'zak leaf, Ot)
- real lug'at: `leaves` → «[leaves?]» (kutilgan «barglar») ✗ — yo'l: so'zma-so'z; leaves: topilmadi

### 2.10 — Ko‘plik affiksi qo‘shilmasdan o‘zakdan o‘zgaradigan otlar (noqoida ko‘plik)

- Spec: `man → men` → `erkak → erkak + lar = erkaklar`
- Tur: **N**, holat: **YO'Q**
- Stub: man→erkak (Ot)
- stub: `men` → «[men?]» (kutilgan «erkaklar») ✗ — yo'l: so'zma-so'z; men: topilmadi
- real lug'at: `men` → «Erkaklar» (kutilgan «erkaklar») ✓ — yo'l: translate_phrase; men: lug'at[chapter2_evx]

### 2.11 — Chiziqcha (defis) bilan ajratib yoziladigan qo‘shma otlarning ko‘pligi

- Spec: `custom + houses = customhouses` → `bojxona + lar = bojxonalar` — *docx izohi:* Tavsifda "chiziqcha (defis) bilan ajratib yoziladigan" deyilgan, lekin ingliz misolida ("custom + houses = customhouses") defis yo'q — natija qo'shib yozilgan.
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: customhouse→bojxona (Ot)
- Izoh: Stub o'zagi "customhouse" — docx'dagi "custom + houses = customhouses" ning birligi (docx'da alohida yozilmagan).
- stub: `customhouses` → «Bojxonalar» (kutilgan «bojxonalar») ✓ — yo'l: translate_phrase; customhouses: qoida -s (o'zak customhouse, Ot)
- real lug'at: `customhouses` → «Bojxonalar» (kutilgan «bojxonalar») ✓ — yo'l: translate_phrase; customhouses: lug'at[chapter2_evx]

### 2.12 — Qo‘shib yoziladigan qo‘shma otlarning ko‘pligi (ikki asosdan iborat)

- Spec: `schoolboy + s = schoolboys` → `maktab bola + lari = maktab bolalari`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: schoolboy→maktab bola (Ot)
- stub: `schoolboys` → «Maktab bolalar» (kutilgan «maktab bolalari») ✗ — yo'l: translate_phrase; schoolboys: qoida -s (o'zak schoolboy, Ot)
- real lug'at: `schoolboys` → «Bojxonalar» (kutilgan «maktab bolalari») ✗ — yo'l: translate_phrase; schoolboys: lug'at[chapter2_evx]

### 2.13 — Fe’l asosiga “-ation” affiksi qo‘shilib ot yasalishi

- Spec: `inform + ation = information` → `axborot (affikssiz)` — *docx izohi:* O'zbek misoli katagida izoh qavs ichida berilgan: "axborot (affikssiz)" — natija so'zi "axborot", "(affikssiz)" misolning bir qismi emas.
- Tur: **M**, holat: **QISMAN MOS**
- Stub: inform→⟨inform⟩ (Fe'l)
- Izoh: Docx "inform" ning o'zbekchasini bermagan, natija esa affikssiz ("axborot") — shu sabab stub'da `⟨inform⟩` BELGI (ma'lumot emas) ishlatildi: u faqat kod o'zbek tomonini qanday qurishini ko'rsatadi. Natija "axborot" ga faqat butun so'z lug'atda bo'lsa teng bo'la oladi.
- stub: `information` → «⟨inform⟩ish» (kutilgan «axborot») ✗ — yo'l: translate_phrase; information: qoida -ation (o'zak inform, Ot)
- real lug'at: `information` → «Axborot» (kutilgan «axborot») ✓ — yo'l: translate_phrase; information: lug'at[chapter2_evx]

### 2.15 — Jamlama otlar – doim ko‘plik shaklida ishlatiladi, lekin o‘zbekchaga birlik bilan tarjima qilinadi

- Spec: `content + s = contents` → `mundarija`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: content→mundarija (Ot)
- Izoh: Spec: jamlama ot o'zbekchaga BIRLIK bilan ("mundarija"). Stub o'zagi "content" → "mundarija" (docx'dagi birlik tarjima).
- stub: `contents` → «Mundarijalar» (kutilgan «mundarija») ✗ — yo'l: translate_phrase; contents: qoida -s (o'zak content, Ot)
- real lug'at: `contents` → «Mazmun» (kutilgan «mundarija») ✗ — yo'l: translate_phrase; contents: lug'at[chapter2_evx]

### 2.16 — Qaratqich kelishigi – apostrof “’s” bilan yoziladi

- Spec: `student’s` → `student + ning`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: student→student (Ot)
- stub: `student's` → «Studentning» (kutilgan «studentning») ✓ — yo'l: translate_phrase; student's: qoida -'s (o'zak student, Ot)
- real lug'at: `student's` → «Studentning» (kutilgan «studentning») ✓ — yo'l: translate_phrase; student's: lug'at[chapter2_evx]

### –(Sifat) — Oddiy sifat – qo‘shimchasiz, o‘zgarmas shaklda

- Spec: `big` → `katta`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `big` → «[big?]» (kutilgan «katta») ✗ — yo'l: so'zma-so'z; big: topilmadi

### 2.19 — Yasama sifat – affiks qo‘shish orqali hosil qilinadi

- Spec: `form + al = formal` → `rasm + iy = rasmiy`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: form→rasm (Ot)
- stub: `formal` → «Rasmga oid» (kutilgan «rasmiy») ✗ — yo'l: translate_phrase; formal: qoida -al (o'zak form, Sifat)
- real lug'at: `formal` → «[formal?]» (kutilgan «rasmiy») ✗ — yo'l: so'zma-so'z; formal: topilmadi

### 2.20 — Qo‘shma sifat – ikki asosdan tashkil topadi

- Spec: `high-dimension + al` → `ko‘p o‘lchov + li` — *docx izohi:* Ingliz misolida natija shakli berilmagan ("high-dimension + al" — "=" yo'q); o'zbek misolida ham ("ko‘p o‘lchov + li").
- Tur: **M**, holat: **QISMAN MOS**
- Stub: high→ko‘p (Sifat), dimension→o‘lchov (Ot)
- Izoh: Docx natija shaklini bermagan — kirish/kutilgan qiymat "+" qismlarini qo'shib olingan.
- stub: `high-dimensional` → «Ko‘p o‘lchovga oid» (kutilgan «ko‘p o‘lchovli») ✗ — yo'l: translate_phrase; high: lug'at[stub]; dimensional: qoida -al (o'zak dimension, Sifat)
- real lug'at: `high-dimensional` → «O‘lchamli» (kutilgan «ko‘p o‘lchovli») ✗ — yo'l: translate_phrase; high: topilmadi; dimensional: lug'at[json]

### 2.21 — Qiyosiy daraja – bir-ikki bo‘g‘inli sifatlarga “-er” qo‘shiladi

- Spec: `clever + er = cleverer` → `aqil + li + roq = aqillroq` — *docx izohi:* "aqil + li + roq = aqillroq": "+" bilan ajratilgan komponentlar qo'shilganda "aqilliroq" hosil bo'ladi, natija sifatida esa "aqillroq" yozilgan.
- Tur: **M**, holat: **QISMAN MOS**
- Stub: clever→aqilli (Sifat, manba 2.22)
- stub: `cleverer` → «Aqilliroq» (kutilgan «aqillroq») ✗ ⚠ natija docx katagining "+" qismlari yig'indisiga («aqilliroq») teng — yo'l: translate_phrase; cleverer: qoida -er (o'zak clever, Sifat)
- real lug'at: `cleverer` → «Aqilliroq» (kutilgan «aqillroq») ✗ ⚠ natija docx katagining "+" qismlari yig'indisiga («aqilliroq») teng — yo'l: translate_phrase; cleverer: lug'at[chapter2_evx]

### 2.22 — Orttirma daraja – bir-ikki bo‘g‘inli sifatlarga “-est” qo‘shiladi

- Spec: `clever + est = cleverest` → `eng aqil + li = eng aqilli`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: clever→aqilli (Sifat)
- stub: `cleverest` → «Eng aqilli» (kutilgan «eng aqilli») ✓ — yo'l: translate_phrase; cleverest: qoida -est (o'zak clever, Sifat)
- real lug'at: `cleverest` → «Eng aqilli» (kutilgan «eng aqilli») ✓ — yo'l: translate_phrase; cleverest: lug'at[chapter2_evx]

### 2.23 — O‘qilmaydigan “e” bilan tugagan sifatlarda “e” tushib, “-er” qo‘shiladi

- Spec: `large → larg + er = larger` → `katta → katta + roq = kattaroq`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: large→katta (Sifat)
- stub: `larger` → «Kattaroq» (kutilgan «kattaroq») ✓ — yo'l: translate_phrase; larger: qoida -er (o'zak large, Sifat)
- real lug'at: `larger` → «[larger?]» (kutilgan «kattaroq») ✗ — yo'l: so'zma-so'z; larger: topilmadi

### 2.24 — O‘qilmaydigan “e” bilan tugagan sifatlarda “e” tushib, “-est” qo‘shiladi

- Spec: `large → larg + est = largest` → `katta → eng katta`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: large→katta (Sifat)
- stub: `largest` → «Eng katta» (kutilgan «eng katta») ✓ — yo'l: translate_phrase; largest: qoida -est (o'zak large, Sifat)
- real lug'at: `largest` → «[largest?]» (kutilgan «eng katta») ✗ — yo'l: so'zma-so'z; largest: topilmadi

### 2.25 — Qisqa unlidan keyin bitta undosh bilan tugagan sifatda undosh ikkilanib “-er” qo‘shiladi

- Spec: `big → bigg + er = bigger` → `katta → katta + roq = kattaroq`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: big→katta (Sifat)
- stub: `bigger` → «Kattaroq» (kutilgan «kattaroq») ✓ — yo'l: translate_phrase; bigger: qoida -er (o'zak big, Sifat)
- real lug'at: `bigger` → «[bigger?]» (kutilgan «kattaroq») ✗ — yo'l: so'zma-so'z; bigger: topilmadi

### 2.26 — Qisqa unlidan keyin bitta undosh bilan tugagan sifatda undosh ikkilanib “-est” qo‘shiladi

- Spec: `big → bigg + est = biggest` → `katta → eng katta`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: big→katta (Sifat)
- stub: `biggest` → «Eng katta» (kutilgan «eng katta») ✓ — yo'l: translate_phrase; biggest: qoida -est (o'zak big, Sifat)
- real lug'at: `biggest` → «[biggest?]» (kutilgan «eng katta») ✗ — yo'l: so'zma-so'z; biggest: topilmadi

### 2.27 — Undoshdan keyin “-y” bilan tugagan sifatda “-y” “-i” ga aylanib “-er” qo‘shiladi

- Spec: `busy → busi + er = busier` → `band → bandroq`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: busy→band (Sifat)
- stub: `busier` → «Bandroq» (kutilgan «bandroq») ✓ — yo'l: translate_phrase; busier: qoida -ier (o'zak busy, Sifat)
- real lug'at: `busier` → «Kattaroq» (kutilgan «bandroq») ✗ — yo'l: translate_phrase; busier: lug'at[chapter2_evx]

### 2.28 — Undoshdan keyin “-y” bilan tugagan sifatda “-y” “-i” ga aylanib “-est” qo‘shiladi

- Spec: `busy → busi + est = busiest` → `band → eng band`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: busy→band (Sifat)
- stub: `busiest` → «Band» (kutilgan «eng band») ✗ — yo'l: translate_phrase; busiest: qoida -∅ (o'zak busy, Sifat)
- real lug'at: `busiest` → «Eng katta» (kutilgan «eng band») ✗ — yo'l: translate_phrase; busiest: lug'at[chapter2_evx]

### 2.29 — Unlidan keyin “-y” bilan tugagan sifatda “-y” o‘zgarmasdan “-er” qo‘shiladi

- Spec: `gay → gay + er = gayer` → `sho‘x → sho‘x + roq = sho‘xroq`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: gay→sho‘x (Sifat)
- stub: `gayer` → «Sho‘xroq» (kutilgan «sho‘xroq») ✓ — yo'l: translate_phrase; gayer: qoida -er (o'zak gay, Sifat)
- real lug'at: `gayer` → «Sho'xroq» (kutilgan «sho‘xroq») ✓ — yo'l: translate_phrase; gayer: lug'at[chapter2_evx]

### 2.30 — Unlidan keyin “-y” bilan tugagan sifatda “-y” o‘zgarmasdan “-est” qo‘shiladi

- Spec: `gay → gay + est = gayest` → `sho‘x → eng sho‘x`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: gay→sho‘x (Sifat)
- stub: `gayest` → «Eng sho‘x» (kutilgan «eng sho‘x») ✓ — yo'l: translate_phrase; gayest: qoida -est (o'zak gay, Sifat)
- real lug'at: `gayest` → «[gayest?]» (kutilgan «eng sho‘x») ✗ — yo'l: so'zma-so'z; gayest: topilmadi

### 2.31 — Ko‘p bo‘g‘inli sifatlarning qiyosiy darajasi “more” so‘zi bilan yasaladi

- Spec: `more comfortable` → `qulay + roq = qulayroq`
- Tur: **S**, holat: **YO'Q**
- Stub: comfortable→qulay (Sifat)
- stub: `more comfortable` → «Qulay» (kutilgan «qulayroq») ✗ — yo'l: translate_phrase; more: topilmadi; comfortable: lug'at[stub]
- real lug'at: `more comfortable` → «[more?] [comfortable?]» (kutilgan «qulayroq») ✗ — yo'l: so'zma-so'z; more: topilmadi; comfortable: topilmadi

### 2.32 — Ko‘p bo‘g‘inli sifatlarning orttirma darajasi “most” so‘zi bilan yasaladi

- Spec: `most comfortable` → `eng qulay`
- Tur: **S**, holat: **YO'Q**
- Stub: comfortable→qulay (Sifat, manba 2.31)
- stub: `most comfortable` → «Qulay» (kutilgan «eng qulay») ✗ — yo'l: translate_phrase; most: topilmadi; comfortable: lug'at[stub]
- real lug'at: `most comfortable` → «Eng ko'p / Aksariyat» (kutilgan «eng qulay») ✗ — yo'l: translate_phrase; most: lug'at[json]; comfortable: topilmadi

### 2.33 — Qoidaga bo‘ysinmaydigan (noqoida) daraja o‘zgarishi

- Spec: `good → better → best` → `yaxshi → yaxshiroq → eng yaxshi`
- Tur: **N**, holat: **QISMAN MOS**
- Stub: good→yaxshi (Sifat)
- stub: `good` → «Yaxshi» (kutilgan «yaxshi») ✓ — yo'l: translate_phrase; good: lug'at[stub]
- stub: `better` → «Yaxshi» (kutilgan «yaxshiroq») ✗ — yo'l: translate_phrase; better: qoida -∅ (o'zak good, Sifat)
- stub: `best` → «[best?]» (kutilgan «eng yaxshi») ✗ — yo'l: so'zma-so'z; best: topilmadi
- real lug'at: `good` → «[good?]» (kutilgan «yaxshi») ✗ — yo'l: so'zma-so'z; good: topilmadi
- real lug'at: `better` → «[better?]» (kutilgan «yaxshiroq») ✗ — yo'l: so'zma-so'z; better: topilmadi
- real lug'at: `best` → «Eng yaxshi» (kutilgan «eng yaxshi») ✓ — yo'l: translate_phrase; best: lug'at[json]

### 2.34 — Kamlik darajasi “less” (qiyosiy) / “least” (orttirma) so‘zlari bilan yasaladi

- Spec: `less interesting` → `kamroq qiziqarli`
- Tur: **S**, holat: **YO'Q**
- Stub: interesting→qiziqarli (Sifat)
- stub: `less interesting` → «Qiziqarli» (kutilgan «kamroq qiziqarli») ✗ — yo'l: translate_phrase; less: topilmadi; interesting: lug'at[stub]
- real lug'at: `less interesting` → «[less?] Qiziqishing» (kutilgan «kamroq qiziqarli») ✗ — yo'l: so'zma-so'z; less: topilmadi; interesting: qoida -ing (o'zak interest, Fe'l)

### 2.36 — Sodda fe’l – affikssiz, o‘zgarmas shaklda

- Spec: `read` → `o‘qimoq`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `read` → «[read?]» (kutilgan «o‘qimoq») ✗ — yo'l: so'zma-so'z; read: topilmadi

### 2.37 — Asosiy fe’l – 3-shaxs birlikda hozirgi zamonda “-s” qo‘shiladi

- Spec: `speak + s = speaks` → `gapir + a + di = gapiradi`
- Tur: **M**, holat: **ZID**
- Stub: speak→gapir (Fe'l)
- stub: `speaks` → «Gapirlar» (kutilgan «gapiradi») ✗ — yo'l: translate_phrase; speaks: qoida -s (o'zak speak, Ot)
- real lug'at: `speaks` → «[speaks?]» (kutilgan «gapiradi») ✗ — yo'l: so'zma-so'z; speaks: topilmadi

### 2.38 — Yordamchi fe’l “to be” – ko‘plab grammatik vazifalarni bajaradi

- Spec: `to be` → `bo‘lmoq`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `to be` → «Ga» (kutilgan «bo‘lmoq») ✗ — yo'l: translate_phrase; to: lug'at[docx]; be: topilmadi

### 2.39 — “to be” fe’lining hozirgi zamon “am” shakli (1-shaxs birlik)

- Spec: `am` → `man (1-shaxs birlik affiksi)`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `am` → «[am?]» (kutilgan «man») ✗ — yo'l: so'zma-so'z; am: topilmadi

### 2.41 — “to be” fe’lining o‘tgan zamon “was / were” shakli

- Spec: `was, were` → `edi`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `was` → «[was?]» (kutilgan «edi») ✗ — yo'l: so'zma-so'z; was: topilmadi
- real lug'at: `were` → «[were?]» (kutilgan «edi») ✗ — yo'l: so'zma-so'z; were: topilmadi

### 2.42 — “to be” fe’lining o‘tgan zamon sifatdoshi “been” (Past Participle)

- Spec: `been` → `bo‘l + gan = bo‘lgan`
- Tur: **N**, holat: **QISMAN MOS**
- Stub: be→bo‘lmoq (Fe'l, manba 2.38)
- stub: `been` → «bo‘ltir» (kutilgan «bo‘lgan») ✗ — yo'l: so'zma-so'z; been: qoida -en (o'zak be, Fe'l)
- real lug'at: `been` → «[been?]» (kutilgan «bo‘lgan») ✗ — yo'l: so'zma-so'z; been: topilmadi

### 2.43 — “to be” fe’lining “being” (gerund / hozirgi zamon sifatdoshi) shakli

- Spec: `be + ing = being` → `bo‘layot + gan = bo‘layotgan`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: be→bo‘lmoq (Fe'l, manba 2.38)
- stub: `being` → «bo‘ling» (kutilgan «bo‘layotgan») ✗ — yo'l: so'zma-so'z; being: qoida -ing (o'zak be, Fe'l)
- real lug'at: `being` → «[being?]» (kutilgan «bo‘layotgan») ✗ — yo'l: so'zma-so'z; being: topilmadi

### 2.44 — Yordamchi fe’l “to have” – egalik/zaruratni ifodalaydi

- Spec: `to have` → `bor bo‘lmoq`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `to have` → «Ga» (kutilgan «bor bo‘lmoq») ✗ — yo'l: translate_phrase; to: lug'at[docx]; have: topilmadi

### 2.45 — Yordamchi/leksik fe’l “to do” – inkor, so‘roq, ta’kid vazifasini bajaradi

- Spec: `to do` → `qilmoq`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `to do` → «Ga» (kutilgan «qilmoq») ✗ — yo'l: translate_phrase; to: lug'at[docx]; do: topilmadi

### 2.46 — Yordamchi fe’l “will” – kelasi zamonni ifodalaydi

- Spec: `will` → `kel + a + di = keladi`
- Tur: **L**, holat: **TO'LIQ MOS**
- real lug'at: `will` → «keladi» (kutilgan «keladi») ✓ — yo'l: so'zma-so'z; will: lug'at[chapter2_evx]

### 2.47 — Yordamchi fe’l “would” – o‘tgan zamonni ifodalaydi

- Spec: `would` → `edi`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `would` → «keladi» (kutilgan «edi») ✗ — yo'l: so'zma-so'z; would: lug'at[chapter2_evx]

### 2.48 — Bog‘lovchi fe’l (linking verb) – o‘zbek tilida mos turi yo‘q

- Spec: `become` → `bo‘lmoq`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `become` → «[become?]» (kutilgan «bo‘lmoq») ✗ — yo'l: so'zma-so'z; become: topilmadi

### 2.49 — Modal fe’l “can” – imkoniyatni bildiradi

- Spec: `can` → `qila olmoq`
- Tur: **L**, holat: **TO'LIQ MOS**
- real lug'at: `can` → «qila  olmoq» (kutilgan «qila olmoq») ✓ — yo'l: so'zma-so'z; can: lug'at[chapter2_evx]

### 2.50 — Modal fe’l “could” – “can”ning o‘tgan zamon shakli

- Spec: `could` → `ol + ar + di = olardi`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `could` → «[could?]» (kutilgan «olardi») ✗ — yo'l: so'zma-so'z; could: topilmadi

### 2.51 — Modal fe’l “may” – ruxsat/ehtimolni bildiradi

- Spec: `may` → `mumkin`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `may` → «Ajratib ko'rsatmoq» (kutilgan «mumkin») ✗ — yo'l: so'zma-so'z; may: lug'at[chapter2_evx] +MDB almashtirdi

### 2.52 — Modal fe’l “might” – “may”dan kamroq ehtimolni bildiradi

- Spec: `might` → `mumkin`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `might` → «Ajratib ko'rsatmoq» (kutilgan «mumkin») ✗ — yo'l: so'zma-so'z; might: lug'at[chapter2_evx] +MDB almashtirdi

### 2.53 — Modal fe’l “must” – majburiyatni bildiradi

- Spec: `must` → `kerak`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `must` → «shart» (kutilgan «kerak») ✗ — yo'l: so'zma-so'z; must: lug'at[chapter2_evx]

### 2.54 — Modal fe’l “ought to” – tavsiya/majburiyatni bildiradi

- Spec: `ought to` → `zarur`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `ought to` → «Ga ajratib ko'rsatmoq» (kutilgan «zarur») ✗ — yo'l: translate_phrase; ought: lug'at[chapter2_evx] +MDB almashtirdi; to: lug'at[docx]

### 2.55a — Modal fe’l “need” – zaruratni bildiradi

- Spec: `need` → `kerak`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `need` → «[need?]» (kutilgan «kerak») ✗ — yo'l: so'zma-so'z; need: topilmadi

### 2.56 — Infinitive fe’l – “to” yuklamasi bilan yoziladi, shaxs-sonni ko‘rsatmaydi

- Spec: `to ask` → `so‘ramoq`
- Tur: **S**, holat: **ZID**
- Stub: ask→so‘ramoq (Fe'l)
- Izoh: `INFINITIVE_MARKERS` (to/will/can/...) kodda bor, lekin faqat `select_meaning_contextual()` da ko'p ma'noli so'zning Fe'l ma'nosini TANLASH uchun ishlatiladi — tarjima qoidasi emas.
- stub: `to ask` → «Ga so‘ramoq» (kutilgan «so‘ramoq») ✗ — yo'l: translate_phrase; to: lug'at[seed(kod)]; ask: lug'at[stub]
- real lug'at: `to ask` → «Ga ajratib ko'rsatmoq» (kutilgan «so‘ramoq») ✗ — yo'l: translate_phrase; to: lug'at[docx]; ask: lug'at[json] +MDB almashtirdi

### 2.55b — Gerund – fe’lga “-ing” qo‘shilib yasaladi, otlashadi

- Spec: `read + ing = reading` → `o‘qish + ni = o‘qishni`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: read→o‘qimoq (Fe'l, manba 2.36)
- stub: `reading` → «o‘qiing» (kutilgan «o‘qishni») ✗ — yo'l: so'zma-so'z; reading: qoida -ing (o'zak read, Fe'l)
- real lug'at: `reading` → «o'qishni» (kutilgan «o‘qishni») ✓ — yo'l: so'zma-so'z; reading: lug'at[chapter2_evx]

### 2.58 — O‘timli fe’l (transitive) – o‘zidan keyin vositasiz to‘ldiruvchi talab qiladi

- Spec: `to follow` → `kuzatmoq`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `to follow` → «Ga» (kutilgan «kuzatmoq») ✗ — yo'l: translate_phrase; to: lug'at[docx]; follow: topilmadi

### 2.59 — O‘timsiz fe’l (intransitive) – o‘zidan keyin vositasiz to‘ldiruvchi talab qilmaydi

- Spec: `listen to me` → `meni tinglamoq`
- Tur: **S**, holat: **ZID**
- Stub: listen→tinglamoq (Fe'l), me→meni (Olmosh, manba 3.22)
- stub: `listen to me` → «Meniga tinglamoq» (kutilgan «meni tinglamoq») ✗ — yo'l: translate_phrase; listen: lug'at[stub]; to: lug'at[seed(kod)]; me: lug'at[stub]
- real lug'at: `listen to me` → «Meniga» (kutilgan «meni tinglamoq») ✗ — yo'l: translate_phrase; listen: topilmadi; to: lug'at[docx]; me: lug'at[json]

### 2.61 — Hozirgi oddiy zamon (Simple Present)

- Spec: `understand` → `tushunmoq`
- Tur: **L**, holat: **TO'LIQ MOS**
- real lug'at: `understand` → «Tushunmoq» (kutilgan «tushunmoq») ✓ — yo'l: so'zma-so'z; understand: lug'at[json]

### 2.62 — Kelasi oddiy zamon (Simple Future) – “will + fe’l”

- Spec: `will return` → `qaytmoq`
- Tur: **S**, holat: **YO'Q**
- Stub: return→qaytmoq (Fe'l)
- Izoh: `INFINITIVE_MARKERS` (to/will/can/...) kodda bor, lekin faqat `select_meaning_contextual()` da ko'p ma'noli so'zning Fe'l ma'nosini TANLASH uchun ishlatiladi — tarjima qoidasi emas.
- stub: `will return` → «[will?] qaytmoq» (kutilgan «qaytmoq») ✗ — yo'l: so'zma-so'z; will: topilmadi; return: lug'at[stub]
- real lug'at: `will return` → «keladi [return?]» (kutilgan «qaytmoq») ✗ — yo'l: so'zma-so'z; will: lug'at[chapter2_evx]; return: topilmadi

### 2.63 — O‘tgan zamon (Simple Past), to‘g‘ri fe’lga “-ed” qo‘shiladi

- Spec: `work + ed = worked` → `ishla + di = ishladi`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: work→ishla (Fe'l)
- stub: `worked` → «ishlaaylik» (kutilgan «ishladi») ✗ — yo'l: so'zma-so'z; worked: qoida -ed (o'zak work, Fe'l)
- real lug'at: `worked` → «Ishlaaylik» (kutilgan «ishladi») ✗ — yo'l: so'zma-so'z; worked: qoida -ed (o'zak work, Fe'l)

### 2.64 — To‘g‘ri fe’l – “-y” harfi “i”ga aylanib “-ed” qo‘shiladi (imlo o‘zgarishi)

- Spec: `simplif(y) + ied = simplified` → `soddalashtiril + di = soddalashtirildi` — *docx izohi:* "simplif(y) + ied = simplified": "+" bilan ajratilgan komponentlar qo'shilganda "simplif(y)ied" hosil bo'ladi, natija sifatida esa "simplified" yozilgan.
- Tur: **M**, holat: **QISMAN MOS**
- Stub: simplify→soddalashtiril (Fe'l)
- stub: `simplified` → «soddalashtirilgan» (kutilgan «soddalashtirildi») ✗ — yo'l: so'zma-so'z; simplified: qoida -ied (o'zak simplify, Fe'l)
- real lug'at: `simplified` → «Oddiylashtirgan» (kutilgan «soddalashtirildi») ✗ — yo'l: so'zma-so'z; simplified: qoida -ify+ied (o'zak simple, Fe'l)

### 2.65 — Noto‘g‘ri fe’l (irregular verb) – o‘zak tovush o‘zgarishi yoki o‘zgarmaslik orqali yasaladi

- Spec: `send → sent → sent` → `yubormoq → yubordi → yuborgan`
- Tur: **N**, holat: **QISMAN MOS**
- Stub: send→yubormoq (Fe'l)
- Izoh: Bitta inglizcha "sent" ikki xil o'zbekcha shaklga (yubordi / yuborgan) mos keladi — kontekstsiz bitta so'z uchun ikkala juft bir vaqtda mos kelishi mumkin emas.
- stub: `send` → «yubormoq» (kutilgan «yubormoq») ✓ — yo'l: so'zma-so'z; send: lug'at[stub]
- stub: `sent` → «yubormoq» (kutilgan «yubordi») ✗ — yo'l: so'zma-so'z; sent: qoida -∅ (o'zak send, Fe'l)
- stub: `sent` → «yubormoq» (kutilgan «yuborgan») ✗ — yo'l: so'zma-so'z; sent: qoida -∅ (o'zak send, Fe'l)
- real lug'at: `send` → «[send?]» (kutilgan «yubormoq») ✗ — yo'l: so'zma-so'z; send: topilmadi
- real lug'at: `sent` → «yuborgan» (kutilgan «yubordi») ✗ — yo'l: so'zma-so'z; sent: lug'at[chapter2_evx]
- real lug'at: `sent` → «yuborgan» (kutilgan «yuborgan») ✓ — yo'l: so'zma-so'z; sent: lug'at[chapter2_evx]

### –(Ravish) — Sodda ravish – qo‘shimchasiz, o‘zgarmas shaklda

- Spec: `very` → `juda`
- Tur: **L**, holat: **YO'Q**
- real lug'at: `very` → «[very?]» (kutilgan «juda») ✗ — yo'l: so'zma-so'z; very: topilmadi

### 3.1 — Sodda ravish (o‘zbekchada asos+affikslar birikmasi bilan beriladi)

- Spec: `here` → `shu yer + da = shu yerda`
- Tur: **L**, holat: **TO'LIQ MOS**
- real lug'at: `here` → «Shu yerda» (kutilgan «shu yerda») ✓ — yo'l: translate_phrase; here: lug'at[chapter2_evx]

### 3.2 — Yasama ravish – sifatga “-ly” affiksi qo‘shilib yasaladi

- Spec: `easi(ly) = easy + ly` → `oson + lik bilan = osonlik bilan` — *docx izohi:* Ingliz misoli boshqa qatorlardan teskari tartibda yozilgan: natija chapda ("easi(ly) = easy + ly"), boshqa qatorlarda "asos + affiks = natija".
- Tur: **M**, holat: **QISMAN MOS**
- Stub: easy→oson (Sifat)
- stub: `easily` → «Oson tarzda» (kutilgan «osonlik bilan») ✗ — yo'l: translate_phrase; easily: qoida -ily (o'zak easy, Ravish)
- real lug'at: `easily` → «Osonlikcha» (kutilgan «osonlik bilan») ✗ — yo'l: translate_phrase; easily: lug'at[json]

### 3.3 — Ravishning qiyosiy darajasi – bir-ikki bo‘g‘inli ravishga “-er” qo‘shiladi

- Spec: `fast + er = faster` → `tez + roq = tezroq`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: fast→tez (Ravish)
- stub: `faster` → «Tezroq» (kutilgan «tezroq») ✓ — yo'l: translate_phrase; faster: qoida -er (o'zak fast, Sifat)
- real lug'at: `faster` → «Tezroq» (kutilgan «tezroq») ✓ — yo'l: translate_phrase; faster: lug'at[chapter2_evx]

### 3.4 — Ravishning orttirma darajasi – bir-ikki bo‘g‘inli ravishga “-est” qo‘shiladi

- Spec: `fast + est = fastest` → `eng tez`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: fast→tez (Ravish)
- stub: `fastest` → «Eng tez» (kutilgan «eng tez») ✓ — yo'l: translate_phrase; fastest: qoida -est (o'zak fast, Sifat)
- real lug'at: `fastest` → «Eng tez» (kutilgan «eng tez») ✓ — yo'l: translate_phrase; fastest: lug'at[chapter2_evx]

### 3.5 — “-ly” bilan yasalgan ravishlarning darajasi “more”/“most” bilan yasaladi

- Spec: `more clearly` → `aniq + roq = aniqroq`
- Tur: **S**, holat: **YO'Q**
- Stub: clearly→aniq (Ravish)
- stub: `more clearly` → «Aniq» (kutilgan «aniqroq») ✗ — yo'l: translate_phrase; more: topilmadi; clearly: lug'at[stub]
- real lug'at: `more clearly` → «Aniq / Ravshan» (kutilgan «aniqroq») ✗ — yo'l: translate_phrase; more: topilmadi; clearly: lug'at[json]

### 3.6 — O‘rin-joy ravishi

- Spec: `inside` → `ichkari + da = ichkarida`
- Tur: **L**, holat: **TO'LIQ MOS**
- real lug'at: `inside` → «Ichkarida» (kutilgan «ichkarida») ✓ — yo'l: translate_phrase; inside: lug'at[chapter2_evx]

### 3.7 — Vaqt (payt) ravishi

- Spec: `today` → `bugun`
- Tur: **L**, holat: **TO'LIQ MOS**
- real lug'at: `today` → «Bugun» (kutilgan «bugun») ✓ — yo'l: translate_phrase; today: lug'at[chapter2_evx]

### 3.8 — O‘lchov va daraja ravishi

- Spec: `much` → `ko‘p`
- Tur: **L**, holat: **TO'LIQ MOS**
- real lug'at: `much` → «Ko'p» (kutilgan «ko‘p») ✓ — yo'l: translate_phrase; much: lug'at[json]

### 3.9 — Holat ravishi – sifatga “-ly” (ingl.) / “-gina” (o‘zb.) qo‘shilib yasaladi

- Spec: `quiet + ly = quietly` → `tinch + gina = tinchgina`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: quiet→tinch (Sifat)
- stub: `quietly` → «Tinch tarzda» (kutilgan «tinchgina») ✗ — yo'l: translate_phrase; quietly: qoida -ly (o'zak quiet, Ravish)
- real lug'at: `quietly` → «Tinchgina» (kutilgan «tinchgina») ✓ — yo'l: translate_phrase; quietly: lug'at[chapter2_evx]

### 3.11 — Sanoq son – asosiy (1–12) shakl, ikki tilda mos keladi

- Spec: `one` → `bir`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `one` → «Biri / Bitta» (kutilgan «bir») ✗ — yo'l: translate_phrase; one: lug'at[json]

### 3.12 — 13–19 oralig‘idagi sonlar “-teen” affiksi bilan yasaladi

- Spec: `fif + teen = fifteen` → `o‘n besh (affikssiz, qo‘shib yoziladi)` — *docx izohi:* O'zbek katagida "(affikssiz, qo‘shib yoziladi)" deyilgan, lekin misolning o'zi bo'shliq bilan yozilgan: "o‘n besh".
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: fif→besh (Son)
- Izoh: Stub o'zagi docx'dagidek "fif" ("fif + teen"). Kodda "five" -> "fif" tiklash funksiyasi yo'q (MORPH_RULES "teen": faqat w[:-4]) — shu sabab real lug'atda bu qoida "five" o'zagi bilan ishlamaydi.
- stub: `fifteen` → «O'n besh» (kutilgan «o‘n besh») ✓ — yo'l: translate_phrase; fifteen: qoida -teen (o'zak fif, Son)
- real lug'at: `fifteen` → «O'n besh» (kutilgan «o‘n besh») ✓ — yo'l: translate_phrase; fifteen: lug'at[chapter2_evx]

### 3.13 — O‘nliklar (20–90) “-ty” affiksi bilan yasaladi

- Spec: `eigh + ty = eighty` → `sakson (affikssiz)`
- Tur: **M**, holat: **QISMAN MOS**
- Stub: eigh→⟨eigh⟩ (Son)
- Izoh: Docx o'zak "eigh" ning o'zbekchasini bermagan, natija affikssiz ("sakson") — stub'da `⟨eigh⟩` BELGI ishlatildi (2.13 dagi kabi).
- stub: `eighty` → «⟨eigh⟩ o'nlik» (kutilgan «sakson») ✗ — yo'l: translate_phrase; eighty: qoida -ty (o'zak eigh, Son)
- real lug'at: `eighty` → «Sakson» (kutilgan «sakson») ✓ — yo'l: translate_phrase; eighty: lug'at[chapter2_evx]

### 3.14 — O‘nlikdan keyingi birlik sonlar ingliz tilida defis bilan yoziladi

- Spec: `eighty-five` → `sakson besh (defissiz)`
- Tur: **S**, holat: **TO'LIQ MOS**
- Stub: eighty→sakson (Son), five→besh (Son, manba 3.12)
- stub: `eighty-five` → «Sakson besh» (kutilgan «sakson besh») ✓ — yo'l: translate_phrase; eighty: lug'at[stub]; five: lug'at[stub]
- real lug'at: `eighty-five` → «Sakson» (kutilgan «sakson besh») ✗ — yo'l: translate_phrase; eighty: lug'at[chapter2_evx]; five: topilmadi

### 3.15 — Yuz, ming, million oldida “one” yoziladi

- Spec: `one hundred` → `bir yuz`
- Tur: **S**, holat: **TO'LIQ MOS**
- Stub: one→bir (Son), hundred→yuz (Son, manba 3.18)
- stub: `one hundred` → «Bir yuz» (kutilgan «bir yuz») ✓ — yo'l: translate_phrase; one: lug'at[stub]; hundred: lug'at[stub]
- real lug'at: `one hundred` → «Biri / Bitta» (kutilgan «bir yuz») ✗ — yo'l: translate_phrase; one: lug'at[json]; hundred: topilmadi

### 3.16 — Yuz/ming/million sonlariga sanoq son kelganda “-s” ko‘plik affiksi qo‘shilmaydi

- Spec: `four million` → `to‘rt million`
- Tur: **S**, holat: **TO'LIQ MOS**
- Stub: four→to‘rt (Son), million→million (Son)
- stub: `four million` → «To‘rt million» (kutilgan «to‘rt million») ✓ — yo'l: translate_phrase; four: lug'at[stub]; million: lug'at[stub]
- real lug'at: `four million` → «[four?] [million?]» (kutilgan «to‘rt million») ✗ — yo'l: so'zma-so'z; four: topilmadi; million: topilmadi

### 3.17 — Ko‘p xonali sonlarda “and” bog‘lovchisi ishlatiladi

- Spec: `three hundred and five` → `uch yuz besh (bog‘lovchisiz)`
- Tur: **S**, holat: **YO'Q**
- Stub: three→uch (Son), hundred→yuz (Son), five→besh (Son)
- stub: `three hundred and five` → «Uch yuz va besh» (kutilgan «uch yuz besh») ✗ — yo'l: translate_phrase; three: lug'at[stub]; hundred: lug'at[stub]; and: lug'at[seed(kod)]; five: lug'at[stub]
- real lug'at: `three hundred and five` → «Va» (kutilgan «uch yuz besh») ✗ — yo'l: translate_phrase; three: topilmadi; hundred: topilmadi; and: lug'at[docx,json]; five: topilmadi

### 3.18 — Tartib son – sanoq songa “-th” affiksi qo‘shiladi

- Spec: `hundred + th = hundredth` → `yuz + inchi = yuzinchi`
- Tur: **M**, holat: **TO'LIQ MOS**
- Stub: hundred→yuz (Son)
- stub: `hundredth` → «Yuzinchi» (kutilgan «yuzinchi») ✓ — yo'l: translate_phrase; hundredth: qoida -th (o'zak hundred, Son)
- real lug'at: `hundredth` → «Yuzinchi» (kutilgan «yuzinchi») ✓ — yo'l: translate_phrase; hundredth: lug'at[chapter2_evx]

### 3.19 — Qo‘shma tartib son – faqat oxirgi son tartib son shaklida bo‘ladi

- Spec: `hundred and twenty-first` → `bir yuz yigirma bir + inchi` — *docx izohi:* O'zbek misolida natija shakli berilmagan ("bir yuz yigirma bir + inchi" — "=" yo'q).
- Tur: **S**, holat: **YO'Q**
- Stub: hundred→yuz (Son), twenty→yigirma (Son)
- Izoh: Docx natija shaklini bermagan ("bir yuz yigirma bir + inchi") — qismlar qo'shildi. "first" uchun stub berilmadi: docx uni "bir + inchi" deb yozadi, ya'ni tartib son qoidasining o'zi tekshiriladi.
- stub: `hundred and twenty-first` → «Yuz va yigirma» (kutilgan «bir yuz yigirma birinchi») ✗ — yo'l: translate_phrase; hundred: lug'at[stub]; and: lug'at[seed(kod)]; twenty: lug'at[stub]; first: topilmadi
- real lug'at: `hundred and twenty-first` → «Va» (kutilgan «bir yuz yigirma birinchi») ✗ — yo'l: translate_phrase; hundred: topilmadi; and: lug'at[docx,json]; twenty: topilmadi; first: topilmadi

### 3.20 — Bob/qism raqami – ingliz tilida son otdan keyin, o‘zbek tilida otdan oldin (“-inchi” bilan) keladi

- Spec: `chapter five` → `besh + inchi bob = beshinchi bob`
- Tur: **S**, holat: **YO'Q**
- Stub: chapter→bob (Ot), five→besh (Son)
- stub: `chapter five` → «Bob besh» (kutilgan «beshinchi bob») ✗ — yo'l: translate_phrase; chapter: lug'at[stub]; five: lug'at[stub]
- real lug'at: `chapter five` → «Bob» (kutilgan «beshinchi bob») ✗ — yo'l: translate_phrase; chapter: lug'at[json]; five: topilmadi

### 3.22 — Kishilik olmoshi – bosh kelishik va obyekt kelishigiga bo‘linadi

- Spec: `I / he / we – me / him / us` → `men / u / biz – meni / uni / bizni`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `I` → «[i?]» (kutilgan «men») ✗ — yo'l: so'zma-so'z; i: topilmadi
- real lug'at: `he` → «U (erkak)» (kutilgan «u») ✓(variant) — yo'l: translate_phrase; he: lug'at[json]
- real lug'at: `we` → «Biz» (kutilgan «biz») ✓ — yo'l: translate_phrase; we: lug'at[json]
- real lug'at: `me` → «Meni / Menga» (kutilgan «meni») ✓(variant) — yo'l: translate_phrase; me: lug'at[json]
- real lug'at: `him` → «Uni (erkak)» (kutilgan «uni») ✓(variant) — yo'l: translate_phrase; him: lug'at[json]
- real lug'at: `us` → «Bizni / Bizga» (kutilgan «bizni») ✓(variant) — yo'l: translate_phrase; us: lug'at[json]

### 3.23 — Kishilik olmoshi – ikki tilda deyarli bir xil matematik model

- Spec: `I, he, she, it, we, you, they` → `men, u, u, u, biz, siz, ular`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `I` → «[i?]» (kutilgan «men») ✗ — yo'l: so'zma-so'z; i: topilmadi
- real lug'at: `he` → «U (erkak)» (kutilgan «u») ✓(variant) — yo'l: translate_phrase; he: lug'at[json]
- real lug'at: `she` → «U (ayol)» (kutilgan «u») ✓(variant) — yo'l: translate_phrase; she: lug'at[json]
- real lug'at: `it` → «U (jonsiz)» (kutilgan «u») ✓(variant) — yo'l: translate_phrase; it: lug'at[json]
- real lug'at: `we` → «Biz» (kutilgan «biz») ✓ — yo'l: translate_phrase; we: lug'at[json]
- real lug'at: `you` → «Siz» (kutilgan «siz») ✓ — yo'l: translate_phrase; you: lug'at[json]
- real lug'at: `they` → «Ular» (kutilgan «ular») ✓ — yo'l: translate_phrase; they: lug'at[json]

### 3.24 — Egalik olmosh-sifat – o‘zbek tilida “-ning” qaratqich affiksi bilan beriladi

- Spec: `my, his, our, your, their` → `men + ning, u + ning, biz + ning, siz + ning, ular + ning`
- Tur: **L**, holat: **QISMAN MOS**
- Izoh: Docx natija shaklini bermagan ("men + ning") — qismlar qo'shildi: "menning".
- real lug'at: `my` → «Mening» (kutilgan «menning») ✗ — yo'l: translate_phrase; my: lug'at[docx]
- real lug'at: `his` → «Uning» (kutilgan «uning») ✓ — yo'l: translate_phrase; his: lug'at[docx]
- real lug'at: `our` → «Bizning» (kutilgan «bizning») ✓ — yo'l: translate_phrase; our: lug'at[docx]
- real lug'at: `your` → «Sizning» (kutilgan «sizning») ✓ — yo'l: translate_phrase; your: lug'at[docx]
- real lug'at: `their` → «Ularning» (kutilgan «ularning») ✓ — yo'l: translate_phrase; their: lug'at[docx]

### 3.25 — Egalik olmosh-ot – o‘zbek tilida mos turi yo‘q, affikslar bilan ifodalanadi

- Spec: `mine, ours, yours, theirs` → `men + niki, biz + ning, siz + ning, ular + ning` — *docx izohi:* 4 ta inglizcha shaklga 4 ta o'zbekcha mos keladi, lekin faqat birinchisi "+ niki" ("men + niki"), qolgan uchtasi "+ ning" bilan berilgan — 3.24-qoidadagi (egalik olmosh-sifat) bilan bir xil. Nomuvofiqlik bo'lishi mumkin — Claude hal qilmaydi.
- Tur: **L**, holat: **QISMAN MOS**
- Izoh: Docx natija shaklini bermagan — qismlar qo'shildi. Docx katagidagi nomuvofiqlik uchun data/kkt_spec.json `izoh` ga qarang.
- real lug'at: `mine` → «Meniki» (kutilgan «menniki») ✗ — yo'l: translate_phrase; mine: lug'at[json]
- real lug'at: `ours` → «Bizniki» (kutilgan «bizning») ✗ — yo'l: translate_phrase; ours: lug'at[json]
- real lug'at: `yours` → «Sizniki» (kutilgan «sizning») ✗ — yo'l: translate_phrase; yours: lug'at[json]
- real lug'at: `theirs` → «Ularniki» (kutilgan «ularning») ✗ — yo'l: translate_phrase; theirs: lug'at[json]

### 3.26 — So‘roq olmoshlari

- Spec: `who, whom, whose, what, which` → `kim, kim + ni, kim + ning, nima, qaysi`
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `who` → «[who?]» (kutilgan «kim») ✗ — yo'l: so'zma-so'z; who: topilmadi
- real lug'at: `whom` → «Kimni / Kimga» (kutilgan «kimni») ✓(variant) — yo'l: translate_phrase; whom: lug'at[json]
- real lug'at: `whose` → «Kimning» (kutilgan «kimning») ✓ — yo'l: translate_phrase; whose: lug'at[json]
- real lug'at: `what` → «Nima» (kutilgan «nima») ✓ — yo'l: translate_phrase; what: lug'at[json]
- real lug'at: `which` → «Qaysi biri» (kutilgan «qaysi») ✗ — yo'l: translate_phrase; which: lug'at[json]

### 3.27 — Gumon/noaniq olmoshlar

- Spec: `some, someone, any, no, much, many, all, each…` → `ba’zi, kimdir, har qanday, yo‘q, ko‘p, ko‘pchilik, hamma, har bir…` — *docx izohi:* Ikkala misol ro'yxati "…" bilan tugaydi — to'liq ro'yxat emas.
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `some` → «Ba’zi» (kutilgan «ba’zi») ✓ — yo'l: translate_phrase; some: lug'at[json]
- real lug'at: `someone` → «Kimdir» (kutilgan «kimdir») ✓ — yo'l: translate_phrase; someone: lug'at[json]
- real lug'at: `any` → «Har qanday» (kutilgan «har qanday») ✓ — yo'l: translate_phrase; any: lug'at[json]
- real lug'at: `no` → «[no?]» (kutilgan «yo‘q») ✗ — yo'l: so'zma-so'z; no: topilmadi
- real lug'at: `much` → «Ko'p» (kutilgan «ko‘p») ✓ — yo'l: translate_phrase; much: lug'at[json]
- real lug'at: `many` → «Ko'p» (kutilgan «ko‘pchilik») ✗ — yo'l: translate_phrase; many: lug'at[json]
- real lug'at: `all` → «Hamma / Barcha» (kutilgan «hamma») ✓(variant) — yo'l: translate_phrase; all: lug'at[json]
- real lug'at: `each` → «Har biri» (kutilgan «har bir») ✗ — yo'l: translate_phrase; each: lug'at[json]

### 3.28 — O‘zlik olmoshlari – o‘zbek tilida egalik affiksi + “o‘z” so‘zi bilan beriladi

- Spec: `myself, yourself, himself, ourselves…` → `o‘zim, o‘zing, o‘zi, o‘zimiz…` — *docx izohi:* Ikkala misol ro'yxati "…" bilan tugaydi — to'liq ro'yxat emas.
- Tur: **L**, holat: **QISMAN MOS**
- real lug'at: `myself` → «O'zim» (kutilgan «o‘zim») ✓ — yo'l: translate_phrase; myself: lug'at[json]
- real lug'at: `yourself` → «O'zingiz» (kutilgan «o‘zing») ✗ — yo'l: translate_phrase; yourself: lug'at[json]
- real lug'at: `himself` → «O'zi (erkak)» (kutilgan «o‘zi») ✓(variant) — yo'l: translate_phrase; himself: lug'at[json]
- real lug'at: `ourselves` → «O'zimiz» (kutilgan «o‘zimiz») ✓ — yo'l: translate_phrase; ourselves: lug'at[json]

