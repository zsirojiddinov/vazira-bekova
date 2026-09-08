# II bob misollari auditi (CH2_EVX_EXAMPLES)

**Generatsiya vaqti:** 2026-09-08T15:07:54+00:00Z
**Manba:** `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` (52 ta misol)
**Buyruq:** `python scripts/audit_examples.py`
**Rejim:** `translate_phrase(text, allow_write=False)` — bazaga yozilmagan.

**so_zlar_bazasi_un.docx qidiruvi:** Topilmadi (`so_zlar_bazasi_un.docx` repoda yo'q) — quyidagi natija to'liq `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` literal ro'yxatiga asoslangan.

## MUHIM METODOLOGIK OGOHLANTIRISH — aylanma (circular) tekshiruv xavfi

`load_ch2_evx_examples()` shu RO'YXATNING HAR BIR so'zini `UB_en_w`ga TO'G'RIDAN-TO'G'RI headword sifatida (`source='chapter2_evx'`) yozib qo'yadi. Shu sabab BITTA-SO'ZLI misol uchun `translate_phrase()` "to'g'ri" javob bersa ham, bu ko'pincha morfologik DERIVATSIYA emas — tizim shu jadvaldan TO'G'RIDAN-TO'G'RI o'qib qaytaryapti (aylanma tekshiruv: ma'lumot qayerdan kelgan bo'lsa, o'sha yerga solishtirilyapti). Har bir moslik pastda ikkiga ajratilgan: **to'g'ridan (aylanma, past ishonchli)** va **derivatsiya orqali (haqiqiy morfologik test)**.

## Umumiy natija

- Jami: **52**
- Aniq mos (normalizatsiya bilan): **26/52**
  - shundan to'g'ridan bazadan (derivatsiya emas): **26**, bulardan:
    - **25 ta TO'LIQ AYLANMA** (headword FAQAT CH2_EVX_EXAMPLES orqali kiritilgan — batafsil jadvalga qarang)
    - **1 ta MUSTAQIL MANBADAN** (headword boshqa, CH2_EVX_EXAMPLES'dan mustaqil yuklovchi orqali ham bor va aynan o'sha qator tanlangan — "aylanma" emas)
  - shundan HAQIQIY derivatsiya orqali (affiks/o'zak ajratish ishlagan): **0**
- `None` qaytardi: **15/52**
- Natija qaytardi, lekin matn mos emas: **11/52**

## Aylanma (circular) tekshiruv — batafsil dalil jadvali

"Aylanma" da'vosini aniqlashtirish uchun har bir to'g'ridan mos kelgan (26 ta) misol uchun: (1) UB_en_w.db dagi HAQIQIY qatorlar (id, tarjima, POS, `source`), (2) shulardan qaysi biri `translate_phrase()` tomonidan tanlangani, (3) shu inglizcha bosh so'z ikkita MUSTAQIL, `CH2_EVX_EXAMPLES`ga aloqasi bo'lmagan inson-manba faylida (`data/1500_EN_UZ_6_POS_sorted.20.json`, `data/100_soz.json`) ham mustaqil ravishda mavjudmi. **Git tarixi bo'yicha eslatma:** `CH2_EVX_EXAMPLES` ro'yxati ham, `.db` bazalarini to'ldiruvchi barcha boshqa manba yuklovchi kod ham BITTA "Initial commit"da (841d174, 2026-09-08) qo'shilgan — shu sabab so'z darajasida ma'noli git sana/tarix solishtiruvi MAVJUD EMAS (`.db` fayllarining o'zi esa umuman git'da kuzatilmaydi, Faza 0). Shu sabab "oldin/keyin" ustuni git sanasiga emas, kodning DETERMINISTIK yuklash tartibiga (`setup_database()` — 1500-so'zlik JSON/docx lug'at — HAR DOIM `load_ch2_evx_examples()`dan OLDIN ishga tushadi, qarang `scripts/build_db.py`) asoslanadi: agar so'z mustaqil manbada bo'lsa, u UB_en_w'ga CH2 ro'yxatidan OLDIN yozilgan bo'lardi.

| Misol (en) | UB_en_w qatorlari (id, tarjima, POS, source) | Tanlangan qator | Mustaqil manbada (1500-so'z/100-so'z)? | Xulosa |
|---|---|---|---|---|
| processes | id=1545 'jarayonlar' Ot src=chapter2_evx | id=1545 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| an example | id=1547 'misol' Ot src=chapter2_evx | id=1547 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| capabilityies | id=1550 'imkonyatlar' Ot src=chapter2_evx | id=1550 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| delays | id=1551 'kechikishlar' Ot src=chapter2_evx | id=1551 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| leafes | id=1552 'barglar' Ot src=chapter2_evx | id=1552 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| men | id=1553 'erkaklar' Ot src=chapter2_evx | id=1553 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| customhouses | id=1554 'Bojxonalar' Ot src=chapter2_evx | id=1554 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| schoolboys | id=1555 'Bojxonalar' Ot src=chapter2_evx | id=1555 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| information | id=1556 'Axborot' Ot src=chapter2_evx | id=1556 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| contents | id=1557 'mazmun' Ot src=chapter2_evx | id=1557 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| student's | id=1558 'studentning' Ot src=chapter2_evx | id=1558 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| cleverer | id=1573 'aqilliroq' Sifat src=chapter2_evx | id=1573 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| cleverest | id=1574 'eng aqilli' Sifat src=chapter2_evx | id=1574 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| busier | id=1575 'kattaroq' Sifat src=chapter2_evx | id=1575 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| busiest | id=1576 'eng katta' Sifat src=chapter2_evx | id=1576 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| gayer | id=1577 "sho'xroq" Sifat src=chapter2_evx; id=1578 "eng sho'x" Sifat src=chapter2_evx | id=1577 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| here | id=1581 'shu yerda' Ravish src=chapter2_evx | id=1581 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| faster | id=1582 'tezroq' Ravish src=chapter2_evx | id=1582 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| fastest | id=1583 'eng tez' Ravish src=chapter2_evx | id=1583 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| inside | id=1584 'ichkarida' Ravish src=chapter2_evx | id=1584 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| today | id=1585 'bugun' Ravish src=chapter2_evx | id=1585 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| much | id=424 "Ko'p" Ot src=json; id=1586 "ko'p" Ravish src=chapter2_evx | id=424 src=json | 1500_EN_UZ_6_POS_sorted.20.json | MUSTAQIL MANBA orqali topilgan (tanlangan qator source='json', CH2_EVX_EXAMPLES emas) |
| quietly | id=1587 'tinchgina' Ravish src=chapter2_evx | id=1587 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| fifteen | id=1589 "o'n besh" Son src=chapter2_evx | id=1589 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| eighty | id=1590 'sakson' Son src=chapter2_evx | id=1590 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |
| hundredth | id=1594 'yuzinchi' Son src=chapter2_evx | id=1594 src=chapter2_evx | yo'q | TO'LIQ AYLANMA — faqat CH2_EVX_EXAMPLES orqali kirgan, boshqa hech qanday manbada yo'q |

**Jadvaldan xulosa:** 26 ta to'g'ridan-mos misoldan **25 tasi to'liq aylanma** (headword FAQAT `CH2_EVX_EXAMPLES` orqali, `load_ch2_evx_examples()` chaqirilganda kiritilgan — boshqa hech qanday mustaqil manbada yo'q) va **1 tasi mustaqil manbadan** (headword `CH2_EVX_EXAMPLES`dan TASHQARI, boshqa yuklovchi orqali ham UB_en_w'ga kirgan va aynan O'SHA mustaqil qator tanlangan — bu holat uchun "aylanma" da'vosi TO'G'RI EMAS, garchi bu baribir morfologik DERIVATSIYA emas, to'g'ridan-to'g'ri lug'at izlashi bo'lsa ham).

## Topshiriqda nomlab o'tilgan misollar

Topshiriq matni: *"capabilityies, leafes, schoolboys, more comfortable, will return shu yo'l bilan topilishi kerak edi"*. Tekshiruv:

- `capabilityies` -> etalon `'imkonyatlar'`, joriy chiqish `'Imkonyatlar'` — **MOS KELDI, LEKIN TO'LIQ AYLANMA (to'g'ridan bazadan, faqat CH2_EVX_EXAMPLES orqali)**
- `leafes` -> etalon `'barglar'`, joriy chiqish `'Barglar'` — **MOS KELDI, LEKIN TO'LIQ AYLANMA (to'g'ridan bazadan, faqat CH2_EVX_EXAMPLES orqali)**
- `more comfortable` -> etalon `'eng qulay'`, joriy chiqish `None` — **MOS EMAS (kutilgan edi)**
- `schoolboys` -> etalon `'Bojxonalar'`, joriy chiqish `'Bojxonalar'` — **MOS KELDI, LEKIN TO'LIQ AYLANMA (to'g'ridan bazadan, faqat CH2_EVX_EXAMPLES orqali)**

## Mos kelmagan barcha qatorlar

| Ingliz | Etalon (uz) | Chiqish | POS |
|---|---|---|---|
| a network | tarmoq | None | Ot |
| the progress | taraqqiyot | None | Ot |
| The Germanys | Germaniyaliklar | None | Ot |
| to do | qilmoq | 'Ga' | Fe'l |
| will | keladi | None | Fe'l |
| would | keladi | None | Fe'l |
| can | qila  olmoq | None | Fe'l |
| may | mumkin | None | Fe'l |
| might | mumkin | None | Fe'l |
| must | shart | None | Fe'l |
| ought | zarur | None | Fe'l |
| ought to | zarur | "Ga ajratib ko'rsatmoq" | Fe'l |
| to ask | so'ramoq | "Ga ajratib ko'rsatmoq" | Fe'l |
| reading | o'qishni | None | Fe'l |
| to follow | ergashmoq | 'Ga' | Fe'l |
| sent | yuborgan | None | Fe'l |
| high dimensional | ko'p o'lchovli | 'O‘lchamli' | Sifat |
| gayer | eng sho'x | "Sho'xroq" | Sifat |
| more comfortable | eng qulay | None | Sifat |
| less interesting | so'z kamroq qiziqarli | None | Sifat |
| one | bir | 'Biri / Bitta' | Son |
| eighty five | sakson besh | 'Sakson' | Son |
| one hundred | bir yuz | 'Biri / Bitta' | Son |
| four million | to'rt million | None | Son |
| hundred and twenty first | bir yuz yigirma birinchi | 'Va' | Son |
| chapter five | beshinchi bob | 'Bob' | Son |

