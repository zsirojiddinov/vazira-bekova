"""
tests/test_kkt_spec_conformance.py
=====================================
Rasmiy KKT spesifikatsiyasi (`data/kkt_spec.json` ← `data/kkt_qoidalari.docx`)
bo'yicha testlar. Bu testlar **FORMAL QOIDANING O'ZINI** tekshiradi —
tarjima sifatini EMAS.

MUHIM CHEGARA: yagona ma'lumot manbai — `data/kkt_spec.json`. Gold to'plamlar
(`100_soz.json`, `1500_EN_UZ_6_POS_sorted.20.json`) bu yerda ISHLATILMAYDI,
hatto bir xil so'z ikkalasida ham uchrasa ham (masalan "capabilities").
Ular end-to-end tarjima sifati uchun; bu fayl — qoida to'g'ri implement
qilinganmi, shuni tekshiradi. Kesishmalar alohida: `scripts/check_leakage.py`.

Tuzilish:
- `test_spec_example_reproduced_by_formal_rule[<uid>]` — HAR BIR docx misoli
  uchun alohida test (87 ta). Hozir mos KELMAYDIGAN qoidalar
  `xfail(strict=True)`: kod tuzatilib qoida mos kela boshlasa, test XPASS
  bo'lib QULAYDI — shunda `EXPECTED_STATUS` va hisobot
  (`python scripts/audit_kkt_spec_conformance.py`) yangilanishi shart.
- `test_audit_status_snapshot` — `reports/faza_2_kkt_spec_conformance.md`
  dagi holatlar kod bilan sinxronligini himoya qiladi.
"""
from __future__ import annotations

import json
import os
import re
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import audit_kkt_spec_conformance as audit  # noqa: E402
import extract_kkt_spec  # noqa: E402
from _common import normalize  # noqa: E402

SPEC_PATH = os.path.join(REPO_ROOT, "data", "kkt_spec.json")
DOCX_PATH = os.path.join(REPO_ROOT, "data", "kkt_qoidalari.docx")

with open(SPEC_PATH, encoding="utf-8") as _f:
    SPEC = json.load(_f)
RULES = SPEC["rules"]
RULE_BY_UID = {r["uid"]: r for r in RULES}

T, Q, Y, Z = audit.TOLIQ, audit.QISMAN, audit.YOQ, audit.ZID

# reports/faza_2_kkt_spec_conformance.md bilan bir xil (USE_LEMMA=True muhitida).
EXPECTED_STATUS = {
    "2.1": T, "2.2": T, "2.3": T, "2.4": T, "2.5": Q, "2.6": T, "2.7": T, "2.8": T, "2.9": T,
    "2.10": Y, "2.11": T, "2.12": Q, "2.13": Q, "2.15": Q, "2.16": T,
    "–(Sifat)": Y, "2.19": Q, "2.20": Q, "2.21": Q, "2.22": T, "2.23": T, "2.24": T, "2.25": T,
    "2.26": T, "2.27": T, "2.28": T, "2.29": T, "2.30": T, "2.31": T, "2.32": T, "2.33": Q, "2.34": T,
    "2.36": Y, "2.37": T, "2.38": Y, "2.39": Y, "2.41": Y, "2.42": Q, "2.43": Q, "2.44": Y, "2.45": Y,
    "2.46": T, "2.47": Q, "2.48": Y, "2.49": T, "2.50": Y, "2.51": T, "2.52": T, "2.53": Q, "2.54": Q,
    "2.55a": Y, "2.56": T, "2.55b": Q, "2.58": Y, "2.59": T, "2.61": T, "2.62": T, "2.63": Q,
    "2.64": Q, "2.65": Q,
    "–(Ravish)": Y, "3.1": T, "3.2": Q, "3.3": Q, "3.4": Q, "3.5": T, "3.6": T, "3.7": T, "3.8": T,
    "3.9": Q,
    "3.11": Q, "3.12": T, "3.13": Q, "3.14": T, "3.15": T, "3.16": T, "3.17": Y, "3.18": T, "3.19": Y,
    "3.20": Y,
    "3.22": Q, "3.23": Q, "3.24": Q, "3.25": Q, "3.26": Q, "3.27": Q, "3.28": Q,
}
# NLTK wordnet bo'lmagan muhitda (USE_LEMMA=False) boshqacha chiqadigan holatlar.
EXPECTED_STATUS_NO_LEMMA = {"2.33": Y, "2.65": Y}


