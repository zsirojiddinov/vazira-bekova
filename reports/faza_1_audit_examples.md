# II bob misollari auditi (CH2_EVX_EXAMPLES)

**Generatsiya vaqti:** 2026-09-08T14:53:08+00:00Z
**Manba:** `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` (52 ta misol)
**Buyruq:** `python scripts/audit_examples.py`
**Rejim:** `translate_phrase(text, allow_write=False)` — bazaga yozilmagan.

**so_zlar_bazasi_un.docx qidiruvi:** Topilmadi (`so_zlar_bazasi_un.docx` repoda yo'q) — quyidagi natija to'liq `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` literal ro'yxatiga asoslangan.

## MUHIM METODOLOGIK OGOHLANTIRISH — aylanma (circular) tekshiruv xavfi

`load_ch2_evx_examples()` shu RO'YXATNING HAR BIR so'zini `UB_en_w`ga TO'G'RIDAN-TO'G'RI headword sifatida (`source='chapter2_evx'`) yozib qo'yadi. Shu sabab BITTA-SO'ZLI misol uchun `translate_phrase()` "to'g'ri" javob bersa ham, bu ko'pincha morfologik DERIVATSIYA emas — tizim shu jadvaldan TO'G'RIDAN-TO'G'RI o'qib qaytaryapti (aylanma tekshiruv: ma'lumot qayerdan kelgan bo'lsa, o'sha yerga solishtirilyapti). Har bir moslik pastda ikkiga ajratilgan: **to'g'ridan (aylanma, past ishonchli)** va **derivatsiya orqali (haqiqiy morfologik test)**.

## Umumiy natija

- Jami: **52**
- Aniq mos (normalizatsiya bilan): **26/52**
  - shundan to'g'ridan (aylanma, CH2_EVX_EXAMPLES headword sifatida o'zi ham bor): **26**
  - shundan HAQIQIY derivatsiya orqali (affiks/o'zak ajratish ishlagan): **0**
- `None` qaytardi: **15/52**
- Natija qaytardi, lekin matn mos emas: **11/52**

## Topshiriqda nomlab o'tilgan misollar

Topshiriq matni: *"capabilityies, leafes, schoolboys, more comfortable, will return shu yo'l bilan topilishi kerak edi"*. Tekshiruv:

- `capabilityies` -> etalon `'imkonyatlar'`, joriy chiqish `'Imkonyatlar'` — **MOS KELDI, LEKIN AYLANMA (to'g'ridan bazadan, morfologik derivatsiya EMAS)**
- `leafes` -> etalon `'barglar'`, joriy chiqish `'Barglar'` — **MOS KELDI, LEKIN AYLANMA (to'g'ridan bazadan, morfologik derivatsiya EMAS)**
- `more comfortable` -> etalon `'eng qulay'`, joriy chiqish `None` — **MOS EMAS (kutilgan edi)**
- `schoolboys` -> etalon `'Bojxonalar'`, joriy chiqish `'Bojxonalar'` — **MOS KELDI, LEKIN AYLANMA (to'g'ridan bazadan, morfologik derivatsiya EMAS)**

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

