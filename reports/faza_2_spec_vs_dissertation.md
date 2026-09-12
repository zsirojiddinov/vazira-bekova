# Spesifikatsiya ↔ dissertatsiya: barcha nomuvofiqliklar

**Generatsiya vaqti:** 2026-09-11T13:00:40+00:00
**Buyruq:** `python scripts/compare_spec_dissertation.py` (`make specdiss`)
**Manbalar:** SPEC = `data/kkt_spec.json` (sha256 `4954c528bc7eec3d…`); DISS = `data/desertatsiya.docx` II bobi (72 ta avtomatik ajratilgan EVX/EVIX juftligi); CH2 = `CH2_EVX_EXAMPLES` (52 ta, dissertatsiyaning kodga qo'lda ko'chirilgan nusxasi).

**Bu hisobot hech qaysi manbani "to'g'ri" deb e'lon qilmaydi** — farqni, xom matnni va kodning joriy holatini ko'rsatadi. Qaror — professor. Kod hozir SPEC ga moslashtirilmoqda (kanonik manba).

## 0. Qisqa xulosa

- Spec misollari (qoida × inglizcha shakl): **123**. Dissertatsiya II bobida avtomatik topilgani: **71** — shundan o'zbekchasi **mos: 56**, **FARQ: 15**. Topilmagani: 52 (5-bo'lim).
- Yozuv darajasida: 7 ta II bob yozuvining o'zbekchasi BOSHQA spec misolinikiga aynan teng (1.1-bo'lim).
- Dissertatsiya II bobida bor, spec'da yo'q misollar: 1 (4-bo'lim).
- FARQ qatorlarida CH2 (kod nusxasi) qaysi manbaga ergashadi: dissertatsiyaga — 9, spec'ga — 0, CH2 da yo'q — 5, ikkalasidan farq — 1.
- Spec'ning o'z katagidagi nomuvofiqliklar: 12 ta qoidada (3-bo'lim). Nazariy daraja: agentiv "-er" (6-bo'lim).

## 1. Spec ≠ dissertatsiya (15 ta)

| qoida | EN | SPEC (docx katagi) | DISS II bob (xom matn, docx idx) | CH2_EVX_EXAMPLES | kodning joriy holati |
|---|---|---|---|---|---|
| 2.2 | a network | `bitta tarmoq` | «tarmoq» ("tarmoq", #338) | «tarmoq» — dissertatsiya bilan bir xil | TO'LIQ MOS |
| 2.3 | an example | `bitta misol` | «misol» ("misol", #344) | «misol» — dissertatsiya bilan bir xil | TO'LIQ MOS |
| 2.7 | capabilities | `imkoniyat + lar = imkoniyatlar` | «imkonyatlar» ("imkonyat + lar", #369) | CH2 da yo'q | TO'LIQ MOS |
| 2.12 | schoolboys | `maktab bola + lari = maktab bolalari` | «maktabbolalar» ("maktab + bola + lar", #409) | «Bojxonalar» — ikkalasidan ham farq | QISMAN MOS |
| 2.15 | contents | `mundarija` | «mazmun» ("mazmun", #425) | «mazmun» — dissertatsiya bilan bir xil | QISMAN MOS |
| 2.21 | cleverer | `aqil + li + roq = aqillroq` ⚠ spec katagining "+" qismlari («aqilliroq») DISS bilan bir xil — spec katagi ichki nomuvofiq | «aqilliroq» ("soʻz:  aqilliroq", #689) | «aqilliroq» — dissertatsiya bilan bir xil | QISMAN MOS |
| 2.26 | biggest | `katta → eng katta` | «kattaroq» ("soʻz:  katta -> katta + roq", #721) | CH2 da yo'q | TO'LIQ MOS |
| 2.27 | busier | `band → bandroq` | «kattaroq» ("soʻz:  katta -> katta + roq", #729) | «kattaroq» — dissertatsiya bilan bir xil | TO'LIQ MOS |
| 2.28 | busiest | `band → eng band` | «eng katta» ("soʻz:  katta -> eng katta", #736) | «eng katta» — dissertatsiya bilan bir xil | TO'LIQ MOS |
| 2.47 | would | `edi` | «keladi» ("kel + a + di", #541) | «keladi» — dissertatsiya bilan bir xil | QISMAN MOS |
| 2.50 | could | `ol + ar + di = olardi` | «qila  olardi» ("qil + a  olardi", #562) | CH2 da yo'q | YO'Q |
| 2.53 | must | `kerak` | «shart» ("shart", #580) | «shart» — dissertatsiya bilan bir xil | QISMAN MOS |
| 2.58 | to follow | `kuzatmoq` | «ergashmoq» ("ergashmoq", #618) | «ergashmoq» — dissertatsiya bilan bir xil | YO'Q |
| 2.59 | listen to me | `meni tinglamoq` | «meni tinglang» ("men + i tingla + ng", #624) | CH2 da yo'q | TO'LIQ MOS |
| 2.62 | will return | `qaytmoq` | «qaytadi» ("qaytadi", #634) | CH2 da yo'q | TO'LIQ MOS |

### 1.1 Yozuv darajasida: dissertatsiya o'zbekchasi BOSHQA spec misolinikiga aynan teng (7 ta)

Inglizcha kalit bo'yicha solishtiruv buni ko'rmaydi (masalan bir inglizcha shakl ikki marta uchrasa). Har bir II bob yozuvi alohida: o'z inglizcha shakli uchun spec kutgan o'zbekchaga mos emas, lekin boshqa (inglizchasi farqli) spec misolining o'zbekchasi bilan bir xil.

| DISS (idx) | DISS EN → UZ | o'z spec misoli | xuddi shu o'zbekcha — boshqa spec misoli |
|---|---|---|---|
| #538 | `would` → «keladi» | 2.47 `would` → edi | 2.46 `will` → keladi |
| #583 | `ought` → «zarur» | spec'da yo'q | 2.54 `ought to` → zarur |
| #666 | `variables` → «rasmiy» | 2.1 `variables` → o‘zgaruvchilar | 2.19 `formal` → rasmiy |
| #716 | `biggest` → «kattaroq» | 2.26 `biggest` → eng katta | 2.23 `larger` → kattaroq; 2.25 `bigger` → kattaroq |
| #724 | `busier` → «kattaroq» | 2.27 `busier` → bandroq | 2.23 `larger` → kattaroq; 2.25 `bigger` → kattaroq |
| #731 | `busiest` → «eng katta» | 2.28 `busiest` → eng band | 2.24 `largest` → eng katta; 2.26 `biggest` → eng katta |
| #746 | `gayer` → «eng shoʻx» | 2.29 `gayer` → sho‘xroq | 2.30 `gayest` → eng sho‘x |

"kodning joriy holati" — `reports/faza_2_kkt_spec_conformance.md` dagi holat (SPEC ga nisbatan). Masalan QISMAN + "CH2 dissertatsiya bilan bir xil" — lug'at dissertatsiya qiymatini beradi, spec esa boshqasini talab qiladi; TO'LIQ — kod spec'ga moslashtirilgan (dissertatsiyadan farqli).

## 2. Spec = dissertatsiya, lekin CH2 (kod nusxasi) farq qiladi (2 ta) va CH2 transkripsiya xatolari

| qoida | EN | SPEC = DISS | CH2 |
|---|---|---|---|
| 2.31 | more comfortable | qulayroq | eng qulay |
| 2.34 | less interesting | kamroq qiziqarli | so'z kamroq qiziqarli |

Inglizcha kaliti dissertatsiya II bobidagi birorta misolga to'g'ri kelmagan CH2 yozuvlari (2 ta — asosan transkripsiya xatosi, `reports/ch2_leakage_check.md`): `capabilityies` → «imkonyatlar», `leafes` → «barglar».

## 3. Spec'ning o'zidagi nomuvofiqliklar (`data/kkt_spec.json` → `izoh`)

- **2.7** (Ot): "capability + ies = capabilities": "+" bilan ajratilgan komponentlar qo'shilganda "capabilityies" hosil bo'ladi, natija sifatida esa "capabilities" yozilgan.
- **2.11** (Ot): Tavsifda "chiziqcha (defis) bilan ajratib yoziladigan" deyilgan, lekin ingliz misolida ("custom + houses = customhouses") defis yo'q — natija qo'shib yozilgan.
- **2.13** (Ot): O'zbek misoli katagida izoh qavs ichida berilgan: "axborot (affikssiz)" — natija so'zi "axborot", "(affikssiz)" misolning bir qismi emas.
- **2.20** (Sifat): Ingliz misolida natija shakli berilmagan ("high-dimension + al" — "=" yo'q); o'zbek misolida ham ("ko‘p o‘lchov + li").
- **2.21** (Sifat): "aqil + li + roq = aqillroq": "+" bilan ajratilgan komponentlar qo'shilganda "aqilliroq" hosil bo'ladi, natija sifatida esa "aqillroq" yozilgan.
- **2.64** (Fe'l): "simplif(y) + ied = simplified": "+" bilan ajratilgan komponentlar qo'shilganda "simplif(y)ied" hosil bo'ladi, natija sifatida esa "simplified" yozilgan.
- **3.2** (Ravish): Ingliz misoli boshqa qatorlardan teskari tartibda yozilgan: natija chapda ("easi(ly) = easy + ly"), boshqa qatorlarda "asos + affiks = natija".
- **3.12** (Son): O'zbek katagida "(affikssiz, qo‘shib yoziladi)" deyilgan, lekin misolning o'zi bo'shliq bilan yozilgan: "o‘n besh".
- **3.19** (Son): O'zbek misolida natija shakli berilmagan ("bir yuz yigirma bir + inchi" — "=" yo'q).
- **3.25** (Olmosh): 4 ta inglizcha shaklga 4 ta o'zbekcha mos keladi, lekin faqat birinchisi "+ niki" ("men + niki"), qolgan uchtasi "+ ning" bilan berilgan — 3.24-qoidadagi (egalik olmosh-sifat) bilan bir xil. Nomuvofiqlik bo'lishi mumkin — Claude hal qilmaydi.
- **3.27** (Olmosh): Ikkala misol ro'yxati "…" bilan tugaydi — to'liq ro'yxat emas.
- **3.28** (Olmosh): Ikkala misol ro'yxati "…" bilan tugaydi — to'liq ro'yxat emas.

- Hujjat darajasida: Qoidalar soni: jami 87 ta (Ot 15, Sifat 17, Fe'l 28, Ravish 10, Son 10, Olmosh 7). Jadvallarning SARLAVHA qatori bilan birga olingan qator soni esa Ot 16, Sifat 18, Fe'l 29, Ravish 11, Son 11, Olmosh 8 = 93 — ya'ni "93 ta qoida" soni sarlavha qatorlarini ham qo'shib sanalgan ko'rinadi.
- Hujjat darajasida: 2 ta qatorda raqam o'rniga "–" turadi (Sifat va Ravish bo'limlarining birinchi qatori: "Oddiy sifat", "Sodda ravish"). Ular uchun `uid` = "–(Sifat)" / "–(Ravish)".
- Hujjat darajasida: Raqamlash uzluksiz emas: 2.14, 2.17, 2.18, 2.35, 2.40, 2.57, 2.60, 3.10, 3.21 raqamlari hujjatda yo'q.
- Hujjat darajasida: Fe'l bo'limida "2.55a" (need) va "2.55b" (gerund) — ikkita alohida qoida, "2.55b" jadvalda "2.56" dan KEYIN turadi.
- Hujjat darajasida: Vazn paragrafida Yordamchi so'z turkumlari uchun belgi "U, L" (ikkita) — bitta vazn (0.07).

## 4. Dissertatsiya II bobida bor, spec'da yo'q (1 ta)

- `ought` → «zarur» (#583, POS Fe'l)

## 5. Spec misollari — dissertatsiya II bobida avtomatik topilmagan (52 ta)

Avtomatik ajratish faqat "Ingliz tilida EVX ... / Oʻzbek tilida EVIX ..." paragraf naqshini taniydi — **topilmadi ≠ dissertatsiyada yo'q** (masalan olmosh ro'yxatlari jadval ichida bo'lishi mumkin).

–(Sifat): big; 2.19: formal; 2.24: largest; 2.30: gayest; 2.33: good, better; 2.36: read; 2.37: speaks; 2.39: am; 2.41: was, were; 2.42: been; 2.43: being; 2.65: send; –(Ravish): very; 3.17: three hundred and five; 3.22: he, we, me, him, us; 3.23: he, she, it, we, you, they; 3.24: my, his, our, your, their; 3.25: mine, ours, yours, theirs; 3.26: who, whom, whose, what, which; 3.27: some, someone, any, no, many, all, each; 3.28: myself, yourself, himself, ourselves.

## 6. Nazariy daraja — agentiv "-er"

- DISS I bob 1.3-jadval ("Yangi ot yasovchi suffikslar", 77 ta): "-er" BOR.
- SPEC: "-er" faqat 6 ta qiyosiy daraja qoidasida (2.21, 2.23, 2.25, 2.27, 2.29, 3.3); agentiv kalit so'zlar: 0 ta.
- Kod: agentiv qoida bor (`MORPH_RULES`), spec'da asosi yo'q — professor qarorini kutmoqda (`reports/faza_2_er_gap.md` 6-bo'lim).

