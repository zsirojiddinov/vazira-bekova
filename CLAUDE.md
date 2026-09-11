# CLAUDE.md — VaziraProject

KKT (Kengayuvchi Kirish Tili) asosidagi ingliz→o'zbek tarjima tizimi (dissertatsiya
dasturi, `kkt_v20_soz_tartibi.py`). Har faza bo'yicha hisobotlar — `reports/`.

## ⚠ DOIMIY OGOHLANTIRISH — mavjud gold to'plam (100_soz) bazaning ICHIDA turibdi

`data/100_soz.json` dagi 100 ta gold test-case'ning HAMMASI
`data/1500_EN_UZ_6_POS_sorted.20.json` ichidagi `"100 SOZ (MORFEMIK TAHLIL)"`
kategoriyasi orqali baza qurilganda UB_en_w/UB_uz_w lug'atiga (`source='json'`)
va MDB_uz_w nomzodlariga yuklanadi (100/100). Hozircha bahoga ta'siri 0 ekani
ablatsiya bilan o'lchangan (56/100 → 56/100) — lekin bu faqat tasodif: iboralar
ko'p so'zli, qidiruv esa token bo'yicha. Dalil va qayta o'lchash:
`python scripts/audit_lexicon_sources.py` → `reports/faza_2_lexicon_sources.md`;
qo'riqlovchi test: `tests/test_audit_lexicon_sources.py`.

Bu holat o'zgarmaguncha (100 SOZ kategoriyasini ajratish — alohida qaror):
100_soz bahosini aylanma baholashdan xoli deb TAQDIM ETMANG, lug'at qidiruviga
butun ibora bo'yicha qidiruv qo'shsangiz — avval shu testni ishga tushiring.

## MAJBURIY: kelajakdagi har qanday gold test baza manbalaridan FIZIK ajratilgan bo'lishi SHART

Gold (etalon) test-case'lar — Faza 3 dagi yangi 200–500 ta va keyingi barcha
to'plamlar — **HECH QACHON, hech qanday shaklda** bazani to'ldiradigan manbaga
qo'yilmaydi:

- `data/` papkasiga (JSON, docx, xlsx yoki boshqa format) — build jarayoni uni o'qiydi;
- `data/1500_EN_UZ_6_POS_sorted.20.json` ichiga kategoriya sifatida — loader barcha
  kategoriyalarni yuklaydi;
- kod ichidagi literal ro'yxat sifatida (`CH2_EVX_EXAMPLES`, `SEED_WORDS` kabi);
- GUI yoki `translate_phrase(..., allow_write=True)` orqali — natija bazaga keshlanadi.
  Gold baholash faqat `allow_write=False` / `readonly_mode()` bilan.

Gold fayllar DB yuklovchi kod ko'rmaydigan alohida papkada saqlanadi (tavsiya:
repo ildizidagi `gold/`, `data/` emas); fayl nomlari yuklovchi naqshlariga mos
kelmasin. Yuklovchi yo'llar ro'yxati va gold to'plam qo'shilishidan oldingi qabul
mezonlari (qo'riqlovchi testlar): `reports/faza_3_plan.md`.
