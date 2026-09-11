# CLAUDE.md — VaziraProject

KKT (Kengayuvchi Kirish Tili) asosidagi ingliz→o'zbek tarjima tizimi (dissertatsiya
dasturi, `kkt_v20_soz_tartibi.py`). Har faza bo'yicha hisobotlar — `reports/`.

## MAJBURIY: gold test ma'lumotlari baza manbalaridan fizik ajratilgan bo'lsin

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
kelmasin.

**Sabab:** mavjud 100 ta gold (`100_soz`) 1500-JSON ichidagi "100 SOZ" kategoriyasi
orqali lug'atga yuklanib qolgan — hozircha natijaga ta'siri 0 ekani o'lchangan,
lekin bu tasodif (`reports/faza_2_lexicon_sources.md`). Batafsil qoidalar, yuklovchi
yo'llar ro'yxati va qabul mezonlari: `reports/faza_3_plan.md`.
