"""
tests/test_affix_tables.py
============================
Affiks jadvallarining STRUKTURAVIY (schema) tekshiruvi — MORPH_RULES,
EN_AFF_V3, UZ_AFF_V3, POSS_PRONOUN_UZ_X2, PREP_UZ_X3, EN_PREFIXES.

DIQQAT: bu testlar affikslarning LINGVISTIK TO'G'RILIGINI baholamaydi
(masalan vaznlar 0.00101 kabi qiymatlarning ma'nosi — bu Faza 5/6 masalasi,
qarang reports/faza_0.md "Yangi topilmalar" #2-bandi doirasidagi vazn
muammosi bilan bog'liq emas, lekin xuddi shunday "jadval satr raqami vazn
sifatida" muammosi bor). Bu yerda faqat: jadval o'zi ICHKI ZIDDIYATSIZ va
kodning qolgan qismi kutayotgan shaklga mos ekanini tekshiradi — masalan
"MORPH_RULES dagi har bir POS qiymati POS_KKT da mavjudmi" kabi.
"""
from __future__ import annotations

import pytest


def test_morph_rules_pos_values_are_known(isolated_kkt_module):
    """MORPH_RULES dagi har bir qoidaning "derived_pos" (3-element) qiymati
    POS_KKT jadvalida mavjud bo'lishi kerak — aks holda kkt_en()/kkt_uz()
    KKT belgisini topa olmay qoladi."""
    m = isolated_kkt_module
    unknown = set()
    for rule in m.MORPH_RULES:
        derived_pos = rule[2]
        if derived_pos not in m.POS_KKT:
            unknown.add(derived_pos)
    assert not unknown, f"POS_KKT da yo'q POS qiymatlari: {unknown}"


def test_morph_rules_required_root_pos_is_known(isolated_kkt_module):
    """5-elementli qoidalarda (talab qilingan ildiz turkumi, masalan
    "-er" -> "Fe'l") ko'rsatilgan qiymat ham POS_KKT'da bo'lishi kerak."""
    m = isolated_kkt_module
    unknown = set()
    for rule in m.MORPH_RULES:
        if len(rule) > 4:
            req = rule[4]
            if req not in m.POS_KKT:
                unknown.add(req)
    assert not unknown, f"POS_KKT da yo'q 'talab qilingan ildiz turkumi' qiymatlari: {unknown}"


def test_morph_rules_restore_functions_do_not_crash(isolated_kkt_module):
    """Har bir qoidaning ildiz-tiklash funksiyalari (lambda) — YETARLICHA
    UZUN (affiksdan uzunroq) sun'iy so'z bilan chaqirilganda IstisNo
    tashlamasligi kerak (funksiyalar w[:-N] shaklida, N affiks uzunligidan
    kelib chiqadi — juda qisqa so'zda IndexError emas, bo'sh satr qaytaradi,
    bu Python slicing xususiyati, shu sabab bu test asosan "funksiya umuman
    chaqiriladimi" ekanini tekshiradi)."""
    m = isolated_kkt_module
    for sfx, fns, derived_pos, label, *_ in m.MORPH_RULES:
        probe = "x" * (len(sfx) + 10) + sfx  # affiksdan yetarlicha uzun sun'iy so'z
        for fn in fns:
            try:
                result = fn(probe)
            except Exception as e:
                pytest.fail(f"MORPH_RULES['{sfx}'] restore-funksiyasi '{probe}' da xato berdi: {e}")
            assert isinstance(result, str)


TAIL_CHAIN_GROUPS = [
    # Har bir guruh — kod izohida ("MUHIM TARTIB QOIDALARI") aytilgan,
    # bir-birining "dumi" bo'lgan affikslar to'plami: uzunrog'i RO'YXATDA
    # albatta qisqarog'idan OLDIN turishi kerak (_try_suffix() birinchi
    # mos kelgan qoidani tanlaydi).
    ["ization", "ation", "tion"],
    ["isation", "ation", "tion"],
    ["ies", "es", "s"],
    ["ves", "es", "s"],
    ["ally", "ly"],
    ["ily", "ly"],
    ["ably", "ly"],
    ["ibly", "ly"],
    ["iest", "est"],
    # DIQQAT: ["ier", "er"] ataylab bu ro'yxatda YO'Q — "er" MORPH_RULES da
    # IKKI MARTA uchraydi (birinchi: Ot/-er "ish bajaruvchi", faqat ildiz
    # Fe'l bo'lsa; ikkinchi: Sifat/-er qiyosiy, cheklovsiz). "-ier" faqat
    # BIRINCHI "-er" dan keyin, IKKINCHI "-er" dan oldin turishi kerak —
    # buni first-occurrence index() bilan oddiy solishtirib bo'lmaydi
    # (list.index() faqat birinchi uchrashni topadi). Bu holat pastdagi
    # alohida testda (`test_morph_rules_er_has_pos_guarded_and_unguarded_variant`)
    # aniq tekshiriladi.
    ["ifying", "ify"],
    ["izing", "ize"],
]


