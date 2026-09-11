# Faza 3 — reja: gold test to'plamini qurish (200–500 ta yangi test-case)

**Holat:** reja hali to'liq tuzilmagan. Bu fayl hozircha Faza 3 boshlanishidan OLDIN
qayd etilishi shart bo'lgan MAJBURIY cheklovni saqlaydi (foydalanuvchi talabi,
2026-09-11). Xuddi shu talab `CLAUDE.md` da ham bor.

---

## ⚠ MAJBURIY OGOHLANTIRISH — gold test-case'lar baza manbalariga HECH QACHON qo'yilmaydi

### Nima uchun (o'lchangan fakt, taxmin emas)

`reports/faza_2_lexicon_sources.md` (`python scripts/audit_lexicon_sources.py`):
mavjud 100 ta gold test-case (`data/100_soz.json`) **tarjima lug'ati bilan bitta
faylda** — `data/1500_EN_UZ_6_POS_sorted.20.json` ichidagi `"100 SOZ (MORFEMIK
TAHLIL)"` kategoriyasida — turibdi. `_load_words_from_json()` →
`data_loader.load_word_pairs()` JSON'dagi BARCHA kategoriyalarni o'qigani uchun,
100 ta gold javobning hammasi baza qurilganda UB_en_w/UB_uz_w lug'atiga
(`source='json'`) va MDB_uz_w nomzodlariga yozilgan (100/100).

Hozircha bu bahoni oshirmagan (ablatsiya: qatorlar olib tashlanganda 100 ta
natijadan 0 tasi o'zgaradi, 56/100 → 56/100) — faqat shu sababli: gold iboralar
ko'p so'zli, `translate_phrase()` esa lug'atni alohida so'z bo'yicha qidiradi.
Bu **tasodif**, himoya emas: butun ibora bo'yicha qidiruv qo'shilsa yoki MDB
tanlov tartibi o'zgarsa, test javoblari to'g'ridan-to'g'ri qaytib, baho aylanma
(circular) bo'lib qoladi. `CH2_EVX_EXAMPLES` (II bob misollari kod ichida yozilgan
va lug'atga yuklangan) xuddi shu yo'l bilan L-turidagi moslik natijalarini
aylanma qilgan (`reports/faza_2_kkt_spec_conformance.md` 0.1-jadval).

### Talab

Faza 3 da yaratiladigan yangi 200–500 ta gold test-case:

1. **Hech qachon, hech qanday shaklda** baza to'ldiradigan manbaga qo'yilmaydi:
   - `data/` papkasiga — JSON, docx, xlsx yoki boshqa formatda (build jarayoni
     `data/` ni to'liq o'qiydi va testlar uni izolyatsiyalangan nusxaga ko'chiradi);
   - `data/1500_EN_UZ_6_POS_sorted.20.json` ichiga yangi kategoriya sifatida
     (loader BARCHA kategoriyalarni yuklaydi);
   - kod ichidagi literal ro'yxat sifatida (`CH2_EVX_EXAMPLES`, `SEED_WORDS` kabi —
     ular ham bazaga yoziladi);
   - GUI orqali yoki `translate_phrase(..., allow_write=True)` bilan ishga
     tushirib (oddiy rejimda natija `db_insert(..., "auto")` bilan bazaga
     keshlanadi). Gold baholash FAQAT `allow_write=False` / `readonly_mode()`.
2. **Fizik jihatdan boshqa papkada** saqlanadi — DB yuklovchi kod ko'rmaydigan joyda.
   Tavsiya: repo ildizidagi alohida `gold/` papkasi (`data/` emas).
3. Fayl nomlari yuklovchilar qidiradigan naqshlarga mos kelmasligi kerak
   (pastdagi ro'yxat).

### DB yuklovchilar qayerdan o'qiydi (2026-09-11 holati — kod o'zgarsa qayta tekshirilsin)

| Joy (kod) | Nimani o'qiydi |
|---|---|
| `data_loader.py`: `WORD_PAIRS_JSON`, `ENGLISH_AFFIXES_JSON`, `UZBEK_AFFIXES_JSON` | `data/` ichidagi 3 ta aniq JSON; 1500-JSON ning **barcha** kategoriyalari |
| `kkt_v20_soz_tartibi.py`: `SEARCH_DIRS = [SCRIPT_DIR, DATA_DIR, os.getcwd()]` | repo ildizi, `data/` va joriy papka — rekursiv EMAS |
| `DOCX_CANDIDATES`, `DOCX2_CANDIDATES`, `DOCX2B_CANDIDATES`, `DOCX3_CANDIDATES` | shu papkalardagi aniq nomli docx'lar (`1500_EN_UZ_6_POS_sorted*.docx`, `bazalar_ma_lumot_09*.docx`, `so_zlar_bazasi_un.docx`) |
| `XLSX_EN` / `XLSX_UZ` (`_find_latest_by_pattern`) | `Table_English*Vazn*Type*2*.xlsx`, `Lotinda*Table*Uzbek*Vazn*.xlsx` glob naqshlari |
| `CH2_EVX_EXAMPLES`, `SEED_WORDS`, `KKT_SYMBOLS`, `AFFIX_TABLES` | kod ichidagi literal ro'yxatlar |
| `db_insert()` (oddiy rejim) | tarjima natijalarini runtime'da bazaga yozadi |

`gold/` (ildizdagi alohida papka) bu yo'llarning hech biriga kirmaydi: `SEARCH_DIRS`
rekursiv emas, testlar izolyatsiyalangan nusxaga faqat `kkt_v20_soz_tartibi.py`,
`data_loader.py` va `data/` ni ko'chiradi. Ehtiyot: build'ni `gold/` ichidan
ishga tushirmang (`os.getcwd()` qidiruv papkasiga aylanadi).

### Faza 3 qabul mezonlari (gold to'plam qo'shilishidan OLDIN bajarilsin)

- [ ] **Qo'riqlovchi test (manba darajasida):** baza qurilishi paytida ochilgan
      barcha fayllar yozib olinadi (masalan `sys.addaudithook` "open" hodisasi) va
      `gold/` ostidagi birorta fayl ochilmagani tasdiqlanadi.
- [ ] **Qo'riqlovchi test (natija darajasida):** qurilgan bazada gold test-case'larning
      inglizcha iboralari UB_en_w headword sifatida, o'zbekcha javoblari UB_uz_w /
      MDB_uz_w da yo'q (1500-lug'atning 6 asosiy kategoriyasida mustaqil bor bo'lgan
      bitta so'zlar alohida ro'yxatlanib, izohlanadi).
- [ ] Gold baholash skripti faqat `allow_write=False` bilan ishlaydi; skript
      ishlagandan keyin baza o'zgarmagani (qator soni/xesh) tekshiriladi.
- [ ] Mavjud `100 SOZ` kategoriyasini 1500-JSON dan ajratish masalasi alohida hal
      qilinsin (hozir ablatsiya ta'siri 0, lekin qoida bo'yicha bu ham buzilish);
      ajratilsa — `reports/db_reproducibility.md` qayta tekshiriladi.
- [ ] `scripts/check_leakage.py` ga yangi gold manbasi qo'shilsin (spec misollari,
      CH2_EVX_EXAMPLES va 1500-lug'at bilan kesishma — ogohlantirish sifatida).
