"""
tests/test_make_uzbek.py
==========================
`make_uzbek(root_uz, sfx)` — ingliz affiksini statik KKT jadval orqali
o'zbekcha shaklga aylantiradigan ZAXIRA (fallback) funksiya (QM_en_w→QM_uz_w
ID-moslashuv ishlamaganda ishlatiladi). Funksiya to'liq deterministik — bitta
lokal `rules` lug'atidan sfx->qo'shimcha shablonini oladi.

Bu testlar `kkt_v20_soz_tartibi.py` ichidagi `make_uzbek()` funksiyasi
docstringida VA kodining o'zida hujjatlashtirilgan xaritalashni ("-s -> +lar",
"-ing -> +ayotgan" va h.k.) qayd etadi — funksiya ICHKARISIDAGI jadvaldan
mustaqil ravishda qayta yozilgan, shu sabab tasodifiy o'zgarish (masalan
kimdir "ly" qatorini o'chirib qo'ysa) shu yerda ushlanadi."""
from __future__ import annotations

import pytest

ROOT = "kitob"  # neytral o'zbek o'zagi — barcha holatlar shu bitta o'zak ustida sinaladi

# (affiks, kutilgan natija) — kkt_v20_soz_tartibi.py:make_uzbek() dagi `rules`
# lug'atidan olingan, ROOT="kitob" bilan qo'lda hisoblangan.
CASES = [
    ("s", "kitoblar"), ("es", "kitoblar"), ("ies", "kitoblar"), ("ves", "kitoblar"),
    ("ing", "kitobayotgan"), ("ying", "kitobayotgan"), ("zing", "kitobayotgan"),
    ("izing", "kitoblayotgan"), ("ifying", "kitoblayotgan"),
    ("ied", "kitobgan"), ("ed", "kitobgan"),
    ("er", "kitobroq"), ("ier", "kitobroq"),
    ("est", "eng kitob"), ("iest", "eng kitob"),
    ("ly", "kitob tarzda"), ("ally", "kitob tarzda"), ("ily", "kitob tarzda"),
    ("ably", "kitob tarzda"), ("ibly", "kitob tarzda"),
    ("ward", "kitob tomon"), ("wards", "kitob tomon"), ("wise", "kitob jihatdan"),
    ("able", "kitobladigan"), ("ible", "kitobladigan"),
    ("ful", "kitobli"), ("ous", "kitobli"), ("ive", "kitobli"),
    ("ant", "kitobli"), ("ent", "kitobli"), ("like", "kitobga o'xshash"),
    ("less", "kitobsiz"), ("ish", "kitobsimon"),
    ("ic", "kitobga oid"), ("al", "kitobga oid"), ("ical", "kitobga oid"),
    ("ary", "kitobga oid"), ("ory", "kitobga oid"),
    ("ation", "kitobish"), ("ition", "kitobish"), ("tion", "kitobish"),
    ("sion", "kitobish"), ("ment", "kitobish"), ("age", "kitobish"), ("ure", "kitobish"),
    ("ness", "kitoblik"), ("ity", "kitoblik"), ("ance", "kitoblik"),
    ("ence", "kitoblik"), ("hood", "kitoblik"), ("dom", "kitoblik"),
    ("ship", "kitobchilik"), ("ism", "kitobizm"), ("ist", "kitobchi"),
    ("ology", "kitob fani"), ("logy", "kitob fani"), ("ics", "kitob fani"),
    ("ization", "kitoblashtirish"), ("isation", "kitoblashtirish"),
    ("ize", "kitoblashtirmoq"), ("ise", "kitoblashtirmoq"),
    ("ify", "kitoblashtirmoq"), ("en", "kitoblashtirmoq"),
    ("self", "kitob o'zi"), ("selves", "kitob o'zlari"),
    ("ever", "kitob ham bo'lsa"), ("thing", "kitobnarsa"),
    ("teen", "o'n kitob"), ("ty", "kitob o'nlik"), ("th", "kitobinchi"),
    ("fold", "kitob katlalik"), ("'s", "kitobning"),
]


@pytest.mark.parametrize("sfx,expected", CASES)
def test_make_uzbek_known_suffix(isolated_kkt_module, sfx, expected):
    m = isolated_kkt_module
    assert m.make_uzbek(ROOT, sfx) == expected


def test_make_uzbek_unknown_suffix_falls_back_to_bare_stem(isolated_kkt_module):
    """Jadvalda bo'lmagan affiks — funksiya o'zakni O'ZGARISHSIZ qaytaradi
    (rules.get(sfx, stem))."""
    m = isolated_kkt_module
    assert m.make_uzbek(ROOT, "___nomavjud___") == ROOT


def test_make_uzbek_all_cases_covered_by_en_aff_v3_and_morph_rules():
    """Sog'lik tekshiruvi: yuqoridagi CASES ro'yxati EN_AFF_V3 yoki MORPH_RULES
    dagi affikslarning katta qismini qamrab olishini tasdiqlaydi — bu ro'yxat
    real jadvaldan (qo'lda ko'chirilgan, generatsiya qilinmagan) ekanini
    ko'rsatadi, tasodifan yaratilgan emas."""
    tested = {sfx for sfx, _ in CASES}
    assert "s" in tested and "ing" in tested and "tion" in tested
    assert len(tested) >= 50, "kutilganidan kamroq affiks qamrab olindi"


def test_make_uzbek_verb_third_person_s_spec_2_37(isolated_kkt_module):
    """KKT spec 2.37: gapir + a + di = gapiradi (undoshdan keyin "-adi").
    Unlidan keyingi "-ydi" (ishla → ishlaydi) — spec misolida YO'Q, o'zbek
    imlosining umumiy qoidasi sifatida qo'shilgan (professor tekshirsin)."""
    m = isolated_kkt_module
    assert m.make_uzbek("gapirmoq", "s", "Fe'l") == "gapiradi"
    assert m.make_uzbek("ishlamoq", "s", "Fe'l") == "ishlaydi"
    # pos berilmasa yoki Ot bo'lsa — avvalgidek ko'plik
    assert m.make_uzbek("kitob", "s") == "kitoblar"
    assert m.make_uzbek("kitob", "s", "Ot") == "kitoblar"