@pytest.mark.parametrize("group", TAIL_CHAIN_GROUPS, ids=lambda g: "<".join(g))
def test_morph_rules_longer_suffix_precedes_shorter_suffix(isolated_kkt_module, group):
    """Kod izohida ta'kidlangan tartib qoidasi (masalan -ies/-ves OLDIN -es
    dan, -ization OLDIN -ation dan) — MORPH_RULES ro'yxatidagi HAQIQIY
    tartibni tekshiradi, chunki _try_suffix() ro'yxatda birinchi mos kelgan
    qoidani tanlaydi (uzunroq oxirgi ustunlar ro'yxatda oldinroq bo'lishi
    kerak, aks holda hech qachon ishlamay qoladi)."""
    m = isolated_kkt_module
    suffixes = [rule[0] for rule in m.MORPH_RULES]
    # Bir xil affiks MORPH_RULES da bir necha marta (turli POS/qoida ostida)
    # uchrashi mumkin (masalan "er" — Ot ham, Sifat ham) — shu sabab HAR BIR
    # uchrashgan indeksni emas, ENG BIRINCHI uchrashgan indeksni solishtiramiz
    # (_try_suffix ham ro'yxatni boshidan aylanadi va BIRINCHI mosni oladi).
    indices = []
    for sfx in group:
        try:
            indices.append((sfx, suffixes.index(sfx)))
        except ValueError:
            pytest.fail(f"'{sfx}' MORPH_RULES da umuman yo'q (kutilgan edi)")
    ordered = [sfx for sfx, _ in indices]
    positions = [idx for _, idx in indices]
    assert positions == sorted(positions), (
        f"Tartib buzilgan: {ordered} ketma-ketligi MORPH_RULES dagi haqiqiy "
        f"pozitsiyalarga mos emas ({positions}) — uzunroq affiks qisqarog'idan "
        f"OLDIN turishi kerak edi."
    )


def test_morph_rules_er_has_pos_guarded_and_unguarded_variant(isolated_kkt_module):
    """"-er" MORPH_RULES da ATAYLAB ikki marta uchraydi: (1) Ot/-er
    ("ish bajaruvchi", masalan work->worker) — FAQAT ildiz "Fe'l" bo'lsa
    ishlaydi (5-elementli qoida, req_root_pos="Fe'l"); (2) Sifat/-er
    (qiyosiy daraja, masalan fast->faster) — cheklovsiz. Birinchisi
    RO'YXATDA ikkinchisidan OLDIN turishi SHART — aks holda "worker" har
    doim (noto'g'ri) qiyosiy sifat sifatida aniqlanib qolardi. Shuningdek
    "-ier" (Sifat qiyosiy, y->i) ikkalasi ORASIDA turadi."""
    m = isolated_kkt_module
    er_rules = [(i, rule) for i, rule in enumerate(m.MORPH_RULES) if rule[0] == "er"]
    assert len(er_rules) == 2, f"'-er' MORPH_RULES da {len(er_rules)} marta uchradi, 2 kutilgan edi"

    (idx_first, rule_first), (idx_second, rule_second) = er_rules
    assert idx_first < idx_second

    req_first = rule_first[4] if len(rule_first) > 4 else None
    req_second = rule_second[4] if len(rule_second) > 4 else None
    assert req_first == "Fe'l", (
        f"Birinchi '-er' qoidasi Fe'l-cheklovli (Ot/ish-bajaruvchi) bo'lishi "
        f"kerak edi, topildi: req_root_pos={req_first!r}"
    )
    assert req_second is None, (
        f"Ikkinchi '-er' qoidasi cheklovsiz (Sifat/qiyosiy) bo'lishi kerak "
        f"edi, topildi: req_root_pos={req_second!r}"
    )

    idx_ier = next(i for i, rule in enumerate(m.MORPH_RULES) if rule[0] == "ier")
    assert idx_first < idx_ier < idx_second, (
        f"'-ier' (indeks {idx_ier}) ikkita '-er' qoidasi ({idx_first}, {idx_second}) "
        f"orasida turishi kutilgan edi."
    )
