# Faza 2 — `kkt_spec.json` misollari va boshqa to'plamlar kesishmasi (ogohlantirish)

**Generatsiya vaqti:** 2026-09-11T11:37:39+00:00
**Buyruq:** `python scripts/check_leakage.py`

**Bu leakage EMAS.** `kkt_spec.json` misollari faqat formal qoidani tekshiradi (`tests/test_kkt_spec_conformance.py`) va gold to'plamlarga QO'SHILMAGAN. Bu ro'yxat — bir xil so'z ikkala joyda uchrasa, bilib turish uchun: masalan shu qoida o'zgartirilsa, quyidagi to'plamlardagi natija ham o'zgarishi mumkin.

Manbalar (normallashtirilgan yozuvlar soni): `1500-lug'at` (1418), `100_soz` (100), `KKT_Terminologik` (75), `CH2_EVX_EXAMPLES` (52).

- `1500-lug'at` — 1500-JSON ning 6 asosiy kategoriyasi; `100_soz` — gold iboralar; `CH2_EVX_EXAMPLES` — kod ichidagi II bob misollari (lug'atga `source='chapter2_evx'` bilan yoziladi).
- `KKT_Terminologik` — `data/KKT_Terminologik_Lugat.json`: 20 ta ko'p ma'noli so'z × soha bo'yicha ma'nolar (soni — (inglizcha, o'zbekcha, soha) yozuvlar). **Kod bu faylni ishlatmaydi** (yuklanmaydi, PSB bo'sh). 100_soz gold iboralari esa lug'atga YUKLANADI, lekin natijaga ta'sir qilmaydi — ikkalasi ham o'lchangan: `reports/faza_2_lexicon_sources.md`.

## 1. Shakl darajasida (to'liq shakl yoki asos aynan teng)

Manba bo'yicha: `1500-lug'at`: **45**, `100_soz`: **0**, `KKT_Terminologik`: **0**, `CH2_EVX_EXAMPLES`: **46**.

| spec qoidasi | POS | tur | shakl | 1500-lug'at | 100_soz | KKT_Terminologik | CH2_EVX_EXAMPLES |
|---|---|---|---|---|---|---|---|
| 2.1 | Ot | asos | variable | ⚠ |  |  |  |
| 2.2 | Ot | misol | a network |  |  |  | ⚠ |
| 2.3 | Ot | misol | an example |  |  |  | ⚠ |
| 2.4 | Ot | misol | the progress |  |  |  | ⚠ |
| 2.5 | Ot | misol | the germanys |  |  |  | ⚠ |
| 2.6 | Ot | asos | process | ⚠ |  |  |  |
| 2.6 | Ot | misol | processes |  |  |  | ⚠ |
| 2.8 | Ot | asos | delay | ⚠ |  |  |  |
| 2.8 | Ot | misol | delays |  |  |  | ⚠ |
| 2.10 | Ot | misol | men |  |  |  | ⚠ |
| 2.11 | Ot | asos | custom | ⚠ |  |  |  |
| 2.11 | Ot | misol | customhouses |  |  |  | ⚠ |
| 2.12 | Ot | misol | schoolboys |  |  |  | ⚠ |
| 2.13 | Ot | misol | information |  |  |  | ⚠ |
| 2.15 | Ot | misol | contents |  |  |  | ⚠ |
| 2.16 | Ot | misol | student's |  |  |  | ⚠ |
| 2.21 | Sifat | misol | cleverer |  |  |  | ⚠ |
| 2.22 | Sifat | misol | cleverest |  |  |  | ⚠ |
| 2.27 | Sifat | misol | busier |  |  |  | ⚠ |
| 2.28 | Sifat | misol | busiest |  |  |  | ⚠ |
| 2.29 | Sifat | misol | gayer |  |  |  | ⚠ |
| 2.31 | Sifat | misol | more comfortable |  |  |  | ⚠ |
| 2.33 | Sifat | misol | best | ⚠ |  |  |  |
| 2.34 | Sifat | misol | less interesting |  |  |  | ⚠ |
| 2.45 | Fe'l | misol | to do |  |  |  | ⚠ |
| 2.46 | Fe'l | misol | will |  |  |  | ⚠ |
| 2.47 | Fe'l | misol | would |  |  |  | ⚠ |
| 2.49 | Fe'l | misol | can |  |  |  | ⚠ |
| 2.51 | Fe'l | misol | may |  |  |  | ⚠ |
| 2.52 | Fe'l | misol | might |  |  |  | ⚠ |
| 2.53 | Fe'l | misol | must |  |  |  | ⚠ |
| 2.54 | Fe'l | misol | ought to |  |  |  | ⚠ |
| 2.56 | Fe'l | misol | to ask |  |  |  | ⚠ |
| 2.55b | Fe'l | misol | reading |  |  |  | ⚠ |
| 2.58 | Fe'l | misol | to follow |  |  |  | ⚠ |
| 2.61 | Fe'l | misol | understand | ⚠ |  |  |  |
| 2.63 | Fe'l | asos | work | ⚠ |  |  |  |
| 2.65 | Fe'l | misol | sent |  |  |  | ⚠ |
| 3.1 | Ravish | misol | here |  |  |  | ⚠ |
| 3.2 | Ravish | misol | easily | ⚠ |  |  |  |
| 3.2 | Ravish | asos | easy | ⚠ |  |  |  |
| 3.3 | Ravish | misol | faster |  |  |  | ⚠ |
| 3.4 | Ravish | misol | fastest |  |  |  | ⚠ |
| 3.6 | Ravish | misol | inside |  |  |  | ⚠ |
| 3.7 | Ravish | misol | today |  |  |  | ⚠ |
| 3.8 | Ravish | misol | much | ⚠ |  |  | ⚠ |
| 3.9 | Ravish | misol | quietly |  |  |  | ⚠ |
| 3.11 | Son | misol | one | ⚠ |  |  | ⚠ |
| 3.12 | Son | misol | fifteen |  |  |  | ⚠ |
| 3.13 | Son | misol | eighty |  |  |  | ⚠ |
| 3.15 | Son | misol | one hundred |  |  |  | ⚠ |
| 3.16 | Son | misol | four million |  |  |  | ⚠ |
| 3.18 | Son | misol | hundredth |  |  |  | ⚠ |
| 3.20 | Son | misol | chapter five |  |  |  | ⚠ |
| 3.22 | Olmosh | misol | he | ⚠ |  |  |  |
| 3.22 | Olmosh | misol | we | ⚠ |  |  |  |
| 3.22 | Olmosh | misol | me | ⚠ |  |  |  |
| 3.22 | Olmosh | misol | him | ⚠ |  |  |  |
| 3.22 | Olmosh | misol | us | ⚠ |  |  |  |
| 3.23 | Olmosh | misol | he | ⚠ |  |  |  |
| 3.23 | Olmosh | misol | she | ⚠ |  |  |  |
| 3.23 | Olmosh | misol | it | ⚠ |  |  |  |
| 3.23 | Olmosh | misol | we | ⚠ |  |  |  |
| 3.23 | Olmosh | misol | you | ⚠ |  |  |  |
| 3.23 | Olmosh | misol | they | ⚠ |  |  |  |
| 3.24 | Olmosh | misol | my | ⚠ |  |  |  |
| 3.24 | Olmosh | misol | his | ⚠ |  |  |  |
| 3.24 | Olmosh | misol | our | ⚠ |  |  |  |
| 3.24 | Olmosh | misol | your | ⚠ |  |  |  |
| 3.25 | Olmosh | misol | mine | ⚠ |  |  |  |
| 3.25 | Olmosh | misol | ours | ⚠ |  |  |  |
| 3.25 | Olmosh | misol | yours | ⚠ |  |  |  |
| 3.25 | Olmosh | misol | theirs | ⚠ |  |  |  |
| 3.26 | Olmosh | misol | whom | ⚠ |  |  |  |
| 3.26 | Olmosh | misol | whose | ⚠ |  |  |  |
| 3.26 | Olmosh | misol | what | ⚠ |  |  |  |
| 3.26 | Olmosh | misol | which | ⚠ |  |  |  |
| 3.27 | Olmosh | misol | some | ⚠ |  |  |  |
| 3.27 | Olmosh | misol | someone | ⚠ |  |  |  |
| 3.27 | Olmosh | misol | any | ⚠ |  |  |  |
| 3.27 | Olmosh | misol | much | ⚠ |  |  | ⚠ |
| 3.27 | Olmosh | misol | many | ⚠ |  |  |  |
| 3.27 | Olmosh | misol | all | ⚠ |  |  |  |
| 3.27 | Olmosh | misol | each | ⚠ |  |  |  |
| 3.28 | Olmosh | misol | myself | ⚠ |  |  |  |
| 3.28 | Olmosh | misol | yourself | ⚠ |  |  |  |
| 3.28 | Olmosh | misol | himself | ⚠ |  |  |  |
| 3.28 | Olmosh | misol | ourselves | ⚠ |  |  |  |

## 2. Token darajasida (ko'p so'zli spec shaklidagi mazmunli so'z)

E'tiborsiz qoldirilgan funksional so'zlar: a, an, and, of, the, to.

| spec qoidasi | shakl | token → manbalar |
|---|---|---|
| 2.2 | a network | network → 1500-lug'at, CH2_EVX_EXAMPLES, KKT_Terminologik |
| 2.3 | an example | example → 1500-lug'at, CH2_EVX_EXAMPLES |
| 2.4 | the progress | progress → CH2_EVX_EXAMPLES |
| 2.5 | the germanys | germanys → CH2_EVX_EXAMPLES |
| 2.31 | more comfortable | more → CH2_EVX_EXAMPLES; comfortable → CH2_EVX_EXAMPLES |
| 2.32 | most comfortable | most → 1500-lug'at; comfortable → CH2_EVX_EXAMPLES |
| 2.34 | less interesting | less → CH2_EVX_EXAMPLES; interesting → CH2_EVX_EXAMPLES |
| 2.45 | to do | do → CH2_EVX_EXAMPLES |
| 2.54 | ought to | ought → CH2_EVX_EXAMPLES |
| 2.56 | to ask | ask → 1500-lug'at, CH2_EVX_EXAMPLES |
| 2.58 | to follow | follow → CH2_EVX_EXAMPLES |
| 2.59 | listen to me | me → 1500-lug'at |
| 2.62 | will return | will → CH2_EVX_EXAMPLES |
| 3.5 | more clearly | more → CH2_EVX_EXAMPLES; clearly → 1500-lug'at |
| 3.15 | one hundred | one → 1500-lug'at, CH2_EVX_EXAMPLES; hundred → CH2_EVX_EXAMPLES |
| 3.16 | four million | four → CH2_EVX_EXAMPLES; million → CH2_EVX_EXAMPLES |
| 3.17 | three hundred and five | hundred → CH2_EVX_EXAMPLES; five → CH2_EVX_EXAMPLES |
| 3.19 | hundred and twenty-first | hundred → CH2_EVX_EXAMPLES; twenty → CH2_EVX_EXAMPLES; first → CH2_EVX_EXAMPLES |
| 3.20 | chapter five | chapter → 1500-lug'at, CH2_EVX_EXAMPLES; five → CH2_EVX_EXAMPLES |

