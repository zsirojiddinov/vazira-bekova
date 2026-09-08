"""
tests/test_translate_phrase_general.py
=========================================
`translate_phrase()` / `translate_phrase_general()` — umumiy grammatik
qayta tartiblash. Bu fayldagi holatlar topshiriq matnida ANIQ nomlab
o'tilgan, foydalanuvchi/dissertatsiya muallifi tomonidan avval qo'lda
TOPILGAN muammoli misollar: "capabilities" (topshiriqda "capabilityies"
deb yozilgan), "leaves" ("leafes"), "schoolboys", "more comfortable",
"will return". Bularning HECH biri uchun Claude tomonidan gold/etalon
tarjima TO'QILMAGAN (Qoida 1) — bu testlar faqat JORIY (hozirgi, 2026-09-08)
xatti-harakatni QAYD ETADI (characterization/regression baseline), ular
"to'g'ri natija" deb da'vo qilmaydi.

Har bir chaqiruv `allow_write=False` bilan — bu skript/test ishga
tushirilganda .db fayllarga yozilmasligi kerak (Faza 0 hodisasi, qarang
reports/faza_0.md)."""
from __future__ import annotations


def test_unknown_word_capabilities_returns_none(isolated_kkt_module):
    """"capabilities" — bazada "capability" (yoki "capabilities") headword
    sifatida yo'q (uz_stem/-ies qoidasi ISHLAYDI, lekin natija sifatida
    hosil bo'lgan "capability" so'zi lug'atda topilmaydi). Natija: None —
    GUI so'zma-so'z parse_sentence()ga o'tadi (u yerda ham "?" markeri
    bilan qoladi). Bu — topshiriqning "II bob misollari" ro'yxatidagi
    aynan shu so'z."""
    m = isolated_kkt_module
    assert m.translate_phrase("capabilities", allow_write=False) is None


def test_unknown_word_leaves_returns_none(isolated_kkt_module):
    """"leaves" — "-ves" qoidasi orqali "leaf" ga tiklanadi (f->v), lekin
    "leaf" o'zi ham lug'atda yo'q. Natija: None."""
    m = isolated_kkt_module
    assert m.translate_phrase("leaves", allow_write=False) is None


def test_more_comfortable_returns_none(isolated_kkt_module):
    """"more comfortable" — na "comfortable" (sifat) na "more" (miqdor
    ravishi) joriy lug'atda/qoidalar to'plamida qiyosiy daraja sifatida
    tanilmagan (kod faqat -er/-ier orqali qiyosiy darajani biladi, "more X"
    analitik shaklini emas). Natija: None."""
    m = isolated_kkt_module
    assert m.translate_phrase("more comfortable", allow_write=False) is None


def test_will_return_modal_verb_returns_none(isolated_kkt_module):
    """"will return" — modal fe'l ("will") + asosiy fe'l birikmasi kod
    tomonidan bitta VP sifatida tanib olinmaydi. Natija: None."""
    m = isolated_kkt_module
    assert m.translate_phrase("will return", allow_write=False) is None


def test_schoolboys_produces_wrong_translation_data_bug(isolated_kkt_module):
    """YANGI TOPILMA (Faza 1 tayyorlash paytida aniqlangan): "schoolboys"
    None QAYTARMAYDI — u UB_en_w'da headword sifatida BOR, lekin XATO
    tarjima bilan: "Bojxonalar" ("customhouses" so'zi bilan bir xil qator!).

    Manba: kkt_v20_soz_tartibi.py ichidagi load_ch2_evx_examples() dagi
    literal (qo'lda kiritilgan) ro'yxat — "customhouses" va "schoolboys"
    qatorlari ketma-ket, ikkalasida ham "uz":"Bojxonalar" — aniq
    copy-paste xatosi (schoolboys "maktab o'quvchilari/o'g'il bolalari"
    kabi biror narsa bo'lishi kerak edi, "bojxona" bilan aloqasi yo'q).

    Bu topshiriqning "II bob misollari orasida schoolboys topilishi kerak
    edi" talabining ANIQ o'zi — audit_examples.py xuddi shu turdagi
    xatolarni avtomatik topish uchun mo'ljallangan (Faza 1, pastga qarang).
    Tuzatish — Faza 2/7 (chapter2_evx literal ro'yxatini tuzatish +
    provenance), Claude BU YERDA tuzatmaydi (Qoida 3/6)."""
    m = isolated_kkt_module
    result = m.translate_phrase("schoolboys", allow_write=False)
    assert result is not None
    assert result["natija"] == "Bojxonalar", (
        "Kutilgan JORIY (xato) natija endi boshqacha chiqyapti — agar bu "
        "tuzatilgan bo'lsa, shu testni yangilang va "
        "reports/faza_1.md dagi 'schoolboys' topilmasini yopilgan deb belgilang."
    )


def test_multi_verb_sentence_silently_drops_the_verb(isolated_kkt_module):
    """Boshlang'ich topshiriq matnidagi #1-kamchilikning to'g'ridan-to'g'ri
    ko'rinishi: "The program processes the data quickly." -> "Dastur
    jarayonlar ma'lumotlar" (fe'l yo'qoladi) — dictionary'da "program" yo'q
    (yuqoridagi missing-noun muammosi bilan bog'liq), shu sabab bu yerda
    o'rniga (dictionary'da BOR so'zlar bilan) tuzilgan sinonim gap
    ishlatiladi: "the student reads the book" -> fe'l ("reads") lug'atda
    aniq shaklda topilmagani uchun VP sifatida aniqlanmaydi va NATIJADAN
    JIMGINA TUSHIB QOLADI (translate_phrase_general: `rest = [c for c in
    chunks if c[0] != "?"]` — topilmagan bo'lak shunchaki o'chiriladi)."""
    m = isolated_kkt_module
    result = m.translate_phrase("the student reads the book", allow_write=False)
    assert result is not None
    # "reads" natijada YO'Q — bu aynan muammoning o'zi (natija fe'lsiz).
    assert "read" not in result["natija"].lower()
    assert result["natija"] == "Talaba kitob", (
        "Kutilgan JORIY (fe'l tushib qolgan) natija endi boshqacha — agar "
        "kod tuzatilgan bo'lsa (masalan noma'lum fe'l endi '?' bilan "
        "belgilanadigan bo'lsa), shu testni yangilang."
    )


def test_bare_possessive_np_missing_accusative_ni(isolated_kkt_module):
    """"our books" (predlogsiz, 2 so'z) — translate_phrase_kkt() bu
    naqshni ushlamaydi (3 so'z talab qiladi), translate_phrase_general()
    esa oddiy NP sifatida ("Kitoblarimiz") beradi — TUSHUM KELISHIGI
    ("-ni") QO'SHILMAYDI. data/100_soz.docx dagi #7-etalon ("our books" ->
    "kitoblarimizni") BOSHQA yo'l (aniq D+M2+C naqshi doirasida, "our
    books" 3-so'zli kontekstda emas, alohida "our books" iborasi sifatida)
    uchun mo'ljallangan bo'lishi mumkin — bu ikkilanish aynan Faza 2 da
    inson qaroriga topshiriladigan masala (reports/accusative_analysis.md).
    Bu test faqat translate_phrase_general() yo'lidagi JORIY natijani
    qayd etadi, "-ni" qo'shish TAVSIYASINI bermaydi."""
    m = isolated_kkt_module
    result = m.translate_phrase("our books", allow_write=False)
    assert result is not None
    assert result["natija"] == "Kitoblarimiz"  # "-ni" YO'Q — joriy holat
    assert not result["natija"].endswith("ni")
