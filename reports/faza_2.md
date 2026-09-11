# Faza 2 — yakuniy hisobot: rasmiy KKT spesifikatsiyasiga moslik

**Sana:** 2026-09-11. **Branch:** `feat/faza2-kkt-spec-conformance` (main'ga hali birlashtirilmagan).

Batafsil, qayta ishlab chiqariladigan hisobotlar:

| Hisobot | Buyruq |
|---|---|
| `reports/faza_2_kkt_spec_conformance.md` — 87 qoida moslik jadvali | `make conformance` |
| `reports/faza_2_kkt_spec_leakage.md` — spec misollari va boshqa to'plamlar kesishmasi | `make leakage` |
| `reports/faza_2_lexicon_sources.md` — KKT_Terminologik, 100_soz qatorlari, ablatsiya | `make lexsources` |
| `reports/faza_2_er_gap.md` (6-bo'lim) — agentiv "-er" spec'da yo'q | `make ergap` |
| `reports/faza_2_confidence_audit.md` — "aniqlik" ko'rsatkichlari (avvalgi ish) | — |

## 1. Yakuniy holat — 87 qoida

| Holat | Faza 2 boshida | Yakunida |
|---|---|---|
| TO'LIQ MOS | 28 (23 mustaqil / 5 aylanma) | **36 (29 mustaqil / 7 aylanma)** |
| QISMAN MOS | 33 | **30** |
| YO'Q | 21 | **21** |
| ZID | 5 | **0** |

"Aylanma" — natija `CH2_EVX_EXAMPLES` (dissertatsiya II bob misollarining lug'atga
yozilgan nusxasi) dan o'qib qaytarilgan, mustaqil dalil emas (conformance hisoboti
0.1-jadval). 7 aylanmadan 2 tasi (2.51/2.52) tuzatish natijasida paydo bo'lgan —
tuzatishning o'z dalili lug'atdan mustaqil mexanizm testi.

34 → 36: oldingi xabarda aytilgan "34 mos" to+fe'l tuzatishidan (2.56, 2.59) OLDINGI
holat edi.

## 2. Tuzatishlar (har biri alohida commit, spec testi bilan)

| Commit | Qoida | O'zgarish | Holat | 100_soz | CH2_EVX_EXAMPLES |
|---|---|---|---|---|---|
| `e742dec` | 2.28 | `-iest` o'zak tiklash `w[:-4]+"y"` (busiest→busy) | QISMAN → TO'LIQ | o'zgarmadi | o'zgarmadi |
| `71908ed` | 2.37 | Fe'l 3-sh. birlik `-s` (speaks→gapiradi), ildiz Fe'l bo'lsa | ZID → TO'LIQ | o'zgarmadi | o'zgarmadi |
| `18c53d9` | 2.2, 2.3 | `a`/`an` → "bitta" (ortidan ot kelsa) | ZID → TO'LIQ | o'zgarmadi | "an example": "Misol" → "Bitta Misol" (CH2 "misol" bilan moslik −1, spec'ga mos) |
| `bd79825` | 2.51, 2.52 | SSM ildiz belgilariga U/L (spec: so'z turkumi) | QISMAN → TO'LIQ | o'zgarmadi | may, might → "mumkin", ought → "zarur" |
| `dbd2a46` | 2.56, 2.59 | `to` + fe'l infinitiv; (listen, to) → vositasiz to'ldiruvchi | ZID → TO'LIQ | o'zgarmadi | "a network" → "Tarmoq", "to ask" → "Ajratib ko'rsatmoq" (3-bo'lim, B) |

100_soz ning barcha 5 tuzatishdan keyingi bahosi: **56/100** (o'zgarmagan). O'lchov:
izolyatsiyalangan bazada har bir tuzatishdan oldin va keyin 100 ta gold + 52 ta CH2
chiqishi qator-ma-qator solishtirildi. Tuzatishlar gold natijani yaxshilash uchun
EMAS, spec'ga moslash uchun qilingan.

## 3. Qolgan qoidalar

**ZID: 0.**

**YO'Q: 21** (ustuvorlik bo'yicha tartiblangan to'liq jadval — conformance hisoboti 4-bo'lim):

| Guruh | Qoidalar | Izoh |
|---|---|---|
| Ibora qoidasi yo'q (S) | 2.31 more, 2.32 most, 2.34 less, 3.5 more+ravish | Analitik daraja uchun qoida yo'q — asos 262 sifat / 168 ravish |
| | 2.62 will + fe'l | `INFINITIVE_MARKERS` faqat ma'no tanlashda ishlatiladi |
| | 3.17, 3.19, 3.20 | Son birikmalari: "and" tushishi, qo'shma tartib son, "chapter five" tartibi |
| Noqoida (N) | 2.10 man→men | NLTK lemmatizer "men" ni tanimaydi |
| Lug'atda so'z yo'q (L) | 2.36 read, 2.38 be, 2.39 am, 2.41 was/were, 2.44 have, 2.45 do, 2.48 become, 2.50 could, 2.55a need, 2.58 follow, –(Sifat) big, –(Ravish) very | Bosh so'z UB_en_w da umuman yo'q (1500-lug'at bo'shlig'i) |

**QISMAN: 30** — qoida kodda bor, natija farq qiladi (masalan `-ed` → "-gan", spec "-di";
`-ly` → "tarzda", spec "-lik bilan"/"-gina"; olmosh ro'yxatlari qisman mos). To'liq
ro'yxat: conformance hisoboti 2-bo'lim.

## 4. Past ustuvorlikdagi topilmalar (qayd etildi, TUZATILMAGAN)

**A. Lug'at teglanishi + `uz_stem()` ning "-moq" kesishi** (`networks` holati).
- 1500-lug'at "Network → Tarmoq" ni VERBS kategoriyasiga yozgan; `uz_stem()` esa
  turkumdan qat'i nazar har qanday so'z oxiridagi "moq" ni kesadi: "Tarmoq" → "Tar".
  Natija (o'lchangan): `networks` → 71908ed dan oldin "Tarlar" (e742dec kodi bilan
  tekshirildi), keyin "Taradi" — ikkalasi ham noto'g'ri, sababi tuzatish emas,
  ma'lumot. "-moq" kesish OT uchun ham ishlaydi: stub lug'atda network→"tarmoq" (Ot)
  bilan "to the network" → "targa" (PP tarmog'i `uz_stem()` ni chaqiradi).
- Izolyatsiyalangan bazada Fe'l bo'lmagan, lekin tarjimasi "-moq" bilan tugaydigan
  yozuvlar: 9 ta 1500-lug'atdan + 1 CH2 — ikki xil: haqiqiy ot (`branch` → "Tarmoq /
  Shox") va noto'g'ri teglangan fe'llar (`confer`, `dump`, `filter` — Ot; `apply`,
  `comply`, `imply`, `rely` — Ravish, ehtimol "-ly" bilan tugagani uchun).
- Tuzatish yo'nalishi (keyinroq, alohida qaror): lug'at teglanishini tozalash va/yoki
  `uz_stem()` ni turkumga bog'lash.

**B. CH2 formal model yozuvidagi belgi xatosi SSM/MDB almashtirishiga olib keladi.**
`ask` → lug'atda "So'ramoq" (json), lekin BM_uz_w dagi CH2 modeli
`G(G_HA1) = $[i,1-h3]GHA1i` (pastki chiziqsiz "GHA1") — SSM ildiz belgisini "GHA"
deb o'qiydi, tanimaydi va MDB_uz_w'dan "Ajratib ko'rsatmoq" qo'yadi. Shu sabab 2.56
real lug'at bilan hali ham noto'g'ri (stub bilan — TO'LIQ).

**C. 2.54 "ought to"** — `to` modal "ought" dan keyin, ortidan fe'l kelmaydi → hali
"Ga zarur" (QISMAN).

## 5. Professor javobini kutayotgan masalalar (kodga TEGILMAGAN)

1. **Unlidan keyingi `-ydi`** (71908ed): spec 2.37 faqat undosh holatini beradi
   (gapir+a+di); "ishla" → "ishlaydi" o'zbek imlosining umumiy qoidasi sifatida
   qo'shilgan. Tasdiq yoki rad kutilmoqda.
2. **Agentiv `-er`** (teacher, worker): spec'da yo'q kategoriya, kodda qoida bor
   (`MORPH_RULES:396`), dissertatsiya I bob 1.3-jadvalida "-er" ot yasovchilar
   ro'yxatida — qaysi manba ustun (`reports/faza_2_er_gap.md` 6-bo'lim).

Docx'ning o'zidagi nomuvofiqliklar (masalan 2.21 "aqillroq", 3.25 "-niki/-ning")
`data/kkt_spec.json` → `izoh` maydonlarida, tuzatilmagan.

## 6. Doimiy ogohlantirish

Mavjud 100_soz gold to'plami baza manbasi ichida turibdi (1500-JSON "100 SOZ"
kategoriyasi) — ta'siri hozircha 0 ekani o'lchangan. Kelajakdagi har qanday gold
to'plam baza manbalaridan FIZIK ajratilgan bo'lishi SHART: `CLAUDE.md`,
`reports/faza_3_plan.md`.

## 7. Testlar

`pytest tests/` — **325 passed, 57 xfailed** (57 = 51 ta mos kelmaydigan spec qoidasi
`xfail(strict=True)` + 6 ta Faza 1 dan qolgan). `data/kkt_qoidalari.docx` (.gitignore)
bo'lmagan muhitda faqat docx sinxronlik testi o'tkazib yuboriladi.