def _expected(m, uid):
    if not m.USE_LEMMA and uid in EXPECTED_STATUS_NO_LEMMA:
        return EXPECTED_STATUS_NO_LEMMA[uid]
    return EXPECTED_STATUS[uid]


# ═══════════════════════════════════════════════════════════════════
#  Spesifikatsiya faylining o'zi
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.skipif(not os.path.exists(DOCX_PATH), reason="data/kkt_qoidalari.docx bu muhitda yo'q")
def test_spec_json_in_sync_with_docx():
    """kkt_spec.json — docx'dan qayta ajratilganda bayt-ma-bayt bir xil
    chiqishi kerak (qo'lda tahrir qilinmagan, "tuzatilmagan")."""
    with open(SPEC_PATH, encoding="utf-8") as f:
        on_disk = f.read()
    assert extract_kkt_spec.dumps(extract_kkt_spec.extract(DOCX_PATH)) == on_disk, (
        "data/kkt_spec.json docx bilan mos emas — `python scripts/extract_kkt_spec.py` ni qayta ishga tushiring"
    )


def test_spec_provenance_records_source_hash_without_the_document():
    """Manba docx .gitignore'da (repoga joylashtirilmaydi) — kkt_spec.json
    esa uning sha256 xeshini saqlaydi. Docx mahalliy mavjud bo'lsa, xesh unga
    aynan teng bo'lishi shart."""
    manba = SPEC["manba"]
    assert re.fullmatch(r"[0-9a-f]{64}", manba["sha256"])
    assert manba["repoda"] is False
    if os.path.exists(DOCX_PATH):
        assert extract_kkt_spec._sha256(DOCX_PATH) == manba["sha256"]
        assert os.path.getsize(DOCX_PATH) == manba["hajm_bayt"]


def test_spec_counts():
    """87 qoida (topshiriqdagi "93" — jadval sarlavha qatorlari bilan)."""
    assert SPEC["sonlar"]["jami_qoida"] == len(RULES) == 87
    assert SPEC["sonlar"]["pos_boyicha"] == {"Ot": 15, "Sifat": 17, "Fe'l": 28, "Ravish": 10, "Son": 10, "Olmosh": 7}
    assert sum(SPEC["sonlar"]["jadval_qatorlari_sarlavha_bilan"].values()) == 93
    assert [o["belgi"] for o in SPEC["operators"]] == ["⊕", "V", "↓ (⇓)", "$"]
    assert len({r["uid"] for r in RULES}) == 87


def test_spec_pos_weights_as_in_docx():
    assert SPEC["pos_weights"] == {"Ot": 0.85, "Sifat": 0.6, "Fe'l": 0.9, "Ravish": 0.4, "Olmosh": 0.5,
                                   "Son": 0.5, "Bog'lovchi": 0.2, "Predlog": 0.4, "Yordamchi": 0.07}


def test_spec_text_fields_are_verbatim():
    """Tipografik belgilar "tuzatilmagan" — docx'dagidek qolgan."""
    assert RULE_BY_UID["2.21"]["uz_misol"] == "aqil + li + roq = aqillroq"
    assert "izoh" in RULE_BY_UID["2.21"]
    assert RULE_BY_UID["2.16"]["en_misol"] == "student’s"


# ═══════════════════════════════════════════════════════════════════
#  Vaznlar va turkum belgilari — kod bilan
# ═══════════════════════════════════════════════════════════════════
def test_pos_v2_and_pos_kkt_match_spec(isolated_kkt_module):
    """8 ta vazn va belgi kodda spec bilan bit-aniq bir xil (taqriz 27-band)."""
    m = isolated_kkt_module
    for w in SPEC["pos_weights_manba"]:
        if w["kalit"] == "Yordamchi":
            continue
        assert m.POS_V2[w["kalit"]] == w["vazn"], w
        assert m.POS_KKT[w["kalit"]] == w["belgi"], w


def test_pos_v2_has_no_yordamchi_documented_gap(isolated_kkt_module):
    """Spec'dagi 9-vazn (Yordamchi U, L — 0.07) POS_V2/POS_KKT da YO'Q
    (hisobot 3-bo'lim). Qo'shilsa — bu test va hisobot yangilansin."""
    m = isolated_kkt_module
    assert "Yordamchi" not in m.POS_V2
    assert "Yordamchi" not in m.POS_KKT


# ═══════════════════════════════════════════════════════════════════
#  PROBES — tekshiruv tavsiflarining o'zi to'g'rimi
# ═══════════════════════════════════════════════════════════════════
def test_every_rule_has_exactly_one_probe():
    assert set(audit.PROBES) == {r["uid"] for r in RULES}
    assert set(EXPECTED_STATUS) == set(audit.PROBES)


