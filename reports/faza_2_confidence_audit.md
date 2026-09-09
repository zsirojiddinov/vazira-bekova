# Faza 2 — "Aniqlik/Ishonch" ko'rsatkichlari auditi (Ustuvorlik 0)

**Sana:** 2026-09-09. **Muallif:** Claude (Sonnet 5), Ziyoviddin so'rovi bilan.
**Qoida:** bu hisobotda hech qanday kod o'zgartirilmagan — faqat mavjud kod va
mavjud dissertatsiya faylini (matn + rasm) o'qib, topilganini hujjatlashtirish.
Xulosalar ikki toifaga bo'lingan: **TASDIQLANGAN** (kod/rasm bilan bevosita
isbotlangan) va **OCHIQ SAVOL** (dalil yo'q, taxmin qilinmagan).

---

## 0.1 — GUI'dagi "aniqlik/foiz/ball" ko'rsatkichlari — to'liq jadval

`grep -n "conf\|SSM\|aniqlik\|_sc_acc\|avg_c\|avg_t"` va qo'shimcha qidiruvlar
(`ishonch`, `ball`, `_stat_card(`, `%"`) orqali `kkt_v20_soz_tartibi.py`da
ko'rsatiladigan **BARCHA** foiz/ball ko'rsatkichlari:

| № | GUI'da qayerda ko'rinadi | Manba (fayl:qator) | Qanday hisoblanadi | Ground truth bilan tekshirilganmi? | Aslida nimani o'lchaydi |
|---|---|---|---|---|---|
| 1 | Statistika kartochkasi **"O'rtacha aniqlik"** (3-ustun, binafsha) | `_build_stats_cards` (3294), hisoblash `_translate` (3342), chiqarish (3347) | `avg_c = (Σ a["conf"] / soʻzlar_soni) * 100` — gapdagi har bir soʻzning `conf` maydoni oʻrtachasi | **YO'Q** | Soʻz qaysi **kod yoʻlidan** oʻtganini (toʻgʻridan-toʻgʻri lugʻat hit / affikssiz / affiksli) — tarjima **mazmunan toʻgʻriligini EMAS** |
| 2 | Har bir soʻz qatorida inline **"Aniqlik: X%"** (ingliz parsing paneli) | `_draw_en_parse`, 3382–3383 | Xuddi shu `a["conf"]*100`, lekin soʻz darajasida (oʻrtacha emas) | **YO'Q** | Xuddi #1 bilan bir xil — yagona soʻz uchun |
| 3 | `conf` manbasi — **toʻgʻridan-toʻgʻri lugʻat hit** | `_smart_parse_core`, 2978 | Qattiq kodlangan konstanta `conf=0.999` | — (konstanta, oʻlchov emas) | "soʻz `UB_en_w` bazasida ID orqali topildi" belgisi |
| 4 | `conf` manbasi — **egalik `'s`** | `_smart_parse_core`, 2994 | Qattiq kodlangan konstanta `conf=0.970` | — | "soʻz `'s` maxsus holati orqali ishlandi" belgisi |
| 5 | `conf` manbasi — **umumiy affiksli/affiksiz soʻz** | `_smart_parse_core`, 3135 | Qattiq kodlangan konstanta: `0.93` (affikssiz yoki faqat suffiksli) / `0.895` (prefiks ham bor) | — | "soʻz 7-19-qadam morfologik zanjiridan oʻtdi" belgisi |
| 6 | `conf` manbasi — **topilmadi** | `_smart_parse_core`, 2952 (`empty` lugʻat) | Qattiq kodlangan konstanta `conf=0.0` | — | "soʻz bazada umuman topilmadi" belgisi |
| 7 | Statistika kartochkasi **"Jami(V2+V3)"** (4-ustun, toq-sariq) | `_build_stats_cards` (3295), hisoblash (3344), chiqarish (3348) | `avg_t = Σ kkt_en(a)["total"] / topilgan_soʻzlar_soni` — formal model vaznlarining (V2+V3) oʻrtachasi | Yorlig'i toʻgʻri — "aniqlik" deb da'vo qilinmaydi, xom vazn yigʻindisi sifatida koʻrsatiladi | Formal model vazni (KKT tenglamasi V2+V3), tarjima sifatiga bevosita aloqasi yoʻq — lekin **yorligʻi chalkashtirmaydi**, shu sabab bu qator tuzatish talab qilmaydi |
| 8 | Chiquvchi (oʻzbek) panelidagi **"SSM = X.XXXXX (daraja)"** va rang belgisi (yashil/toʻq sariq/qizil) | `ssm_score()` 2688–2744, `evaluate_and_refine_ssm()` 2846–2921, chiqarish `_draw_uz_parse` 3438–3448 | M. Xakimov (IJIRSS 8(6) 2025) formula (1): `SSM=(Mor+Sq+Mav+Qb+Muk)/Count − Penalty` — EVIX ning morfologik-formal model satri (`MM`) tuzilishidan hisoblanadi | **QISMAN.** Kod izohi (2692–2696-qator): formula **maqolaning oʻzidagi jadval qiymatlariga mos ekani** tekshirilgan (ya'ni kod formulani toʻgʻri implementatsiya qilgani tasdiqlangan). LEKIN: formulaning **oʻzi** haqiqiy tarjima toʻgʻriligi bilan qanchalik bogʻliqligi (ya'ni yuqori SSM = toʻgʻri tarjima demak-mi) **hech qayerda inson bahosi/gold-set bilan tekshirilmagan** | EVIX soʻzining **morfologik-strukturaviy toʻliqligi** (ildiz+qoʻshimcha segmentlari formulaga qanchalik "toʻgʻri" mos kelishi) — **leksik/semantik toʻgʻrilik EMAS**. Taqrizning 35–41-bandi aynan shu SSM metrikasini tanqid qiladi (band matni bu repoda yoʻq, faqat raqami addendumda keltirilgan — Ziyoviddin qoʻlda tekshirsin) |
| 9 | `quality_flag` (yashil/toʻq sariq/qizil) — SSM asosida MDB_uz_w orqali qayta izlash zanjirini ishga tushiradimi | `evaluate_and_refine_ssm()`, 2846–2921 | SSM ≥ 0.80 boʻlsa "green", aks holda MDB_uz_w/QM_uz_w orqali qayta urinish, muvaffaqiyatli boʻlsa "orange", aks holda "red" | Xuddi #8 bilan bir xil muammo — SSM ustiga qurilgan | Tarjimaning oxirgi natijasi qaysi "ishonch darajasi"da qabul qilinganini koʻrsatadi, lekin bu ham SSM'ning oʻzi kabi tekshirilmagan zanjirga tayanadi |

**Xulosa (0.1):** GUI'da foiz/ball koʻrinishidagi **3 ta mustaqil mexanizm** bor —
(a) `conf` (qattiq kodlangan konstanta, #1–6), (b) `avg_t`/Jami(V2+V3) (formal
model vazni, yorligʻi toʻgʻri, #7), (c) SSM (hisoblanadigan formula, #8–9).
Faqat (a) — yagona **"aniqlik"** deb nomlangan koʻrsatkich — va u **hech qanday
ma'noda tarjima toʻgʻriligini oʻlchamaydi**.

---

## 0.1-qo'shimcha — Table 4.3 (97,7%) va "O'rtacha aniqlik" kartochkasi orasidagi bogʻliqlik

`reports/ch2_leakage_check.md` (3.3-boʻlim) allaqachon aniqlagan: dissertatsiyaning
**yagona raqamli aniqlik jadvali** — 4.3-jadval (docx idx 1287–1288, IV bob) —
Google Translate (46%), DeepL (72%), Yandex (80%) va "Ingliz tilidan oʻzbek
tiliga rasmiy modellar asosida kompyuter tarjima moduli" (**97,7%**) ni "280 ta
soʻz" ustida solishtiradi, lekin **280 ta soʻzning matni docx'ning hech
qayerida yoʻq**.

Bu safar **jadval atrofidagi rasmlarni** (4.10/4.11/4.12-rasm, `python-docx`
matn sifatida oʻqiy olmaydigan skrinshotlar) docx'dan ajratib chiqarib
koʻrib chiqdim (`data/desertatsiya.docx` → `word/media/image60.png`,
`image61.png`, `image62.png`, `image63.png` — quyidagi "Reproduksiya"
boʻlimida toʻliq buyruq berilgan):

### TASDIQLANGAN (rasm bilan bevosita isbotlangan)

- **4.10-rasm** ("Kompyuter tarjima modul natijasi", docx idx 1279,
  `image60.png`) — bu **aynan** yuqoridagi jadval #1 dagi GUI kartochkasining
  skrinshoti: soʻz **"books" → "kitoblar"**, kartochkada **"93.0% O'rtacha
  aniqlik"** va soʻz qatorida **"Aniqlik: 93.0%"** koʻrsatilgan. Bu raqam
  **bit-aniq** mos keladi: `round(0.93*100,1) = 93.0` — yaʼni koddagi
  umumiy-affiksli-soʻz konstantasi (3135-qator, `conf=0.93 if not pfx`),
  chunki "books" faqat "-s" suffiksi bilan (prefikssiz) topilgan. **Bu —
  dissertatsiyaning IV bobidagi dastur natijasini koʻrsatuvchi rasmiy
  skrinshot ANIQ shu qattiq-kodlangan `conf` koʻrsatkichini "aniqlik" deb
  koʻrsatishini bevosita isbotlaydi.**
- **4.11-rasm** ("Ingliz tilidan oʻzbek tiliga kompyuter tarjima moduli",
  docx idx 1282, `image61.png`) — yana shu kartochka: "from our book" → 3
  soʻz, hammasi toʻgʻridan-toʻgʻri lugʻat hit (conf=0.999 har biri) →
  **"99.9% O'rtacha aniqlik"**. Bu ham konstantalarning oʻrtachasi, tarjima
  tekshiruvi emas (va "from our book"→"kitobimizdan" tarjimasining oʻzi ham
  bahsli — lekin bu alohida masala, bu auditning doirasidan tashqarida).
- **4.12-rasm** ("Google va Yandex tarjimondagi natija", docx idx 1284,
  `image62.png`+`image63.png`) — Google: **"our books" → "bizning
  kitoblarimiz"**; Yandex: **"our book" → "bizning kitobimiz"** (diqqat:
  ikkalasi bir xil soʻz emas — biri "books" biri "book"). Bu — **bitta-
  ikkita soʻz birikmasining** tasodifiy skrinshoti, "280 ta soʻz"lik
  tizimli test EMAS. Bunday sinov jarayonining (280 ta soʻz roʻyxati,
  Google/DeepL/Yandex natijalari, ularni "toʻgʻri/notoʻgʻri" deb hisoblash
  mezoni) docx ichida **hech qanday izi yoʻq** — na matnda, na rasmda.

### Kod tomonidan mustaqil tasdiq

`grep -rn "Google\|DeepL\|Yandex\|280" --include="*.py" .` — bu repoda
Google/DeepL/Yandex bilan solishtiruvchi yoki 280 ta soʻzlik test toʻplamini
ishlatuvchi **hech qanday kod yoʻq**. Bundan tashqari, butun
`kkt_v20_soz_tartibi.py` faylida foiz koʻrinishida chiqadigan **yagona**
hisoblash — yuqoridagi 0.1-jadval #1/#2 (`conf`ning oʻrtachasi). Boshqacha
aytganda: **97,7% raqamini "haqiqiy solishtiruv orqali" ishlab chiqaradigan
birorta kod yoʻli repoda mavjud emas** — bunday solishtiruv yozilmagan.

### YANGILANDI — endi TASDIQLANGAN (ILOVA/appendix rasmlari topilgandan keyin)

Foydalanuvchi so'rovi bilan ("yana shunga o'xshash skrinshot bormi —
hammasini toping") dissertatsiyaning **BARCHA** rasmlarini (67 ta embedded
image, butun hujjat boʻyicha) tekshirdim. Natijada dissertatsiyaning eng
oxirida, **"ILOVA"** (Appendix) boʻlimida (docx idx 1439–1442, "IV bob
boʻyicha xulosa"dan keyin, adabiyotlar roʻyxatidan oldin) **4 ta yangi
skrinshot** topildi — bittasi 4-ustunli jadval ichida joylashgan
(`image64.png`, `image65.png`, `image66.png`, `image67.png`). Bularning
hammasi **bitta umumiy inglizcha ibora roʻyxatini** (kamida "1.from our
books" dan "100 of your results"gacha — 100 ta band koʻrinadi, ehtimol
jami 280 ta) toʻrtta turli tizimda tarjima qilingan holda koʻrsatadi:

- `image64.png` — **Google Translate**, roʻyxat 76–100 bandlari (batch).
- `image65.png` — **Yandex Translate**, roʻyxat 1–14 bandlari (batch,
  "1.from our books" bilan boshlanadi — bu 4.12-rasmdagi "our books"
  misolining aynan shu katta roʻyxatdan olinganini koʻrsatadi).
- `image66.png` — **DeepL**, roʻyxat 93–100 (kirish) / 61–68 (chiqish)
  bandlari.
- **`image67.png` — bu repodagi KKT GUI**, xuddi shu roʻyxatning boshini
  ("1.from our books / 2. from your books") kiritilgan holda koʻrsatadi,
  va statistika kartochkalarida:

  > **So'zlar soni: 280** · Affiks/Prefiks: 90 · **O'rtacha aniqlik: 97.7%**
  > · Jami(V2+V3): 0.5968

**Bu — bit-aniq, toʻgʻridan-toʻgʻri dalil.** "280 So'zlar soni" va "97.7%
O'rtacha aniqlik" — ikkalasi ham dissertatsiyaning 4.3-jadvalidagi qatorga
(**"280 ta", "97,7%"**) **aynan mos keladi**. Bu endi taxmin emas:
**dissertatsiyaning 4.3-jadvalidagi "97,7%" raqami — ILOVAdagi shu
skrinshotdan (yoki uni hosil qilgan xuddi shu GUI ishga tushirishdan)
toʻgʻridan-toʻgʻri olingan, va bu raqam — 0.1-jadval #1'da tasvirlangan
`avg_c` (qattiq kodlangan `conf` konstantalarining oʻrtachasi) dan boshqa
narsa emas.** Yaʼni Google/DeepL/Yandex ustunlaridagi 46%/72%/80% choʻqi
haqiqiy tarjima-toʻgʻriligini bildirishi mumkin boʻlsa-da (bu alohida
tekshirilmagan — Google/Yandex/DeepL natijalarini "toʻgʻri/notoʻgʻri" deb
hisoblash mezoni ham docx'da yoʻq), **"97,7%" ustuni tizimning tarjima
toʻgʻriligini emas — parserning konstanta-asoslangan ishonch belgisini
oʻrtachalab koʻrsatadi.** Bu — toʻrtta tizim solishtirilayotgandek koʻrinsa
ham, aslida **oʻlchov birligi bir xil emas** (uchtasi = haqiqiy tarjima
sifati boʻyicha inson bahosi, bittasi = kod-yoʻli belgisi).

**Muhim tafsilot:** Bu 100+ bandli roʻyxat — endi topilgan, lekin uning
**toʻliq matni** (barcha 280 ta band) hali docx'da yoʻq, faqat rasmlarda
qisman koʻrinadigan qismlar (76–100, 1–14, 93–100/61–68) bor. Demak,
**280 ta soʻzning toʻliq roʻyxati hamon qayta tiklanmagan** — bu CH2/1500-
soʻzlik lugʻat bilan soʻz darajasidagi aylanma-tekshiruv (leakage) savolini
(3.3-boʻlim, `ch2_leakage_check.md`) hali ham OCHIQ qoldiradi. Agar
Ziyoviddin xohlasa, qolgan rasm qismlaridan (agar boshqa joyda saqlangan
boʻlsa) yoki original tajriba loglaridan bu roʻyxatni toʻliq tiklash
mumkin — lekin bu Claude vazifasi emas (ma'lumot toʻqilmasligi kerak).

---

## 0.1-qo'shimcha #2 — Dissertatsiyadagi BARCHA skrinshot-asosli rasmlar (to'liq ro'yxat)

Foydalanuvchi so'rovi: "4.10/4.11 dan tashqari yana shunga o'xshash rasm
bormi — hammasini toping, faqat shu ikkitasi bilan cheklanmang". Butun
`data/desertatsiya.docx`dagi **67 ta embedded image**ning har biri (yoki
har bir aniq turkumdan namuna) koʻrib chiqildi — `python-docx` bilan har
bir rasmning docx ichidagi joylashuvi (bob, paragraf idx, yonidagi "N.N-
rasm" sarlavhasi) aniqlandi, so'ng shubhali/nomaʼlum turkumlar (jami 24 ta
rasm: III bobdan 4 tasi namuna sifatida + IV bobning barcha 18 tasi + ILOVA
2 ta) bevosita ochib koʻrildi.

### A) Dastur/veb-sayt natijasining jonli skrinshoti (TASDIQLANGAN — hammasi)

| № | Rasm/joylashuv | Dastur | Kontent (kiritilgan → natija) | Aloqador foiz/raqam |
|---|---|---|---|---|
| 1 | 4.10-rasm (2-marta ishlatilgan raqam), IV bob, idx 1279, `image60.png` | **KKT GUI (bu repo)** | "books" → "kitoblar" | **93.0% O'rtacha aniqlik** = `conf=0.93` (3135-qator) |
| 2 | 4.11-rasm, IV bob, idx 1282, `image61.png` | **KKT GUI** | "from our book" → "kitobimizdan" | **99.9%** = `conf=0.999`ning oʻrtachasi |
| 3 | 4.12-rasm (chap qism), IV bob, idx 1284, `image62.png` | **Google Translate** | "our books" → "bizning kitoblarimiz" | raqam yoʻq, bitta soʻz birikmasi |
| 4 | 4.12-rasm (oʻng qism), IV bob, idx 1284, `image63.png` | **Yandex Translate** | "our book" → "bizning kitobimiz" | raqam yoʻq |
| 5 | ILOVA, "4.10-rasm" (3-marta ishlatilgan raqam — xato/dublikat), idx 1441–1442, `image64.png` | **Google Translate** | 100-band roʻyxat, 76–100 koʻrinadi | raqam yoʻq (faqat ro'yxat) |
| 6 | ILOVA, xuddi shu jadval, `image65.png` | **Yandex Translate** | xuddi shu roʻyxat, 1–14 koʻrinadi | raqam yoʻq |
| 7 | ILOVA, xuddi shu jadval, `image66.png` | **DeepL** | xuddi shu roʻyxat, 93–100/61–68 koʻrinadi | raqam yoʻq |
| 8 | ILOVA, xuddi shu jadval, `image67.png` | **KKT GUI** | roʻyxat boshi kiritilgan | **"280 So'zlar soni / 90 Affiks-Prefiks / 97.7% O'rtacha aniqlik / 0.5968 Jami(V2+V3)"** — 4.3-jadval bilan bit-aniq mos (yuqoridagi boʻlimga qarang) |

**Jami: 8 ta skrinshot, 5 ta joylashuv (4.10 ×2 marta raqamlangan, 4.11,
4.12, ILOVA jadvali)** — hammasi yuqorida hisobga olindi, boshqa hech
qanday dastur-natija skrinshoti dissertatsiyada topilmadi.

### B) Diagramma/sxema/statik jadval rasmlari (tekshirildi — bular SKRINSHOT EMAS, shu sabab 0.1 auditiga aloqasi yoʻq)

| Rasm(lar) | Bob | Turkum | Tekshirilgan namuna |
|---|---|---|---|
| 3.1/3.2/3.3-jadval (`image1`–`image49` oralig'idagi ko'plab rasmlar) | III bob | Statik maʼlumot jadvallari (formal model vazn qiymatlari, Word/Excel'dan rasmga aylantirilgan) va SSM ball-diagrammalari (bar chart) | `image1.png` (Formal modellar_ot jadvali), `image40.png` (Formal modellar_fe'l jadvali), `image28.png` (SSM bar-chart, M_1..M_11) — barchasi statik/hisoblangan, jonli dastur natijasi emas |
| 4.1-rasm | IV bob | Qoʻlda tuzilgan qiyosiy infografika (KKT vs AI/NMT/LLM) | `image50.png` — matn/rangli bloklar, raqam yoʻq |
| 4.2-rasm | IV bob | IDEF1X maʼlumotlar bazasi sxemasi (ER-diagramma) | `image51.png` |
| 4.3-rasm | IV bob | Algoritm blok-sxemasi (kod bilan 1:1 mos — MDB_uz_w, "\|farq\|≤0.23", "\|EVX-EVIX\|<0.26" chegaralari kod bilan aynan bir xil) | `image52.png` |
| 4.4-rasm | IV bob | Algoritm blok-sxemasi (parsing, QM_en_w/QM_uz_w) | `image53.png` |
| 4.5-rasm | IV bob | Semantik tahlil quvur (pipeline) chizmasi | `image54.png` |
| 4.6-rasm | IV bob | IDEF0 funksional model diagrammasi | `image55.png` |
| 4.7-rasm | IV bob | Maʼlumotlar oqimi (data-flow) chizmasi | `image56.png` |
| (sarlavhasiz, 4.7-rasm yonidagi jadvalda) | IV bob | Qoʻlda chizilgan misol-oqimi ("From our books" → "Kitob+lar+imiz+dan") | `image57.png` |
| 4.9-rasm | IV bob | UML komponent diagrammasi | `image58.png` |
| 4.10-rasm (1-marta ishlatilgan raqam) | IV bob | Arxitektura diagrammasi ("funksional arxitektura") | `image59.png` — **image60 bilan ADASHTIRMASLIK kerak**: bu ikkalasi ham "4.10-rasm" deb nomlangan, lekin biri diagramma (59), biri skrinshot (60) — dissertatsiyadagi raqamlash xatosi, alohida masala |

**Muhim yon-topilma (auditga aloqasi yoʻq, lekin qayd etildi):** "4.10-rasm"
raqami dissertatsiyada **3 marta** qaytarilgan (idx 1271 — arxitektura
diagrammasi; idx 1279 — GUI skrinshoti; idx 1441 — ILOVA jadvali). Bu —
sof raqamlash/redaktsiya xatosi (formatlash muammosi), ma'no jihatidan
xato emas, lekin professor tekshiruvida chalkashlikka sabab boʻlishi
mumkin — Ziyoviddin xohlasa alohida qayd etish kerak.

---

## 0.2 — GUI yorlig'ini aniqlashtirish

**Bajarildi (2026-09-09, Ziyoviddin tasdigʻidan keyin), alohida commitda.**
Faqat nom/izoh oʻzgardi — hisoblash mantigʻiga (`avg_c`, `conf`
konstantalari) hech narsa tegilmadi:

- Statistika kartochkasi: **"O'rtacha aniqlik"** → **"Parse ishonchi
  (morfologik)"**, ostiga doim koʻrinadigan qisqa izoh qoʻshildi:
  *"Tarjima to'g'riligini EMAS — so'z lug'at/affiks bazasida qanday
  topilganini bildiradi."* (hover-tooltip emas — doim koʻrinadigan matn
  tanlandi, chunki topilma jiddiy va hover osongina eʼtibordan chetda
  qolishi mumkin edi).
- Soʻz darajasidagi inline yozuv: **"Aniqlik: X%"** → **"Parse ishonchi:
  X%"** — bu xuddi shu `conf` qiymatini ikkinchi marta koʻrsatgani uchun,
  bir joyda tuzatib ikkinchisini eskicha qoldirish chalkashtiruvchi
  boʻlar edi (addendumda aniq koʻrsatilmagan, lekin 0.1-jadval #2 xuddi
  shu muammoni belgilagan edi — shu sabab qoʻshib tuzatildi).
- Ikkala matn ham `kkt_v20_soz_tartibi.py`da **modul darajasidagi
  konstanta** sifatida chiqarildi (`ACC_CARD_LABEL`, `ACC_CARD_NOTE`,
  `ACC_INLINE_LABEL`) — CI'da (Ubuntu, displeysiz) haqiqiy Tk oynasi
  ochilmagani uchun test shu konstantalarni va GUI metodlarining manba
  kodini (`inspect.getsource`) tekshiradi, `tk.Tk()` chaqirmaydi.
- Yangi test fayli: `tests/test_gui_labels.py` (7 ta test, jumladan
  `test_conf_constants_unchanged` — bu Faza `conf` qiymatlarini
  oʻzgartirmaganini alohida tasdiqlaydi). Toʻliq suite: **174 passed, 6
  xfailed** (oldin 148+6xfail edi — farq shu 7 ta yangi test + bu
  sessiyadan oldingi boshqa Faza 2 ishlaridan).

---

## 0.3 — CLLT / LRE / CyS qoʻlyozmalarida shu chalkashuvni qidirish

Repo va loyiha papkasida `.docx`/`.tex` maqola fayli yoʻq. Addendum
koʻrsatmasiga koʻra ("agar mahalliy diskda mavjud boʻlsa — tekshir, aks
holda oʻzing izlama") **~/Desktop, ~/Documents, ~/Downloads** papkalarini
nom boʻyicha (`*CLLT*`, `*LRE*`, `*CyS*`) qidirdim — bu uchtasi ham
**topildi**, koʻplab versiya/nusxa bilan `~/Downloads`da. Har biri uchun
eng soʻnggi versiyani (fayl sanasi boʻyicha) matnga aylantirib
(`python-docx` / `pdfplumber`), quyidagi kalit soʻzlarni qidirdim:
`accuracy`, `confidence`, `SSM`, `97.7`/`97,7`.

**MUHIM — muallif eslatmasi:** Bu uchala qoʻlyozmaning ham muallifi
**Ziyoviddin Sirojiddinov** (email: `ziyoviddin.sirojiddinov@gmail.com` /
`ziyo07070@gmail.com` — bu sessiyaning `userEmail`si bilan bir xil),
hammuallif **Muftakh Khakimov** (`kkt_v20_soz_tartibi.py`dagi SSM formula
va KKT formalizmining muallifi). Bu — addendum matnidagi "Vazira" bilan
qanday bogʻliqligi menga noma'lum bir fakt; men bu haqda taxmin
qilmayman, faqat qayd etaman — **Ziyoviddin bu uchta maqola bilan
Vazira dissertatsiyasi orasidagi aloqani (bir xil loyiha ustida ishlaydimi,
alohida tadqiqotmi) aniqlashtirsin.**

### Har bir qoʻlyozma boʻyicha topilma

| Qoʻlyozma (tekshirilgan versiya) | Mavzu | `conf`/`_sc_acc`ga oʻxshash mexanizm topildimi? | Foydalanilgan "aniqlik" metodologiyasi |
|---|---|---|---|
| **CLLT** — `CLLT.2026.0147_Proof_hi.pdf` (nashr **proof**'i, 2026-08-25; qoʻshimcha tekshirilgan: `CLLT_main_document_anonymous_v3.docx`) | Oʻzbek tili sxema-inventarizatsiyasi (Zipf/Heaps qonuni, uch daraja: soʻz/guruh/gap) — **tarjima sifatiga umuman aloqasi yoʻq mavzu** | **Yoʻq** | POS-teglashning ishonchliligi — 300 tokenlik tasodifiy tanlanma, 2 mustaqil "annotator" (2 xil LLM), inson tomonidan hakamlik qilingan gold-set bilan solishtirib **80,5% aniqlik (223/277 token)** — haqiqiy solishtiruvga asoslangan |
| **LRE** — `LRE_manuscript_EN (1) (1).docx` (2026-08-13) | Inson bahosi orqali tarjima sifatini baholash (adequacy/fluency, BLEU/chrF bilan solishtirib) | **Yoʻq** | 216 ta element, 2 baholovchi, preregistratsiya qilingan protokol, bootstrap ishonch intervallari, Wilcoxon/Spearman testlari — haqiqiy inson bahosiga asoslangan |
| **CyS** — `CyS_full_with_authors (1) (1).pdf` (2026-07-10; qoʻshimcha: `CyS_blind_review.pdf`) | Soʻz darajasidagi tarjima aniqligi (Oʻzbek→Ingliz yoʻnalishi!) — 5 bosqichli test, held-out korpus | **Yoʻq** | Har bir bosqichda **haqiqiy nisbat** (masalan "631/715 toʻgʻri" — 88,25%), yashirin (held-out) test toʻplami, SHA-256 bilan bazaning oʻzgarmaganini tasdiqlash, "tuning leakage"ni oldini olish protokoli — bu 0.1-jadvaldagi muammodan **butunlay farqli, ancha qattiqroq metodologiya** |

**Muhim ogohlantirish:** CyS/LRE qoʻlyozmalarida tasvirlangan tizim **Oʻzbek→
Ingliz** yoʻnalishida ishlaydi va ~27 000 yozuvli lugʻat, "backtracking"
algoritm, sessiya-ichi vaqtinchalik lugʻat overlay tajribasi kabi bu
repodagi `kkt_v20_soz_tartibi.py` (faqat **Ingliz→Oʻzbek**, ~1500 soʻzlik
lugʻat, README'da hujjatlashtirilgan) bilan **mos kelmaydigan** muhandislik
tafsilotlariga ega. Xulosa: **bu uchta maqolada koddagi `conf`/`_sc_acc`
kabi tekshirilmagan koʻrsatkichning "aniqlik" sifatida ishlatilgani
TOPILMADI** — lekin bu, ehtimol, ular **shu repodagi tizim haqida umuman
emas**, balki bogʻliq-lekin-boshqa (aksincha yoʻnalishdagi, ancha rivojlangan)
tizim haqida yozilgani uchundir. **Bu ikkalasi bir xil kodmi — Claude
aniqlay olmaydi, Ziyoviddin tasdiqlashi kerak.**

---

## Reproduksiya

```bash
# 0.1-jadval — koddagi conf/SSM manzillarini qayta topish:
grep -n "conf\|SSM\|aniqlik\|_sc_acc\|avg_c\|avg_t" kkt_v20_soz_tartibi.py

# 0.1-qoʻshimcha — rasmlarni docx'dan qayta ajratib olish
# (data/desertatsiya.docx repoda yoʻq — .gitignore, shaxsiy fayl):
unzip -o -q data/desertatsiya.docx -d /tmp/docx_dump
# paragraf/rasm indekslarini tekshirish uchun scripts/check_ch2_leakage.py
# dagi load_docx()/_iter_block_items() dan foydalaniladi (idx→rasm xaritasi
# shu hisobotdagi jadvalda toʻliq berilgan; batafsil skript git tarixida
# yoʻq, chunki hech narsa commit qilinmadi — kerak boʻlsa qayta yozib
# berish mumkin).
open /tmp/docx_dump/word/media/image60.png   # 4.10-rasm (KKT GUI, "books")
open /tmp/docx_dump/word/media/image61.png   # 4.11-rasm (KKT GUI, "from our book")
open /tmp/docx_dump/word/media/image62.png   # 4.12-rasm (Google)
open /tmp/docx_dump/word/media/image63.png   # 4.12-rasm (Yandex)
open /tmp/docx_dump/word/media/image64.png   # ILOVA (Google, 100-band roʻyxat)
open /tmp/docx_dump/word/media/image65.png   # ILOVA (Yandex, 100-band roʻyxat)
open /tmp/docx_dump/word/media/image66.png   # ILOVA (DeepL, 100-band roʻyxat)
open /tmp/docx_dump/word/media/image67.png   # ILOVA (KKT GUI — "280/97.7%" manbasi)

# 0.3 — qoʻlyozmalarni qidirish (mahalliy disk, shaxsiy papkalar):
find ~/Desktop ~/Documents ~/Downloads -maxdepth 4 \
  \( -iname "*CLLT*" -o -iname "*LRE*" -o -iname "*CyS*" \)
```

---

## Nima o'zgartirildi va nima o'zgartirilmadi

- **0.2 doirasida oʻzgardi (Ziyoviddin tasdigʻidan keyin, alohida
  commitda):** faqat ikkita GUI matn-yorligʻi (`ACC_CARD_LABEL`,
  `ACC_CARD_NOTE`, `ACC_INLINE_LABEL`) va `_stat_card()`ga izoh chizish
  imkoniyati (`note=` parametri). Batafsil — yuqoridagi "0.2" boʻlimida.
- **O'zgarmadi:** `conf` konstantalari (0.999/0.970/0.93/0.895/0.0),
  `avg_c`/`avg_t` hisoblash mantigʻi, `ssm_score()`/
  `evaluate_and_refine_ssm()` — hammasi bexatar qoldi (Qoida: vaznni
  oʻzgartirma, natijaga qarab kod tuzatma). `test_conf_constants_unchanged`
  buni avtomatik tasdiqlaydi.
- 0.1/0.1-qoʻshimcha (audit + rasm tahlili) va 0.3 (uch maqola) doirasida
  hech narsa oʻzgartirilmadi — faqat hujjatlashtirildi.

## Keyingi qadam

**2026-09-09: Ziyoviddin tasdiqladi.** 0.2 endi bajarilmoqda (alohida
commit, quyidagi "Faza 2.0.2" boʻlimiga/commitiga qarang). Qolgan qadamlar:
1. ~~0.2 — GUI label + tooltip oʻzgartirish~~ — bajarilmoqda.
2. Ustuvorlik 1 (CH2_EVX_EXAMPLES yakunlash) va Ustuvorlik 2 (`-er`
   boʻshligʻi) — bular Priority 0'ga bogʻliq emas, parallel boshlanishi
   mumkin, agar Ziyoviddin xohlasa.
3. Vazira/CLLT-LRE-CyS aloqasi boʻyicha aniqlik — professor/Vazira bilan
   muhokama qilinishi kerak (Claude hal qila olmaydi).
4. **4.3-jadval / ILOVA topilmasi** — bu Ustuvorlik 0'dan tashqarida
   (addendum rejasida yoʻq edi, foydalanuvchi so'rovi bilan qo'shildi),
   lekin eng jiddiy topilma: 97,7% raqami endi bevosita GUI'ning
   `conf`-asoslangan kartochkasiga bogʻlangan holda TASDIQLANGAN.
   Bu — dissertatsiya himoyasiga (yoki taqrizga javobga) qadar professor
   bilan **shoshilinch** muhokama qilinishi tavsiya etiladi.
