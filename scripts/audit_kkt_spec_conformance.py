#!/usr/bin/env python3
"""
scripts/audit_kkt_spec_conformance.py
========================================
`data/kkt_spec.json` (rasmiy KKT qoidalari — `data/kkt_qoidalari.docx` dan
`scripts/extract_kkt_spec.py` bilan ajratilgan) dagi HAR BIR qoidani kod
bilan solishtiradi va natijani `reports/faza_2_kkt_spec_conformance.md` ga
yozadi (conformance matrix).

HOLATLAR (topshiriq ta'rifi):
  TO'LIQ MOS  — qoida kodda bor va docx misoli bilan bir xil natija beradi
  QISMAN MOS  — qoida kodda bor, lekin natija docx misolidan farq qiladi
  YO'Q        — qoida kodda umuman implement qilinmagan
  ZID         — kod docx'ga zid boshqa qoida bilan ishlaydi

HAR BIR HOLAT KODNI CHAQIRIB OLINADI (taxmin emas). Qoidalar 4 turga
bo'lingan (`PROBES`), chunki "qoida" ba'zan affiks, ba'zan so'z tartibi,
ba'zan esa bitta leksik moslik:

  M (morfologik)  — docx "asos + affiks = natija" beradi. Tekshiruv LUG'ATDAN
      MUSTAQIL: `stub_lexicon()` UB_en_w/UB_uz_w o'rniga FAQAT docx'ning o'zidagi
      o'zakni (masalan capability->imkoniyat) ko'rsatadi, so'ng HAQIQIY
      `translate_phrase()` zanjiri ishga tushadi. Shunday qilib "o'zak lug'atda
      yo'q" (lug'at bo'shlig'i) va "qoida noto'g'ri" (qoida bo'shlig'i) bir-
      biridan ajratiladi. Holat: affiks + turkum tanildimi, natija mosmi.
  N (noqoida)     — o'zak o'zgaradigan shakllar (man->men, good->better).
      Xuddi M kabi stub bilan; o'zak tanildimi (masalan NLTK lemmatizer
      orqali), natija mosmi.
  S (ibora)       — so'z tartibi/funksional so'z qoidasi (artikl, more/most,
      to+fe'l, son birikmalari). Stub: docx'dagi mazmunli so'zlar. Mos
      kelmasa: kodda AYNAN shu hodisa uchun alohida qoida bo'lsa (`mex`,
      masalan `_DETERMINERS` artiklni tashlaydi) — ZID, bo'lmasa — YO'Q.
  L (leksik)      — qoida bitta so'z moslashuvidan iborat (can->qila olmoq,
      I->men). Stub ma'nosiz (natija o'zi stub bo'lardi), shu sabab HAQIQIY
      lug'at bilan tekshiriladi va natija qayerdan kelgani (1500-so'zlik
      lug'at / CH2_EVX_EXAMPLES — aylanma / kod ichidagi SEED_WORDS) qayd
      etiladi.

Stub rejimida ham `SEED_WORDS` (kod ichidagi o'rnatilgan minimal lug'at:
from/to/my/and ...) ko'rinadi — ular tashqi ma'lumot emas, kodning o'zi.

Qo'shimcha ravishda HAR BIR qoida uchun (B) HAQIQIY lug'at bilan natija ham
chiqariladi — faqat dalil sifatida (holatga ta'sir qilmaydi, L turidan
tashqari).

Bazalar har safar data/ dan IZOLYATSIYALANGAN vaqtinchalik papkada noldan
quriladi (tests/conftest.py bilan bir xil ketma-ketlik) — repo ildizidagi
.db fayllarga tegilmaydi, natija faqat git'dagi fayllarga bog'liq.

Ishlatish:
    python scripts/audit_kkt_spec_conformance.py
    python scripts/audit_kkt_spec_conformance.py --no-out   # faqat konsolga
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from _common import normalize  # noqa: E402

SPEC_PATH = os.path.join(REPO_ROOT, "data", "kkt_spec.json")
LEX_1500_PATH = os.path.join(REPO_ROOT, "data", "1500_EN_UZ_6_POS_sorted.20.json")
DEFAULT_OUT = os.path.join(REPO_ROOT, "reports", "faza_2_kkt_spec_conformance.md")

TOLIQ, QISMAN, YOQ, ZID = "TO'LIQ MOS", "QISMAN MOS", "YO'Q", "ZID"
HOLATLAR = (TOLIQ, QISMAN, YOQ, ZID)

NOUNS, VERBS, ADJS, ADVS = ("NOUNS (OTLAR)", "VERBS (FE'LLAR)",
                            "ADJECTIVES (SIFATLAR)", "ADVERBS (RAVISHLAR)")


def _p(tur, juftlar, stub=(), aff=None, soz=None, mex=None, bosh=None,
       izoh=None, asos=None, sirt=None):
    """Bitta qoida uchun tekshiruv tavsifi.

    juftlar — [(EN kirish, kutilgan UZ natija), ...] — docx katagidan: "+"
              bilan ajratilgan qismlar qo'shilgan, qavs ichidagi izoh va "…"
              olib tashlangan, tipografik apostrof ASCII ga almashtirilgan
              (kod faqat ASCII ' ni taniydi). Kuzatiluvchanlik testi:
              tests/test_kkt_spec_conformance.py::test_probe_values_trace_to_docx_cells
    stub    — [(en, uz, pos) yoki (en, uz, pos, manba_uid)] — M/N/S uchun
              ko'rinadigan yagona lug'at; manba_uid — qiymat boshqa qoida
              katagidan olingan bo'lsa.
    aff     — M: kod tanishi kerak bo'lgan inglizcha affiks.
    soz     — M: tahlil qilinadigan token (standart: 1-juftning oxirgi so'zi).
    mex     — S: kodda AYNAN shu hodisaga tegishli qoida — (belgi, tavsif).
    bosh    — L: lug'atda borligi tekshiriladigan bosh so'z(lar).
    asos    — ustuvorlik: qoida qo'llanadigan 1500-lug'at kategoriyasi.
    sirt    — ustuvorlik: 1500-lug'atda sirt shakli shu qoidaga mos so'zlar regexi.
    """
    return {"tur": tur, "juftlar": list(juftlar), "stub": list(stub), "aff": aff,
            "soz": soz, "mex": mex, "bosh": bosh, "izoh": izoh, "asos": asos, "sirt": sirt}


_DET = ("_DETERMINERS", "aniq artikl \"the\" va ko'rsatish so'zlarini (this/that ...) iboradan olib tashlaydi")
_INDEF = ("_INDEFINITE_ARTICLE_UZ", "noaniq artikl a/an — keyin ot kelsa, ot iborasiga \"bitta\" bo'lib kiradi")
_TO_INF = ("INFINITIVE_PARTICLE_EN", "\"to\" + fe'l — infinitiv yuklamasi, tarjima qilinmaydi (spec 2.56)")
_TO_OBJ = ("PREP_OBJECT_VERBS", "(listen, to): predlog tushadi, to'ldiruvchi vositasiz; me/him/us obyekt shakli "
           "(OBJECT_CASE_PRONOUNS) qayta \"-ni\" olmaydi")
_INF_IZOH = ("`INFINITIVE_MARKERS` (to/will/can/...) kodda bor, lekin faqat `select_meaning_contextual()` da "
             "ko'p ma'noli so'zning Fe'l ma'nosini TANLASH uchun ishlatiladi — \"will + fe'l\" uchun tarjima "
             "qoidasi emas.")
# Stub'dagi "⟨...⟩" qiymat — ma'lumot emas, BELGI: docx o'zakning o'zbekchasini
# bermagan joyda kod o'zbek tomonini qanday qurishini ko'rsatish uchun.
_PLACEHOLDER_RE = re.compile(r"^⟨.*⟩$")
# MORPH_RULES dan tashqari, _smart_parse_core ichidagi alohida tarmoq bilan
# ishlanadigan affikslar (kodda qoida BOR — faqat boshqa joyda).
_SPECIAL_BRANCH = {"'s": "w.endswith(\"'s\")"}

PROBES = {
    # ── OT ──────────────────────────────────────────────────────────────
    "2.1": _p("M", [("variables", "o‘zgaruvchilar")], [("variable", "o‘zgaruvchi", "Ot")], aff="s",
              asos=NOUNS, sirt=r"[^s]s$"),
    "2.2": _p("S", [("a network", "bitta tarmoq")], [("network", "tarmoq", "Ot")], mex=_INDEF, asos=NOUNS),
    "2.3": _p("S", [("an example", "bitta misol")], [("example", "misol", "Ot")], mex=_INDEF, asos=NOUNS),
    "2.4": _p("S", [("the progress", "taraqqiyot")], [("progress", "taraqqiyot", "Ot")], mex=_DET, asos=NOUNS),
    "2.5": _p("M", [("The Germanys", "Germaniyaliklar")], [("germany", "Germaniya", "Ot")], aff="s",
              asos=NOUNS),
    "2.6": _p("M", [("processes", "jarayonlar")], [("process", "jarayon", "Ot")], aff="es",
              asos=NOUNS, sirt=r"(s|ss|x|ch|sh)es$"),
    "2.7": _p("M", [("capabilities", "imkoniyatlar")], [("capability", "imkoniyat", "Ot")], aff="ies",
              asos=NOUNS, sirt=r"[^aeiou]ies$"),
    "2.8": _p("M", [("delays", "kechikishlar")], [("delay", "kechikish", "Ot")], aff="s",
              asos=NOUNS, sirt=r"[aeiou]ys$"),
    "2.9": _p("M", [("leaves", "barglar")], [("leaf", "barg", "Ot")], aff="ves",
              asos=NOUNS, sirt=r"ves$"),
    "2.10": _p("N", [("men", "erkaklar")], [("man", "erkak", "Ot")]),
    "2.11": _p("M", [("customhouses", "bojxonalar")], [("customhouse", "bojxona", "Ot")], aff="s",
               izoh="Stub o'zagi \"customhouse\" — docx'dagi \"custom + houses = customhouses\" ning birligi "
                    "(docx'da alohida yozilmagan).", asos=NOUNS),
    "2.12": _p("M", [("schoolboys", "maktab bolalari")], [("schoolboy", "maktab bola", "Ot")], aff="s",
               asos=NOUNS),
    "2.13": _p("M", [("information", "axborot")], [("inform", "⟨inform⟩", "Fe'l")], aff="ation",
               izoh="Docx \"inform\" ning o'zbekchasini bermagan, natija esa affikssiz (\"axborot\") — shu sabab "
                    "stub'da `⟨inform⟩` BELGI (ma'lumot emas) ishlatildi: u faqat kod o'zbek tomonini qanday "
                    "qurishini ko'rsatadi. Natija \"axborot\" ga faqat butun so'z lug'atda bo'lsa teng bo'la oladi.",
               asos=VERBS, sirt=r"ation$"),
    "2.15": _p("M", [("contents", "mundarija")], [("content", "mundarija", "Ot")], aff="s",
               izoh="Spec: jamlama ot o'zbekchaga BIRLIK bilan (\"mundarija\"). Stub o'zagi \"content\" → "
                    "\"mundarija\" (docx'dagi birlik tarjima).", asos=NOUNS),
    "2.16": _p("M", [("student's", "studentning")], [("student", "student", "Ot")], aff="'s",
               asos=NOUNS),
    # ── SIFAT ───────────────────────────────────────────────────────────
    "–(Sifat)": _p("L", [("big", "katta")], bosh=["big"]),
    "2.19": _p("M", [("formal", "rasmiy")], [("form", "rasm", "Ot")], aff="al", asos=NOUNS, sirt=r"al$"),
    "2.20": _p("M", [("high-dimensional", "ko‘p o‘lchovli")],
               [("high", "ko‘p", "Sifat"), ("dimension", "o‘lchov", "Ot")], aff="al", soz="dimensional",
               izoh="Docx natija shaklini bermagan — kirish/kutilgan qiymat \"+\" qismlarini qo'shib olingan.",
               asos=NOUNS),
    "2.21": _p("M", [("cleverer", "aqillroq")], [("clever", "aqilli", "Sifat", "2.22")], aff="er",
               asos=ADJS, sirt=r"er$"),
    "2.22": _p("M", [("cleverest", "eng aqilli")], [("clever", "aqilli", "Sifat")], aff="est",
               asos=ADJS, sirt=r"est$"),
    "2.23": _p("M", [("larger", "kattaroq")], [("large", "katta", "Sifat")], aff="er", asos=ADJS, sirt=r"er$"),
    "2.24": _p("M", [("largest", "eng katta")], [("large", "katta", "Sifat")], aff="est", asos=ADJS, sirt=r"est$"),
    "2.25": _p("M", [("bigger", "kattaroq")], [("big", "katta", "Sifat")], aff="er", asos=ADJS, sirt=r"er$"),
    "2.26": _p("M", [("biggest", "eng katta")], [("big", "katta", "Sifat")], aff="est", asos=ADJS, sirt=r"est$"),
    "2.27": _p("M", [("busier", "bandroq")], [("busy", "band", "Sifat")], aff="ier", asos=ADJS, sirt=r"ier$"),
    "2.28": _p("M", [("busiest", "eng band")], [("busy", "band", "Sifat")], aff="iest", asos=ADJS, sirt=r"iest$"),
    "2.29": _p("M", [("gayer", "sho‘xroq")], [("gay", "sho‘x", "Sifat")], aff="er", asos=ADJS, sirt=r"yer$"),
    "2.30": _p("M", [("gayest", "eng sho‘x")], [("gay", "sho‘x", "Sifat")], aff="est", asos=ADJS, sirt=r"yest$"),
    "2.31": _p("S", [("more comfortable", "qulayroq")], [("comfortable", "qulay", "Sifat")], asos=ADJS),
    "2.32": _p("S", [("most comfortable", "eng qulay")], [("comfortable", "qulay", "Sifat", "2.31")], asos=ADJS),
    "2.33": _p("N", [("good", "yaxshi"), ("better", "yaxshiroq"), ("best", "eng yaxshi")],
               [("good", "yaxshi", "Sifat")]),
    "2.34": _p("S", [("less interesting", "kamroq qiziqarli")], [("interesting", "qiziqarli", "Sifat")],
               asos=ADJS),
    # ── FE'L ────────────────────────────────────────────────────────────
    "2.36": _p("L", [("read", "o‘qimoq")], bosh=["read"]),
    "2.37": _p("M", [("speaks", "gapiradi")], [("speak", "gapir", "Fe'l")], aff="s", asos=VERBS),
    "2.38": _p("L", [("to be", "bo‘lmoq")], bosh=["be"]),
    "2.39": _p("L", [("am", "man")], bosh=["am"]),
    "2.41": _p("L", [("was", "edi"), ("were", "edi")], bosh=["was", "were"]),
    "2.42": _p("N", [("been", "bo‘lgan")], [("be", "bo‘lmoq", "Fe'l", "2.38")]),
    "2.43": _p("M", [("being", "bo‘layotgan")], [("be", "bo‘lmoq", "Fe'l", "2.38")], aff="ing",
               asos=VERBS, sirt=r"ing$"),
    "2.44": _p("L", [("to have", "bor bo‘lmoq")], bosh=["have"]),
    "2.45": _p("L", [("to do", "qilmoq")], bosh=["do"]),
    "2.46": _p("L", [("will", "keladi")], bosh=["will"]),
    "2.47": _p("L", [("would", "edi")], bosh=["would"]),
    "2.48": _p("L", [("become", "bo‘lmoq")], bosh=["become"]),
    "2.49": _p("L", [("can", "qila olmoq")], bosh=["can"]),
    "2.50": _p("L", [("could", "olardi")], bosh=["could"]),
    "2.51": _p("L", [("may", "mumkin")], bosh=["may"]),
    "2.52": _p("L", [("might", "mumkin")], bosh=["might"]),
    "2.53": _p("L", [("must", "kerak")], bosh=["must"]),
    "2.54": _p("L", [("ought to", "zarur")], bosh=["ought"]),
    "2.55a": _p("L", [("need", "kerak")], bosh=["need"]),
    "2.56": _p("S", [("to ask", "so‘ramoq")], [("ask", "so‘ramoq", "Fe'l")], mex=_TO_INF, asos=VERBS),
    "2.55b": _p("M", [("reading", "o‘qishni")], [("read", "o‘qimoq", "Fe'l", "2.36")], aff="ing",
                asos=VERBS, sirt=r"ing$"),
    "2.58": _p("L", [("to follow", "kuzatmoq")], bosh=["follow"]),
    "2.59": _p("S", [("listen to me", "meni tinglamoq")],
               [("listen", "tinglamoq", "Fe'l"), ("me", "meni", "Olmosh", "3.22")], mex=_TO_OBJ, asos=VERBS),
    "2.61": _p("L", [("understand", "tushunmoq")], bosh=["understand"]),
    "2.62": _p("S", [("will return", "qaytmoq")], [("return", "qaytmoq", "Fe'l")], asos=VERBS, izoh=_INF_IZOH),
    "2.63": _p("M", [("worked", "ishladi")], [("work", "ishla", "Fe'l")], aff="ed", asos=VERBS, sirt=r"ed$"),
    "2.64": _p("M", [("simplified", "soddalashtirildi")], [("simplify", "soddalashtiril", "Fe'l")], aff="ied",
               asos=VERBS, sirt=r"[^aeiou]ied$"),
    "2.65": _p("N", [("send", "yubormoq"), ("sent", "yubordi"), ("sent", "yuborgan")],
               [("send", "yubormoq", "Fe'l")],
               izoh="Bitta inglizcha \"sent\" ikki xil o'zbekcha shaklga (yubordi / yuborgan) mos keladi — "
                    "kontekstsiz bitta so'z uchun ikkala juft bir vaqtda mos kelishi mumkin emas."),
    # ── RAVISH ──────────────────────────────────────────────────────────
    "–(Ravish)": _p("L", [("very", "juda")], bosh=["very"]),
    "3.1": _p("L", [("here", "shu yerda")], bosh=["here"]),
    "3.2": _p("M", [("easily", "osonlik bilan")], [("easy", "oson", "Sifat")], aff="ily",
              asos=ADJS, sirt=r"ily$"),
    "3.3": _p("M", [("faster", "tezroq")], [("fast", "tez", "Ravish")], aff="er", asos=ADVS, sirt=r"er$"),
    "3.4": _p("M", [("fastest", "eng tez")], [("fast", "tez", "Ravish")], aff="est", asos=ADVS, sirt=r"est$"),
    "3.5": _p("S", [("more clearly", "aniqroq")], [("clearly", "aniq", "Ravish")], asos=ADVS, sirt=r"ly$"),
    "3.6": _p("L", [("inside", "ichkarida")], bosh=["inside"]),
    "3.7": _p("L", [("today", "bugun")], bosh=["today"]),
    "3.8": _p("L", [("much", "ko‘p")], bosh=["much"]),
    "3.9": _p("M", [("quietly", "tinchgina")], [("quiet", "tinch", "Sifat")], aff="ly",
              asos=ADJS, sirt=r"ly$"),
    # ── SON ─────────────────────────────────────────────────────────────
    "3.11": _p("L", [("one", "bir")], bosh=["one"]),
    "3.12": _p("M", [("fifteen", "o‘n besh")], [("fif", "besh", "Son")], aff="teen",
               izoh="Stub o'zagi docx'dagidek \"fif\" (\"fif + teen\"). Kodda \"five\" -> \"fif\" tiklash "
                    "funksiyasi yo'q (MORPH_RULES \"teen\": faqat w[:-4]) — shu sabab real lug'atda bu qoida "
                    "\"five\" o'zagi bilan ishlamaydi.", sirt=r"teen$"),
    "3.13": _p("M", [("eighty", "sakson")], [("eigh", "⟨eigh⟩", "Son")], aff="ty",
               izoh="Docx o'zak \"eigh\" ning o'zbekchasini bermagan, natija affikssiz (\"sakson\") — stub'da "
                    "`⟨eigh⟩` BELGI ishlatildi (2.13 dagi kabi).", sirt=r"ty$"),
    "3.14": _p("S", [("eighty-five", "sakson besh")], [("eighty", "sakson", "Son"), ("five", "besh", "Son", "3.12")]),
    "3.15": _p("S", [("one hundred", "bir yuz")], [("one", "bir", "Son"), ("hundred", "yuz", "Son", "3.18")]),
    "3.16": _p("S", [("four million", "to‘rt million")], [("four", "to‘rt", "Son"), ("million", "million", "Son")]),
    "3.17": _p("S", [("three hundred and five", "uch yuz besh")],
               [("three", "uch", "Son"), ("hundred", "yuz", "Son"), ("five", "besh", "Son")]),
    "3.18": _p("M", [("hundredth", "yuzinchi")], [("hundred", "yuz", "Son")], aff="th", sirt=r"th$"),
    "3.19": _p("S", [("hundred and twenty-first", "bir yuz yigirma birinchi")],
               [("hundred", "yuz", "Son"), ("twenty", "yigirma", "Son")],
               izoh="Docx natija shaklini bermagan (\"bir yuz yigirma bir + inchi\") — qismlar qo'shildi. "
                    "\"first\" uchun stub berilmadi: docx uni \"bir + inchi\" deb yozadi, ya'ni tartib son "
                    "qoidasining o'zi tekshiriladi."),
    "3.20": _p("S", [("chapter five", "beshinchi bob")], [("chapter", "bob", "Ot"), ("five", "besh", "Son")]),
    # ── OLMOSH ──────────────────────────────────────────────────────────
    "3.22": _p("L", [("I", "men"), ("he", "u"), ("we", "biz"), ("me", "meni"), ("him", "uni"), ("us", "bizni")],
               bosh=["i", "he", "we", "me", "him", "us"]),
    "3.23": _p("L", [("I", "men"), ("he", "u"), ("she", "u"), ("it", "u"), ("we", "biz"), ("you", "siz"),
                     ("they", "ular")], bosh=["i", "he", "she", "it", "we", "you", "they"]),
    "3.24": _p("L", [("my", "menning"), ("his", "uning"), ("our", "bizning"), ("your", "sizning"),
                     ("their", "ularning")], bosh=["my", "his", "our", "your", "their"],
               izoh="Docx natija shaklini bermagan (\"men + ning\") — qismlar qo'shildi: \"menning\"."),
    "3.25": _p("L", [("mine", "menniki"), ("ours", "bizning"), ("yours", "sizning"), ("theirs", "ularning")],
               bosh=["mine", "ours", "yours", "theirs"],
               izoh="Docx natija shaklini bermagan — qismlar qo'shildi. Docx katagidagi nomuvofiqlik uchun "
                    "data/kkt_spec.json `izoh` ga qarang."),
    "3.26": _p("L", [("who", "kim"), ("whom", "kimni"), ("whose", "kimning"), ("what", "nima"),
                     ("which", "qaysi")], bosh=["who", "whom", "whose", "what", "which"]),
    "3.27": _p("L", [("some", "ba’zi"), ("someone", "kimdir"), ("any", "har qanday"), ("no", "yo‘q"),
                     ("much", "ko‘p"), ("many", "ko‘pchilik"), ("all", "hamma"), ("each", "har bir")],
               bosh=["some", "someone", "any", "no", "much", "many", "all", "each"]),
    "3.28": _p("L", [("myself", "o‘zim"), ("yourself", "o‘zing"), ("himself", "o‘zi"), ("ourselves", "o‘zimiz")],
               bosh=["myself", "yourself", "himself", "ourselves"]),
}


# ═══════════════════════════════════════════════════════════════════
#  Izolyatsiyalangan modul (tests/conftest.py bilan bir xil ketma-ketlik)
# ═══════════════════════════════════════════════════════════════════
def build_isolated_module(tmp_dir: str):
    for item in ("kkt_v20_soz_tartibi.py", "data_loader.py", "data"):
        src, dst = os.path.join(REPO_ROOT, item), os.path.join(tmp_dir, item)
        shutil.copytree(src, dst) if os.path.isdir(src) else shutil.copy2(src, dst)
    for name in ("kkt_v20_soz_tartibi", "data_loader"):
        sys.modules.pop(name, None)
    sys.path.insert(0, tmp_dir)
    with contextlib.redirect_stdout(io.StringIO()):
        import kkt_v20_soz_tartibi as m
        assert m.SCRIPT_DIR == tmp_dir, "modul izolyatsiyalangan nusxadan import qilinmadi"
        m._safe_step("init_all_databases", m.init_all_databases)
        docx_path = m._safe_step("find_docx", m.find_docx) if m.HAS_DOCX else None
        m._safe_step("setup_database", m.setup_database, docx_path)
        m._safe_step("load_xlsx_affixes", m.load_xlsx_affixes)
        bz = m._safe_step("find_bazalar_docx", m.find_bazalar_docx)
        if bz:
            m._safe_step("load_bazalar_docx", m.load_bazalar_docx, bz)
        m._safe_step("seed_core_demo_data", m.seed_core_demo_data)
        bz2 = m._safe_step("find_bazalar_affixes_docx", m.find_bazalar_affixes_docx)
        if bz2:
            m._safe_step("load_bazalar_affixes_docx", m.load_bazalar_affixes_docx, bz2)
        m._safe_step("load_pdf_kkt_bazalar", m.load_pdf_kkt_bazalar)
        m._safe_step("load_ch2_evx_examples", m.load_ch2_evx_examples)
        m._safe_step("resync_all_ids", m.resync_all_ids)
        m._safe_step("mdb_seed_if_empty", m.mdb_seed_if_empty)
    return m


# ═══════════════════════════════════════════════════════════════════
#  Stub lug'at — M/N/S qoidalari uchun lug'atdan mustaqil tekshiruv
# ═══════════════════════════════════════════════════════════════════
@contextlib.contextmanager
def stub_lexicon(m, entries):
    """`db_lookup`/`db_lookup_all`/`db_lookup_by_id` ni vaqtincha almashtiradi:
    faqat `entries` + `m.SEED_WORDS` ko'rinadi. Kod runtime'da so'z jadvaliga
    faqat shu 3 funksiya orqali murojaat qiladi (grep "FROM words"), QM/BM/MDB
    bazalari o'zgarishsiz qoladi. Chiqishda asl funksiyalar tiklanadi."""
    lex: dict[str, tuple] = {}
    by_id: dict[int, tuple] = {}
    next_id = 9_000_000
    probe_words = {e[0].lower() for e in entries}
    rows = [(e[0], e[1], e[2], "stub") for e in entries]
    rows += [(en, uz, pos, "seed(kod)") for en, uz, pos in m.SEED_WORDS if en.lower() not in probe_words]
    for en, uz, pos, src in rows:
        next_id += 1
        row = (next_id, en.lower(), uz, pos, src, None)
        lex.setdefault(en.lower(), []).append(row)
        by_id[next_id] = row

    def db_lookup(english):
        r = lex.get(english.lower().strip())
        return (r[0][1], r[0][2], r[0][3], r[0][4]) if r else None

    def db_lookup_all(english):
        return list(lex.get(english.lower().strip(), []))

    def db_lookup_by_id(db_path, wid):
        r = by_id.get(wid)
        if r is None:
            return None
        return (r[0], r[2], r[1], r[3], r[4], r[5]) if db_path == m.DB_UB_UZ else r

    orig = (m.db_lookup, m.db_lookup_all, m.db_lookup_by_id)
    m.db_lookup, m.db_lookup_all, m.db_lookup_by_id = db_lookup, db_lookup_all, db_lookup_by_id
    try:
        yield
    finally:
        m.db_lookup, m.db_lookup_all, m.db_lookup_by_id = orig


# ═══════════════════════════════════════════════════════════════════
#  Tizim chiqishi va solishtiruv
# ═══════════════════════════════════════════════════════════════════
def _tokens_info(m, aa):
    """Har bir token uchun tahlil + (to'g'ridan lug'atdan topilgan bo'lsa)
    TANLANGAN qatorning manbasi (`source`): tarjimasi VA turkumi natijaga
    teng qator(lar); topilmasa (masalan MDB almashtirgan) — barcha qatorlar."""
    out = []
    for a in aa:
        sources = []
        if a["found"] and a["method"].startswith("UB_en_w[ID]"):
            rows = m.db_lookup_all(a["word"])
            chosen = [r for r in rows if normalize(r[2]) == normalize(a["uz"]) and r[3] == a["pos"]]
            sources = sorted({r[4] for r in (chosen or rows)})
        out.append({"word": a["word"], "found": a["found"], "uz": a["uz"], "pos": a["pos"],
                    "method": a["method"], "suffix": a["suffix"], "root": a["root"], "sources": sources})
    return out


def system_output(m, text: str) -> dict:
    """GUI'dagi `_translate` bilan bir xil: `translate_phrase()` natija
    bersa — o'sha, aks holda so'zma-so'z (topilmagan so'z "[so'z?]")."""
    with m.readonly_mode():
        r = m.translate_phrase(text, allow_write=False)
        aa = m.parse_sentence(text)
        tokens = _tokens_info(m, aa)
    if r:
        return {"natija": r["natija"], "yol": "translate_phrase", "tokens": tokens}
    joined = " ".join(t["uz"] if t["found"] else f"[{t['word']}?]" for t in tokens)
    return {"natija": joined, "yol": "so'zma-so'z", "tokens": tokens}


_PAREN_RE = re.compile(r"\s*\([^)]*\)")


def _clean(s: str) -> str:
    return normalize(_PAREN_RE.sub("", s).replace("…", "")) or ""


def compare(output: str, expected: str, single_token: bool) -> str | None:
    """"aniq" — normalizatsiyadan keyin teng; "variant" — (faqat bitta
    so'zli kirish uchun) lug'at yozuvidagi " / " bilan ajratilgan
    variantlardan biri, qavs ichidagi izohsiz, kutilganga teng
    (masalan "Meni / Menga" ~ "meni", "U (erkak)" ~ "u"); None — mos emas."""
    exp = _clean(expected)
    if normalize(output) == exp:
        return "aniq"
    if single_token and _clean(output) == exp:
        return "variant"
    if single_token and exp in {_clean(v) for v in output.split("/")}:
        return "variant"
    return None


def _token_path(t: dict) -> str:
    if not t["found"]:
        return f"{t['word']}: topilmadi"
    if t["method"].startswith("UB_en_w[ID]"):
        src = ",".join(t["sources"]) or "?"
        extra = " +MDB almashtirdi" if "MDB_uz_w" in t["method"] else ""
        return f"{t['word']}: lug'at[{src}]{extra}"
    return f"{t['word']}: qoida -{t['suffix'] or '∅'} (o'zak {t['root']}, {t['pos']})"


# ═══════════════════════════════════════════════════════════════════
#  Qoidani baholash
# ═══════════════════════════════════════════════════════════════════
def _run_pairs(m, pairs):
    res = []
    for en, exp in pairs:
        out = system_output(m, en)
        res.append({"en": en, "kutilgan": exp, "natija": out["natija"], "yol": out["yol"],
                    "tokens": out["tokens"], "mos": compare(out["natija"], exp, " " not in en.strip())})
    return res


def _analysis_token(pair_res, soz):
    toks = pair_res["tokens"]
    if soz:
        for t in toks:
            if t["word"] == soz.lower():
                return t
    return toks[-1] if toks else None


def _docx_components(cell: str) -> str | None:
    """"A + B = C" katagida "+" qismlari qo'shilganda C dan FARQLI shakl
    hosil bo'lsa — o'sha shakl (docx ichki nomuvofiqligi, masalan
    "aqil + li + roq = aqillroq" -> "aqilliroq"); aks holda None."""
    if cell.count("=") != 1 or "+" not in cell:
        return None
    lhs, rhs = (x.strip() for x in cell.split("="))
    lhs = lhs.split("→")[-1]
    joined = re.sub(r"\s*\+\s*", "", lhs).strip()
    return joined if joined != rhs else None


def _mark_docx_internal(pairs, rule):
    alt = _docx_components(rule["uz_misol"])
    for p in pairs:
        p["docx_ichki"] = alt if (alt and not p["mos"] and compare(p["natija"], alt, True)) else None


def evaluate_rule(m, rule: dict, probe: dict) -> dict:
    tur = probe["tur"]
    stub = [s[:3] for s in probe["stub"]]
    real = _run_pairs(m, probe["juftlar"])
    _mark_docx_internal(real, rule)
    ev = {"uid": rule["uid"], "pos": rule["pos"], "tur": tur, "probe": probe, "real": real}

    if tur == "L":
        n_mos = sum(1 for p in real if p["mos"])
        found = {t["word"]: t["found"] for p in real for t in p["tokens"]}
        n_bosh = sum(1 for b in probe["bosh"] if found.get(b))
        if n_mos == len(real):
            holat = TOLIQ
        elif n_mos or n_bosh:
            holat = QISMAN
        else:
            holat = YOQ
        ev.update(holat=holat, n_mos=n_mos, n_jami=len(real), n_bosh=n_bosh)
        return ev

    with stub_lexicon(m, stub):
        mech = _run_pairs(m, probe["juftlar"])
    _mark_docx_internal(mech, rule)
    ev["mech"] = mech
    n_mos = sum(1 for p in mech if p["mos"])
    ev.update(n_mos=n_mos, n_jami=len(mech))
    stub_roots = {s[0].lower() for s in stub}

    if tur == "M":
        aff = probe["aff"]
        a = _analysis_token(mech[0], probe["soz"])
        last_sfx = (a["suffix"] or "").split("+")[-1] if a else ""
        tanildi = bool(a and a["found"] and last_sfx == aff and a["root"] in stub_roots)
        pos_ok = bool(a and a["pos"] == rule["pos"])
        # Kodda shu affiks uchun qoida BORMI (tanilmagan bo'lsa ham) — va
        # bo'lsa, uning o'zak-tiklash funksiyalari qanday nomzod beradi.
        soz = (probe["soz"] or probe["juftlar"][0][0].split()[-1]).lower()
        qoida_bor = aff in _SPECIAL_BRANCH or any(r[0] == aff for r in m.MORPH_RULES)
        nomzodlar = []
        for r in m.MORPH_RULES:
            if r[0] == aff and soz.endswith(aff):
                for fn in r[1]:
                    try:
                        c = fn(soz)
                    except Exception:
                        continue
                    if c not in nomzodlar:
                        nomzodlar.append(c)
        ev.update(tahlil=a, tanildi=tanildi, pos_ok=pos_ok, qoida_bor=qoida_bor, nomzodlar=nomzodlar)
        if tanildi and pos_ok:
            holat = TOLIQ if n_mos == len(mech) else QISMAN
        elif tanildi:
            holat = QISMAN if n_mos == len(mech) else ZID
        elif qoida_bor or n_mos == len(mech):
            holat = QISMAN
        else:
            holat = YOQ
    elif tur == "N":
        irregular = [p for p in mech if p["en"].lower() not in stub_roots]
        tanildi = any(t["found"] and t["root"] in stub_roots for p in irregular for t in p["tokens"])
        ev.update(tanildi=tanildi)
        if n_mos == len(mech):
            holat = TOLIQ
        elif tanildi or any(p["mos"] for p in irregular):
            holat = QISMAN
        else:
            holat = YOQ
    else:  # S
        if n_mos == len(mech):
            holat = TOLIQ
        elif probe["mex"]:
            holat = ZID
        else:
            holat = YOQ
    ev["holat"] = holat
    return ev


# ═══════════════════════════════════════════════════════════════════
#  Kod joylashuvi (dalil ustuni uchun — qator raqamlari manba fayldan
#  avtomatik o'qiladi, qo'lda yozilmagan)
# ═══════════════════════════════════════════════════════════════════
class CodeIndex:
    def __init__(self, path: str):
        with open(path, encoding="utf-8") as f:
            self.lines = f.read().splitlines()
        self._morph = self._block("MORPH_RULES = [", "]")
        self._make_uz = self._block("def make_uzbek(", None)

    def _block(self, start: str, end: str | None) -> tuple[int, int]:
        s = next(i for i, ln in enumerate(self.lines) if ln.startswith(start))
        for j in range(s + 1, len(self.lines)):
            ln = self.lines[j]
            if (end is not None and ln == end) or (end is None and ln.startswith(("def ", "# ═"))):
                return s, j
        return s, len(self.lines)

    def morph_rule_lines(self, aff: str) -> list[int]:
        s, e = self._morph
        pat = re.compile(r'^\s*\(' + re.escape(json.dumps(aff)) + r",")
        return [i + 1 for i in range(s, e) if pat.match(self.lines[i])]

    def make_uzbek_line(self, aff: str) -> int | None:
        s, e = self._make_uz
        key = json.dumps(aff)
        return next((i + 1 for i in range(s + 1, e) if key in self.lines[i]), None)

    def symbol_line(self, name: str) -> int | None:
        pat = re.compile(r"^" + re.escape(name) + r"\s*=")
        return next((i + 1 for i, ln in enumerate(self.lines) if pat.match(ln)), None)

    def find(self, needle: str) -> int | None:
        return next((i + 1 for i, ln in enumerate(self.lines) if needle in ln), None)

    def affix_location(self, aff: str) -> str:
        if aff in _SPECIAL_BRANCH:
            return f"_smart_parse_core:{self.find(_SPECIAL_BRANCH[aff])} (alohida tarmoq)"
        lines = self.morph_rule_lines(aff)
        mu = self.make_uzbek_line(aff)
        return f"MORPH_RULES:{','.join(map(str, lines)) or '—'}" + (f", make_uzbek:{mu}" if mu else "")


def _fmt_pair(p: dict) -> str:
    mark = {"aniq": "✓", "variant": "✓(variant)"}.get(p["mos"], "✗")
    s = f"`{p['en']}` → «{p['natija']}» (kutilgan «{p['kutilgan']}») {mark}"
    if p.get("docx_ichki"):
        s += f" ⚠ natija docx katagining \"+\" qismlari yig'indisiga («{p['docx_ichki']}») teng"
    return s


def build_dalil(ev: dict, idx: CodeIndex, m) -> str:
    probe, tur = ev["probe"], ev["tur"]
    parts = []
    if tur == "M":
        a = ev["tahlil"]
        tah = (f"tahlil: -{a['suffix'] or '∅'} + {a['root']} → {a['pos'] or '—'}" if a and a["found"]
               else "tahlil: topilmadi")
        s = f"{idx.affix_location(probe['aff'])}; stub: {tah}"
        if not ev["tanildi"] and ev["qoida_bor"]:
            s += (f"; qoida BOR, lekin bu so'zni tanimadi — o'zak tiklash nomzodlari: "
                  f"{', '.join(ev['nomzodlar']) or '—'} (stub o'zagi: "
                  f"{', '.join(x[0] for x in probe['stub'])})")
        parts.append(s)
    elif tur == "S" and probe["mex"]:
        name, desc = probe["mex"]
        parts.append(f"{name}:{idx.symbol_line(name)} — {desc}")
    elif tur == "S" and ev["holat"] == TOLIQ:
        parts.append("kodda bu hodisa uchun maxsus qoida yo'q — natija so'zma-so'z birikmadan kelib chiqdi")
    elif tur == "N":
        parts.append(f"o'zak tanildi: {'ha' if ev['tanildi'] else 'yo‘q'} (USE_LEMMA={m.USE_LEMMA})")
    rows = ev["mech"] if tur != "L" else ev["real"]
    label = "stub" if tur != "L" else "real lug'at"
    shown = rows if len(rows) <= 3 else [p for p in rows if not p["mos"]][:3]
    parts.append(f"{label}: " + "; ".join(_fmt_pair(p) for p in shown)
                 + (f" … ({ev['n_mos']}/{ev['n_jami']} mos)" if len(rows) > 3 else ""))
    if tur == "L":
        parts.append("yo'l: " + "; ".join(_token_path(t) for p in ev["real"] for t in p["tokens"]
                                          if t["word"] not in {"to"})[:300])
    return " — ".join(parts).replace("|", "\\|")


# ═══════════════════════════════════════════════════════════════════
#  Ustuvorlik (Vazifa 4) — 1500-so'zlik lug'at bo'yicha qamrov
# ═══════════════════════════════════════════════════════════════════
def load_1500() -> dict[str, list[str]]:
    with open(LEX_1500_PATH, encoding="utf-8") as f:
        raw = json.load(f)["categories"]
    main = (NOUNS, VERBS, ADJS, ADVS, "PRONOUNS (OLMOSHLAR)",
            "CONJUNCTIONS & PREPOSITIONS (BOG'LOVCHI / KO'MAKCHI)")
    return {k: [e["english"].strip().lower() for e in raw[k]] for k in main}


def priority_row(probe: dict, lex: dict[str, list[str]]) -> dict:
    all_words = [w for ws in lex.values() for w in ws]
    asos_n = len(lex[probe["asos"]]) if probe["asos"] else None
    if probe["sirt"]:
        rx = re.compile(probe["sirt"])
        sirt = sorted({w for w in all_words if " " not in w and rx.search(w)})
    elif probe["tur"] == "L":
        sirt = sorted({b for b in probe["bosh"] if b in all_words})
    else:
        sirt = []
    return {"asos_n": asos_n, "sirt_n": len(sirt), "sirt_misol": sirt[:5]}


# ═══════════════════════════════════════════════════════════════════
#  Asosiy
# ═══════════════════════════════════════════════════════════════════
def load_spec() -> dict:
    with open(SPEC_PATH, encoding="utf-8") as f:
        return json.load(f)


def evaluate_all(m, spec: dict) -> list[dict]:
    missing = [r["uid"] for r in spec["rules"] if r["uid"] not in PROBES]
    if missing:
        raise KeyError(f"PROBES da yo'q qoidalar: {missing}")
    return [evaluate_rule(m, r, PROBES[r["uid"]]) for r in spec["rules"]]


def lemma_dependence(m, spec: dict, evs: list[dict]) -> dict[str, tuple[str, str]]:
    """Holati NLTK lemmatizer'ga bog'liq qoidalar: {uid: (joriy holat,
    USE_LEMMA=False dagi holat)}. CI/boshqa muhitda wordnet bo'lmasa natija
    shu ro'yxat bo'yicha farq qiladi."""
    if not m.USE_LEMMA:
        return {}
    before = {e["uid"]: e["holat"] for e in evs}
    m.USE_LEMMA = False
    try:
        after = {r["uid"]: evaluate_rule(m, r, PROBES[r["uid"]])["holat"] for r in spec["rules"]}
    finally:
        m.USE_LEMMA = True
    return {u: (before[u], after[u]) for u in before if before[u] != after[u]}


def side_checks(m, spec: dict, idx: CodeIndex) -> dict:
    """87 qoidadan tashqari: vaznlar, turkum belgilari, operatorlar."""
    weights = []
    with m.readonly_mode():
        for w in spec["pos_weights_manba"]:
            key = w["kalit"]
            runtime = m.bm_get_or_create_pos_model(m.DB_BM_EN, key)["weight"] if key in m.POS_V2 else None
            weights.append({**w, "pos_v2": m.POS_V2.get(key), "pos_kkt": m.POS_KKT.get(key),
                            "runtime_bm_en": runtime})
    return {"weights": weights, "pos_v2_line": idx.symbol_line("POS_V2"), "pos_kkt_line": idx.symbol_line("POS_KKT")}


def _code_affixes_not_in_spec(idx: CodeIndex, m) -> list[str]:
    tested = {p["aff"] for p in PROBES.values() if p["aff"]}
    code = []
    for rule in m.MORPH_RULES:
        if rule[0] not in tested and rule[0] not in code:
            code.append(rule[0])
    return code


MUSTAQIL = "mustaqil hisoblangan"
AYLANMA = "CH2_EVX_EXAMPLES orqali aylanma"
AYLANMA_100 = "100_soz gold qatori orqali aylanma"
_SOURCE_LABEL = {"json": "1500-lug'at", "docx": "kod SEED_WORDS", "chapter2_evx": "CH2_EVX_EXAMPLES",
                 "stub": "stub", "seed(kod)": "kod SEED_WORDS"}


def load_100_soz_phrases() -> set[str]:
    """Faqat PROVENANCE uchun: 100_soz gold iboralari `_load_words_from_json`
    orqali UB_en_w ga `source='json'` bilan tushadi (1500 JSON ichidagi
    "100 SOZ" kategoriyasi) — ular 1500-lug'at yozuvidan farqlanishi kerak."""
    with open(os.path.join(REPO_ROOT, "data", "100_soz.json"), encoding="utf-8") as f:
        return {normalize(e["english"]) for e in json.load(f)}


def provenance(ev: dict, gold100: set[str]) -> tuple[str, str]:
    """TO'LIQ MOS natija qanday olinganini belgilaydi: (belgi, izoh)."""
    if ev["tur"] == "L":
        toks = [t for p in ev["real"] for t in p["tokens"] if t["found"] and t["word"] != "to"]
        srcs = set().union(*(set(t["sources"]) for t in toks)) if toks else set()
        if any(normalize(p["en"]) in gold100 for p in ev["real"]):
            return AYLANMA_100, "natija 100_soz gold iborasining lug'at qatoridan"
        if any("MDB_uz_w" in t["method"] for t in toks):
            return AYLANMA, "natija MDB_uz_w almashtirishidan (MDB CH2 yozuvlarini ham saqlaydi)"
        if srcs and srcs <= {"chapter2_evx"}:
            return AYLANMA, "haqiqiy lug'at: natija FAQAT CH2_EVX_EXAMPLES yozuvidan (docx misoli bilan bir manba)"
        return MUSTAQIL, "haqiqiy lug'at: " + ", ".join(_SOURCE_LABEL.get(s, s) for s in sorted(srcs)) + " yozuvi"
    toks = [t for p in ev["mech"] for t in p["tokens"]]
    if any("MDB_uz_w" in t["method"] for t in toks):
        return AYLANMA, "stub, lekin natija MDB_uz_w almashtirishidan"
    if ev["tur"] == "S" and not ev["probe"]["mex"]:
        return MUSTAQIL, "stub; maxsus qoida yo'q — so'zma-so'z birikma"
    return MUSTAQIL, "stub: kodga faqat docx o'zagi berildi, natijani qoida zanjiri hisobladi"


def render(spec, evs, side, idx, m, lex) -> str:
    counts = {h: sum(1 for e in evs if e["holat"] == h) for h in HOLATLAR}
    by_pos = {}
    for e in evs:
        by_pos.setdefault(e["pos"], {h: 0 for h in HOLATLAR})[e["holat"]] += 1
    by_tur = {}
    for e in evs:
        by_tur.setdefault(e["tur"], {h: 0 for h in HOLATLAR})[e["holat"]] += 1
    total = len(evs)

    L = []
    L.append("# Faza 2 — KKT rasmiy spesifikatsiyasiga moslik auditi (conformance matrix)")
    L.append("")
    L.append(f"**Generatsiya vaqti:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    L.append(f"**Buyruq:** `python scripts/audit_kkt_spec_conformance.py`")
    L.append(f"**Spesifikatsiya:** `data/kkt_spec.json` ← `{spec['manba']['fayl']}` "
             f"(sha256 `{spec['manba']['sha256'][:16]}…`)")
    L.append(f"**Kod:** `kkt_v20_soz_tartibi.py` (bazalar data/ dan izolyatsiyalangan papkada noldan qurilgan, "
             f"`readonly_mode`; NLTK lemmatizer: `USE_LEMMA={m.USE_LEMMA}`)")
    L.append("")
    gold100 = load_100_soz_phrases()
    toliq = [e for e in evs if e["holat"] == TOLIQ]
    prov = {e["uid"]: provenance(e, gold100) for e in toliq}
    n_must = sum(1 for b, _ in prov.values() if b == MUSTAQIL)
    n_ayl = len(toliq) - n_must
    n_ayl_ch2 = sum(1 for b, _ in prov.values() if b == AYLANMA)

    L.append("## 0. Asosiy natija")
    L.append("")
    L.append(f"Spesifikatsiyadagi **{total} ta qoida** kod bilan solishtirildi. **{counts[TOLIQ]} ta to'liq mos "
             f"({n_must} tasi mustaqil hisoblangan, {n_ayl} tasi aylanma"
             + (f" — shundan {n_ayl_ch2} tasi CH2_EVX_EXAMPLES orqali" if n_ayl != n_ayl_ch2 else
                " — hammasi CH2_EVX_EXAMPLES orqali") + ")**, "
             f"{counts[QISMAN]} ta qisman mos, {counts[YOQ]} ta yo'q, {counts[ZID]} ta zid.")
    L.append("")
    L.append("| Holat | Soni | Ulushi |")
    L.append("|---|---|---|")
    for h in HOLATLAR:
        extra = f" ({n_must} mustaqil / {n_ayl} aylanma)" if h == TOLIQ else ""
        L.append(f"| **{h}** | **{counts[h]}**{extra} | {counts[h] / total:.1%} |")
    L.append(f"| Jami | {total} | 100% |")
    L.append("")
    L.append(f"### 0.1 {counts[TOLIQ]} ta TO'LIQ MOS — haqiqiy tarkibi")
    L.append("")
    L.append("- **mustaqil hisoblangan** — natijani kod o'zi hisobladi: M/N/S turida kodga FAQAT docx'dagi o'zak "
             "berildi (stub, real lug'at yashirilgan), L turida natija CH2_EVX_EXAMPLES'dan mustaqil lug'at yozuvidan "
             "(1500-lug'at yoki kod ichidagi SEED_WORDS) keldi.")
    L.append("- **CH2_EVX_EXAMPLES orqali aylanma** — natija dissertatsiya II bob misollarining lug'atga yozilgan "
             "nusxasidan (`source='chapter2_evx'`) o'qib qaytarildi; docx misoli ham shu manbadan — mustaqil dalil emas.")
    L.append("- Oxirgi ustun — xuddi shu misol HAQIQIY lug'at bilan qanday yo'l orqali chiqishi (M/N/S uchun holatga "
             "ta'sir qilmaydi, lekin amaliyotda ko'p misol baribir CH2 dan qaytishini ko'rsatadi).")
    L.append("")
    L.append("| qoida_id | POS | tur | belgi | qanday aniqlandi | haqiqiy lug'at bilan yo'l |")
    L.append("|---|---|---|---|---|---|")
    for e in toliq:
        b, izoh = prov[e["uid"]]
        real_path = "; ".join(_token_path(t) for p in e["real"] for t in p["tokens"])
        L.append(f"| {e['uid']} | {e['pos']} | {e['tur']} | **{b}** | {izoh} | {real_path} |")
    L.append("")
    L.append("**\"93 ta qoida\" haqida — tuzatish:** docx jadvallarida **87 ta** qoida bor. \"93\" soni (Ot 16, "
             "Sifat 18, Fe'l 29, Ravish 11, Son 11, Olmosh 8) har bir jadvalning SARLAVHA qatorini ham qo'shib "
             "sanalgan (16−1 + 18−1 + 29−1 + 11−1 + 11−1 + 8−1 = 87). Tekshiruv: `data/kkt_spec.json` → "
             "`sonlar`.")
    L.append("")
    L.append("### Turkum bo'yicha")
    L.append("")
    L.append("| POS | " + " | ".join(HOLATLAR) + " | Jami |")
    L.append("|---|" + "---|" * (len(HOLATLAR) + 1))
    for pos, c in by_pos.items():
        L.append(f"| {pos} | " + " | ".join(str(c[h]) for h in HOLATLAR) + f" | {sum(c.values())} |")
    L.append("")
    tur_names = {"M": "M — morfologik (affiks)", "N": "N — noqoida (o'zak o'zgarishi)",
                 "S": "S — ibora (so'z tartibi / funksional so'z)", "L": "L — leksik moslik"}
    L.append("### Qoida turi bo'yicha")
    L.append("")
    L.append("| Tur | " + " | ".join(HOLATLAR) + " | Jami |")
    L.append("|---|" + "---|" * (len(HOLATLAR) + 1))
    for t in ("M", "N", "S", "L"):
        c = by_tur.get(t, {h: 0 for h in HOLATLAR})
        L.append(f"| {tur_names[t]} | " + " | ".join(str(c[h]) for h in HOLATLAR) + f" | {sum(c.values())} |")
    L.append("")

    # TO'LIQ MOS ichidagi yo'llar — aylanma ogohlantirish
    toliq_L = [e for e in evs if e["holat"] == TOLIQ and e["tur"] == "L"]
    ch2_only = [e for e in toliq_L
                if all(t["sources"] == ["chapter2_evx"] for p in e["real"] for t in p["tokens"] if t["found"]
                       and t["word"] != "to")]
    sozma = [e for e in evs if e["holat"] == TOLIQ and e["tur"] == "S" and not e["probe"]["mex"]]
    variant = [e for e in evs if e["holat"] == TOLIQ and any(p["mos"] == "variant"
                                                             for p in (e["real"] if e["tur"] == "L" else e["mech"]))]
    docx_ichki = [e for e in evs if any(p.get("docx_ichki") for p in (e["real"] if e["tur"] == "L" else e["mech"]))]
    L.append("### TO'LIQ MOS natijalarini qanday o'qish kerak (halol baho)")
    L.append("")
    L.append(f"- M/N/S turidagi TO'LIQ MOS ({counts[TOLIQ] - len(toliq_L)} ta) — **lug'atdan mustaqil** "
             "tekshirilgan: kodga faqat docx'dagi o'zak berilgan (stub), qolgani haqiqiy qoida zanjiri. Bu — "
             "formal qoidaning o'zi ishlashining dalili. Lekin real lug'atda o'sha o'zak bo'lmasa, amaliy "
             "tarjima baribir chiqmaydi (quyidagi batafsil jadvaldagi \"real lug'at\" qatori).")
    L.append(f"- L turidagi TO'LIQ MOS ({len(toliq_L)} ta) — HAQIQIY lug'at bilan. Shundan **{len(ch2_only)} "
             "tasi natijani FAQAT `CH2_EVX_EXAMPLES` (dissertatsiya II bob misollari, `source='chapter2_evx'`) "
             "yozuvidan oladi** — ya'ni docx misoli bilan bir xil manbadan ko'chirilgan so'z qaytyapti "
             "(aylanma; mustaqil dalil emas): "
             + (", ".join(e["uid"] for e in ch2_only) or "—") + ".")
    L.append(f"- S turidagi TO'LIQ MOS ichida **{len(sozma)} tasi** uchun kodda maxsus qoida YO'Q — natija oddiy "
             "so'zma-so'z birikmadan to'g'ri chiqib qolgan (masalan son birikmalari): "
             + (", ".join(e["uid"] for e in sozma) or "—") + ".")
    if variant:
        L.append(f"- \"variant\" darajasida mos kelganlar ({len(variant)} ta TO'LIQ MOS ichida): lug'at yozuvi bir "
                 "nechta variant yoki qavsli izoh saqlaydi (masalan «U (erkak)» ~ «u») — solishtiruv qoidasi "
                 "1-bo'lim 3-bandda: " + ", ".join(e["uid"] for e in variant) + ".")
    if side.get("lemma_farq"):
        L.append("- **Muhitga bog'liq holatlar** (NLTK wordnet lemmatizer bor/yo'qligiga qarab o'zgaradi — "
                 "hisobot `USE_LEMMA=True` bilan): "
                 + "; ".join(f"{u}: {a} → wordnet'siz {b}" for u, (a, b) in side["lemma_farq"].items()) + ".")
    if docx_ichki:
        L.append(f"- **Docx ichki nomuvofiqligi tufayli QISMAN** ({len(docx_ichki)} ta): kod natijasi docx "
                 "katagidagi \"+\" qismlarining yig'indisiga teng, lekin docx natija katagida boshqacha yozilgan "
                 "(`data/kkt_spec.json` → `izoh`). Holat docx matni bo'yicha (tuzatilmagan) qoldirildi: "
                 + ", ".join(e["uid"] for e in docx_ichki) + ".")
    L.append("")

    L.append("## 1. Metodika")
    L.append("")
    L.append("1. **Spesifikatsiya** — `scripts/extract_kkt_spec.py` docx'dan avtomatik ajratadi (matn aynan "
             "ko'chirilgan, `--check` rejimi JSON docx bilan sinxronligini tekshiradi).")
    L.append("2. **Har bir qoida uchun tekshiruv** — `PROBES` (skript ichida): docx katagidagi misoldan olingan "
             "kirish/kutilgan juftlar. Har bir qiymat docx katagidan kelib chiqishi test bilan tekshiriladi "
             "(`tests/test_kkt_spec_conformance.py::test_probe_values_trace_to_docx_cells`). Kirishdagi tipografik "
             "apostrof (’) ASCII (') ga almashtirilgan — kod tokenizatori (`[A-Za-z']+`) faqat ASCII ni taniydi.")
    L.append("3. **Solishtiruv** — `scripts/_common.normalize()` (NFC, kichik harf, apostroflar bir xil, "
             "bo'shliqlar siqilgan); kutilgan qiymatdan qavs ichidagi izoh (masalan \"(affikssiz)\") va \"…\" olib "
             "tashlanadi. Bitta so'zli kirishda lug'at yozuvining \" / \" variantlaridan biri ham qabul qilinadi "
             "(\"variant\" belgisi bilan ko'rsatiladi).")
    L.append("4. **Tizim chiqishi** — GUI'dagi kabi: `translate_phrase(..., allow_write=False)` natija bersa — "
             "o'sha, aks holda `parse_sentence()` so'zma-so'z natijasi (topilmagan so'z `[so'z?]`).")
    L.append("5. **Holat mantig'i** (tur bo'yicha, `evaluate_rule()`):")
    L.append("   - **M**: stub bilan — affiks va o'zak tanildi + turkum spec bilan bir xil + natija mos → TO'LIQ MOS; "
             "tanildi, turkum bir xil, natija farq → QISMAN; tanildi, lekin kod uni BOSHQA turkumga qo'yadi: natija "
             "mos → QISMAN, farq → ZID; tanilmadi, lekin kodda shu affiks uchun qoida BOR (ishlamadi — dalilda "
             "o'zak-tiklash nomzodlari ko'rsatilgan) → QISMAN; affiks uchun qoida umuman yo'q → YO'Q.")
    L.append("   - Stub'dagi `⟨...⟩` qiymat — ma'lumot emas, BELGI: docx o'zakning o'zbekchasini bermagan joyda "
             "(2.13, 3.13) kod o'zbek tomonini qanday qurishini ko'rsatadi.")
    L.append("   - **N**: hamma juft mos → TO'LIQ MOS; noqoida shakldan asosiy o'zak tanildi (masalan lemmatizer "
             "orqali), natija farq → QISMAN; tanilmadi → YO'Q.")
    L.append("   - **S**: stub bilan natija mos → TO'LIQ MOS; mos emas va kodda AYNAN shu hodisa uchun alohida qoida "
             "bor (`mex` — masalan `_DETERMINERS`, `PREP_UZ_X3`) → ZID; bunday qoida yo'q → YO'Q.")
    L.append("   - **L**: haqiqiy lug'at bilan — hamma juft mos → TO'LIQ MOS; qisman mos yoki bosh so'z topildi-yu "
             "natija farq → QISMAN; bosh so'z(lar) umuman topilmadi → YO'Q.")
    L.append("6. **Chegara** — bu audit formal qoidaning TO'G'RI IMPLEMENT QILINGANINI tekshiradi, tarjima "
             "sifatini emas. Gold to'plamlar (`100_soz`, `1500_...`) bu yerda ishlatilmaydi — 1500-lug'at faqat "
             "4-bo'limdagi ustuvorlik hisobida (qamrov soni) ishlatiladi.")
    L.append("")

    L.append("## 2. Moslik jadvali (87 qoida)")
    L.append("")
    L.append("| qoida_id | POS | holat | dalil (kod qatori yoki test natijasi) |")
    L.append("|---|---|---|---|")
    for e in evs:
        L.append(f"| {e['uid']} | {e['pos']} | **{e['holat']}** | [{e['tur']}] {build_dalil(e, idx, m)} |")
    L.append("")

    L.append("### 2.1 Qo'shimcha: real lug'at bilan natija (M/N/S qoidalari, holatga ta'sir qilmaydi)")
    L.append("")
    L.append("Stub tekshiruvi formal qoidani ajratib oladi; bu jadval o'sha misollar HAQIQIY lug'at bilan nima "
             "berishini ko'rsatadi — farq qilsa, sabab ko'pincha lug'at bo'shlig'i (o'zak yo'q) yoki misolning "
             "o'zi `CH2_EVX_EXAMPLES` dan to'g'ridan-to'g'ri qaytishi.")
    L.append("")
    L.append("| qoida_id | holat (stub) | real lug'at natijasi | yo'l |")
    L.append("|---|---|---|---|")
    for e in evs:
        if e["tur"] == "L":
            continue
        for p in e["real"]:
            mark = "✓" if p["mos"] else "✗"
            path = "; ".join(_token_path(t) for t in p["tokens"])
            L.append(f"| {e['uid']} | {e['holat']} | `{p['en']}` → «{p['natija']}» {mark} | {path} |"
                     .replace("||", "|"))
    L.append("")

    # ── 3. Yon tekshiruvlar ──
    L.append("## 3. 87 qoidadan tashqari: vaznlar, turkum belgilari, operatorlar")
    L.append("")
    L.append(f"`POS_V2` (`kkt_v20_soz_tartibi.py:{side['pos_v2_line']}`) va `POS_KKT` "
             f"(`:{side['pos_kkt_line']}`) spesifikatsiya bilan. \"runtime\" — tarjima paytida haqiqatda "
             "ishlatiladigan qiymat (`bm_get_or_create_pos_model(DB_BM_EN, pos)` — avval BM_en_w.pos_weight "
             "jadvaliga qaraydi):")
    L.append("")
    L.append("| Spec (docx matni) | Spec vazni | `POS_V2` | runtime (BM_en_w) | Spec belgisi | `POS_KKT` | Xulosa |")
    L.append("|---|---|---|---|---|---|---|")
    for w in side["weights"]:
        same_v = w["pos_v2"] is not None and w["pos_v2"] == w["vazn"]
        same_rt = w["runtime_bm_en"] is not None and w["runtime_bm_en"] == w["vazn"]
        same_s = w["pos_kkt"] is not None and w["pos_kkt"] == w["belgi"]
        if w["pos_v2"] is None:
            xulosa = "**kodda yo'q** (POS_V2/POS_KKT kaliti yo'q)"
        else:
            xulosa = ("bit-aniq mos" if same_v and same_rt and same_s else
                      f"farq: POS_V2={'✓' if same_v else '✗'}, runtime={'✓' if same_rt else '✗'}, "
                      f"belgi={'✓' if same_s else '✗'}")
        L.append(f"| {w['docx_matn']} | {w['vazn']} | {w['pos_v2'] if w['pos_v2'] is not None else '—'} | "
                 f"{w['runtime_bm_en'] if w['runtime_bm_en'] is not None else '—'} | {w['belgi']} | "
                 f"{w['pos_kkt'] or '—'} | {xulosa} |")
    L.append("")
    yord = next(w for w in side["weights"] if w["kalit"] == "Yordamchi")
    L.append(f"- **Yordamchi so'z turkumlari ({yord['belgi']}) — {yord['vazn']}:** `POS_V2`/`POS_KKT` da kalit "
             "yo'q. `0.07` qiymati kodda hisob-kitobda faqat bitta joyda qattiq yozilgan: `kkt_uz()` ichida "
             "o'zbekcha \"eng\" (orttirma, belgisi `P2_D`) uchun "
             f"(`kkt_v20_soz_tartibi.py:{idx.find('0.07+v2')}`) — ya'ni vazn qiymati mos, lekin spec'dagi U/L "
             "belgisi bilan emas, `P2_D` bilan bog'langan.")
    L.append("- Taqrizning 27-bandi (\"vaznlar qayerdan olingan\") uchun: 8 ta vazn kodda spec bilan bir xil. "
             "Bu — qiymatlarning MANBASINI ko'rsatadi, ularning ILMIY ASOSINI emas (28-band ochiq qoladi).")
    L.append("")
    L.append("**Operatorlar** (spec 1-jadval) — kodda qanday ishlatilishi (faqat `grep`, bajarilmaydi):")
    L.append("")
    L.append("| Belgi | Spec ma'nosi | Kodda |")
    L.append("|---|---|---|")
    op_code = {
        "⊕": "Formal model satrlarida biriktirish sifatida (`kkt_en()` — `'⊕↓'.join(segs)`, "
             f"`:{idx.find(chr(39) + '⊕↓' + chr(39) + '.join')}`); SSM segment ajratgichi "
             f"(`_ssm_split_segments`, `:{idx.find('re.split(r' + chr(34) + '⊕')}`).",
        "V": "\"Yoki\" amali sifatida ISHLATILMAYDI. `KKT_SYMBOLS` da `(\"V\",\"umumiy BB\")` — boshqa ma'noda "
             "(umumiy baza) belgilangan.",
        "↓ (⇓)": "Faqat `⊕↓` juftligi ichida va SSM'da \"ixtiyoriy segment\" belgisi sifatida "
                 "(`_ssm_split_segments`: `p.startswith(\"↓\")`). `⇓` kodda yo'q.",
        "$": "Formal model satrlarida `$[i,1-h]Ci` ko'rinishida (matn sifatida) hosil qilinadi; tanlash amali "
             "sifatida hisoblanmaydi.",
    }
    for op in spec["operators"]:
        L.append(f"| {op['belgi']} | {op['mano']} | {op_code.get(op['belgi'], '—')} |")
    L.append("")
    extra = _code_affixes_not_in_spec(idx, m)
    L.append(f"**Teskari yo'nalish (kodda bor, spec misollarida tekshirilmagan affikslar)** — `MORPH_RULES` dagi "
             f"{len(extra)} ta affiks hech bir spec qoidasining misoli bilan qamrab olinmagan: "
             + ", ".join(f"`-{a}`" for a in extra) + ". Xususan `-er` (Ot←Fe'l, ish bajaruvchi, "
             f"`MORPH_RULES:{idx.morph_rule_lines('er')[0]}`) — spesifikatsiyada umuman yo'q kategoriya "
             "(`reports/faza_2_er_gap.md` 6-bo'lim).")
    L.append("")

    # ── 4. YO'Q / ZID — ustuvorlik ──
    L.append("## 4. YO'Q va ZID qoidalar — ustuvorlik bo'yicha (Vazifa 4)")
    L.append("")
    L.append("**Kod o'zgartirilmadi.** Bu ro'yxat — keyingi bosqich uchun. Tuzatish maqsadi faqat spesifikatsiyaga "
             "moslash (gold test natijasini yaxshilash emas).")
    L.append("")
    L.append("Ustuvorlik o'lchovlari (ikkalasi ham `data/1500_EN_UZ_6_POS_sorted.20.json` 6 asosiy kategoriyasi "
             "bo'yicha, avtomatik hisoblangan):")
    L.append("- **Asos soni** — qoida qo'llanadigan kategoriyadagi yozuvlar soni (masalan fe'l qoidasi uchun "
             "VERBS). Qoida implement qilinsa, shuncha lug'at so'zi uchun yangi shakl hosil bo'la oladi.")
    L.append("- **Sirt soni** — lug'atda bosh so'zi AYNAN shu qoida shakliga mos yozuvlar (regex skriptdagi `sirt`); "
             "L turi uchun — bosh so'z(lar) lug'atda bor-yo'qligi.")
    L.append("")
    bad = [e for e in evs if e["holat"] in (YOQ, ZID)]
    rows = []
    for e in bad:
        pr = priority_row(e["probe"], lex)
        rows.append((e, pr))
    rows.sort(key=lambda x: (-(x[1]["asos_n"] or 0), -x[1]["sirt_n"], x[0]["uid"]))
    L.append("| # | qoida_id | POS | holat | tur | asos soni (kategoriya) | sirt soni (misollar) | spec misoli |")
    L.append("|---|---|---|---|---|---|---|---|")
    rule_by_uid = {r["uid"]: r for r in spec["rules"]}
    for n, (e, pr) in enumerate(rows, 1):
        r = rule_by_uid[e["uid"]]
        asos = f"{pr['asos_n']} ({e['probe']['asos']})" if pr["asos_n"] else "—"
        sirt = f"{pr['sirt_n']}" + (f" ({', '.join(pr['sirt_misol'])})" if pr["sirt_misol"] else "")
        L.append(f"| {n} | {e['uid']} | {e['pos']} | {e['holat']} | {e['tur']} | {asos} | {sirt} | "
                 f"`{r['en_misol']}` ⟹ `{r['uz_misol']}` |")
    L.append("")
    L.append(f"Jami YO'Q: **{counts[YOQ]}**, ZID: **{counts[ZID]}**.")
    L.append("")

    # ── 6 (5 dan oldin chiqariladi — qisqa). CH2_EVX_EXAMPLES ↔ spec ──
    def _en_key(s):  # defis/bo'shliq farqi hisobga olinmaydi ("eighty-five" ~ "eighty five")
        return normalize(s.replace("-", " "))

    spec_pairs: dict[str, list] = {}
    for uid, pr in PROBES.items():
        for en, exp in pr["juftlar"]:
            spec_pairs.setdefault(_en_key(en), []).append((uid, exp))
    ch2_rows, ch2_no_spec = [], []
    for ex in m.CH2_EVX_EXAMPLES:
        hits = spec_pairs.get(_en_key(ex["en"]))
        if not hits:
            ch2_no_spec.append(ex)
            continue
        single = " " not in ex["en"].strip()
        ok = any(compare(ex["uz"], exp, single) for _, exp in hits)
        uids = sorted({u for u, _ in hits})
        exps = " / ".join(dict.fromkeys(exp for _, exp in hits))
        ichki = [alt for u in uids if (alt := _docx_components(rule_by_uid[u]["uz_misol"]))
                 and compare(ex["uz"], alt, single)]
        ch2_rows.append((ex, ", ".join(uids), exps, ok, ichki[0] if ichki else None))
    ch2_bad = [r for r in ch2_rows if not r[3]]
    L.append("## 5. `CH2_EVX_EXAMPLES` ↔ spesifikatsiya (lug'atdagi dissertatsiya nusxalari rasmiy qoidaga mosmi)")
    L.append("")
    L.append(f"`load_ch2_evx_examples()` bu {len(m.CH2_EVX_EXAMPLES)} ta yozuvni UB_en_w'ga headword sifatida "
             "yozadi — L turidagi ko'p natijalar aynan shu yerdan keladi. Inglizcha shakli spec misoli bilan "
             f"bir xil bo'lgan {len(ch2_rows)} ta juftdan **{len(ch2_bad)} tasida o'zbekcha tarjima spec'dan farq "
             "qiladi**:")
    L.append("")
    L.append("| CH2 en | CH2 uz | spec qoidasi | spec kutilgan | izoh |")
    L.append("|---|---|---|---|---|")
    for ex, uid, exp, _, ichki in ch2_bad:
        note = f"CH2 docx katagining \"+\" qismlari yig'indisiga («{ichki}») teng — docx ichki nomuvofiqligi" \
            if ichki else ""
        L.append(f"| {ex['en']} | {ex['uz']} | {uid} | {exp} | {note} |")
    L.append("")
    L.append(f"Inglizcha shakli hech bir spec misoliga to'g'ri kelmagan CH2 yozuvlari ({len(ch2_no_spec)} ta): "
             + ", ".join(f"`{ex['en']}`" for ex in ch2_no_spec) + ". (Masalan `capabilityies`/`leafes` — "
             "`reports/ch2_leakage_check.md` dagi transkripsiya xatolari; spec'da to'g'ri `capabilities`/`leaves`.)")
    L.append("")

    # ── 6. Batafsil ──
    L.append("## 6. Batafsil — har bir qoida bo'yicha to'liq xom natija")
    L.append("")
    for e in evs:
        r = rule_by_uid[e["uid"]]
        pr = e["probe"]
        L.append(f"### {e['uid']} — {r['tavsif']}")
        L.append("")
        L.append(f"- Spec: `{r['en_misol']}` → `{r['uz_misol']}`" + (f" — *docx izohi:* {r['izoh']}" if r.get("izoh") else ""))
        L.append(f"- Tur: **{e['tur']}**, holat: **{e['holat']}**")
        if pr["stub"]:
            L.append("- Stub: " + ", ".join(f"{s[0]}→{s[1]} ({s[2]}" + (f", manba {s[3]}" if len(s) > 3 else "") + ")"
                                             for s in pr["stub"]))
        if pr["izoh"]:
            L.append(f"- Izoh: {pr['izoh']}")
        for label, rows_ in (("stub", e.get("mech")), ("real lug'at", e["real"])):
            if not rows_:
                continue
            for p in rows_:
                L.append(f"- {label}: {_fmt_pair(p)} — yo'l: {p['yol']}; "
                         + "; ".join(_token_path(t) for t in p["tokens"]))
        L.append("")
    return "\n".join(L)


def run(out_path: str | None) -> int:
    spec = load_spec()
    idx = CodeIndex(os.path.join(REPO_ROOT, "kkt_v20_soz_tartibi.py"))
    tmp = tempfile.mkdtemp(prefix="kkt_spec_audit_")
    try:
        m = build_isolated_module(tmp)
        evs = evaluate_all(m, spec)
        side = side_checks(m, spec, idx)
        side["lemma_farq"] = lemma_dependence(m, spec, evs)
        report = render(spec, evs, side, idx, m, load_1500())
    finally:
        if tmp in sys.path:
            sys.path.remove(tmp)
        shutil.rmtree(tmp, ignore_errors=True)
    counts = {h: sum(1 for e in evs if e["holat"] == h) for h in HOLATLAR}
    print(f"{len(evs)} qoida: " + ", ".join(f"{h}={n}" for h, n in counts.items()))
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print(f"[yozildi: {out_path}]")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--no-out", action="store_true")
    args = ap.parse_args()
    return run(None if args.no_out else args.out)


if __name__ == "__main__":
    raise SystemExit(main())