def _cell_norm(cell: str) -> str:
    """"+" bilan ajratilgan qismlar qo'shiladi, qavslar olib tashlanadi."""
    s = re.sub(r"\s*\+\s*", "", cell).replace("(", "").replace(")", "")
    return normalize(s)


@pytest.mark.parametrize("uid", list(audit.PROBES))
def test_probe_values_trace_to_docx_cells(uid):
    """Har bir kirish/kutilgan/stub qiymat docx katagidan (yoki `manba_uid`
    qoidaning katagidan) kelib chiqadi — Claude tomonidan to'qilmagan.
    Yagona istisno — "⟨...⟩" BELGI (docx o'zbekchasini bermagan joy)."""
    rule = RULE_BY_UID[uid]
    probe = audit.PROBES[uid]
    en_cell, uz_cell = _cell_norm(rule["en_misol"]), _cell_norm(rule["uz_misol"])
    for en, exp in probe["juftlar"]:
        assert normalize(en) in en_cell or normalize(en.replace("-", " ")) in en_cell, (uid, en)
        assert audit._clean(exp) in uz_cell, (uid, exp)
    for entry in probe["stub"]:
        en, uz = entry[0], entry[1]
        src = RULE_BY_UID[entry[3]] if len(entry) > 3 else rule
        en_cells = en_cell + " " + _cell_norm(src["en_misol"])
        uz_cells = uz_cell + " " + _cell_norm(src["uz_misol"])
        assert normalize(en) in en_cells, (uid, en)
        if not audit._PLACEHOLDER_RE.match(uz):
            assert normalize(uz) in uz_cells, (uid, uz)


# ═══════════════════════════════════════════════════════════════════
#  Har bir docx misoli — alohida test (formal qoida)
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("uid", [r["uid"] for r in RULES])
def test_spec_example_reproduced_by_formal_rule(isolated_kkt_module, uid, request):
    m = isolated_kkt_module
    expected = _expected(m, uid)
    if expected != T:
        request.applymarker(pytest.mark.xfail(
            strict=True, reason=f"{expected} — reports/faza_2_kkt_spec_conformance.md"))
    ev = audit.evaluate_rule(m, RULE_BY_UID[uid], audit.PROBES[uid])
    rows = ev["real"] if ev["tur"] == "L" else ev["mech"]
    assert ev["holat"] == T, "; ".join(f"{p['en']} → {p['natija']!r} (kutilgan {p['kutilgan']!r})" for p in rows)


def test_audit_status_snapshot(isolated_kkt_module):
    """Hisobotdagi 87 holat kod bilan sinxron. Kod o'zgarib biror holat
    o'zgarsa: hisobotni qayta generatsiya qiling va shu lug'atni yangilang."""
    m = isolated_kkt_module
    got = {e["uid"]: e["holat"] for e in audit.evaluate_all(m, SPEC)}
    want = {uid: _expected(m, uid) for uid in got}
    diff = {u: (want[u], got[u]) for u in got if got[u] != want[u]}
    assert not diff, f"holat o'zgardi (kutilgan, hozirgi): {diff}"


# ═══════════════════════════════════════════════════════════════════
#  Hisobotdagi aniq da'volarni tasdiqlovchi testlar
# ═══════════════════════════════════════════════════════════════════
def test_iest_rule_restores_y_final_root_spec_2_28(isolated_kkt_module):
    """KKT spec 2.28: "busy → busi + est = busiest" → "eng band". "-iest"
    qoidasining birinchi o'zak-tiklash funksiyasi "busy" ni qaytarishi va
    stub lug'at (busy→band) bilan natija "eng band" bo'lishi shart.
    (Tuzatishdan oldin w[:-3]+"y" = "busiy" edi — qoida hech ishlamasdi.)"""
    m = isolated_kkt_module
    fns = next(r[1] for r in m.MORPH_RULES if r[0] == "iest")
    assert fns[0]("busiest") == "busy"
    with audit.stub_lexicon(m, [("busy", "band", "Sifat")]):
        out = audit.system_output(m, "busiest")
    tok = out["tokens"][0]
    assert (tok["suffix"], tok["root"], tok["pos"]) == ("iest", "busy", "Sifat")
    assert normalize(out["natija"]) == "eng band"


