# Faza 0 — hisobot

**Sana:** 2026-09-08

## Nima qilindi

1. **`requirements.txt`** — o'rnatilgan muhitdagi aniq versiyalar bilan
   qulflandi (`python-docx==1.2.0`, `openpyxl==3.1.5`, `nltk==3.10.3`,
   `pytest==9.1.1` + to'g'ridan-to'g'ri bog'liqliklar).
2. **`README.md`** — muhit (Python 3.14.0, SQLite 3.51.0, macOS
   Darwin 25.4.0 arm64), o'rnatish, kerakli manba fayllar (aniq nomlar
   bilan, `data/` dagi haqiqiy fayl nomlariga moslab — topshiriqdagi
   tavsifdan farqli ekani hujjatlashtirildi), `make db`, testlarni ishga
   tushirish, va **yon ta'sir haqida ogohlantirish** (pastga qarang).
3. **`.gitignore`** — `*.db` va `.pytest_cache/` qo'shildi.
4. **`Makefile`** — `make install`, `make db`, `make test`, `make clean`.
5. **`scripts/build_db.py`** — `main()` dagi baza-to'ldirish ketma-ketligini
   GUI ochmasdan qayta ishlatadi. Mavjud funksiyalarni faqat **chaqiradi**,
   birortasining mantig'i o'zgartirilmagan.
6. **`kkt_v20_soz_tartibi.py` — bitta maqsadli tuzatish**: `import tkinter`
   try/except bilan o'raldi (`HAS_TK` flag), `MTSystem` klassi butunlay
   `if HAS_TK:` blokiga olindi, `show_error_dialog()` va `main()`
   `HAS_TK=False` holatini xavfsiz boshqaradi (aniq xabar bilan to'xtaydi,
   yiqilmaydi). **Boshqa hech qanday qator o'zgartirilmagan** — bu sof
   import-chegarasi tuzatishi, tarjima mantig'i bit-ma-bit bir xil qoladi
   (testlar bilan tasdiqlangan, pastga qarang).
7. **`tests/`** — `conftest.py` + `test_smoke.py`: 3 ta test, hammasi
   izolyatsiyalangan muhitda ishlaydi (pastdagi hodisaga qarang).
8. **`.db` fayllar git tracking'dan chiqarildi** (`git rm --cached`),
   avval qayta ishlab chiqarilishi isbotlangandan keyin (pastga qarang).
9. **Read-only rejim** (`readonly_mode()` kontekst-menejer,
   `translate_phrase(text, allow_write=False)`) — foydalanuvchi so'rovi
   bo'yicha Faza 0 yakunida qo'shildi, Faza 1'dan oldingi xavfsizlik
   chorasi. To'rtta yozish-nuqtasini (`db_insert`, `qm_confirm_or_add`,
   `bm_get_or_create_pos_model`, `bm_get_or_create_affix_model`) global
   bayroq orqali o'chiradi — keshlash MANTIG'INI (vazn/kkt_symbol
   hisoblashni) saqlab qolgan holda, faqat sqlite'ga yozishni bloklaydi.
   5 test bilan tasdiqlangan (`tests/test_readonly_mode.py`), jumladan
   tarjima natijasi ikkala rejimda ham bir xilligi. Batafsil: alohida
   commit xabari. Faza 1'dagi `scripts/audit_examples.py` va gold-test
   runner shu rejimda ishlashi SHART.

## Kutilmagan hodisa: birinchi test yozuvi repo bazalarini "ifloslagan" edi

Faza 0 rejasiga ko'ra, `.db` fayllarni git'dan chiqarishdan oldin ular
`data/` dan qayta qurilib, git'dagi nusxa bilan solishtirilishi kerak edi.
Birinchi solishtirishda **`UB_en_w.db` va `UB_uz_w.db` da bitta qo'shimcha
qator topildi**: `('books', 'kitoblar', 'Ot', source='auto')`.

