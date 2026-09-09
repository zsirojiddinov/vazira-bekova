# Faza 2 — "-er" bo'shlig'i: sifat+er (qiyosiy) vs fe'l+er (agentiv)

**Generatsiya vaqti:** 2026-09-08T15:39:55+00:00Z
**Buyruq:** `python scripts/audit_er_gap.py`

**Kontekst:** `"worker"->"Ishlaroq"` ma'lum xatosi (`make_uzbek()` "-er"ni HAR DOIM qiyosiy daraja deb hisoblaydi, agentiv ma'noni ajratmaydi — qarang `reports/faza_1.md`#2-band, `tests/test_smart_parse.py::test_smart_parse_agentive_er_uses_wrong_fallback_suffix_data_bug`). **Bu hisobot xatoni TUZATMAYDI** — foydalanuvchi so'rovi bo'yicha faqat ikkita guruhning hajmini hisoblab, professor bilan muhokama uchun xom dalil taqdim etadi. Qaysi guruh "dissertatsiyada bor/yo'q" degan yakuniy xulosani Claude CHIQARMAYDI.

## 1. Kod darajasidagi holat (kontekst)

`kkt_v20_soz_tartibi.py:MORPH_RULES` da "-er" ATAYLAB IKKI MARTA uchraydi (izoh, 391-398-qatorlar): (1) `Ot←Fe'l` ("C←G(-er): ish bajaruvchi, work→worker", FAQAT ildiz lug'atda Fe'l bo'lsa ishlaydi) — bu birinchi turadi; (2) `Sifat←Sifat` ("P1←P(-er): qiyosiy", cheklovsiz). POS ANIQLASH bosqichida (`smart_parse`) bu ikkalasi TO'G'RI farqlanadi (`tests/test_affix_tables.py::test_morph_rules_er_has_pos_guarded_and_unguarded_variant`). LEKIN zaxira tarjima bosqichida (`make_uzbek(root_uz, sfx)`) faqat AFFIKS MATNI ("er") uzatiladi, `derived_pos` YO'Q — shu sabab `"er": stem+"roq"` qoidasi ikkalasini ham bir xil (qiyosiy) deb hisoblaydi.

## 2. 1500 so'zlik lug'atdagi natija

Manba: `data/1500_EN_UZ_6_POS_sorted.20.json`, 6 ta asosiy kategoriya (README.md "1417+ juft, 6 POS" ta'rifiga mos, jami **1418** juftlik).

- Bitta-so'zli "-er" bilan tugaydigan headword: **48**
  - SIFAT+ER (qiyosiy, o'zak ADJECTIVES/ADVERBS da topildi): **0**
  - FE'L+ER (agentiv, o'zak VERBS da topildi): **3**
  - ANIQLANMAGAN (avtomatik hal qilinmadi — pastga qarang): **45**

**"ANIQLANMAGAN" haqida:** bu guruhga ikki xil holat kiradi — (a) "-er" so'z ILDIZINING bir qismi, umuman suffiks EMAS (masalan `water`, `other`, `however` kabi — root-tiklash funksiyalari "wat"/"oth"/"howev" kabi mavjud bo'lmagan "o'zak"lar hosil qiladi, lug'atda topilmaydi — bu TO'G'RI natija), (b) haqiqatan ham fe'l+er/sifat+er, lekin ildiz so'z 1500-so'zlik lug'atning o'zida MUSTAQIL yozuv sifatida yo'q (masalan `User`ning ildizi "use", `Leader`ning ildizi "lead" lug'atda alohida yo'q) YOKI root-tiklash 4 ta funksiya (`y→i` almashtirishni QAMRAB OLMAYDI, masalan `Supplier`) — bu ikkinchi holat KODNING O'ZIDA ham bor bo'lgan CHEKLOV (xuddi shu 4 ta funksiya `MORPH_RULES`da ham ishlatiladi), Claude buni "aniqlab bermaydi".

### To'liq jadval (48 ta so'z, barchasi — hech biri chiqarib tashlanmagan)

| Kategoriya | So'z | O'zbekcha | Sinovdan o'tgan o'zaklar | Guruh |
|---|---|---|---|---|
| NOUNS (OTLAR) | After | Keyin | aft, afte, af, afe | ANIQLANMAGAN |
| NOUNS (OTLAR) | Another | Boshqa | anoth, anothe, anot, anote | ANIQLANMAGAN |
| NOUNS (OTLAR) | Buffer | Bufer / Oraqliq xotira | buff, buffe, buf, bufe | ANIQLANMAGAN |
| NOUNS (OTLAR) | Center | Markaz | cent, cente, cen, cene | ANIQLANMAGAN |
| NOUNS (OTLAR) | Chapter | Bob | chapt, chapte, chap, chape | ANIQLANMAGAN |
| NOUNS (OTLAR) | Chapter | Bob / Bo'lim | chapt, chapte, chap, chape | ANIQLANMAGAN |
| NOUNS (OTLAR) | Character | Belgisi / Simvol | charact, characte, charac, charace | ANIQLANMAGAN |
| NOUNS (OTLAR) | Cluster | Klaster / To'da | clust, cluste, clus, cluse | ANIQLANMAGAN |
| NOUNS (OTLAR) | Confer | Maslahatlashmoq / Berish | conf, confe, con, cone | ANIQLANMAGAN |
| NOUNS (OTLAR) | Consumer | Iste'molchi | consum, consume, consu, consue | FE'L+ER (agentiv) |
| NOUNS (OTLAR) | Counter | Hisoblagich | count, counte, coun, coune | FE'L+ER (agentiv) |
| NOUNS (OTLAR) | Crossover | Krossover (genetik algoritmlarda chatishish) | crossov, crossove, crosso, crossoe | ANIQLANMAGAN |
| NOUNS (OTLAR) | Cylinder | Silindr | cylind, cylinde, cylin, cyline | ANIQLANMAGAN |
| NOUNS (OTLAR) | Diameter | Diametr | diamet, diamete, diame, diamee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Eager | Ishtiyoqmand | eag, eage, ea, eae | ANIQLANMAGAN |
| NOUNS (OTLAR) | Either | Shuningdek (inkor gapda) | eith, eithe, eit, eite | ANIQLANMAGAN |
| NOUNS (OTLAR) | Encoder | Kodlovchi / Enkoder | encod, encode, enco, encoe | FE'L+ER (agentiv) |
| NOUNS (OTLAR) | Ever | Hech qachon / Qachondir | ev, eve, e, ee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Filter | Saralamoq / Filtrlash | filt, filte, fil, file | ANIQLANMAGAN |
| NOUNS (OTLAR) | Layer | Qatlam | lay, laye, la, lae | ANIQLANMAGAN |
| NOUNS (OTLAR) | Leader | Rahbar / Yetakchi | lead, leade, lea, leae | ANIQLANMAGAN |
| NOUNS (OTLAR) | Neither | Na u, na bu | neith, neithe, neit, neite | ANIQLANMAGAN |
| NOUNS (OTLAR) | Other | Boshqa | oth, othe, ot, ote | ANIQLANMAGAN |
| NOUNS (OTLAR) | Partner | Sherik | partn, partne, part, parte | ANIQLANMAGAN |
| NOUNS (OTLAR) | Supplier | Ta'minotchi | suppli, supplie, suppl, supple | ANIQLANMAGAN |
| NOUNS (OTLAR) | Together | Birgalikda | togeth, togethe, toget, togete | ANIQLANMAGAN |
| NOUNS (OTLAR) | Transfer | O'tkazish / Ko'chirish | transf, transfe, trans, transe | ANIQLANMAGAN |
| NOUNS (OTLAR) | User | Foydalanuvchi | us, use, u, ue | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whatever | Nima bo'lganda ham | whatev, whateve, whate, whatee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whatever | Nima bo'lsa ham | whatev, whateve, whate, whatee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whenever | Qachonki | whenev, wheneve, whene, whenee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Wherever | Qayerdaki / Qayerga bo‘lmasin | wherev, whereve, where, wheree | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whether | ...-mi yoki yo'q | wheth, whethe, whet, whete | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whichever | Qaysi biri bo'lsa ham | whichev, whicheve, whiche, whichee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whoever | Kim bo'lsa ham | whoev, whoeve, whoe, whoee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whomsoever | Kim bo'lishidan qat'i nazar | whomsoev, whomsoeve, whomsoe, whomsoee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whosever | Kimniki bo'lsa ham | whosev, whoseve, whose, whosee | ANIQLANMAGAN |
| NOUNS (OTLAR) | Whosoever | Kim bo'lishidan qat'i nazar | whosoev, whosoeve, whosoe, whosoee | ANIQLANMAGAN |
| VERBS (FE'LLAR) | Alter | O'zgartirmoq | alt, alte, al, ale | ANIQLANMAGAN |
| VERBS (FE'LLAR) | Cover | Qoplamoq | cov, cove, co, coe | ANIQLANMAGAN |
| VERBS (FE'LLAR) | Decipher | Shifrni ochmoq | deciph, deciphe, decip, decipe | ANIQLANMAGAN |
| VERBS (FE'LLAR) | Deliver | Yetkazib bermoq | deliv, delive, deli, delie | ANIQLANMAGAN |
| VERBS (FE'LLAR) | Differ | Farq qilmoq | diff, diffe, dif, dife | ANIQLANMAGAN |
| VERBS (FE'LLAR) | Discover | Kashf qilmoq | discov, discove, disco, discoe | ANIQLANMAGAN |
| VERBS (FE'LLAR) | Wonder | Hayron qolmoq | wond, wonde, won, wone | ANIQLANMAGAN |
| PRONOUNS (OLMOSHLAR) | Her | Uni / Uniki (ayol) | h, he, , e | ANIQLANMAGAN |
| CONJUNCTIONS & PREPOSITIONS (BOG'LOVCHI / KO'MAKCHI) | However | Biroq / Lekin | howev, howeve, howe, howee | ANIQLANMAGAN |
| CONJUNCTIONS & PREPOSITIONS (BOG'LOVCHI / KO'MAKCHI) | Moreover | Bundan tashqari | moreov, moreove, moreo, moreoe | ANIQLANMAGAN |

**Qo'shimcha ("1500 so'zlik lug'at"ning bir qismi EMAS, lekin xuddi shu JSON faylda mavjud):** "100 SOZ" va "KKT TERMINOLOGIK LUGAT" kategoriyalarida (boshqa manba fayllardan olingan) oddiy `english` maydoni bo'yicha qidiruvda **2** ta "-er"-so'z topildi (DRIVER (KKT TERMINOLOGIK LUGAT (KO'P MA'NOLI TERMINLAR)), POWER (KKT TERMINOLOGIK LUGAT (KO'P MA'NOLI TERMINLAR))).

## 3. "Test to'plami"dagi natija

### 3a. `CH2_EVX_EXAMPLES` (dissertatsiya II bobidan ko'chirilgan 52 misol)

Bitta-so'zli "-er" bilan tugaydigan yozuvlar: **5**

| So'z | O'zbekcha | CH2 POS | Guruh |
|---|---|---|---|
| cleverer | aqilliroq | Sifat | SIFAT+ER (qiyosiy) |
| busier | kattaroq | Sifat | SIFAT+ER (qiyosiy) |
| gayer | sho'xroq | Sifat | SIFAT+ER (qiyosiy) |
| gayer | eng sho'x | Sifat | SIFAT+ER (qiyosiy) |
| faster | tezroq | Ravish | SIFAT+ER (qiyosiy) |

- SIFAT+ER (qiyosiy): **5** (busier, cleverer, faster, gayer)
- FE'L+ER (agentiv): **0**

**Diqqat:** `CH2_EVX_EXAMPLES`da FE'L+ER (agentiv) misoli **YO'Q** — barcha bitta-so'zli "-er" yozuvlari qiyosiy daraja. (`reports/ch2_leakage_check.md` — endi asl dissertatsiya fayli bilan tasdiqlangan — bu ro'yxat II bobning HAMMASI emasligini ko'rsatadi, lekin II bobning O'ZIDA ham hech qanday fe'l+er/agentiv EVX misoli TOPILMADI, qarang 4-bo'lim.)

### 3b. `tests/*.py` (pytest to'plami) — haqiqiy so'z-darajasidagi kirishlar

Metodika bo'limida tavsiflangan qo'lda tekshiruv natijasi (barcha `tests/*.py` fayllaridagi "-er"ga o'xshash tokenlar ko'rib chiqildi, faqat HAQIQIY funksiya-chaqiruv argumentlari qoldirildi):

| So'z | Fayl:qator | Ishlatilishi | Guruh |
|---|---|---|---|
| teacher | tests/test_smart_parse.py:15 | m.smart_parse('teacher') — to'g'ridan lug'at solishtiruvi | FE'L+ER (agentiv) |
| worker | tests/test_smart_parse.py:61 | m.smart_parse('worker') — ma'lum xato (Ishlaroq) testi | FE'L+ER (agentiv) |

- SIFAT+ER (qiyosiy) test kirishi: **0** (faqat bitta ESLATMA bor — `tests/test_affix_tables.py:123` docstring ichida "masalan fast->faster" — bu HAQIQIY funksiya chaqiruvi EMAS, hisobga qo'shilmadi)
- FE'L+ER (agentiv) test kirishi: **2** (`teacher`, `worker`)

## 4. Dissertatsiya matni bo'yicha nazariy dalil

Manba: `data/desertatsiya.docx`, I bob ("HISOBLASH MASHINALARIDA TARJIMA MUAMMOLARI" — adabiyotlar sharhi/nazariy qism) va butun hujjat bo'yicha to'liq matnli qidiruv.

- **1.3-jadval "Yangi ot yasovchi suffikslar"** (77 ta suffiks, KKT notatsiyasi C(S)) — "-er" bu jadvalda BOR, "-or" BOR.
- **1.7-jadval "Sifatning qiyosiy va orttirma darajasini yasovchi suffikslar"** — tarkibi: ['-er', '-est'] — "-er" bu jadvalda BOR.

- Butun hujjat (barcha 4 bob + xulosa + adabiyotlar) bo'yicha "ish bajaruvchi"/"agentiv"/"harakat bajaruvchi"/"bajaruvchi shaxs" so'z birikmalari qidirildi: **0** ta joyda topildi.

**Jadvaldan chiqadigan (talqin qilinmagan) fakt:** I bobning nazariy suffiks-inventarizatsiya jadvali (1.3-jadval, 77 ta suffiks) "-er"ni ("-or" bilan birga) OT YASOVCHI suffikslar ro'yxatiga kiritadi (izohsiz, misolsiz — 77 tadan biri sifatida). Alohida 1.7-jadval esa "-er"/"-est"ni SIFAT DARAJASI suffikslari sifatida ALOHIDA kataloglaydi. Dissertatsiyaning II bobidagi (formal model ishlab chiqilgan, EVX/EVIX misollari bilan) qismida esa "-er" FAQAT qiyosiy daraja funksiyasida ishlatilgan (5+ misol: cleverer, busier, gayer, larger, bigger, har biriga formal model/vazn berilgan) — agentiv funksiyasi uchun na misol, na formal model, na alohida muhokama bor (yuqoridagi qidiruv, 0 ta natija).

## 5. Xulosa — faqat sonlar (talqin/tavsiya emas)

| Manba | SIFAT+ER (qiyosiy) | FE'L+ER (agentiv) | Aniqlanmagan |
|---|---|---|---|
| 1500 so'zlik lug'at (48 ta "-er" so'zdan) | 0 | 3 | 45 |
| CH2_EVX_EXAMPLES (5 ta "-er" so'zdan) | 5 | 0 | 0 |
| tests/*.py (haqiqiy so'z kirishlari) | 0 | 2 | — |