def test_teen_rule_cannot_restore_five_from_fif(isolated_kkt_module):
    """3.12 izohi: stub'da "five" (haqiqiy asos) bo'lsa, "fifteen" topilmaydi —
    "-teen" qoidasi faqat w[:-4]="fif" ni sinaydi. Docx o'zagi "fif" bilan
    esa qoida ishlaydi (3.12 = TO'LIQ MOS)."""
    m = isolated_kkt_module
    with audit.stub_lexicon(m, [("five", "besh", "Son")]):
        out = audit.system_output(m, "fifteen")
    assert out["natija"] == "[fifteen?]"
    with audit.stub_lexicon(m, [("fif", "besh", "Son")]):
        out = audit.system_output(m, "fifteen")
    assert normalize(out["natija"]) == normalize("o‘n besh")


def test_verb_third_person_s_spec_2_37(isolated_kkt_module):
    """KKT spec 2.37: "speak + s = speaks" → "gapir + a + di = gapiradi".
    Ildiz lug'atda Fe'l bo'lsa "-s" fe'l 3-shaxs birlik (G←G) deb tahlil
    qilinadi (tuzatishdan oldin Ot ko'plik: "gapirlar" edi)."""
    m = isolated_kkt_module
    with audit.stub_lexicon(m, [("speak", "gapir", "Fe'l")]):
        out = audit.system_output(m, "speaks")
    tok = out["tokens"][0]
    assert (tok["suffix"], tok["root"], tok["pos"]) == ("s", "speak", "Fe'l")
    assert normalize(out["natija"]) == "gapiradi"


def test_noun_plural_s_unchanged_by_verb_s_rule(isolated_kkt_module):
    """Fe'l "-s" qoidasi FAQAT ildiz Fe'l bo'lganda ishlaydi: ot ildizlar
    (spec 2.1 variable) va ikki qatlamli ot ("work+er+s" — oraliq "worker"
    Ot) avvalgidek ot ko'pligi bo'lib qoladi."""
    m = isolated_kkt_module
    with audit.stub_lexicon(m, [("variable", "o‘zgaruvchi", "Ot")]):
        tok = audit.system_output(m, "variables")["tokens"][0]
    assert (tok["suffix"], tok["pos"]) == ("s", "Ot")
    with audit.stub_lexicon(m, [("work", "ishlamoq", "Fe'l")]):
        tok = audit.system_output(m, "workers")["tokens"][0]
    assert (tok["suffix"], tok["root"], tok["pos"]) == ("er+s", "work", "Ot")


def test_stub_lexicon_restores_original_lookup_functions(isolated_kkt_module):
    m = isolated_kkt_module
    orig = (m.db_lookup, m.db_lookup_all, m.db_lookup_by_id)
    with pytest.raises(RuntimeError):
        with audit.stub_lexicon(m, [("x", "y", "Ot")]):
            assert m.db_lookup("x") is not None
            raise RuntimeError
    assert (m.db_lookup, m.db_lookup_all, m.db_lookup_by_id) == orig
    assert m.db_lookup("book") is not None  # haqiqiy lug'at qaytdi


def test_stub_lexicon_hides_real_dictionary(isolated_kkt_module):
    """Stub ichida real lug'atdagi so'z (masalan CH2 dan "processes") ko'rinmaydi —
    aks holda M-tekshiruvi yana aylanma bo'lib qolardi."""
    m = isolated_kkt_module
    assert m.db_lookup("processes") is not None
    with audit.stub_lexicon(m, []):
        assert m.db_lookup("processes") is None
        assert m.db_lookup("from") is not None  # SEED_WORDS (kod) ko'rinadi


def test_indefinite_article_becomes_bitta_spec_2_2_2_3(isolated_kkt_module):
    """KKT spec 2.2/2.3: "a network" → "bitta tarmoq", "an example" → "bitta
    misol"; 2.4: "the progress" → "taraqqiyot" (aniq artikl tarjima qilinmaydi).
    Sifat oraliqda bo'lsa ham artikl ot iborasiga kiradi (big→katta: spec
    "–(Sifat)"); ortidan ot kelmasa — avvalgidek tashlanadi."""
    m = isolated_kkt_module
    stub = [("network", "tarmoq", "Ot"), ("example", "misol", "Ot"), ("progress", "taraqqiyot", "Ot"),
            ("big", "katta", "Sifat")]
    with audit.stub_lexicon(m, stub):
        got = {t: normalize(audit.system_output(m, t)["natija"])
               for t in ("a network", "an example", "the progress", "a big network", "big a")}
    assert got["a network"] == "bitta tarmoq"
    assert got["an example"] == "bitta misol"
    assert got["the progress"] == "taraqqiyot"
    assert got["a big network"] == "bitta katta tarmoq"
    assert "bitta" not in got["big a"]


