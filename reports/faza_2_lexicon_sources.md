# Faza 2 — Lug'at manbalari: KKT_Terminologik va 100_soz qatorlari qayerda ishlatiladi

**Generatsiya vaqti:** 2026-09-11T11:50:03+00:00
**Buyruq:** `python scripts/audit_lexicon_sources.py` (bazalar izolyatsiyalangan papkada noldan quriladi)

## 0. Qisqa javob

1. **`KKT_Terminologik` (75)** — `data/KKT_Terminologik_Lugat.json`: 20 ta ko'p ma'noli so'z (BOOK, MOUSE, ...), har biri soha bo'yicha bir nechta tarjima bilan — jami 75 ta (inglizcha, o'zbekcha, soha) yozuv. `check_leakage.py` dagi "75" — shu yozuvlar soni. **Kod bu manbani ISHLATMAYDI:** fayl nomi kodda uchramaydi, 1500-JSON ichidagi nusxasi esa boshqa tuzilishda (`word` + `entries`) bo'lgani uchun yuklovchi uni o'tkazib yuboradi, predmet sohalar bazasi (PSB) `terms` jadvali bo'sh (PSB_en_w.db=0, PSB_uz_w.db=0). Demak u hech qanday tarjima yoki aniqlik/foiz hisobiga kirmaydi.
2. **Lekin tekshiruv davomida boshqa "oldindan yozilgan javoblar" jadvali topildi:** 100_soz GOLD to'plamining 100 ta iborasi ("from our books" → "kitoblarimizdan" ...) 1500-JSON ichidagi "100 SOZ (MORFEMIK TAHLIL)" kategoriyasi orqali UB_en_w/UB_uz_w lug'atiga (`source='json'`, pos='Ot') va MDB_uz_w nomzodlariga YUKLANADI (100/100 UB_en_w da, 100/100 MDB_uz_w da).
3. **Ablatsiya natijasi:** bu 100 qator olib tashlangan baza nusxasida 100 ta gold kirishning `translate_phrase()` natijasi **0 tasida o'zgardi**; normalizatsiyalangan aniq moslik 56/100 → 56/100. Ya'ni **Faza 1 dagi 100_soz bahosi (56/100) bu qatorlar tufayli sun'iy oshmagan** — sababi: hamma 100 ta ibora ko'p so'zli, `translate_phrase()` esa lug'atni faqat alohida so'z (token) bo'yicha qidiradi. **Xavf yashirin qoladi:** kelajakda butun ibora bo'yicha qidiruv qo'shilsa yoki MDB tanlov tartibi o'zgarsa, gold javoblar to'g'ridan-to'g'ri qaytib qolishi mumkin — `tests/test_audit_lexicon_sources.py` shu holatni qo'riqlaydi.

## 1. 1500-JSON kategoriyalari — nima lug'atga yuklanadi

`_load_words_from_json()` (`kkt_v20_soz_tartibi.py`) → `data_loader.load_word_pairs()` JSON'dagi BARCHA kategoriyalarni aylanadi va `english` + `uzbek` maydoni bor har bir yozuvni UB_en_w/UB_uz_w ga yozadi (`POS_MAP` ga mos kelmagan kategoriya → pos='Ot').

| Kategoriya | Yozuvlar | `english`+`uzbek` bor | UB_en_w da (source='json') | Yozuv kalitlari |
|---|---|---|---|---|
| NOUNS (OTLAR) | 630 | 630 | 625 | english, no, uzbek |
| VERBS (FE'LLAR) | 317 | 317 | 317 | english, no, uzbek |
| ADJECTIVES (SIFATLAR) | 262 | 262 | 262 | english, no, uzbek |
| ADVERBS (RAVISHLAR) | 168 | 168 | 168 | english, no, uzbek |
| PRONOUNS (OLMOSHLAR) | 21 | 21 | 21 | english, no, uzbek |
| CONJUNCTIONS & PREPOSITIONS (BOG'LOVCHI / KO'MAKCHI) | 20 | 20 | 20 | english, no, uzbek |
| 100 SOZ (MORFEMIK TAHLIL) | 100 | 100 | 100 | english, morphemes, no, uzbek |
| KKT TERMINOLOGIK LUGAT (KO'P MA'NOLI TERMINLAR) | 20 | 0 | 0 | entries, word |

## 2. `KKT_Terminologik_Lugat.json` — batafsil

- Tuzilishi: 20 ta so'z × soha bo'yicha ma'nolar = 75 ta yozuv; sohalar: AI, Aloqa, Biologiya, Biznes, Botanika, Buxgalteriya, Dasturlash, Database, Dengiz, Elektronika, Falsafa, Fizika, Grammatika, Harbiy, Huquq, Ijtimoiy, Informatika, Kimyo, Kriptografiya, Lingvistika, Marketing, Matematika, Mebel, Mehmonxona, Moda, Muhandislik, Musiqa, Psixologiya, Qamoqxona, Qishloq xo‘jaligi, Savdo, Siyosat, Sport, Suv fizikasi, TV, Tarmoq, Ta’lim, Telekom, Tibbiyot, Transport, Vaqt, Zoologiya.
- Kodda fayl nomiga havola: **yo'q**.
- PSB `terms` jadvaliga yozuvchi kod (`INSERT ... INTO terms`): **yo'q** — jadval hech qachon to'ldirilmaydi. Qurilgan bazada qatorlar: {'PSB_en_w.db': 0, 'PSB_uz_w.db': 0}.
- `psb_select_meaning()` chaqiruvlari (3 ta: kkt_v20_soz_tartibi.py:3019; kkt_v20_soz_tartibi.py:3038; kkt_v20_soz_tartibi.py:3103). `domain` argumenti uzatilgan chaqiruv: 0 ta — ya'ni funksiya har doim birinchi ma'noni qaytaradi.
- Terminologik juftlarning (75) AYNAN o'zi (inglizcha + o'zbekcha) UB_en_w da boshqa manbadan tasodifan bor: 3 ta — book→kitob [docx], model→model [docx], table→stol [docx]. Bu terminologik fayl orqali emas (u yuklanmaydi), 1500-lug'at/SEED/CH2 orqali kelgan.
- Hisobotlarda: README.md "kod tomonidan hozircha ishlatilmaydi" deb qayd etgan — shu skript bu da'voni tasdiqlaydi. Dissertatsiya IV bobida PSB "semantik noaniqlikni bartaraf etishning asosiy mexanizmi" deb tasvirlanadi (`reports/ch2_leakage_check.md` 3.3) — kodda esa bu mexanizm bo'sh jadval bilan ishlaydi.

## 3. 100_soz gold qatorlari — ablatsiya

- Olib tashlangan qatorlar (baza NUSXASIDAN): {'DB_UB_EN': 100, 'DB_UB_UZ': 100, 'DB_MDB_UZ': 100}.
- Normalizatsiyalangan aniq moslik: oddiy baza **56/100**, qatorlarsiz **56/100**; farqli chiqishlar: **0**.
- Tavsiya qilinmaydi, faqat qayd: bu qatorlar lug'atda turishi — gold to'plam va tarjima lug'ati bitta faylda aralashganining natijasi (1500-JSON ichida "100 SOZ" kategoriyasi). Ajratish — alohida qaror.