Tekshiruv shuni ko'rsatdiki, bu qator **manba hujjatlarda yo'q va qo'lda
kiritilmagan** — u `translate_phrase("from our books")` chaqirilganda
`smart_parse()` ichidagi avtomatik ko'plik-xulosa mexanizmi tomonidan
**shu tekshiruv jarayonida, mening birinchi (izolyatsiyalanmagan) pytest
ishga tushirishim natijasida**, repo ildizidagi haqiqiy `.db` fayllarga
yozilgan edi (`db_insert(w, uz, pos, "auto")`, `kkt_v20_soz_tartibi.py:3037`
atrofida). Ya'ni: **`translate_phrase()` — yon ta'sirga ega funksiya**,
u chaqirilganda diskdagi bazani o'zgartirishi mumkin.

Bu `git status` va `git diff` bilan aniqlandi, so'ng `git checkout --
UB_en_w.db UB_uz_w.db` bilan darhol asl (git HEAD) holatga qaytarildi va
tasdiqlandi (`source='auto'` qatorlar soni = 0, git HEAD bilan mos).
**Repo ildizidagi haqiqiy `.db` fayllar hozir git HEAD bilan bit-ma-bit
bir xil — hech narsa yo'qotilmadi.**

Bu hodisadan keyin test infratuzilmasi qayta ishlab chiqildi:
- `tests/conftest.py` endi HAR BIR test sessiyasi uchun
  `kkt_v20_soz_tartibi.py` + `data_loader.py` + `data/` ni **vaqtinchalik,
  izolyatsiyalangan papkaga** nusxalaydi va modulni O'SHA nusxadan import
  qiladi (`SCRIPT_DIR` orqali baza yo'llari avtomatik izolyatsiya qilinadi).
- Qo'shimcha test (`test_translate_phrase_runs_in_isolation`) repo
  ildizidagi `.db` fayllar `mtime`si `translate_phrase()` chaqirilishidan
  oldin/keyin **o'zgarmasligini** aniq tekshiradi — bu izolyatsiya
  kafolatini kelajakda ham qo'riqlaydi.
- Tekshirildi: testlar qayta ishga tushirilgach, repo ildizidagi
  `UB_en_w.db`/`UB_uz_w.db` `git status`da o'zgarmagan holda qoldi.

**Bu — Qoida 5 ("muvaffaqiyatsizlikni yashirma") talabiga ko'ra ochiq
qayd etilyapti**: bu mening xatoyim edi (test yozishda izolyatsiyani
avval o'ylamadim), lekin aynan shu sabab bilan muhim arxitektura muammosi
ochildi — **tarjima funksiyasi sof (pure) emas**, diskka yozadi. Bu Faza 2/8
uchun yangi topilma sifatida qayd etiladi (pastga qarang).

## Baza qayta ishlab chiqarilishi — tasdiqlangan

Yuqoridagi hodisa tuzatilgandan so'ng, `.db` fayllar `data/` dan qayta
qurilib, git HEAD bilan **to'liq solishtirildi** (sxema + har bir qator,
barcha 9 baza): **farq topilmadi**. To'liq metodika va jadval:
`reports/db_reproducibility.md`.

Muhim shart: qayta ishlab chiqarish faqat `data_loader.py` skript bilan
bir joyda bo'lganda ishlaydi — aks holda kod **jimgina** boshqa (docx
zaxira) yo'lga o'tib, boshqa sonlar beradi (xato chiqarmaydi). Bu README'da
alohida ta'kidlangan va Faza 2/8 uchun topilma sifatida qayd etilgan.

## Ikkita savolga javob (foydalanuvchi so'rovi)

**1. Git'dagi (asl) bazalarda `SELECT COUNT(*) FROM words WHERE source='auto'` nechchi?**

**0** — ikkalasida ham (`UB_en_w.db` va `UB_uz_w.db`). Tekshirildi bevosita
git HEAD holatidagi (hozirgi ishchi papkadagi, `git status` toza ekani
tasdiqlangan) fayllarda. To'liq `source` taqsimoti (1596 ta yozuvning
hammasi): `json`(1513), `chapter2_evx`(52), `docx`(31). `auto` yoki `user`
manbali (ya'ni dastur ishlayotganda runtime'da qo'shilgan) birorta ham
yozuv git'da saqlanmagan — bazalar faqat qurish-vaqtidagi (build-time)
manbalardan iborat. (Bu Faza 0 dagi yuqoridagi hodisada MEN o'zim
qo'shib qo'ygan `books/kitoblar` qatoridan FARQLI — o'sha `git checkout`
bilan allaqachon olib tashlangan edi, shu tekshiruv o'sha tozalashdan
KEYIN, alohida, qayta tasdiqlash sifatida bajarildi.)

**2. "Bit-ma-bit bir xil" qanday tekshirilgan — md5 bilanmi, kontent bilanmi?**

**Kontent bilan, md5 bilan EMAS.** Asosiy tekshiruv (`reports/db_reproducibility.md`)
har bir jadvalni `SELECT *` orqali o'qib, qatorlarni (Python tuple sifatida,
barqaror tartiblab) git'dagi nusxa bilan solishtirdi — fayl baytlarini emas.
Bu ataylab shunday tanlangan: SQLite fayllari bir xil MANTIQIY kontentga
ega bo'lsa ham sahifa joylashuvi/freelist holati farqi sababli bayt
darajasida farqlanishi mumkin — md5 shu sababli soxta "farq" ko'rsatishi
mumkin edi. Foydalanuvchi so'rovidan keyin qo'shimcha tekshiruv sifatida
md5 HAM solishtirildi — bu aniq holatda **md5 ham mos chiqdi** (barcha 9
baza), lekin bu tasodifiy natija, metodologiya asosi emas. To'liq
tafsilot va jadval: `reports/db_reproducibility.md` ("Uslub — ANIQLASHTIRISH"
bo'limi, yangilangan).

**Xulosa:** hisobotlarda ishlatilgan "bit-ma-bit bir xil" iborasi ikki xil
narsaga tegishli edi — (a) `git checkout` bilan asl holatga qaytarish
(bu HAQIQATAN HAM bit-ma-bit, git'ning o'zi kafolatlaydi) va (b) qayta
qurilgan bazani asl bilan solishtirish (bu KONTENT darajasida, md5 emas).
Bu ikkisi noaniq aralashtirilgani uchun yuqoridagi ikkala hisobotda
so'z birikmasi aniqlashtirildi.

## Tasdiqlanmagan (eski) natijalar — hali yakuniy DEB HISOBLANMASIN

Topshiriqda keltirilgan sonlar — **100 ta etalon ustida to'liq lug'at bilan
56/100; yetishmayotgan 3 ta ot (`school`, `program`, `article`)
qo'shilgandan keyin 80/100** — foydalanuvchining o'zi tomonidan, mustaqil
ravishda, DASTURNING BU JORIY holatidan OLDIN, qo'lda o'tkazilgan sinovlar
edi. Bu sonlar:

- **hech qanday skript bilan qayta ishlab chiqarilmagan** (repoda bunday
  skript hozircha yo'q — `scripts/audit_examples.py` va gold-test runner
  Faza 1/3 da yoziladi);
- **read-only rejimsiz** olingan bo'lishi mumkin (ya'ni sinov jarayonining
  o'zi bazani o'zgartirgan bo'lishi mumkin — xuddi Faza 0 dagi hodisadagi
  kabi), demak sinov N va sinov N+1 bir xil sharoitda o'tkazilgan
  ekanligiga kafolat yo'q;
- **qaysi baza holatida** (qaysi commit, qaysi qo'shimcha so'zlar bilan)
  olinganligi hujjatlashtirilmagan.

Shu sabablarga ko'ra, **56/100 va 80/100 raqamlari BU HISOBOTDA HAM,
kelajakdagi hech qanday hisobotda ham YAKUNIY natija sifatida
ko'rsatilmaydi.** Ular faqat "boshlang'ich gipoteza / kutilayotgan taxminiy
tartib" sifatida eslatilishi mumkin, aniq manba (foydalanuvchining qo'lda
sinovi, sana ko'rsatilmagan) bilan birga.

Faza 1 da (`audit_examples.py` va gold-test runner tayyor bo'lgach) bu
son **read-only rejimda** (`translate_phrase(text, allow_write=False)`),
**toza, `make db` bilan qaytadan qurilgan bazada**, 100_soz.docx/json dan
avtomatik o'qilgan holda qaytadan hisoblanadi va natija shu aniq
buyruq/commit bilan bog'liq holda qayd etiladi. O'sha yangi son — birinchi
RASMAN tasdiqlangan natija bo'ladi.

## Yangi topilmalar (keyingi fazalar uchun qayd)

1. **`translate_phrase()`/`smart_parse()` yon ta'sirga ega** — noma'lum
   ko'plik shakllarini avtomatik xulosa qilib, natijani to'g'ridan-to'g'ri
   `.db` fayllarga yozadi (`source="auto"`). Bu: (a) funksiyani sinash
   qiyinlashtiradi (test/audit skriptlari izolyatsiya talab qiladi — endi
   `tests/`da hal qilingan), (b) ishlab chiqarishda ikkita parallel
   foydalanuvchi bir xil bazaga yozsa poyga holati (race condition)
   yaratishi mumkin, (c) "auto" manbali yozuvlar sifat nazoratisiz bazaga
   kirib qoladi — Faza 8 (error analysis) va Faza 7 (`provenance` ustuni)
   buni hisobga olishi kerak.
2. **`load_pdf_kkt_bazalar()` (90 KKT belgi, 313 affiks) va
   `load_ch2_evx_examples()` (52 so'z/model/qoida) manbasi — tashqi qayta
   o'qiladigan fayl emas, balki `kkt_v20_soz_tartibi.py` ichiga qo'lda
   transkripsiya qilingan literal Python ro'yxatlar.** Deterministik
   (kod o'zgarmasa natija bir xil), lekin Faza 7 provenance ustunida
   "manba: docx" emas, "manba: kodga qo'lda kiritilgan" deb yozilishi kerak.
3. `data_loader.py` (JSON asosida) va `kkt_v20_soz_tartibi.py` ichidagi
   to'g'ridan-to'g'ri docx/xlsx o'qish — ikki mustaqil yo'l, birinchisi
   ustunlik qiladi, ikkinchisi faqat zaxira. Ikkalasi hozircha
   birlashtirilmagan (Faza 0 doirasidan tashqarida qoldirildi).

## Qaysi taqriz bandlari yopildi

- **50-band** (test yo'qligi) — **qisman yopildi**. Infratuzilma (pytest,
  izolyatsiyalangan muhit, `make test`) tayyor va ishlaydi. To'liq
  regression (tarjima sifatini o'lchovchi testlar) — Faza 1.
- **51-band** (fayl nomi/versiya, ishga tushirish tartibi hujjatlashmagan) —
  **qisman yopildi**. README to'liq ishga tushirish tartibini yozadi.
  Fayl nomi/`__version__` birxillashtirilishi — Faza 2.

## Qayta ishlab chiqarish buyruqlari

```bash
pip install -r requirements.txt   # muhit
make db                           # 9 ta .db ni data/ dan noldan quradi
make test                         # pytest (izolyatsiyalangan)
```

`reports/db_reproducibility.md` dagi solishtiruv jadvali — qo'lda qayta
ishga tushirish uchun o'sha hisobotdagi "Uslub" bo'limiga qarang (vaqtinchalik
skript, repoga kiritilmagan, chunki bir martalik tekshiruv edi; xohlasa
keyingi fazada `scripts/verify_db_reproducibility.py` sifatida doimiylashtirish mumkin).

## Nima ishlamadi / ochiq qoldi

- `data_loader.py` va docx-to'g'ridan-o'qish yo'llarini birlashtirish —
  qilinmadi, doirada emas edi.
- `.db` fayllarni git tarixidan (eski commit'lardan) butunlay olib
  tashlash — qilinmadi, faqat kelajakdagi commit'lar uchun tracking
  to'xtatildi (`git rm --cached`). Eski commit'larda baribir qoladi.
- Baza qayta ishlab chiqarilish tekshiruvi bir martalik qo'lda bajarildi;
  doimiy CI tekshiruvi sifatida skriptlashtirilmadi (Faza 1 kandidat).
- `sacrebleu` va boshqa Faza 4+ kutubxonalari `requirements.txt`ga hali
  qo'shilmadi — kerak bo'lganda o'sha fazada qo'shiladi.