def test_ssm_treats_spec_word_class_symbols_u_l_as_root_spec_2_51_2_52(isolated_kkt_module):
    """KKT spec vazn jadvali: "Yordamchi so'z turkumlari (U, L)" — so'z turkumi,
    ya'ni ildiz belgisi. SSM mexanizmi (lug'atdan mustaqil): "L(L)" va "U(U)"
    modellarida ildiz topilishi shart. Ilgari "L" ildiz deb tanilmagani uchun
    "may"/"might" ning lug'atdagi "mumkin" tarjimasi MDB_uz_w orqali tasodifiy
    "Ajratib ko'rsatmoq" bilan almashtirilardi."""
    m = isolated_kkt_module
    assert m.ssm_score("L(L) = $[i,1-h2]Li", "uz")["root_found"] is True
    assert m.ssm_score("U(U) = $[i,1-h2]Ui", "uz")["root_found"] is True
    with m.readonly_mode():
        for w in ("may", "might"):
            a = m.smart_parse(w)
            assert a["uz"] == "mumkin", (w, a["uz"], a["method"])
            assert "MDB_uz_w" not in a["method"]


def test_to_infinitive_and_prepositional_object_spec_2_56_2_59(isolated_kkt_module):
    """KKT spec 2.56: "to ask" → "so‘ramoq" (infinitiv "to" tarjima qilinmaydi).
    KKT spec 2.59: "listen to me" → "meni tinglamoq" (predlog tushadi,
    to'ldiruvchi vositasiz, fe'ldan oldin; "me" obyekt shakli — spec 3.22 —
    ustiga "-ni" qo'shilmaydi). Regressiya qo'riqlari: "to" + OT avvalgidek
    kelishik (to→ga), bitta so'zli fe'l kirishi avvalgidek None."""
    m = isolated_kkt_module
    stub = [("ask", "so‘ramoq", "Fe'l"), ("listen", "tinglamoq", "Fe'l"), ("me", "meni", "Olmosh"),
            ("example", "misol", "Ot")]
    with audit.stub_lexicon(m, stub):
        got = {t: normalize(audit.system_output(m, t)["natija"])
               for t in ("to ask", "listen to me", "to the example")}
        with m.readonly_mode():
            single = m.translate_phrase("ask", allow_write=False)
    assert got["to ask"] == normalize("so‘ramoq")
    assert got["listen to me"] == normalize("meni tinglamoq")
    assert got["to the example"] == "misolga"
    assert single is None


def test_analytic_degree_more_most_less_spec_2_31_2_32_2_34_3_5(isolated_kkt_module):
    """KKT spec: "more comfortable" → "qulayroq" (2.31), "most comfortable" →
    "eng qulay" (2.32), "less interesting" → "kamroq qiziqarli" (2.34),
    "more clearly" → "aniqroq" (3.5). Qo'riq: keyingi so'z ot bo'lsa ("more
    network") daraja qoidasi qo'llanmaydi."""
    m = isolated_kkt_module
    stub = [("comfortable", "qulay", "Sifat"), ("interesting", "qiziqarli", "Sifat"),
            ("clearly", "aniq", "Ravish"), ("network", "tarmoq", "Ot")]
    with audit.stub_lexicon(m, stub):
        got = {t: normalize(audit.system_output(m, t)["natija"])
               for t in ("more comfortable", "most comfortable", "less interesting", "more clearly", "more network")}
    assert got["more comfortable"] == "qulayroq"
    assert got["most comfortable"] == "eng qulay"
    assert got["less interesting"] == "kamroq qiziqarli"
    assert got["more clearly"] == "aniqroq"
    assert "roq" not in got["more network"]


def test_future_will_plus_verb_spec_2_62(isolated_kkt_module):
    """KKT spec 2.62: "will return" → "qaytmoq" ("will" fe'ldan oldin tushadi).
    Qo'riqlar: yakka "will" (spec 2.46) tegilmaydi — bitta so'zli kirish
    avvalgidek None; "will" dan keyin fe'l bo'lmasa u tashlanmaydi."""
    m = isolated_kkt_module
    stub = [("return", "qaytmoq", "Fe'l"), ("will", "keladi", "Fe'l"), ("example", "misol", "Ot")]
    with audit.stub_lexicon(m, stub):
        got = normalize(audit.system_output(m, "will return")["natija"])
        with m.readonly_mode():
            single = m.translate_phrase("will", allow_write=False)
            chunks = m._chunk_phrase("will example")
    assert got == "qaytmoq"
    assert single is None
    assert ("VP", "keladi") in chunks
