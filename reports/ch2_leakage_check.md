# CH2_EVX_EXAMPLES — dissertatsiya docx bilan solishtiruv va III/IV bob leakage tekshiruvi

**Generatsiya vaqti:** 2026-09-09T05:41:16+00:00Z
**Manba:** `data/desertatsiya.docx` (foydalanuvchi tomonidan 2026-09-08 da qo'shildi) va `kkt_v20_soz_tartibi.py:CH2_EVX_EXAMPLES` (52 ta yozuv)
**Buyruq:** `python scripts/check_ch2_leakage.py`

Bu hisobot ikkita ALOHIDA topshiriqni bittada bajaradi (foydalanuvchi so'rovi, 2026-09-08):
1. CH2_EVX_EXAMPLES ro'yxatini II bobdagi haqiqiy paragraflar bilan solishtirish (mos kelmasliklar jadvali).
2. CH2_EVX_EXAMPLES headword'larining III/IV bobda uchrashini (leakage xavfi) tekshirish.

## 0. `CH2_EVX_EXAMPLES` docstring da'vosi: "52 ta" — tekshirildi

`len(CH2_EVX_EXAMPLES) = 52`. Docstring "52 ta ingliz-o'zbek EVXs/EVIXs namuna so'z" deb da'vo qiladi — bu **TASDIQLANDI** (52 == 52). Ilgari suhbatda aytilgan "~44 ta" taxmini **NOTO'G'RI** edi. Noyob inglizcha bosh so'zlar soni: **51** (`gayer` ikki marta uchraydi — qiyosiy "sho'xroq" va orttirma "eng sho'x" uchun ikkita alohida yozuv, ikkalasi ham `en='gayer'`).

**LEKIN — ro'yxat TO'LIQ EMAS:** II bobning o'zida `CH2_EVX_EXAMPLES`ga umuman kiritilmagan qo'shimcha "Ingliz tilida EVX ... / Oʻzbek tilida EVIX ..." namunalar ham bor — pastda (20 ta, 3-bo'lim) ro'yxat qilingan (masalan `to be`, `to have`, `become`, `need`, `large->larger`, `big->bigger/biggest`, `good->better->best`, `easily`, `more clearly`, olmosh jadvali "I"->"men" va h.k.). Demak "52 ta" — II bobning HAMMASI emas, balki dastur muallifi TANLAB ko'chirgan qism.

## 1. Paragraf darajasidagi solishtiruv — natija

- Jami CH2_EVX_EXAMPLES yozuvi: **52**
- Docx'da avtomatik topilgan (paragraf juftligi aniqlandi): **52**
- Docx'da avtomatik topilMAdi (qo'lda tekshirish kerak): **0**
- Topilganlardan MOS KELMAGAN (en va/yoki uz farq qiladi): **5**

### Mos kelmasliklar — to'liq jadval (xom docx dalili bilan)

| CH2 en | CH2 uz | Docx en (paragraf, idx) | Docx uz (paragraf, idx) | Docx en (jadval katakchasi) | Verdikt |
|---|---|---|---|---|---|
| capabilityies | imkonyatlar | capabilities (#364) | imkonyatlar (#369) | — | EN FARQ QILADI |
| leafes | barglar | leaves (#383) | barglar (#388) | leafes | EN FARQ QILADI |
| schoolboys | Bojxonalar | schoolboys (#404) | maktabbolalar (#409) | — | UZ FARQ QILADI |
| more comfortable | eng qulay | more comfortable (#754) | qulayroq (#759) | morecomfortable | UZ FARQ QILADI |
| less interesting | so'z kamroq qiziqarli | less interesting (#775) | kamroq qiziqarli (#777) | — | UZ FARQ QILADI |

**"Docx en (jadval katakchasi)" ustuni haqida:** ba'zi yozuvlarda "Ingliz tilida EVX <so'z>" paragrafidan keyin kichik bir o'zak+affiks jadvali keladi (masalan `leaf | + es`). Bu katakchalarni to'g'ridan-to'g'ri qo'shib o'qish paragrafdagi TO'G'RI yozilgan shakldan farq qilishi mumkin (masalan jadval "leaf"+"es"="leafes" beradi, paragrafning o'zida esa to'g'ri "leaves" yozilgan). Bu ustun FAQAT qo'shimcha dalil — qaysi manba "to'g'ri" ekanini bu skript HAL QILMAYDI.

## 2. II bobdagi, lekin CH2_EVX_EXAMPLES ga KIRITILMAGAN namunalar

Docx'dan avtomatik ajratib olingan 72 ta "Ingliz tilida EVX" belgisidan 20 tasi CH2_EVX_EXAMPLES dagi hech qaysi yozuv bilan bog'lanmadi — demak ular II bobda BOR, lekin dastur muallifi CH2_EVX_EXAMPLES ga KIRITMAGAN:

| # (docx paragraf idx) | Ingliz (paragraf) | O'zbek (paragraf) |
|---|---|---|
| 310 | variables | oʻzgaruvchilar |
| 492 | to be | boʻlmoq |
| 515 | to have | bor boʻlmoq |
| 545 | become | boʻlmoq |
| 559 | Could | qila  olardi |
| 595 | need | kerak |
| 621 | listen to me | meni tinglang |
| 627 | understand | tushunmoq |
| 632 | will return | qaytadi |
| 637 | worked | ishladi |
| 642 | simplified | soddalashtirildi |
| 666 | variables | rasmiy |
| 700 | larger | kattaroq |
| 709 | bigger | kattaroq |
| 716 | biggest | kattaroq |
| 761 | most comfortable | eng qulay |
| 770 | best | eng yaxshi |
| 800 | easily | osonlik bilan |
| 815 | more clearly | aniqroq |
| 932 | I | men |

Diqqat: bu jadvaldagi ba'zi qatorlar dissertatsiyaning O'ZIDAGI (Claude yoki avvalgi transkripsiya emas) ichki nomuvofiqlikni aks ettirishi mumkin — masalan #666 qatorida "Ingliz tilida EVX so'z: **variables**" deb yozilgan, lekin undan keyingi o'zak+affiks jadvali `form|+al` va o'zbekcha tarjimasi "rasmiy" (=formal) — ya'ni bu qatordagi haqiqiy misol "formal" bo'lishi kerak edi, "variables" so'zi avvalgi bo'limdan (#310) qolib ketgan nusxa xatosi ko'rinadi (docx #664-673 qarang). Bu skript bunday holatlarni ANIQLAMAYDI/TUZATMAYDI — faqat xom matnni ko'rsatadi.

## 3. Headword darajasidagi "aylanma"/leakage tekshiruvi — III va IV bob

### 3.0 Aniq metodika — qanday qidiruv ishlatildi (foydalanuvchi so'rovi, 2026-09-09)

**Bu — oddiy matnli (substring) qidiruv, professor darajasidagi qo'lda-o'qib-chiqish EMAS.** Aniq algoritm:

1. CH2_EVX_EXAMPLES dagi 51 ta NOYOB inglizcha bosh so'z/ibora (`ex["en"]` maydoni, kichik harfga o'tkazilgan) ro'yxati olinadi.
2. Har bir headword uchun ALOHIDA regex naqshi tuziladi: `(?<![A-Za-z'’])<headword>(?![A-Za-z'’])` — ya'ni headworddan OLDIN va KEYIN lotin harfi yoki apostrof (oddiy `'` yoki tipografik `’`) kelmasligi shart. Bu — Python'ning standart `\b` chegarasidan ATAYLAB farqli: `\b` ko'p so'zli iboralar ("a network", "more comfortable") ichidagi bo'shliqni to'g'ri ushlamasligi, apostrofni esa so'z ichidagi belgi deb hisoblamasligi mumkin edi.
3. `re.search(naqsh, matn, re.IGNORECASE)` — bobning III va IV oralig'idagi (`find_chapter_bounds()` bilan aniqlangan blok-indekslar) **HAR BIR paragraf matni** va **HAR BIR jadval katak matni** ustida, birma-bir, alohida chaqiriladi.
4. Moslik topilsa, o'sha paragraf/katak matnining o'zida (BOSHQA hech qanday tashqi ma'lumot qo'shilmasdan) "aniqlik"/"foiz"/"%"/"misol"/"natija"/"test" so'zlaridan biri ham bor-yo'qligi tekshiriladi (`context_flag`) — bu ham oddiy substring tekshiruvi, na jadval sarlavhasi, na yaqin-atrofdagi paragraflar hisobga olinadi.
5. Natija: HAR BIR headword uchun 0 yoki undan ko'p "hit". "Topilmadi" xulosasi — shu headword uchun yuqoridagi regex III/IV bobning HECH bir paragraf/katagida `re.search` orqali moslik TOPMAGANI degani, boshqa hech narsa emas.

**Bu — funksiya darajasida qayta ishlatiladigan kod** (`scripts/check_ch2_leakage.py:search_leakage()`/`summarize_leakage_by_headword()`), demak boshqa birov xuddi shu skriptni qayta ishga tushirib, xuddi shu natijani oladi (git tarixi/versiya farqi bo'lmasa).

### 3.1 Har bir headword uchun natija (51 ta, HAMMASI — hit=0 bo'lganlar ham)

| Headword | Qidiruv naqshi | III bobda | IV bobda | Jami | Birinchi moslik (idx, bob) |
|---|---|---|---|---|---|
| hundred and twenty first | `(?<![A-Za-z'’])hundred\ and\ twenty\ first(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| less interesting | `(?<![A-Za-z'’])less\ interesting(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| more comfortable | `(?<![A-Za-z'’])more\ comfortable(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| high dimensional | `(?<![A-Za-z'’])high\ dimensional(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| capabilityies | `(?<![A-Za-z'’])capabilityies(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| chapter five | `(?<![A-Za-z'’])chapter\ five(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| four million | `(?<![A-Za-z'’])four\ million(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| the progress | `(?<![A-Za-z'’])the\ progress(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| the germanys | `(?<![A-Za-z'’])the\ germanys(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| customhouses | `(?<![A-Za-z'’])customhouses(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| information | `(?<![A-Za-z'’])information(?![A-Za-z'’])` | 0 | 5 | 5 | #1337 (IV) |
| one hundred | `(?<![A-Za-z'’])one\ hundred(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| eighty five | `(?<![A-Za-z'’])eighty\ five(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| an example | `(?<![A-Za-z'’])an\ example(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| schoolboys | `(?<![A-Za-z'’])schoolboys(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| cleverest | `(?<![A-Za-z'’])cleverest(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| processes | `(?<![A-Za-z'’])processes(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| student's | `(?<![A-Za-z'’])student's(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| hundredth | `(?<![A-Za-z'’])hundredth(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| to follow | `(?<![A-Za-z'’])to\ follow(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| a network | `(?<![A-Za-z'’])a\ network(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| contents | `(?<![A-Za-z'’])contents(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| ought to | `(?<![A-Za-z'’])ought\ to(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| cleverer | `(?<![A-Za-z'’])cleverer(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| reading | `(?<![A-Za-z'’])reading(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| fastest | `(?<![A-Za-z'’])fastest(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| fifteen | `(?<![A-Za-z'’])fifteen(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| busiest | `(?<![A-Za-z'’])busiest(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| quietly | `(?<![A-Za-z'’])quietly(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| faster | `(?<![A-Za-z'’])faster(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| busier | `(?<![A-Za-z'’])busier(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| leafes | `(?<![A-Za-z'’])leafes(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| delays | `(?<![A-Za-z'’])delays(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| eighty | `(?<![A-Za-z'’])eighty(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| to ask | `(?<![A-Za-z'’])to\ ask(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| inside | `(?<![A-Za-z'’])inside(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| ought | `(?<![A-Za-z'’])ought(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| might | `(?<![A-Za-z'’])might(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| would | `(?<![A-Za-z'’])would(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| to do | `(?<![A-Za-z'’])to\ do(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| gayer | `(?<![A-Za-z'’])gayer(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| today | `(?<![A-Za-z'’])today(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| sent | `(?<![A-Za-z'’])sent(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| much | `(?<![A-Za-z'’])much(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| will | `(?<![A-Za-z'’])will(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| must | `(?<![A-Za-z'’])must(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| here | `(?<![A-Za-z'’])here(?![A-Za-z'’])` | 0 | 1 | 1 | #1364 (IV) |
| men | `(?<![A-Za-z'’])men(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| one | `(?<![A-Za-z'’])one(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| can | `(?<![A-Za-z'’])can(?![A-Za-z'’])` | 0 | 0 | 0 | — |
| may | `(?<![A-Za-z'’])may(?![A-Za-z'’])` | 0 | 0 | 0 | — |

**49/51** headword uchun jami = 0, ya'ni yuqoridagi regex III/IV bobning hech bir paragraf/jadval-katagida bu so'zni topmadi (5-band metodikaga qarang).

### 3.2 Topilgan holatlar — batafsil (6 ta xom moslik)

- shundan jadval ichida: **0**
- shundan "aniqlik"/"foiz"/"%"/"misol"/"natija"/"test" so'zi bilan bir paragrafda/katakda: **0**

| Bob | Headword | Naqsh | Jadvalda? | Kontekst belgisi? | Docx idx | Matn parchasi |
|---|---|---|---|---|---|---|
| IV | information | `(?<![A-Za-z'’])information(?![A-Za-z'’])` | yo'q | yo'q | 1337 | Jones, Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin. Attention is all you need. In Proceedings of the 31st International Conference on Neural Information Processing Systems (NIPS’17). Curran As |
| IV | information | `(?<![A-Za-z'’])information(?![A-Za-z'’])` | yo'q | yo'q | 1351 | Khakimov M. Kh., Sirojiddinov Z. Sh. Computer algorithmization in multi-language modelled translator technology // Modern problems of applied mathematics and information technologies al-Khwarizmi. – 2 |
| IV | here | `(?<![A-Za-z'’])here(?![A-Za-z'’])` | yo'q | yo'q | 1364 | Rosenfeld R. “Two decades of statistical language modeling: where do we go from here?”, Proceedings of the IEEE. 2000. Vol. 88. No pp. 1270-1278. August. doi: 10.1109/5.880083. Accessed 2024-05-21 |
| IV | information | `(?<![A-Za-z'’])information(?![A-Za-z'’])` | yo'q | yo'q | 1367 | Vaswani A., Shazeer N., Parmar N., Uszkoreit J., Jones L., Gomez A. N., Kaiser L., Polosukhin I. Attention is all you need. Advances in Neural Information Processing Systems (NeurIPS), 2017. 30, 5998  |
| IV | information | `(?<![A-Za-z'’])information(?![A-Za-z'’])` | yo'q | yo'q | 1409 | Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., Polosukhin, I. Attention is all you need. Advances in Neural Information Processing Systems NeurIPS 2017, 30.  |
| IV | information | `(?<![A-Za-z'’])information(?![A-Za-z'’])` | yo'q | yo'q | 1414 | 101. Nazirova E., Usmonova K. Algorithmic strategies for stemming complex word from Uzbek to English in machine translation. In Communications in Computer and Information Science 2024. pp.97-105. Spri |

**Diqqat — bu jadval XULOSA EMAS:** ko'p qisqa inglizcha funksional so'zlar (masalan "will", "can", "one", "here") III/IV bobning umumiy (asosan o'zbek tilidagi) matnida TASODIFAN ham uchrashi mumkin (masalan boshqa inglizcha misol sifatida, yoki umuman aloqasiz kontekstda). Har bir qatorni qo'lda ko'rib chiqish kerak — bu skript faqat HAR BIR uchrashni xom docx manzili bilan ko'rsatadi, "bu aylanma" yoki "bu tasodifiy" degan xulosani Claude chiqarmaydi (professor/Ziyoviddin qarori).

### 3.3 Mustaqil tekshiruv — headword ro'yxatidan qat'i nazar, III/IV bobdagi BARCHA "baholash-shaklidagi" matn

Yuqoridagi 3.1/3.2 — headword'dan boshlab qidiradi ("ichkaridan tashqariga"). Bu bo'lim esa TESKARI yo'nalishda ishlaydi: CH2 so'zlaridan MUSTAQIL ravishda, III/IV bobdagi "aniqlik"/"foiz"/"%"/"misol"/"natija"/"test" so'zlaridan birortasini o'z ichiga olgan **HAR BIR** paragraf va jadval katakni to'liq ro'yxatlaydi — shu orqali o'qiuvchi (professor/Ziyoviddin) bu ro'yxatni QO'LDA ko'rib chiqib, yuqoridagi avtomatik so'z-qidiruvi biror haqiqiy baholash/aniqlik da'vosini "ko'rmay o'tib ketmaganini" MUSTAQIL tekshirishi mumkin (masalan, agar bir jadval CH2 so'zlarini so'zma-so'z yozmasdan, faqat "52 ta misol asosida" kabi umumiy iboralar bilan tasvirlasa, 3.1/3.2 buni topa OLMAYDI — lekin bu ro'yxatda o'sha jadval BOR, o'qib chiqish mumkin).

Jami topilgan blok: **55** (III bobda 15, IV bobda 40)

| Bob | Docx idx | Jadval katagi? | Matn |
|---|---|---|---|
| III | 983 | yo'q | Ushbu tadqiqot ishida KT uchun ishlab chiqilgan rasmiy modellarning raqamli vazn qiymatlarini aniqlash, ingliz tilidan oʻzbek tiliga tarjima qilish jarayonida morfologik tahlil qilish natijasida. Kiruvchi soʻzning tarkib |
| III | 984 | yo'q | Ingliz tilidan oʻzbek tiliga mashina tarjimasida vazn koeffitsientlaridan foydalanish tarjima aniqligini oshirish, lingvistik noaniqliklarni kamaytirish va avtomatik tarjima modulining samaradorligini yaxshilashga xizmat |
| III | 998 | yo'q | Ushbu (3.1) rasmiy model ot soʻz turkumida soʻzlarning koʻplik affiksi bilan kelgan barcha soʻzlar uchun ishlab chiqilgan. Ingliz tilidagi EVX oʻngdan chapga  parsinglaganda soʻzning har bir qismini boʻlaklash orqali aff |
| III | 1017 | yo'q | Yuqorida olingan natijalar tahliliga asoslanib, shuni ta’kidlash mumkinki, ilmiy soʻz va iboralarning  ingliz tilidan oʻzbek tiliga kompyuter tarjima sifatini oshirishda kiruvchi soʻzni chiquvchi soʻzning  morfologik bir |
| III | 1022 | yo'q | Ushbu dissertatsiyaning maqsadi ingliz tilidagi ot, sifat, fe’l, ravish, son va olmosh soʻz turkumlariga oid turli xil qoidalar asosida quriladigan soʻzlarning  modellarini baholashni tavsiflash boʻlib, u inson tarjimasi |
| III | 1024 | ha | Matematik natija |
| III | 1060 | yo'q | Ingliz tilidagi ot va fe’l soʻz turkumlariga oid soʻzlarning rasmiy modellari huddi shu usulda SSM metrikasi bilan hisoblandi va quyidagi 3.6- jadvalda natijalari berildi. |
| III | 1069 | yo'q | Ingliz tilidagi sifat va ravish soʻz turkumlariga oid soʻzlarning rasmiy modellari huddi shu usulda SSM metrikasi bilan hisoblandi va quyidagi 3.7- jadvalda natijalari berildi. |
| III | 1077 | yo'q | Ingliz tilidagi son va olmosh soʻz turkumlariga oid soʻzlarning rasmiy modellari huddi shu usulda SSM metrikasi bilan hisoblandi va yuqoridagi 3.8- jadval va 3.3-rasmda natijalari berildi. |
| III | 1078 | yo'q | Ushbu tadqiqot ishida ingliz tilidagi soʻz turkaumlaridan ot, sifat, fe’l, ravish, son va olmosh soʻz turkumiga oid soʻzlarning rasmiy modellarini, faqat Structural-Semantic Metric (SSM) tuzulmaviy-semantik metrikasi [85 |
| III | 1082 | yo'q | Ingliz tilidagi soʻz turkumlarining rasmiy modellarini ishlab chiqish tabiiy tilni qayta ishlash (Natural Language Processing – NLP) jarayonida KT modulini yaratishda muhim ilmiy-amaliy ahamiyatga ega. Rasmiy model til b |
| III | 1083 | yo'q | Rasmiy modellar ingliz tilidan boshqa tillarga, xususan, oʻzbek tiliga avtomatik tarjima qilish tizimlarining sifatini oshiradi. Soʻz turkumlarining rasmiy tavsifi orqali manba tildagi grammatik birliklarning maqsad tili |
| III | 1087 | yo'q | «BM_en_w» va «BM_uz_w» KTsining nazariy poydevori hisoblanadi. Bu bazalar ingliz va oʻzbek tillaridagi har bir mustaqil soʻz turkumining rasmiy modelini oʻz ichiga oladi. Uning asosiy vazifasi – tabiiy tilning grammatik  |
| III | 1119 | yo'q | Ushbu bobda ingliz va o‘zbek tillaridagi so‘z turkumlarining morfologik hamda semantik xususiyatlarini kompyuter tarjimasi jarayonida avtomatik qayta ishlashga yo‘naltirilgan matematik va formal modellarni shakllantirish |
| III | 1120 | yo'q | Ingliz tilidagi so‘z turkumlariga oid asos so‘zlar va affikslarning lingvistik xususiyatlarini hisobga olgan holda ularning vazn qiymatlarini aniqlash orqali so‘zning morfologik tuzilishini formal ifodalash imkoniyati ya |
| IV | 1126 | yo'q | Mashina tarjimasining dasturiy ta’minoti ayrim tizimlarda oddiy ikki tillik lugʻatli bazalardan tashkil topadi. Masalan: Google neyron mashina tarjima tizimi paradigmasiga asoslanadi [93]. Tabiiy tillarni tarjima qilishd |
| IV | 1127 | yo'q | KKT asosidagi KTda Hakimov M.X. yondashuvi qoidalarga asoslangan mashina tarjima tizimi sifatida tasniflanadi [98]. Ushbu yondashuvning asosiy g‘oyasi shundan iboratki, TT rasmiy grammatik va morfologik qoidalar orqali t |
| IV | 1138 | yo'q | «PSB_en_w» KTsida semantik noaniqlikni bartaraf etishning asosiy mexanizmi hisoblanadi. Koʻp ma’noli soʻzlarni toʻgʻri tarjima qilish uchun tizim soʻz qaysi predmet sohalarga tegishli soʻz ekanligini  aniqlab olishi shar |
| IV | 1145 | yo'q | Ushbu IDEF1X modelida KKT_ID jadvalida KKT belgilarining barchasi saqlanadi va BM_EN_W va BM_UZ_W jadvallari bilan bog’langan. BM_en_w jadvalida ingliz tilidagi har bir soʻz turkumining rasmiy modellarini saqlaydi. Hamda |
| IV | 1149 | yo'q | Ushbu keltirilgan  4.2-rasm IDEF1X  modelida berilgan jadvallarni ixtiyoriy  kengaytrish mumkin. Tadqiqot ishidagi funksianal berilganlar bazasi Primary Key, Foreign Key va ID qo‘llanildi. Natijada qidirish tezligi yuqor |
| IV | 1151 | yo'q | KTsi mazmunining samaradorligi va aniqligi eng avvalo qoʻllanilayotgan algoritmning toʻgʻri qadamlar bilan tuzilganligiga bevosita bogʻliq. KT uchun tuzilgan algoritim bu EVX ma’lum qoidalarga asoslangan holda qayta ishl |
| IV | 1173 | yo'q | Ushbu 4.4-rasmda keltirilgan algoritm ingliz tilidagi soʻz turkumlariga oid soʻzlarning qoidalarga asoslangan avtomatik rasmiy modellash, vaznlash va taqqoslash uchun umumiylashtrilgan morfologik algoritm Algoritmda tabi |
| IV | 1176 | yo'q | Mazkur shartlarning bajarilishi morfologik tahlilning muvaffaqiyatli yakunlanganligini bildiradi hamda keyingi bosqich semantik moslikni aniqlash va morfologik sintez jarayoniga o‘tish uchun asos yaratadi. EVX soʻzni gra |
| IV | 1226 | yo'q | Natijada grammatik jihatdan toʻg‘ri shakllangan oʻzbekcha soʻz (EVIX) hosil qilinadi. |
| IV | 1229 | yo'q | Agar boshqa token boʻlmasa, yakuniy natijani chiqarish bosqichiga oʻtiladi. |
| IV | 1232 | yo'q | Mazkur bosqich tarjima algoritmining yakuniy natijasini ifodalaydi. |
| IV | 1235 | yo'q | Ishlab chiqilgan algoritmlarda ikkita tabiiy tillarning murakkabligini,  so‘z shakli, grammatik tuzilma, sintaktik bog‘lanish va semantik munosabatlarni hisobga olgan holda ishlab chiqildi. Ushbu algoritmda o‘ngdan chapg |
| IV | 1239 | yo'q | Dissertatsiya ishining Ingliz-oʻzbek yoʻnalishidagi kompyuter tarjima dastur modulini yaratish bagʻishlangan toʻrtinchi bob uchinchi boʻlimi, yuqorida keltirilgan ikkinchi va uchinchi boblarda nazariy berilgan qoidalarni |
| IV | 1247 | yo'q | Ushbu 4.6-rasm IDEF0 (Integration Definition for Function Modeling) modelda  har bir modul qaysi ma’lumotlarni qabul qilish va qanday  qoidalar asosida  natijalar chop qilinishini   ifodalovchi  rasmiy model hisoblanadi. |
| IV | 1248 | yo'q | A1 - EVX so‘zni parsinglash blokida tarjima jarayoni foydalanuvchi tomonidan kiritilgan inglizcha so‘zni qabul qilishdan boshlanadi. Dastlab so‘z parsinglash algoritmi yordamida boshqa belgilar va bo‘sh joylardan ajratil |
| IV | 1249 | yo'q | A2 – Funksianal berilganlar bazasidan qidirish blokida parsing natijasida olingan so‘z UB_en_w berilganlar bazasi orqali tekshiriladi. So‘zning identifikatori (ID) aniqlanadi hamda mavjud bo‘lsa uning grammatik tavsifi v |
| IV | 1250 | yo'q | A3 – Morfologik tahlil blokida so‘zning asosiy grammatik tuzilishini aniqlash maqsadida morfologik tahlil bajariladi. Tahlil jarayonida QM_en_w qo‘shimchalar bazasidan foydalanilib, prsinglash algoritmi asosida so‘z o‘ng |
| IV | 1251 | yo'q | A4 – Rasmiy model va vazn qiymati blokIda. Morfologik tahlildan olingan natijalar asosida so‘zning grammatik kategoriyasi aniqlanadi va unga mos rasmiy model tanlanadi. Ushbu bosqichda BM_en_w rasmiy modellar bazasidan f |
| IV | 1253 | yo'q | A6 – O‘zbekcha asos so‘z va qo‘shimchani birlashtrish blokida. Tanlangan o‘zbekcha asos so‘z va unga mos grammatik qo‘shimchalar birlashtiriladi. Ushbu jarayonda BM_uz_w, UB_uz_w hamda QM_uz_w berilganlar bazalaridan foy |
| IV | 1257 | yo'q | Keltirilgan 4.7-rasmda KKT belgilari asosida va funksianal BB hamda rasmiy   modellar bilan KT modulining vazifalarni tanlash orqali ishlash funksional chizmasi quyidagicha chizildi.  Chizmada KT uchun ishlab chiqilgan m |
| IV | 1264 | yo'q | Natijada Kitob + lar + imiz + dan koʻrinishidagi morfemalar yagona "Kitoblarimizdan" soʻz shakliga birlashtiriladi. Bunda oʻzak va qoʻshimchalar oʻzbek tilining rasmiy modeli asosida sintez qilinadi. Rasmiy modelning aso |
| IV | 1269 | yo'q | Quyida berilgan 4.10-rasm ingliz tilidan oʻzbek tiliga kompyuter tarjima dastur modullarining funstional arxitekturasining tuzilish jarayoni aks ettirilgan. Dasturiy modulda foydalanuvchi tomonidan ingliz tilidagi EVX so |
| IV | 1273 | yo'q | Algoritmda KKT bazasi, funksianal bazalar va morfologik qoidalar bazasi axborot manbalari sifatida xizmat qiladi, funksional modullar esa ushbu berilganlardan foydalanib lingvistik tahlil, semantik moslashtirish, rasmiy  |
| IV | 1276 | yo'q | Sun’iy intellekt (SI) transformer modellari asosan statistik ehtimolliklarga tayanaib tarjima qiladi. KKTni va KKTga asoslangan modellarni SIga oʻrgatilganda, SI gapni shunchaki soʻzlar zanjiri emas, balki “$[i,1-h]$” ko |
| IV | 1277 | yo'q | Jahonda aniq va sifatli tarjima qilish vazifasi tabiiy tilga ishlov berishning (NLP) oʻta muhim vazifalaridan biri hisoblanadi. Mashinaviy oʻrganish yordamida aniq va tez amalga oshiriladigan avtomatlashtirilgan tarjima  |
| IV | 1279 | yo'q | 4.10-rasm. Kompyuter tarjima modul natijasi |
| IV | 1280 | yo'q | Ingliz tilida kiruvchi soʻzni oʻngdan chapga parsinglashni _rtl_parse () funksiyasi orqali bajariladi. Bu jarayon quyidagi qadamlardan iborat:  Kiruvchi soʻzning qoʻshimchasini tekshirganida eng uzun qoʻshimchadan qisqa  |
| IV | 1284 | yo'q | 4.12-rasm Google va Yandex tarjimondagi natija |
| IV | 1286 | yo'q | Yuqorida keltirilgan 4.11 va 4.12- rasmlarda KKT asosidagi tarjima moduli va google tarjimon bilan Yandex tarjimonlar asosida “our books” tarjimasi 2 xil natija chop qilingan. Hamda ilovada keltirilgan 1-rasmda ham Googl |
| IV | 1288 | ha | Tarjima foizi |
| IV | 1288 | ha | 46% |
| IV | 1288 | ha | 72% |
| IV | 1288 | ha | 80% |
| IV | 1288 | ha | 97,7% |
| IV | 1290 | yo'q | Shu natijalardan aniqlashimiz mumkin ingliz tilidan o‘zbek tiliga KKT asosida yaratilgan rasmiy modellar orqali KT dastur modulini yaratish tarjima tizimlaridan mazmunan sifatli tarjimaga ega bo‘lishning eng samarali usu |
| IV | 1293 | yo'q | Ushbu bobda ingliz tilidan o‘zbek tiliga so‘z va so‘z birikmalarini avtomatik tarjima qilish jarayonini amalga oshirishga yo‘naltirilgan universal algoritm ishlab chiqildi. Natijada, algoritmda ingliz tilidagi so‘zlarnin |
| IV | 1294 | yo'q | Ishlab chiqilgan universal algoritmning ishlash jarayoni avvalgi boblarda shakllantirilgan morfologik va semantik modellar, so‘z turkumlari hamda affikslarning vazn qiymatlari va semantik o‘xshashlik ko‘rsatkichlaridan f |
| IV | 1296 | yo'q | Tadqiqot doirasida ishlab chiqilgan matematik modellar, morfologik va semantik ma’lumotlar bazasi hamda universal algoritm asosida ingliz-o‘zbek yo‘nalishidagi kompyuter tarjimasi dasturiy moduli ishlab chiqildi. Natijad |
| IV | 1298 | yo'q | Umuman, IV bobda ishlab chiqilgan universal algoritm, funksional va axborot modellar hamda dasturiy modul tadqiqotning nazariy natijalarini amaliy tizimga integratsiya qilish imkonini berdi. Olingan natijalar ingliz-o‘zb |
| IV | 1307 | yo'q | Kompyuter tarjima modulining 8 ta funksional bazalaridan foydalangan holda, avtomatik modellash, vaznlash va taqqoslash uchun tadqiqot doirasidagi yiriklashtirilgan universal algoritm qurildi hamda dasturiy tarjima modul |

**MUHIM — dissertatsiyaning YAKKA-YAGONA raqamli aniqlik jadvali (4.3-jadval, docx idx 1287-1288, IV bob) alohida ko'rib chiqildi, chunki bu — butun hujjatdagi YAGONA joy, u yerda "foiz" bilan bog'liq son (97,7% va h.k.) HAQIQIY natija sifatida keltirilgan (qolgan barcha 54 blok umumiy matn, rasm izohi yoki bibliografiya):**

> **4.3-jadval**
>
> | № | Tarjima tizimlari | So'zlar soni | Tarjima foizi |
> |---|---|---|---|
> | 1 | Google Translate | 280 ta | 46% |
> | 2 | DeepL Translate | 280 ta | 72% |
> | 3 | Yandex Translate | 280 ta | 80% |
> | 4 | Ingliz tilidan o'zbek tiliga rasmiy modellar asosida kompyuter tarjima moduli | 280 ta | 97,7% |

**Bu jadval haqida aniq/tekshirilgan faktlar (talqin emas):** jadval "So'zlar soni: 280 ta" deydi — LEKIN o'sha 280 ta so'zning O'ZI (ro'yxati) na jadvalning o'zida, na uning atrofidagi paragraflarda (docx idx 1284-1290, to'liq o'qildi) berilmagan. Shu sabab: **CH2_EVX_EXAMPLES (52 ta) yoki 1500 so'zlik lug'atning ushbu "280 ta" test to'plami bilan qanday bog'liqligini (mos keladimi, ustma-ust tushadimi, umuman aloqasi yo'qmi) SO'Z DARAJASIDA TEKSHIRISH BU DOCX ICHIDA MUMKIN EMAS** — chunki solishtirish uchun kerakli 280 ta so'zning matni umuman yo'q. Yuqoridagi atrofdagi yagona konkret misol — "our books" (item 1286, ilova/screenshot misoli sifatida keltirilgan, CH2_EVX_EXAMPLES yoki 1500-so'zlik lug'atda YO'Q so'z birikmasi). Bu — bu hisobotning ENG MUHIM OCHIQ SAVOLI: "280 ta so'z" test to'plamining aynan qaysi so'zlardan iboratligi aniqlanmaguncha, 97,7% ko'rsatkichi bilan CH2/1500-so'zlik lug'at orasidagi haqiqiy "aylanma baholash" xavfini SO'Z DARAJASIDA tekshirib bo'lmaydi.

**Qo'lda ko'rib chiqish natijasi (qolgan bloklar, Claude tomonidan, bir marta, 2026-09-09):** yuqoridagi 55 ta blokdan yuqoridagi 4.3-jadval BUNDAN MUSTASNO, qolganlarning HECH birida CH2_EVX_EXAMPLES so'zlari (yoki ularga ishora) TOPILMADI — bularning deyarli barchasi (a) III bobdagi baza-qurish/vazn-hisoblash metodologiyasi tavsifi (masalan "rasmiy modellar barcha so'z turkumlari uchun hisoblandi" kabi UMUMIY bayonotlar, aniq so'z sanamasdan) yoki (b) IV bobdagi dastur-modul tavsifi/skrinshot izohlari va bibliografiya. **Bu qo'lda ko'rib chiqish rasmiy audit emas** — bitta o'qishda amalga oshirildi, boshqa birov xatolik topishi mumkin; shu sabab to'liq ro'yxat yuqorida qoldirildi.

### 3.4 Cheklovlar (nima bu tekshiruv doirasidan TASHQARIDA qoldi)

- Bu — **so'zma-so'z matn qidiruvi**, semantik/ma'no darajasidagi tahlil EMAS. Agar III/IV bobdagi biror "aniqlik"/"foiz" jadvali test to'plamini CH2 so'zlarini AYNAN yozmasdan tasvirlasa (masalan faqat son bilan: "52 ta misol", yoki umuman tavsiflamasdan), bu skript buni ANIQLAY OLMAYDI.
- Rasm ichidagi matn (screenshot, diagram label) `python-docx` orqali UMUMAN o'qilmaydi — agar IV bobdagi dastur skrinshotlarida CH2 so'zlari ko'rinsa, bu skript ularni ko'rmaydi.
- Footnote/izoh matnlari (agar alohida XML qismida saqlangan bo'lsa) tekshirilmagan — bu docx'da shunday joy borligi alohida tasdiqlanmagan.
- 3.3-bo'limdagi "qo'lda ko'rib chiqish" — professor darajasidagi rasmiy audit emas, Claude tomonidan bitta o'qishda bajarilgan; qayta tekshirish tavsiya etiladi.

## Xulosa (faqat aniqlangan faktlar — professor bilan muhokama uchun)

1. **"52 ta" da'vosi to'g'ri** (52 yozuv), lekin bu ro'yxat II bobning HAMMASI emas — kamida 20 ta qo'shimcha misol (shu jumladan **`will return` -> `qaytadi`**, ilgari "CH2_EVX_EXAMPLES da yo'q" deb qayd etilgan edi — ENDI docx'da TOPILDI, #632-634) II bobda bor-yu, CH2_EVX_EXAMPLES ga kiritilmagan.
2. **5 ta haqiqiy mos kelmaslik** topildi (yuqoridagi 1-bo'lim jadvali), ikki xil sababga ega ko'rinadi: (a) transkripsiya xatosi (CH2 ro'yxatini qo'lda ko'chirishda paydo bo'lgan, masalan `capabilityies` — docx'da hech qayerda bunday yozilish yo'q, faqat to'g'ri `capabilities`), (b) docx'dagi ikkita QO'SHNI misoldan noto'g'ri qator ko'chirilgani (masalan `more comfortable` uchun uz='eng qulay' olingan, lekin bu aslida QO'SHNI `most comfortable` misolining tarjimasi — docx'da `more comfortable`->`qulayroq`, alohida). `schoolboys`->`Bojxonalar` xatosi ham xuddi shu turdagi (oldingi `customhouses` qatoridan noto'g'ri ko'chirilgan) — bu docx dalili bilan ENDI TASDIQLANDI (ilgari reports/faza_1.md da faqat FARAZ qilingan edi).
3. **So'z-darajasidagi (substring) qidiruv bo'yicha III/IV bobda CH2 headword'lari topilmadi** (6 ta xom moslikning barchasi adabiyotlar ro'yxatidagi (bibliografiya) inglizcha maqola sarlavhalarida — "information", "here" so'zlari, batafsil 3.2-bo'lim). **LEKIN bu "leakage yo'q" degani EMAS** — dissertatsiyaning yagona raqamli aniqlik jadvali (4.3-jadval, IV bob, 97,7% ko'rsatkichi) "280 ta so'z" ustida hisoblangan, LEKIN o'sha 280 ta so'zning matni docx'ning hech qayerida berilmagan — shu sabab bu 280 ta so'z bilan CH2/1500-so'zlik lug'at orasidagi bog'liqlikni SO'Z DARAJASIDA TEKSHIRISH BU DOCX ICHIDA MUMKIN EMAS (batafsil 3.3-bo'lim, "4.3-jadval" alohida ko'rib chiqilgan qismi). Bu — reproduksiya qilingan METODIKANING (nima qilindi/qilinmadi) o'zi, "leakage bor/yo'q" degan yakuniy xulosa EMAS.

