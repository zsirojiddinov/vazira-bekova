# Faza 7 — ochiq ro'yxat: lug'at-ma'lumot yetishmovchiligi (spec qoidalari)

**Holat:** qayd etildi, TEGILMAGAN (foydalanuvchi qarori, 2026-09-11: bazalar sxemasi
bilan bog'liq bo'lishi mumkin — Faza 7). Manba: `reports/faza_2_kkt_spec_conformance.md`
(L turidagi YO'Q qoidalar), tekshiruv izolyatsiyalangan bazada (`make db` bilan bir xil
ketma-ketlik).

## 1. 12 ta spec qoidasi — bosh so'z lug'atda umuman yo'q

Bu qoidalar kod qoidasi emas, **leksik moslik**: spec so'zning tarjimasini beradi, kodda
esa so'zning o'zi yo'q. Hammasida bosh so'z na UB_en_w bazasida, na
`data/1500_EN_UZ_6_POS_sorted.20.json` da bor.

| Spec qoidasi | POS | Spec misoli | Yo'q bosh so'z | Izoh |
|---|---|---|---|---|
| 2.36 | Fe'l | read → o‘qimoq | read | sodda fe'l |
| 2.38 | Fe'l | to be → bo‘lmoq | be | |
| 2.39 | Fe'l | am → man (1-shaxs birlik affiksi) | am | "to be" shakli |
| 2.41 | Fe'l | was, were → edi | was, were | "to be" o'tgan zamon |
| 2.44 | Fe'l | to have → bor bo‘lmoq | have | |
| 2.45 | Fe'l | to do → qilmoq | do | CH2 da faqat "to do" IBORA headword (`qilmoq`) — token qidiruvi uni hech qachon topmaydi |
| 2.48 | Fe'l | become → bo‘lmoq | become | bog'lovchi fe'l |
| 2.50 | Fe'l | could → ol + ar + di = olardi | could | modal |
| 2.55a | Fe'l | need → kerak | need | modal |
| 2.58 | Fe'l | to follow → kuzatmoq | follow | CH2 da faqat "to follow" IBORA headword (`ergashmoq` — spec'dan farqli) |
| –(Ravish) | Ravish | very → juda | very | sodda ravish |
| –(Sifat) | Sifat | big → katta | big | oddiy sifat |

E'tibor: bu so'zlarning ko'pchiligi — tilning eng tez-tez uchraydigan yordamchi/modal
fe'llari (be, have, do, could, need). Ular bo'lmagani sababli ular qatnashgan har qanday
ibora so'zma-so'z `[so'z?]` bilan chiqadi.

## 2. Bog'liq lug'at/ma'lumot topilmalari (Faza 2 davomida qayd etilgan)

`reports/faza_2.md` 4-bo'lim, qisqacha:

- Lug'at teglanishi: "Network → Tarmoq" VERBS'da; `apply/comply/imply/rely` — Ravish,
  `confer/dump/filter` — Ot (tarjimasi fe'l); `uz_stem()` turkumdan qat'i nazar "-moq"
  kesadi ("Tarmoq" → "Tar").
- "one" → 1500-lug'atda "Biri / Bitta" (Ot) birinchi qator — Son "bir" (CH2) emas; natijada
  noqoida tartib son "first" real lug'at bilan "biriinchi" bo'ladi (stub bilan to'g'ri,
  spec 3.19).
- CH2 formal modelidagi belgi yozuvi ("GHA1") SSM ildizini buzadi → "ask" MDB bilan
  almashtiriladi.
- CH2_EVX_EXAMPLES dagi ko'p so'zli headword'lar ("to do", "to follow", "a network",
  "the progress", "more comfortable", ...) token bo'yicha qidiruvda umuman ishlatilmaydi.

## 3. Kod qoidasi kerak, lekin ro'yxat leksik: 2.10 (hozircha YO'Q)

2.10 "man → men → erkaklar" — noqoida ko'plik. Kodda yagona mexanizm NLTK lemmatizer,
u "men" ni tanimaydi. Dissertatsiya II bob qoida matni (CH2_EVX_EXAMPLES `rule` maydoni) 7 ta
so'zni sanaydi: man/men, woman/women, foot/feet, tooth/teeth, goose/geese, mouse/mice,
louse/lice. Bu — lug'at emas, kichik jadval qoidasi; alohida qaror bilan qo'shilishi mumkin.
