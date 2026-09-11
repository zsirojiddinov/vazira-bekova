"""
ISHGA TUSHIRISH:
  pip install python-docx nltk openpyxl
  python mt_system_v5.py
"""

import sqlite3, os, re, sys, glob, contextlib
from datetime import datetime

try:
    # GUI (Tkinter) ixtiyoriy: tarjima mantig'i (translate_phrase va uning
    # bog'liqliklari) tkinter'siz muhitda (masalan CI/server, Tk kutubxonasi
    # o'rnatilmagan konteyner) ham ishlashi kerak — shuning uchun bu import
    # majburiy emas. HAS_TK=False bo'lsa, faqat GUI (MTSystem klassi va uni
    # ochuvchi main()) ishlamaydi; tarjima funksiyalari va baza qurish
    # (scripts/build_db.py) ta'sirlanmaydi.
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    HAS_TK = True
except Exception:
    HAS_TK = False
    tk = ttk = filedialog = messagebox = None

try:
    from docx import Document; HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import socket
    _old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(3)          # nltk tarmoqqa cheksiz osilib qolmasin
    from nltk.stem import WordNetLemmatizer
    import nltk
    try:    nltk.data.find("corpora/wordnet")
    except: nltk.download("wordnet", quiet=True)
    _lemmatizer = WordNetLemmatizer()
    USE_LEMMA = True
except Exception:
    USE_LEMMA = False; _lemmatizer = None
finally:
    try: socket.setdefaulttimeout(_old_timeout)
    except Exception: pass

# ═══════════════════════════════════════════════════════════════════
#  O'QISH-FAQAT (READ-ONLY) REJIM
# ═══════════════════════════════════════════════════════════════════
# translate_phrase() (aniqrog'i uning ichki chaqiruv zanjiri —
# translate_phrase_general -> _chunk_phrase -> parse_sentence ->
# smart_parse -> _smart_parse_core) NOMA'LUM so'zlarni/qo'shimchalarni
# avtomatik xulosa chiqarib, natijani to'g'ridan-to'g'ri diskdagi .db
# fayllarga YOZIB QO'YADI (o'z-o'zini keshlash — db_insert, qm_confirm_or_add,
# bm_get_or_create_pos_model, bm_get_or_create_affix_model). Bu GUI orqali
# qo'lda ishlatilganda maqsadli xatti-harakat, lekin O'LCHOV/AUDIT
# skriptlari (scripts/audit_examples.py, gold-test runner va h.k.) uchun
# XAVFLI: ular tarjimani ko'p marta, ko'p matn ustida qayta-qayta ishga
# tushiradi va shu jarayonning o'zi bazani o'zgartirib qo'yishi mumkin
# (bu aynan Faza 0 da bir marta yuz berdi — qarang: reports/faza_0.md).
#
# readonly_mode() shu 4 ta yozish-nuqtasini (write-primitive) global
# ravishda o'chiradi — lekin ULARNING KESHLASH MANTIG'INI EMAS: har bir
# funksiya baribir mos vazn/KKT-belgi qiymatini hisoblab qaytaradi (shu
# sabab tarjima NATIJASI readonly_mode ichida ham, tashqarisida ham bir
# xil bo'ladi — faqat sqlite'ga yozilmaydi). Har bir chaqiruv zanjirini
# alohida "allow_write" parametri bilan o'rab chiqish o'rniga (bu ~15 ta
# oraliq funksiya imzosini o'zgartirishni talab qilardi — katta va xavfli
# diff), yagona umumiy holat (global chuqurlik hisoblagichi) ishlatildi —
# bu translate_phrase() dan tashqari smart_parse()/parse_sentence() kabi
# funksiyalarni to'g'ridan-to'g'ri chaqiradigan skriptlarni ham qamrab
# oladi.
_READONLY_DEPTH = 0

def is_readonly() -> bool:
    """True bo'lsa — db_insert/qm_confirm_or_add/bm_get_or_create_pos_model/
    bm_get_or_create_affix_model hech qanday INSERT/COMMIT qilmaydi."""
    return _READONLY_DEPTH > 0

@contextlib.contextmanager
def readonly_mode():
    """
    Kontekst-menejer: ichida translate_phrase() (va uni chaqiradigan yoki u
    chaqiradigan hamma joy — smart_parse(), parse_sentence() ham) diskdagi
    .db fayllarga HECH QANDAY yozuv qilmaydi. Ichma-ich chaqirilishi
    (nesting) xavfsiz — hisoblagich orqali qo'llab-quvvatlanadi.

    O'lchov/audit skriptlari SHU REJIMDA ishlashi SHART:

        from kkt_v20_soz_tartibi import translate_phrase, readonly_mode
        with readonly_mode():
            natija = translate_phrase(matn)

    Yoki, faqat translate_phrase() uchun qulay yorliq:

        translate_phrase(matn, allow_write=False)
    """
    global _READONLY_DEPTH
    _READONLY_DEPTH += 1
    try:
        yield
    finally:
        _READONLY_DEPTH -= 1

# ═══════════════════════════════════════════════════════════════════
#  SOZLAMALAR
# ═══════════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, "data")   # foydalanuvchi manba fayllarni shu yerga tashlaydi
SEARCH_DIRS = [SCRIPT_DIR, DATA_DIR, os.getcwd()]

# ═══════════════════════════════════════════════════════════════════
#  XATOLIKLARNI DIALOG OYNASI SIFATIDA KO'RSATISH
# ═══════════════════════════════════════════════════════════════════
# Dastur hali GUI (MTSystem) ochilmagan bosqichda (bazalar/docx/xlsx
# yuklanayotganda) yuzaga kelgan xatoliklar uchun ham, GUI ochilgandan
# keyingi (tugma bosish va h.k.) xatoliklar uchun ham bitta umumiy
# ko'rinishdagi xabar oynasi (messagebox) chiqarish uchun ishlatiladi.
_dialog_root = None

def show_error_dialog(title, message):
    """Har qanday xatolikni konsolga chop etish bilan bir qatorda
    foydalanuvchiga tushunarli xabar oynasi (dialog) sifatida ham chiqaradi.
    Tkinter mavjud bo'lmagan muhitda (HAS_TK=False) faqat konsolga yozadi."""
    global _dialog_root
    print(f"  [XATOLIK] {title}: {message}")
    if not HAS_TK:
        return
    try:
        if getattr(tk, "_default_root", None) is None:
            # Hali birorta ham Tk oynasi yaratilmagan (masalan, bazalar
            # yuklanayotgan bosqich) — dialogni ko'rsatish uchun vaqtinchalik
            # yashirin ildiz oyna kerak.
            if _dialog_root is None or not _dialog_root.winfo_exists():
                _dialog_root = tk.Tk()
                _dialog_root.withdraw()
        messagebox.showerror(title, str(message))
    except Exception as e:
        # Dialog oynaning o'zi ham ochilmasa (masalan, displey yo'q muhitda),
        # kamida konsolga yozib qo'yamiz — dastur bu sababli yiqilmasin.
        print(f"  [DIQQAT] Xatolik dialogini ko'rsatib bo'lmadi: {e}")


def _find_latest_by_pattern(patterns, dirs=None):
    """Berilgan glob patternlarga mos fayllarni SEARCH_DIRS ichida (skript
    papkasi, data/ va joriy papka) qidiradi. Bir nechta versiya (masalan
    turli sanadagi nusxalar) topilsa — nomidagi sanaga (kk.oo.yyyy) qarab
    ENG YANGISINI qaytaradi; sana topilmasa faylning o'zgartirilgan vaqtiga
    qaraladi."""
    if dirs is None: dirs = SEARCH_DIRS
    found = []
    for d in dirs:
        if not os.path.isdir(d): continue
        for pat in patterns:
            found.extend(glob.glob(os.path.join(d, pat)))
    if not found: return None

    def date_key(p):
        m = re.search(r"(\d{1,2})[.\-_](\d{1,2})[.\-_](\d{4})", os.path.basename(p))
        if m:
            try: return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except Exception: pass
        return datetime.fromtimestamp(os.path.getmtime(p))

    return sorted(set(found), key=date_key)[-1]

# ── 8 ta SQLite baza (KKT arxitekturasi) ─────────────────────────────
DB_BM_EN  = os.path.join(SCRIPT_DIR, "BM_en_w.db")   # Ingliz — FORMAL modellar bazasi
DB_BM_UZ  = os.path.join(SCRIPT_DIR, "BM_uz_w.db")   # O'zbek — FORMAL modellar bazasi
DB_UB_EN  = os.path.join(SCRIPT_DIR, "UB_en_w.db")   # Ingliz — so'z turkumlari bazasi
DB_UB_UZ  = os.path.join(SCRIPT_DIR, "UB_uz_w.db")   # O'zbek — so'z turkumlari bazasi
DB_QM_EN  = os.path.join(SCRIPT_DIR, "QM_en_w.db")   # Ingliz — qo'shimchalar bazasi
DB_QM_UZ  = os.path.join(SCRIPT_DIR, "QM_uz_w.db")   # O'zbek — qo'shimchalar bazasi
DB_PSB_EN = os.path.join(SCRIPT_DIR, "PSB_en_w.db")  # Ingliz — predmet sohalar bazasi
DB_PSB_UZ = os.path.join(SCRIPT_DIR, "PSB_uz_w.db")  # O'zbek — predmet sohalar bazasi
ALL_DBS = [DB_BM_EN, DB_BM_UZ, DB_UB_EN, DB_UB_UZ, DB_QM_EN, DB_QM_UZ, DB_PSB_EN, DB_PSB_UZ]

DB_NAME = DB_UB_EN  # asosiy tarjima bazasi (eski nom bilan moslik uchun)
DOCX_CANDIDATES = [
    "1500_EN_UZ_6_POS_sorted_20_docx.docx",
    "1500_EN_UZ_6_POS_sorted.20.docx",
    "1500_EN_UZ_6_POS_sorted 20.docx",
]
DOCX2_CANDIDATES = [
    "bazalar_ma_lumot_09.docx",
]
DOCX2B_CANDIDATES = [
    "bazalar_ma_lumot_09_07.docx",
]
DOCX3_CANDIDATES = [
    "so_zlar_bazasi_un.docx",
]
XLSX_EN = (
    _find_latest_by_pattern(["Table_English_1-7_Vazn_Type_2_09.xlsx", "Table_English*Vazn*Type*2*.xlsx"])
    or os.path.join(SCRIPT_DIR, "Table_English_1-7_Vazn_Type_2_09.xlsx")
)
XLSX_UZ = (
    _find_latest_by_pattern(["Lotinda_Table_Uzbek_1-7_Vazn_30_10_2025.xlsx", "Lotinda*Table*Uzbek*Vazn*.xlsx"])
    or os.path.join(SCRIPT_DIR, "Lotinda_Table_Uzbek_1-7_Vazn_30_10_2025.xlsx")
)
POS_MAP = {
    "NOUNS":"Ot","VERBS":"Fe'l","ADJECTIVES":"Sifat",
    "ADVERBS":"Ravish","PRONOUNS":"Olmosh","CONJUNCTIONS":"Bog'lovchi",
}

# ═══════════════════════════════════════════════════════════════════
#  KKT — 6 POS belgilari va vaznlari (Bekova, 2026 §2.1)
# ═══════════════════════════════════════════════════════════════════
POS_KKT = {
    "Ot":"C","Fe'l":"G","Sifat":"P","Ravish":"N",
    "Olmosh":"M","Son":"F","Bog'lovchi":"Y","Predlog":"D",
}
POS_V2 = {
    "Ot":0.85,"Fe'l":0.90,"Sifat":0.60,"Ravish":0.40,
    "Olmosh":0.50,"Son":0.50,"Bog'lovchi":0.20,"Predlog":0.40,
}
# Har bir so'z turkumi uchun KKT rasmiy modelidagi "h" diapazon indeksi
# (dissertatsiya namuna jadvallariga mos: Ot=h1, Sifat=h2, Fe'l=h3,
#  Ravish=h4, Olmosh=h5, Son=h6). Bog'lovchi/Predlog uchun aniq indeks
# dissertatsiyada berilmagan — umumiy "h" qoldiriladi.
POS_H = {
    "Ot":"h1","Sifat":"h2","Fe'l":"h3","Ravish":"h4",
    "Olmosh":"h5","Son":"h6",
}

# Ingliz affikslari → (KKT belgisi, V3 qiymati)
EN_AFF_V3 = {
    # Ot ko'plik — C(C,X)
    "s":    ("X",     0.00101),  # dog+s
    "es":   ("X1",    0.00102),  # process+es
    "ies":  ("X1",    0.00103),  # capabilit+ies
    "ves":  ("X1",    0.00104),  # lea+ves
    "'s":   ("X3",    0.00205),  # student+'s
    # Fe'l zamon — G(G_A1)
    "ing":  ("G_A1",  0.00303),  # work+ing
    "ied":  ("G_A1",  0.00301),  # studi+ed
    "ed":   ("G_A1",  0.00301),  # work+ed
    # Sifat daraja — P1_SF, P2_SF
    "ier":  ("P1_SF", 0.00301),  # happi+er
    "iest": ("P2_SF", 0.00302),  # happi+est
    "er":   ("P1_SF", 0.00301),  # fast+er
    "est":  ("P2_SF", 0.00302),  # fast+est
    # Sifat yasovchi — P_A1
    "ical": ("P_A1",  0.00219),  "able": ("P_A1",  0.00219),
    "ible": ("P_A1",  0.00219),  "ful":  ("P_A1",  0.00219),
    "less": ("P_A1",  0.00219),  "ous":  ("P_A1",  0.00219),
    "ive":  ("P_A1",  0.00219),  "ic":   ("P_A1",  0.00219),
    "al":   ("P_A1",  0.00219),  "ish":  ("P_A1",  0.00219),
    "ary":  ("P_A1",  0.00219),  "ory":  ("P_A1",  0.00219),
    "ant":  ("P_A1",  0.00219),  "ent":  ("P_A1",  0.00219),
    "like": ("P_A1",  0.00219),
    # Ot yasovchi — C_A1
    "ation":("C_A1",  0.00209),  "ition":("C_A1",  0.00209),
    "tion": ("C_A1",  0.00209),  "sion": ("C_A1",  0.00209),
    "ment": ("C_A1",  0.00209),  "ness": ("C_A1",  0.00209),
    "ity":  ("C_A1",  0.00219),  "ance": ("C_A1",  0.00219),
    "ence": ("C_A1",  0.00219),  "ism":  ("C_A1",  0.00209),
    "ist":  ("C_A1",  0.00219),  "ship": ("C_A1",  0.00219),
    "hood": ("C_A1",  0.00219),  "dom":  ("C_A1",  0.00209),
    "age":  ("C_A1",  0.00219),  "ure":  ("C_A1",  0.00219),
    "ology":("C_A1",  0.00219),  "logy": ("C_A1",  0.00219),
    "ics":  ("C_A1",  0.00219),  "ization":("C_A1",0.00219),
    # Ravish yasovchi — N_A1
    "ally": ("N_A1",  0.00204),  "ily":  ("N_A1",  0.00204),
    "ably": ("N_A1",  0.00204),  "ibly": ("N_A1",  0.00204),
    "ly":   ("N_A1",  0.00204),  "ward": ("N_A1",  0.00204),
    "wards":("N_A1",  0.00204),  "wise": ("N_A1",  0.00204),
    # Fe'l yasovchi — G_SF
    "ize":  ("G_SF",  0.00219),  "ise":  ("G_SF",  0.00219),
    "ify":  ("G_SF",  0.00219),  "en":   ("G_SF",  0.00219),
    "izing":("G_A1",  0.00303),
    # Olmosh — M_A1
    "selves":("M_A1", 0.00219),  "self": ("M_A1",  0.00219),
    "ever": ("M_A1",  0.00219),  "thing":("M_A1",  0.00219),
    # Son — F_A1
    "teen": ("F_A1",  0.00102),  "ty":   ("F_A1",  0.00104),
    "th":   ("F_A1",  0.00103),  "fold": ("F_A1",  0.00219),
}

# O'zbek affikslari → (KKT belgisi, V3)
UZ_AFF_V3 = {
    "lar":("X",0.00101),"ning":("X3",0.00205),"ni":("X3",0.00204),
    "ga":("X3",0.00204),"da":("X3",0.00203),"dan":("X3",0.00204),
    "roq":("P1_A1",0.00304),"lik":("C_A1",0.00119),
    "iy":("P_A1",0.00123),"li":("P_A1",0.00145),"siz":("P_A1",0.00501),
    "chi":("C_A1",0.00219),"gan":("G_A1",0.00702),"ayotgan":("G_A1",0.00702),
    "di":("G_A1",0.00301),"moq":("G_A1",0.00303),"ish":("C_A1",0.00204),
    "izm":("C_A1",0.00209),"inchi":("F_A1",0.00103),
    "tarzda":("N_A1",0.00204),"jihatdan":("N_A1",0.00204),
    "tomon":("N_A1",0.00204),"lashtirmoq":("G_A1",0.00303),
    "ladigan":("G_A1",0.00303),"bilan":("D",0.00204),
}

UZ_AFFIXES = {
    "X":["lar"],"X3":["ga","da","dan","ni","ning","ka","qa","ta"],
    "C-A4":["chi","chilik","lik","gar"],
    "G-A":["a","ay","ar","la","lan","lash","lashtir","i","ik","il","in"],
    "G-V1":["adi","adigan","ayotgan","ayotib","gan","di","digan","ib","moqda"],
    "G-U1":["ma","yo'q","emas"],
    "P-A1":["li","lik","siz","roq","iy","viy","vor","bop","dor"],
    "P-P1":["roq","ishroq"],"P-P2":["juda","nihoyatda","behad"],
    "N-A4":["gina","lab","an","iga","in","roq","gani"],
    "F-A4":["inchi","nchi","ta","tadan","gina","lab"],
    "U":["mi","ku","chi","da","yu","ya","gina","ki","ham","faqat"],
}

# ═══════════════════════════════════════════════════════════════════
#  INGLIZ PREFIKSLARI (uzundan qisqaga)
# ═══════════════════════════════════════════════════════════════════
EN_PREFIXES = [
    ("counter","qarshi"),("under","osti/kam"),("super","yuqori"),
    ("inter","oraliq"),("trans","o'tkazuvchi"),("pseudo","soxta"),
    ("proto","birlamchi"),("ultra","o'ta"),("circum","atrofida"),
    ("retro","orqaga"),("extra","tashqarida"),("over","haddan"),
    ("fore","oldindan"),("with","birgalikda"),("poly","ko'p"),
    ("post","keyin"),("para","yonida"),("mono","bitta"),
    ("homo","bir xil"),("auto","o'z-o'zi"),("arch","bosh"),
    ("neo","yangi"),("tele","uzoq"),("bene","yaxshi"),
    ("self","o'z-o'zi"),("anti","qarshi"),("some","ba'zi"),
    ("mid","o'rta"),("non","emas"),("out","tashqari"),
    ("mis","noto'g'ri"),("pre","oldindan"),("dis","inkor"),
    ("sub","ostki"),("pro","foyda"),("re","qayta"),
    ("de","aksi"),("co","birgalikda"),("un","inkor"),
    ("be","qilmoq"),("up","yuqori"),("en","qilmoq"),
    ("bi","ikki"),("ad","tomon"),("ex","eski"),
    ("ab","uzoqlashtirish"),("ob","qarshi"),
    ("em","ichida"),("ir","inkor"),("il","inkor"),
    ("im","inkor"),("in","inkor"),("semi","yarim"),
]
EN_PREFIX_UZ = {
    "un":"...siz","re":"qayta ...","pre":"oldindan ...","dis":"...siz",
    "mis":"noto'g'ri ...","over":"haddan ...","under":"kam ...",
    "non":"...emas","anti":"qarshi ...","inter":"oraliq ...",
    "super":"yuqori ...","sub":"ostki ...","de":"aksi ...",
    "co":"birga ...","semi":"yarim ...","auto":"o'z-o'zi ...",
    "out":"tashqarida ...","fore":"oldindan ...","mid":"o'rtacha ...",
    "pro":"...tarafdori","in":"...siz","im":"...siz",
    "il":"...siz","ir":"...siz","poly":"ko'p ...",
    "mono":"bir ...","neo":"yangi ...","trans":"o'tuvchi ...",
    "tele":"uzoqdan ...","counter":"qarshi ...","bi":"ikki ...",
    "ab":"uzoqlashtir...","ob":"qarshi...",
}

# ═══════════════════════════════════════════════════════════════════
#  6 POS MORFOLOGIK QOIDALAR — To'liq va To'g'ri
#
#  NAZARIYA:
#  Har bir qoida: (affiks, ildiz_tiklash_funksiyalari, POS, tavsif)
#
#  Imlo qoidalari (ildiz tiklash):
#    fn1: oddiy        — work+ing → w[:-3] = "work"
#    fn2: silent-e     — making → w[:-3]+"e" = "make"
#    fn3: ikkilanish   — running → w[:-4] = "run" (runn→run)
#    fn4: y→i tiklash  — studied → w[:-3]+"y" = "study"
#    fn5: f→v tiklash  — leaves → w[:-3]+"f" = "leaf"
#
#  MUHIM TARTIB QOIDALARI:
#    1. Uzun affikslar qisqalardan OLDIN (ization > ation > tion)
#    2. Ko'plik: -ies, -ves OLDIN, so'ng -es (FAQAT fn1), oxirda -s
#    3. -es uchun w[:-1] ISHLATILMAYDI — bu "s" ning ishi
#    4. -ly OLDIN tekshiriladi, -ely KEYIN (yoki umuman yo'q)
# ═══════════════════════════════════════════════════════════════════
MORPH_RULES = [

    # ── OLMOSH (M) — M(M,M_A1) = $[i,1-h]Mi ⊕↓ $[j,1-M]M_A1j ──
    ("selves", [lambda w:w[:-5], lambda w:w[:-5]+"f"],               "Olmosh","M←M(-selves o'zlik ko'p)"),
    ("self",   [lambda w:w[:-4]],                                     "Olmosh","M←M(-self o'zlik)"),
    ("ever",   [lambda w:w[:-4]],                                     "Olmosh","M←M(-ever har)"),
    ("thing",  [lambda w:w[:-5]],                                     "Olmosh","M←M(-thing narsa)"),

    # ── SON (F) — F(F,F_A1) = $[i,1-h]Fi ⊕↓ $[j,1-M]F_A1j ──────
    ("fold",   [lambda w:w[:-4]],                                     "Son","F←F(-fold katlalik)"),
    ("teen",   [lambda w:w[:-4]],                                     "Son","F←F(-teen o'ndan ortiq)"),
    ("th",     [lambda w:w[:-2], lambda w:w[:-2]+"e"],                "Son","F←F(-th tartib)"),
    ("ty",     [lambda w:w[:-2]],                                     "Son","F←F(-ty o'nlik)"),

    # ── RAVISH (N) — N(N,N_A1) = $[i,1-h]Ni ⊕↓ $[j,1-M]N_A1j ───
    # NAZARIYA: Ravish = Sifat ildizi + N_A1 affiksi
    # Imlo: quick+ly, easy(y→i)+ly=easily, accurate(e)+ly=accurately
    # TARTIB: -ally, -ily, -ably, -ibly OLDIN; -ly KEYIN
    ("ally",   [lambda w:w[:-4], lambda w:w[:-4]+"al",
                lambda w:w[:-4]+"ic"],                                "Ravish","N←P(-ally: S+ally)"),
    ("ily",    [lambda w:w[:-3]+"y"],                                 "Ravish","N←P(-ily: y→i+ly)"),
    ("ably",   [lambda w:w[:-4]+"able"],                              "Ravish","N←P(-ably: able+ly)"),
    ("ibly",   [lambda w:w[:-4]+"ible", lambda w:w[:-4]],            "Ravish","N←P(-ibly: ible+ly)"),
    # MUHIM: -ly OLDIN -ely dan. "accurately" → -ly fn1="accurate" ✓
    ("ly",     [lambda w:w[:-2], lambda w:w[:-2]+"le",
                lambda w:w[:-2]+"l",  lambda w:w[:-2]+"e"],           "Ravish","N←P(-ly: S+ly)"),
    ("ward",   [lambda w:w[:-4]],                                     "Ravish","N←N(-ward yo'nalish)"),
    ("wards",  [lambda w:w[:-5]],                                     "Ravish","N←N(-wards yo'nalish)"),
    ("wise",   [lambda w:w[:-4]],                                     "Ravish","N←N(-wise usul)"),

    # ── OT (C) — FE'LDAN ISH BAJARUVCHI OT YASOVCHI "-er"/"-or" ──────
    # MUHIM: bu qoidalar "-er" qiyosiy sifat qoidasidan OLDIN turishi shart —
    # aks holda "worker"/"builder"/"tester" (fe'l+er = kim bajaradi) xato
    # ravishda qiyosiy sifat (P1_SF) deb aniqlanib qolardi. Faqat ILDIZ
    # lug'atda FE'L bo'lsa qo'llaniladi (5-element: talab qilingan ildiz turkumi).
    ("er",     [lambda w:w[:-2], lambda w:w[:-2]+"e",
                lambda w:w[:-3], lambda w:w[:-3]+"e"],
                "Ot","C←G(-er: ish bajaruvchi, work→worker)","Fe'l"),
    ("or",     [lambda w:w[:-2], lambda w:w[:-2]+"e"],
                "Ot","C←G(-or: ish bajaruvchi, act→actor)","Fe'l"),

    # ── SIFAT (P) DARAJA — P1_SF qiyosiy, P2_SF orttirma ─────────
    # NAZARIYA:
    #   P1(P1_SF) = $[i,1-h2]P1_SFi  (qiyosiy)
    #   P2(P2_SF) = $[i,1-h2]P2_SFi  (orttirma)
    # Imlo: big+er→bigger(ikkilanish→w[:-3]), large+er→larger(silent-e→w[:-2]+"e")
    #       happy+er→happier(y→i→w[:-3]+"y")
    # TARTIB: -iest,-ier OLDIN (uzunroq), -est,-er KEYIN
    # -iest 4 harfli: y-tiklash w[:-4]+"y" (busiest→busy, KKT spec 2.28). Ilgari
    # w[:-3]+"y" edi — "busiy" berardi, qoida hech qachon ishlamasdi.
    ("iest",   [lambda w:w[:-4]+"y", lambda w:w[:-3]],               "Sifat","P2←P(-iest: y→i orttirma)"),
    ("ier",    [lambda w:w[:-3]+"y"],                                 "Sifat","P1←P(-ier: y→i qiyosiy)"),
    ("est",    [lambda w:w[:-3], lambda w:w[:-3]+"e",
                lambda w:w[:-4], lambda w:w[:-4]+"e"],                "Sifat","P2←P(-est: orttirma)"),
    ("er",     [lambda w:w[:-2], lambda w:w[:-2]+"e",
                lambda w:w[:-3], lambda w:w[:-3]+"e"],                "Sifat","P1←P(-er: qiyosiy)"),

    # ── SIFAT (P) YASOVCHI — P(P,P_A1) = $[i,1-h2]Pi ⊕↓ $[j,1-h2]P_A1j ──
    # Ot yoki Fe'ldan sifat hosil qilish
    ("ical",   [lambda w:w[:-4], lambda w:w[:-2]],                   "Sifat","P←C(-ical: atom→atomic)"),
    ("able",   [lambda w:w[:-4], lambda w:w[:-4]+"e",
                lambda w:w[:-3]],                                      "Sifat","P←G(-able: read→readable)"),
    ("ible",   [lambda w:w[:-4], lambda w:w[:-3]+"e"],               "Sifat","P←G(-ible: access→ible)"),
    ("ful",    [lambda w:w[:-3]],                                     "Sifat","P←C(-ful: use→useful)"),
    ("less",   [lambda w:w[:-4]],                                     "Sifat","P←C(-less: use→useless)"),
    ("ous",    [lambda w:w[:-3], lambda w:w[:-2]+"e"],                "Sifat","P←C(-ous: danger→ous)"),
    ("ive",    [lambda w:w[:-3], lambda w:w[:-3]+"e"],                "Sifat","P←G(-ive: act→ive)"),
    ("ory",    [lambda w:w[:-3], lambda w:w[:-4]+"e",
                lambda w:w[:-4]+"at"],                                 "Sifat","P←G(-ory: mandate→ory)"),
    ("ary",    [lambda w:w[:-3]],                                     "Sifat","P←C(-ary: revolution→ary)"),
    ("ant",    [lambda w:w[:-3]],                                     "Sifat","P←G(-ant: observ→ant)"),
    ("ent",    [lambda w:w[:-3]],                                     "Sifat","P←G(-ent: differ→ent)"),
    ("ic",     [lambda w:w[:-2]],                                     "Sifat","P←C(-ic: atom→ic)"),
    ("al",     [lambda w:w[:-2], lambda w:w[:-2]+"e"],                "Sifat","P←C(-al: form→al)"),
    ("ish",    [lambda w:w[:-3]],                                     "Sifat","P←C(-ish: fool→ish)"),
    ("like",   [lambda w:w[:-4]],                                     "Sifat","P←C(-like: child→like)"),

    # ── OT (C) YASOVCHI — C(G,C_A1) yoki C(P,C_A1) ───────────────
    # NAZARIYA: Fe'l yoki Sifatdan Ot yasash
    # C(G,C_A1) = $[i,1-h]Gi ⊕↓ $[j,1-h1]C_A1j
    # Imlo: optimiz(e)+ation, connect+ion, express→expression
    # TARTIB: uzunroq affikslar OLDIN (-ization > -ation > -tion)
    ("ization",[lambda w:w[:-8]+"ize", lambda w:w[:-7]+"e"],          "Ot","C←G(-ization: modern→ization)"),
    ("isation",[lambda w:w[:-8]+"ise"],                                "Ot","C←G(-isation: organ→isation)"),
    ("ation",  [lambda w:w[:-5], lambda w:w[:-5]+"e",
                lambda w:w[:-5]+"ate"],                                "Ot","C←G(-ation: inform→ation)"),
    ("ition",  [lambda w:w[:-5], lambda w:w[:-4]+"e"],                "Ot","C←G(-ition: add→ition)"),
    ("tion",   [lambda w:w[:-4], lambda w:w[:-4]+"e",
                lambda w:w[:-4]+"t"],                                  "Ot","C←G(-tion: connect→ion)"),
    ("sion",   [lambda w:w[:-4], lambda w:w[:-3]+"d",
                lambda w:w[:-3]+"de"],                                 "Ot","C←G(-sion: express→ion)"),
    ("ment",   [lambda w:w[:-4]],                                     "Ot","C←G(-ment: develop→ment)"),
    ("ness",   [lambda w:w[:-4]],                                     "Ot","C←P(-ness: happy→ness)"),
    ("ity",    [lambda w:w[:-3], lambda w:w[:-3]+"e",
                lambda w:w[:-2]+"ue"],                                 "Ot","C←P(-ity: active→ity)"),
    ("ance",   [lambda w:w[:-4], lambda w:w[:-4]+"e"],                "Ot","C←G(-ance: perform→ance)"),
    ("ence",   [lambda w:w[:-4], lambda w:w[:-4]+"e"],                "Ot","C←G(-ence: exist→ence)"),
    ("ism",    [lambda w:w[:-3]],                                     "Ot","C←C(-ism: real→ism)"),
    ("ist",    [lambda w:w[:-3]],                                     "Ot","C←C(-ist: real→ist)"),
    ("ship",   [lambda w:w[:-4]],                                     "Ot","C←C(-ship: friend→ship)"),
    ("hood",   [lambda w:w[:-4]],                                     "Ot","C←C(-hood: neighbor→hood)"),
    ("dom",    [lambda w:w[:-3]],                                     "Ot","C←C(-dom: free→dom)"),
    ("age",    [lambda w:w[:-3], lambda w:w[:-3]+"e"],                "Ot","C←G(-age: use→age)"),
    ("ure",    [lambda w:w[:-3]],                                     "Ot","C←G(-ure: fail→ure)"),
    ("ology",  [lambda w:w[:-5]],                                     "Ot","C←C(-ology: bi→ology)"),
    ("logy",   [lambda w:w[:-4]],                                     "Ot","C←C(-logy: techno→logy)"),
    ("ics",    [lambda w:w[:-3]],                                     "Ot","C←C(-ics: economic→s)"),

    # ── FE'L (G) YASOVCHI — G(G,G_SF) = $[i,1-h3]Gi ⊕↓ $[j,1-h3]G_SFj ──
    # NAZARIYA: Ot yoki Sifatdan Fe'l yasash
    # Imlo: simplify → simpl+ify (w[:-3]+"e"="simple" → simple+ify)
    #       modernize → modern+ize (w[:-3]="modern")
    ("izing",  [lambda w:w[:-4]+"e", lambda w:w[:-3]],               "Fe'l","G←G(-izing: optim→izing)"),
    ("ifying", [lambda w:w[:-4]+"y"],                                 "Fe'l","G←G(-ifying: simpl→ifying)"),
    # MUHIM: -ize va -ify uchun silent-e tiklash qo'shildi
    ("ize",    [lambda w:w[:-3], lambda w:w[:-3]+"e"],               "Fe'l","G←C/P(-ize: modern→ize)"),
    ("ise",    [lambda w:w[:-3], lambda w:w[:-3]+"e"],               "Fe'l","G←C/P(-ise: organ→ise)"),
    ("ify",    [lambda w:w[:-3], lambda w:w[:-3]+"e",
                lambda w:w[:-2]+"y"],                                  "Fe'l","G←C/P(-ify: simpl→ify=simple)"),
    ("en",     [lambda w:w[:-2]],                                     "Fe'l","G←P(-en: bright→en)"),

    # ── FE'L (G) ZAMON — G(G_A1) = $[i,1-h3]G_A1i ───────────────
    # NAZARIYA: Fe'l shakllari — Ingliz grammarsidagi 4 asosiy shakl
    # Imlo qoidalari:
    #   -ing: work+ing (oddiy), mak+ing → make (silent-e), runn+ing → run (ikkilanish)
    #   -ied: studi+ed → study (y→i qoidasi)
    #   -ed:  work+ed (oddiy), lov+ed → love (silent-e), stopp+ed → stop (ikkilanish)
    # TARTIB: -ied OLDIN (y→i aniqroq), -ing, so'ng -ed
    ("ied",    [lambda w:w[:-3]+"y"],                                 "Fe'l","G←G(-ied: y→i o'tgan)"),
    ("ing",    [lambda w:w[:-3], lambda w:w[:-3]+"e",
                lambda w:w[:-4], lambda w:w[:-4]+"e"],                "Fe'l","G←G(-ing sifatdosh)"),
    ("ed",     [lambda w:w[:-2], lambda w:w[:-2]+"e",
                lambda w:w[:-3], lambda w:w[:-3]+"e"],                "Fe'l","G←G(-ed o'tgan)"),

    # ── OT (C) KO'PLIK — C(C,X) = $[i,1-h]Ci ⊕↓ $[j,1-2]Xj ─────
    # NAZARIYA: Ingliz tilida 4 xil ko'plik shakli:
    #   X:  -s  → oddiy (algorithm+s, model+s)
    #   X1: -es → s,ss,x,ch,sh da tugasa (process+es)
    #   X1: -ies → y→i+es (capabilit+ies ← capability)
    #   X1: -ves → f→v+es (leav+es ← leaf)
    #
    # MUHIM TARTIB QOIDASI:
    #   1. -ies OLDIN (y→i): "capabilities" → capability ✓
    #   2. -ves OLDIN (f→v): "leaves" → leaf ✓
    #   3. -es FAQAT w[:-2] (fn1): "variabl" yo'q, "process" bor
    #      w[:-1] ISHLATILMAYDI! → bu -s ning ishi
    #   4. -s OXIRIDA: "variable" bor → to'g'ri
    ("ies",    [lambda w:w[:-3]+"y"],                                 "Ot","C4←C(-ies: y→i ko'plik)"),
    ("ves",    [lambda w:w[:-3]+"f", lambda w:w[:-3]+"fe"],          "Ot","C7←C(-ves: f→v ko'plik)"),
    # MUHIM: -es uchun FAQAT fn1=w[:-2] — w[:-1] YO'Q!
    ("es",     [lambda w:w[:-2]],                                     "Ot","C3←C(-es ko'plik)"),
    # ── FE'L (G) 3-SHAXS BIRLIK HOZIRGI ZAMON "-s" (KKT spec 2.37: speak+s =
    #    speaks → gapir+a+di = gapiradi). Ot ko'plik "-s" dan OLDIN turishi
    #    shart, lekin FAQAT ildiz lug'atda FE'L bo'lsa ishlaydi (5-element —
    #    agentiv "-er" bilan bir xil mexanizm); qolgan barcha "-s" so'zlar
    #    avvalgidek ot ko'pligiga tushadi.
    ("s",      [lambda w:w[:-1]],
                "Fe'l","G←G(-s: 3-shaxs birlik hozirgi zamon)","Fe'l"),
    # -s oxirida — barcha qolganlarni tutib oladi
    ("s",      [lambda w:w[:-1]],                                     "Ot","C1←C(-s ko'plik)"),
]

# ═══════════════════════════════════════════════════════════════════
#  O'ZBEK MORFOLOGIYA — KKT MM asosida tarjima
# ═══════════════════════════════════════════════════════════════════
def uz_stem(uz_text):
    """O'zbek so'zining ildizini ajratadi."""
    t = re.split(r"\s*/\s*|\s*\|\s*", uz_text)[0].strip()
    t = re.sub(r"\s*\(.*?\)", "", t).strip()
    if t.endswith("moq"): t = t[:-3].rstrip()
    return t.strip()


def make_uzbek(root_uz, sfx, pos=None):
    """
    KKT MM asosida ingliz affiksiga mos o'zbek morfologik shakli.

    `pos` — ingliz so'zining ANIQLANGAN turkumi (ixtiyoriy). Hozircha faqat
    bitta affiks turkumga qarab ikki xil ma'noga ega: "-s" (Ot ko'plik yoki
    Fe'l 3-shaxs birlik hozirgi zamon, KKT spec 2.37).

    Har bir ingliz affiks → o'zbek ekvivalenti:
      Fe'l 3-sh. birlik: -s (pos=Fe'l)  → +adi (undoshdan keyin, spec 2.37:
                                          gapir+a+di) / +ydi (unlidan keyin —
                                          o'zbek imlosi, spec misolida yo'q)
      Ot ko'plik:      -s/-es/-ies/-ves → +lar    [X: 0.00101]
      Fe'l sifatdosh:  -ing             → +ayotgan [G_A1: 0.00303]
      Fe'l o'tgan:     -ed/-ied         → +gan     [G_A1: 0.00301]
      Sifat qiyosiy:   -er/-ier         → +roq     [P1_A1: 0.00304]
      Sifat orttirma:  -est/-iest       → eng+     [P2_D: 0.07]
      Ravish:          -ly/-ally        → +tarzda  [N_A1: 0.00204]
      Sifat yasovchi:  -able/-ible      → +ladigan [P_A1: 0.00219]
      Ot yasovchi:     -tion/-ment      → +ish     [C_A1: 0.00209]
      Fe'l yasovchi:   -ize/-ify        → +lashtirmoq [G_SF: 0.00219]
    """
    stem = uz_stem(root_uz)
    if sfx in ("est","iest"): return "eng " + stem
    if sfx == "s" and pos == "Fe'l":
        ends_vowel = stem.rstrip("'‘’ʻʼ")[-1:].lower() in "aeiou"
        return stem + ("ydi" if ends_vowel else "adi")
    rules = {
        # OT ko'plik
        "s":    stem+"lar", "es":  stem+"lar",
        "ies":  stem+"lar", "ves": stem+"lar",
        # FE'L shakllari
        "ing":  stem+"ayotgan", "ying": stem+"ayotgan",
        "zing": stem+"ayotgan", "izing":stem+"layotgan",
        "ifying":stem+"layotgan",
        "ied":  stem+"gan",     "ed":   stem+"gan",
        # SIFAT daraja
        "er":   stem+"roq",     "ier":  stem+"roq",
        # RAVISH
        "ly":   stem+" tarzda", "ally": stem+" tarzda",
        "ily":  stem+" tarzda", "ably": stem+" tarzda",
        "ibly": stem+" tarzda",
        "ward": stem+" tomon",  "wards":stem+" tomon",
        "wise": stem+" jihatdan",
        # SIFAT yasovchi
        "able": stem+"ladigan", "ible": stem+"ladigan",
        "ful":  stem+"li",      "ous":  stem+"li",
        "ive":  stem+"li",      "ant":  stem+"li",
        "ent":  stem+"li",      "like": stem+"ga o'xshash",
        "less": stem+"siz",     "ish":  stem+"simon",
        "ic":   stem+"ga oid",  "al":   stem+"ga oid",
        "ical": stem+"ga oid",  "ary":  stem+"ga oid",
        "ory":  stem+"ga oid",
        # OT yasovchi
        "ation":stem+"ish",     "ition":stem+"ish",
        "tion": stem+"ish",     "sion": stem+"ish",
        "ment": stem+"ish",     "age":  stem+"ish",
        "ure":  stem+"ish",     "ness": stem+"lik",
        "ity":  stem+"lik",     "ance": stem+"lik",
        "ence": stem+"lik",     "hood": stem+"lik",
        "dom":  stem+"lik",     "ship": stem+"chilik",
        "ism":  stem+"izm",     "ist":  stem+"chi",
        "ology":stem+" fani",   "logy": stem+" fani",
        "ics":  stem+" fani",
        "ization":stem+"lashtirish",
        "isation":stem+"lashtirish",
        # FE'L yasovchi
        "ize":  stem+"lashtirmoq", "ise": stem+"lashtirmoq",
        "ify":  stem+"lashtirmoq", "en":  stem+"lashtirmoq",
        # OLMOSH
        "self": stem+" o'zi",   "selves":stem+" o'zlari",
        "ever": stem+" ham bo'lsa", "thing":stem+"narsa",
        # SON
        "teen": "o'n "+stem,    "ty":   stem+" o'nlik",
        "th":   stem+"inchi",   "fold": stem+" katlalik",
        # EGALIK (qaratqich kelishigi)
        "'s":   stem+"ning",
    }
    return rules.get(sfx, stem)

# ═══════════════════════════════════════════════════════════════════
#  KKT MM HISOBLASH FUNKSIYALARI
# ═══════════════════════════════════════════════════════════════════
def kkt_en(analysis):
    """Ingliz so'zi uchun KKT MM: K(K,A1) = $[i,1-h]Ki ⊕↓ $[j,1-M]A1j
    (13-15-qadam: vaznlar BM_en_w bazasidan — smart_parse orqali — olinadi).
    Avval BM_en_w.word_models'da (so_zlar_bazasi_un.docx'dan yuklangan,
    dissertatsiyada TEKSHIRILGAN) aniq so'z uchun model bor-yo'qligi
    tekshiriladi — bo'lsa O'SHA ishlatiladi (haqiqiy manba, taxminiy emas)."""
    if not analysis.get("found"):
        return {"kkt":"?","mm":"Topilmadi","v2":0.0,"v3":0.0,"total":0.0,"sfx_kkt":"","pfx_kkt":""}
    verified = bm_lookup_word_model(DB_BM_EN, analysis.get("word",""))
    kkt=analysis.get("bm_pos_kkt_en") or POS_KKT.get(analysis.get("pos") or "Ot","C")
    v2=analysis.get("bm_pos_v2_en", POS_V2.get(analysis.get("pos") or "Ot",0.85))
    sfx=analysis.get("suffix",""); pfx=analysis.get("prefix","")
    sfx_kkt=analysis.get("bm_sfx_kkt_en","") if sfx else ""
    sfx_v3=analysis.get("bm_sfx_v3_en",0.0) if sfx else 0.0
    pfx_v3=analysis.get("bm_pfx_v3_en",0.01 if pfx else 0.0)
    pfx_kkt=analysis.get("bm_pfx_kkt_en","T") if pfx else ""
    total_v3=sfx_v3+pfx_v3
    if verified:
        mm = verified["mm"]
    else:
        hv=POS_H.get(analysis.get("pos") or "Ot","h")
        segs=[]
        if pfx:  segs.append(f"$[i,1-L]{pfx_kkt}i")
        segs.append(f"$[i,1-{hv}]{kkt}i")
        if sfx:  segs.append(f"$[j,1-M]{sfx_kkt}j")
        labels=[x for x in [pfx_kkt,kkt,sfx_kkt] if x]
        mm=f"{kkt}({','.join(labels)}) = {'⊕↓'.join(segs)}"
    return {"kkt":kkt,"mm":mm,"v2":v2,"v3":total_v3,"total":v2+total_v3,"sfx_kkt":sfx_kkt,"pfx_kkt":pfx_kkt,
            "verified":bool(verified)}


def kkt_uz(analysis):
    """O'zbek so'zi uchun KKT MM (16-qadam: POS vazni BM_uz_w bazasidan;
    qo'shimcha esa yakuniy sintez qilingan so'zdan qayta aniqlanadi).
    Avval BM_uz_w.word_models'da tekshirilgan model bor-yo'qligi ko'riladi."""
    if not analysis.get("found") or not analysis.get("uz"):
        return {"kkt":"?","mm":"Topilmadi","v2":0.0,"v3":0.0,"total":0.0,"sfx_kkt":"","sfx":"","root":""}
    uz=analysis["uz"]; pos=analysis.get("pos") or "Ot"
    verified = bm_lookup_word_model(DB_BM_UZ, uz)
    kkt=analysis.get("bm_pos_kkt_uz") or POS_KKT.get(pos,"C")
    v2=analysis.get("bm_pos_v2_uz", POS_V2.get(pos,0.85))
    us,uk,uv,ur=_detect_uz_affix(uz)
    if verified:
        return {"kkt":kkt,"mm":verified["mm"],"v2":v2,"v3":uv,"total":v2+uv,"sfx_kkt":uk,"sfx":us,"root":ur,"verified":True}
    hv=POS_H.get(pos,"h")
    if uz.startswith("eng "):
        mm=f"{kkt}(P2_D,{kkt}) = $[i,1-3]P2_Di ⊕↓ $[j,1-{hv}]{kkt}j"
        return {"kkt":kkt,"mm":mm,"v2":0.07+v2,"v3":0.0,"total":0.07+v2,"sfx_kkt":"P2_D","sfx":"eng","root":uz[4:],"verified":False}
    if us:
        mm=f"{kkt}({kkt},{uk}) = $[i,1-{hv}]{kkt}i ⊕↓ $[j,1-M]{uk}j"
    else:
        mm=f"{kkt}({kkt}) = $[i,1-{hv}]{kkt}i"
    return {"kkt":kkt,"mm":mm,"v2":v2,"v3":uv,"total":v2+uv,"sfx_kkt":uk,"sfx":us,"root":ur,"verified":False}


def _detect_uz_affix(word):
    """O'zbek so'zidan affiksni ajratadi — uzundan qisqaga."""
    w=re.split(r"\s*/\s*|\s*\|\s*",word)[0].strip()
    w=re.sub(r"\s*\(.*?\)","",w).strip()
    if w.endswith("moq"): return "moq","G_A1",0.00303,w[:-3].rstrip()
    for sfx in sorted(UZ_AFF_V3.keys(),key=lambda x:-len(x)):
        if w.endswith(sfx) and len(w)>len(sfx)+1:
            kk,v3=UZ_AFF_V3[sfx]; return sfx,kk,v3,w[:-len(sfx)]
    return "","",0.0,w

# ═══════════════════════════════════════════════════════════════════
#  BAZA OPERATSIYALARI — 8 ta SQLite baza (BM / UB / QM / PSB × en/uz)
# ═══════════════════════════════════════════════════════════════════
def _create_bm_tables(conn):
    """BM_en_w / BM_uz_w — so'z turkumlari uchun FORMAL modellar bazasi."""
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS formal_model(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        affix TEXT NOT NULL,
        kkt_symbol TEXT NOT NULL,
        v3_weight REAL NOT NULL DEFAULT 0.0,
        UNIQUE(affix))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS kkt_symbols(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kkt_symbol TEXT NOT NULL,
        funktsiya TEXT,
        weight REAL,
        UNIQUE(kkt_symbol))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS pos_weight(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pos TEXT NOT NULL UNIQUE,
        kkt_symbol TEXT NOT NULL,
        v2_weight REAL NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS word_models(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        headword TEXT NOT NULL,
        pos TEXT NOT NULL,
        kkt_model TEXT NOT NULL,
        UNIQUE(headword,kkt_model))""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_wm_headword ON word_models(headword)")
    cur.execute("""CREATE TABLE IF NOT EXISTS grammar_rules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        headword TEXT,
        pos TEXT,
        rule_text TEXT NOT NULL,
        UNIQUE(headword,rule_text))""")
    conn.commit()

def _create_ub_tables(conn):
    """UB_en_w / UB_uz_w — so'z turkumlarining (lug'at) bazasi."""
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS words(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        headword TEXT NOT NULL,
        translation TEXT NOT NULL,
        pos TEXT NOT NULL DEFAULT 'Ot',
        source TEXT NOT NULL DEFAULT 'docx',
        formal_model TEXT,
        UNIQUE(headword,translation))""")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_headword ON words(headword)")
    conn.commit()

def _create_qm_tables(conn):
    """QM_en_w / QM_uz_w — qo'shimchalar (affikslar) bazasi."""
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS affixes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pos TEXT NOT NULL,
        category TEXT NOT NULL,
        kkt_symbol TEXT,
        value TEXT NOT NULL,
        weight REAL,
        UNIQUE(category,value))""")
    conn.commit()

def _create_psb_tables(conn):
    """PSB_en_w / PSB_uz_w — predmet sohalar (terminologik) bazasi."""
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS terms(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT NOT NULL,
        domain TEXT NOT NULL DEFAULT 'Umumiy',
        pos TEXT NOT NULL DEFAULT 'Ot',
        definition TEXT,
        UNIQUE(term,domain))""")
    conn.commit()

def _ensure_column(conn, table, column, coltype):
    """Jadval MAVJUD bo'lsa-yu, lekin unda `column` yo'q bo'lsa (masalan
    ESKI versiyadan qolgan .db fayl) — ustunni ALTER TABLE bilan qo'shadi.
    Bu, aynan, versiyalar orasida (v13->v18) bir xil papkada saqlanib
    qolgan eski bazalar sababli 'no such column' xatoligini (va shu bilan
    GUI ochilishidan OLDIN dastur to'xtab qolishini) oldini oladi."""
    try:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if cols and column not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
            conn.commit()
    except Exception as e:
        show_error_dialog("Baza sxemasi xatosi",
            f"{table}.{column} ustunini tekshirishda xatolik:\n{e}")


def init_all_databases():
    """9 ta bazani (bo'sh sxema bilan) yaratadi/tekshiradi va ESKI
    versiyalardan qolgan bazalarni yangi sxemaga moslashtiradi (migratsiya)."""
    for path,creator in (
        (DB_BM_EN,_create_bm_tables),(DB_BM_UZ,_create_bm_tables),
        (DB_UB_EN,_create_ub_tables),(DB_UB_UZ,_create_ub_tables),
        (DB_QM_EN,_create_qm_tables),(DB_QM_UZ,_create_qm_tables),
        (DB_PSB_EN,_create_psb_tables),(DB_PSB_UZ,_create_psb_tables),
        (DB_MDB_UZ,_create_mdb_tables)):
        try:
            conn=sqlite3.connect(path); creator(conn)
        except Exception as e:
            show_error_dialog("Baza yaratish xatosi",
                f"{os.path.basename(path)} yaratishda xatolik:\n{e}")
            conn=sqlite3.connect(path)
        # ── migratsiya: eski bazalarda yo'q bo'lishi mumkin bo'lgan ustunlar ──
        if path in (DB_UB_EN,DB_UB_UZ):
            _ensure_column(conn,"words","formal_model","TEXT")
        conn.close()

def setup_database(docx_path=None):
    """UB_en_w / UB_uz_w (lug'at) va BM_en_w / BM_uz_w (formal modellar) bazalarini to'ldiradi."""
    for path in (DB_UB_EN,DB_UB_UZ,DB_BM_EN,DB_BM_UZ):
        if os.path.exists(path): os.remove(path)
    init_all_databases()

    # BM_en_w — Ingliz affikslarining formal modellari (EN_AFF_V3)
    conn=sqlite3.connect(DB_BM_EN); cur=conn.cursor()
    for aff,(kkt,v3) in EN_AFF_V3.items():
        cur.execute("INSERT OR IGNORE INTO formal_model(affix,kkt_symbol,v3_weight) VALUES(?,?,?)",(aff,kkt,v3))
    for pos,sym in POS_KKT.items():
        cur.execute("INSERT OR IGNORE INTO pos_weight(pos,kkt_symbol,v2_weight) VALUES(?,?,?)",(pos,sym,POS_V2.get(pos,0.5)))
    conn.commit(); conn.close()

    # BM_uz_w — O'zbek affikslarining formal modellari (UZ_AFF_V3)
    conn=sqlite3.connect(DB_BM_UZ); cur=conn.cursor()
    for aff,(kkt,v3) in UZ_AFF_V3.items():
        cur.execute("INSERT OR IGNORE INTO formal_model(affix,kkt_symbol,v3_weight) VALUES(?,?,?)",(aff,kkt,v3))
    for pos,sym in POS_KKT.items():
        cur.execute("INSERT OR IGNORE INTO pos_weight(pos,kkt_symbol,v2_weight) VALUES(?,?,?)",(pos,sym,POS_V2.get(pos,0.5)))
    conn.commit(); conn.close()

    # UB_en_w / UB_uz_w — EN-UZ so'z juftliklari (har til o'z bazasida).
    # Avval data/*.json (data_loader.py) dan, topilmasa/xato bo'lsa — DOCX'dan.
    inserted=0
    conn_en=sqlite3.connect(DB_UB_EN); cur_en=conn_en.cursor()
    conn_uz=sqlite3.connect(DB_UB_UZ); cur_uz=conn_uz.cursor()
    try:
        inserted = _load_words_from_json(cur_en, cur_uz)
        if inserted: print(f"  JSON dan {inserted} ta so'z jufti topildi (data/1500_EN_UZ_6_POS_sorted.20.json).")
    except Exception as e:
        show_error_dialog("So'z juftlarini yuklash xatosi",
            f"JSON so'z juftlari xatosi, DOCX zaxiraga o'tilmoqda:\n{e}")
    if not inserted and docx_path and HAS_DOCX:
        try:
            inserted = _load_words_from_docx(docx_path, cur_en, cur_uz)
        except Exception as e:
            show_error_dialog("So'z juftlarini yuklash xatosi", f"DOCX xatosi:\n{e}")
    conn_en.commit(); conn_en.close(); conn_uz.commit(); conn_uz.close()
    return inserted


def _load_words_from_json(cur_en, cur_uz):
    """data/1500_EN_UZ_6_POS_sorted.20.json (data_loader.py orqali) dan
    EN-UZ so'z juftlarini UB_en_w / UB_uz_w kursorlariga yozadi."""
    from data_loader import load_word_pairs
    wp_table = load_word_pairs()
    inserted = 0
    for cat in wp_table.category_names:
        cpos = "Ot"
        upper = cat.upper()
        for key, label in POS_MAP.items():
            if upper.startswith(key): cpos = label; break
        for wp in wp_table.by_category(cat):
            eng = wp.english.strip().lower(); uzb = wp.uzbek.strip()
            if not eng or not uzb: continue
            try:
                cur_en.execute("INSERT OR IGNORE INTO words(headword,translation,pos,source) VALUES(?,?,?,'json')",(eng,uzb,cpos))
                cur_uz.execute("INSERT OR IGNORE INTO words(headword,translation,pos,source) VALUES(?,?,?,'json')",(uzb,eng,cpos))
                inserted += 1
            except: pass
    return inserted


def _load_words_from_docx(docx_path, cur_en, cur_uz):
    """Zaxira yo'l: asl .docx faylni to'g'ridan-to'g'ri o'qib EN-UZ so'z
    juftlarini UB_en_w / UB_uz_w kursorlariga yozadi (JSON topilmasa)."""
    inserted = 0
    doc=Document(docx_path); cpos="Ot"
    for para in doc.paragraphs:
        text=para.text.strip()
        if not text: continue
        upper=text.upper()
        for key,label in POS_MAP.items():
            if upper.startswith(key): cpos=label; break
        m=re.match(r"^\d+\.\s+(.+?)\s+[\u2013\u2014-]{1,2}\s+(.+)$",text)
        if m:
            eng=m.group(1).strip().lower(); uzb=m.group(2).strip()
            try:
                cur_en.execute("INSERT OR IGNORE INTO words(headword,translation,pos,source) VALUES(?,?,?,'docx')",(eng,uzb,cpos))
                cur_uz.execute("INSERT OR IGNORE INTO words(headword,translation,pos,source) VALUES(?,?,?,'docx')",(uzb,eng,cpos))
                inserted+=1
            except: pass
    return inserted

# Varaq -> POS xaritasi (ingliz va o'zbek affikslar uchun, xlsx davridan
# meros — 7-BOSHQA faqat UZ tomonida ishlatiladi, EN tomonida ishlatilmagan).
_EN_AFF_SHEET_POS = {'1-OT':'Ot','2-SIFAT':'Sifat',"3-FE'L":"Fe'l",'4-RAVISH':'Ravish','5-OLMOSH':'Olmosh','6-SON':'Son'}
_UZ_AFF_SHEET_POS = {'1-OT':'Ot','2-SIFAT':'Sifat',"3-FE'L":"Fe'l",'4-RAVISH':'Ravish','5-OLMOSH':'Olmosh','6-SON':'Son','7-BOSHQA':'Boshqa'}


def _load_en_affixes_from_json(cur_en):
    """data/Table_English ...json (data_loader.py orqali) dan ingliz
    affikslarini QM_en_w kursoriga yozadi. Qaytaradi: qo'shilgan qatorlar soni."""
    from data_loader import load_english_affixes
    en_table = load_english_affixes()
    added = 0
    for shnm,pos in _EN_AFF_SHEET_POS.items():
        for g in en_table.groups(shnm):
            cat = g.code
            if not cat: continue
            for it in g.items:
                v = it.value
                if v is None: continue
                vs = str(v).strip()
                if not vs or vs=='None': continue
                try: float(vs); continue
                except: pass
                vclean = vs.strip('-').strip()
                if not vclean: continue
                wv = it.weight if it.weight is not None else 0.01
                cur_en.execute("INSERT OR IGNORE INTO affixes(pos,category,value,weight) VALUES(?,?,?,?)",(pos,cat,vclean,wv)); added+=cur_en.rowcount
    return added


def _load_en_affixes_from_xlsx(cur_en):
    """Zaxira yo'l: asl Table_English ...xlsx faylni to'g'ridan-to'g'ri o'qiydi (JSON topilmasa)."""
    import openpyxl
    added = 0
    if not os.path.exists(XLSX_EN): return added
    wb=openpyxl.load_workbook(XLSX_EN)
    for shnm,pos in _EN_AFF_SHEET_POS.items():
        if shnm not in wb.sheetnames: continue
        ws=wb[shnm]; rows=list(ws.iter_rows(values_only=True))
        if len(rows)<2: continue
        cc=[]
        for ci,cell in enumerate(rows[1]):
            if cell and str(cell).strip() and '-' in str(cell): cc.append((str(cell).strip(),ci,ci+1))
        for cat,vc,wc in cc:
            for row in rows[2:]:
                v=row[vc] if vc<len(row) else None
                if not v or str(v).strip() in ('','None'): continue
                try: float(str(v)); continue
                except: pass
                vclean=str(v).strip().strip('-').strip()
                if not vclean: continue
                wv=0.01
                try:
                    wr=row[wc] if wc<len(row) else None
                    if wr: wv=float(str(wr).replace(',','.'))
                except: pass
                cur_en.execute("INSERT OR IGNORE INTO affixes(pos,category,value,weight) VALUES(?,?,?,?)",(pos,cat,vclean,wv)); added+=cur_en.rowcount
    return added


def _load_uz_affixes_from_json(cur_uz):
    """data/Lotinda Table_Uzbek ...json (data_loader.py orqali) dan o'zbek
    affikslarini QM_uz_w kursoriga yozadi. Qaytaradi: qo'shilgan qatorlar soni."""
    from data_loader import load_uzbek_affixes
    uz_table = load_uzbek_affixes()
    added = 0
    for shnm,pos in _UZ_AFF_SHEET_POS.items():
        for g in uz_table.groups(shnm):
            cat = g.code
            if not cat: continue
            for it in g.items:
                v = it.value
                if v is None: continue
                vs = str(v).strip()
                if not vs or vs=='None': continue
                try: float(vs); continue
                except: pass
                if any('\u0400'<=c<='\u04ff' for c in vs): continue
                cur_uz.execute("INSERT OR IGNORE INTO affixes(pos,category,value,weight) VALUES(?,?,?,0.01)",(pos,cat,vs)); added+=cur_uz.rowcount
    return added


def _load_uz_affixes_from_xlsx(cur_uz):
    """Zaxira yo'l: asl Lotinda Table_Uzbek ...xlsx faylni to'g'ridan-to'g'ri o'qiydi (JSON topilmasa)."""
    import openpyxl
    added = 0
    if not os.path.exists(XLSX_UZ): return added
    wb2=openpyxl.load_workbook(XLSX_UZ)
    for shnm,pos in _UZ_AFF_SHEET_POS.items():
        if shnm not in wb2.sheetnames: continue
        ws=wb2[shnm]; rows=list(ws.iter_rows(values_only=True))
        for ri,row in enumerate(rows):
            if ri==0: continue
            rs=[str(c).strip() if c else '' for c in row]
            hc=any('-' in c or c in ('X','U') for c in rs if c and c!='No')
            if not hc: continue
            cats=[]
            for ci,cell in enumerate(row):
                if not cell: continue
                cs=str(cell).strip()
                if cs in ('No','None',''): continue
                try: float(cs); continue
                except: pass
                cats.append((cs,ci))
            for dr in rows[ri+1:]:
                for cat,ci in cats:
                    val=dr[ci] if ci<len(dr) else None
                    if not val: continue
                    vs=str(val).strip()
                    if not vs or vs=='None': continue
                    try: float(vs); continue
                    except: pass
                    if any('\u0400'<=c<='\u04ff' for c in vs): continue
                    cur_uz.execute("INSERT OR IGNORE INTO affixes(pos,category,value,weight) VALUES(?,?,?,0.01)",(pos,cat,vs)); added+=cur_uz.rowcount
    return added


def load_xlsx_affixes():
    """QM_en_w / QM_uz_w — qo'shimchalarni yuklaydi. Avval data/*.json
    (data_loader.py) dan, topilmasa/xato bo'lsa — asl Excel fayllardan."""
    for path in (DB_QM_EN,DB_QM_UZ):
        if os.path.exists(path): os.remove(path)
    init_all_databases()

    conn_uz=sqlite3.connect(DB_QM_UZ); cur_uz=conn_uz.cursor()
    for cat,afl in UZ_AFFIXES.items():
        for a in afl:
            cur_uz.execute("INSERT OR IGNORE INTO affixes(pos,category,value,weight) VALUES('*',?,?,0.01)",(cat,a.strip()))
    added=0

    conn_en=sqlite3.connect(DB_QM_EN); cur_en=conn_en.cursor()
    try:
        n = _load_en_affixes_from_json(cur_en)
        added += n
        if n: print(f"  JSON dan {n} ta ingliz affiksi topildi (data/Table_English 1-7 Vazn Type 2 14.02.2024.json).")
    except Exception as e:
        show_error_dialog("Affikslarni yuklash xatosi",
            f"JSON (EN affikslar) xatosi, XLSX zaxiraga o'tilmoqda:\n{e}")
        try: added += _load_en_affixes_from_xlsx(cur_en)
        except Exception as e2:
            show_error_dialog("Affikslarni yuklash xatosi", f"XLSX_EN:\n{e2}")
    conn_en.commit(); conn_en.close()

    try:
        n = _load_uz_affixes_from_json(cur_uz)
        added += n
        if n: print(f"  JSON dan {n} ta o'zbek affiksi topildi (data/Lotinda Table_Uzbek 1-7 Vazn 11.02.2025.json).")
    except Exception as e:
        show_error_dialog("Affikslarni yuklash xatosi",
            f"JSON (UZ affikslar) xatosi, XLSX zaxiraga o'tilmoqda:\n{e}")
        try: added += _load_uz_affixes_from_xlsx(cur_uz)
        except Exception as e2:
            show_error_dialog("Affikslarni yuklash xatosi", f"XLSX_UZ:\n{e2}")
    conn_uz.commit(); conn_uz.close()
    return added

def db_lookup(english):
    """UB_en_w bazasidan inglizcha so'zni qidiradi -> (english,uzbek,pos,source)."""
    try:
        conn=sqlite3.connect(DB_UB_EN); cur=conn.cursor()
        cur.execute("SELECT headword,translation,pos,source FROM words WHERE headword=?",(english.lower().strip(),))
        row=cur.fetchone(); conn.close(); return row
    except: return None

def db_insert(english, uzbek, pos, source="auto"):
    """Yangi juftlikni UB_en_w va UB_uz_w bazalariga (har biriga o'z yo'nalishida) qo'shadi.
    readonly_mode() ichida hech narsa yozmaydi, False qaytaradi (chunki
    haqiqatan ham hech narsa qo'shilmadi)."""
    if is_readonly(): return False
    try:
        conn=sqlite3.connect(DB_UB_EN); cur=conn.cursor()
        cur.execute("INSERT OR IGNORE INTO words(headword,translation,pos,source) VALUES(?,?,?,?)",
                    (english.lower().strip(),uzbek.strip(),pos,source))
        added=cur.rowcount>0; conn.commit(); conn.close()
        conn2=sqlite3.connect(DB_UB_UZ); cur2=conn2.cursor()
        cur2.execute("INSERT OR IGNORE INTO words(headword,translation,pos,source) VALUES(?,?,?,?)",
                    (uzbek.strip(),english.lower().strip(),pos,source))
        conn2.commit(); conn2.close()
        return added
    except: return False

def db_stats():
    try:
        conn=sqlite3.connect(DB_UB_EN); cur=conn.cursor()
        cur.execute("SELECT COUNT(*) FROM words"); total=cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM words WHERE source='auto'"); auto=cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM words WHERE source='user'"); user=cur.fetchone()[0]
        cur.execute("SELECT pos,COUNT(*) FROM words GROUP BY pos ORDER BY COUNT(*) DESC")
        bp=cur.fetchall(); conn.close()
        ae=au=0
        if os.path.exists(DB_QM_EN):
            c=sqlite3.connect(DB_QM_EN); ae=c.execute("SELECT COUNT(*) FROM affixes").fetchone()[0]; c.close()
        if os.path.exists(DB_QM_UZ):
            c=sqlite3.connect(DB_QM_UZ); au=c.execute("SELECT COUNT(*) FROM affixes").fetchone()[0]; c.close()
        return {"total":total,"auto":auto,"user":user,"aff_en":ae,"aff_uz":au,"by_pos":bp}
    except: return {"total":0,"auto":0,"user":0,"aff_en":0,"aff_uz":0,"by_pos":[]}

# ═══════════════════════════════════════════════════════════════════
#  21-QADAMLI KKT TARJIMA ALGORITMI — baza-yordamchi funksiyalar
#  (4,5,6,17,18-qadam: UB/QM dan ID orqali qidirish, ko'p ma'nolilik;
#   13,14,16-qadam: BM_en_w/BM_uz_w dan formal model qidirish/yaratish)
# ═══════════════════════════════════════════════════════════════════
def db_lookup_all(english):
    """4-qadam: UB_en_w bazasidan berilgan so'zning BARCHA yozuvlarini (ko'p
    ma'noli bo'lsa hammasini) qaytaradi -> [(id,headword,translation,pos,source,formal_model), ...]"""
    try:
        conn=sqlite3.connect(DB_UB_EN)
        rows=conn.execute("""SELECT id,headword,translation,pos,source,formal_model
                              FROM words WHERE headword=? ORDER BY id""",
                           (english.lower().strip(),)).fetchall()
        conn.close(); return rows
    except: return []

def db_lookup_by_id(db_path, wid):
    """17-qadam: berilgan ID bo'yicha UB_uz_w (yoki UB_en_w) dan to'g'ridan-to'g'ri qidiradi."""
    if wid is None: return None
    try:
        conn=sqlite3.connect(db_path)
        row=conn.execute("""SELECT id,headword,translation,pos,source,formal_model
                             FROM words WHERE id=?""",(wid,)).fetchone()
        conn.close(); return row
    except: return None

def psb_select_meaning(rows, domain=None):
    """6/20-qadam: so'z ko'p ma'noli bo'lsa, PSB_uz_w (predmet sohalar bazasi) asosida
    ustuvor ma'noni tanlaydi. PSB'da mos domain topilmasa — birinchi (asosiy) ma'no olinadi."""
    if not rows: return None
    if len(rows)==1 or not domain: return rows[0]
    try:
        conn=sqlite3.connect(DB_PSB_UZ)
        for r in rows:
            hit=conn.execute("SELECT 1 FROM terms WHERE term=? AND domain=?",(r[2],domain)).fetchone()
            if hit: conn.close(); return r
        conn.close()
    except: pass
    return rows[0]

def qm_confirm_or_add(db_path, affix_text, pos, is_prefix, kkt_symbol_hint=None):
    """8-9 / 10-11-qadam: QM_en_w(yoki QM_uz_w)da qo'shimcha borligini tekshiradi;
    topilmasa — YANGI qo'shimcha sifatida bazaga yozadi (o'z-o'zini rivojlantirish).
    readonly_mode() ichida topilmagan holatda hech narsa yaratmaydi, None
    qaytaradi (xuddi hozircha ham topilmagan/yaratilmagandagidek — chaqiruvchi
    tomon buni allaqachon "topilmadi" deb talqin qiladi, natija o'zgarmaydi)."""
    val = (affix_text+"-") if is_prefix else ("-"+affix_text)
    try:
        conn=sqlite3.connect(db_path); cur=conn.cursor()
        row=cur.execute("SELECT id,kkt_symbol,weight FROM affixes WHERE value=?",(val,)).fetchone()
        if row: conn.close(); return row
        if is_readonly(): conn.close(); return None
        sym = kkt_symbol_hint or "A1"
        cur.execute("INSERT OR IGNORE INTO affixes(pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,NULL)",
                    (pos,sym,sym,val))
        conn.commit()
        row=cur.execute("SELECT id,kkt_symbol,weight FROM affixes WHERE value=?",(val,)).fetchone()
        conn.close(); return row
    except: return None

def qm_lookup_by_id(db_path, aid):
    """18-qadam: QM_en_w'dagi qo'shimcha ID'siga mos (bir xil ID) qo'shimchani
    QM_uz_w (yoki aksincha) dan ID orqali oladi."""
    if aid is None: return None
    try:
        conn=sqlite3.connect(db_path)
        row=conn.execute("SELECT id,value,kkt_symbol,weight FROM affixes WHERE id=?",(aid,)).fetchone()
        conn.close(); return row
    except: return None

def qm_uz_equivalent(en_affix_id, pos):
    """18-qadam (davomi): QM_en_w'dagi qo'shimcha ID'siga mos keluvchi QM_uz_w
    yozuvini ID orqali oladi VA so'z turkumi (pos) mosligini tekshiradi
    (chalkashmaslik uchun). Mos kelmasa None — chaqiruvchi statik jadvalga
    (make_uzbek) zaxira sifatida murojaat qiladi."""
    if en_affix_id is None: return None
    row = qm_lookup_by_id(DB_QM_UZ, en_affix_id)
    if not row: return None
    try:
        conn=sqlite3.connect(DB_QM_UZ)
        posrow=conn.execute("SELECT pos FROM affixes WHERE id=?",(row[0],)).fetchone()
        conn.close()
    except: posrow=None
    if posrow and posrow[0]==pos: return row
    return None

def bm_get_or_create_pos_model(db_path, pos):
    """13/16-qadam: BM_en_w/BM_uz_w dan so'z turkumining formal modelini (KKT
    belgi + vazn) qidiradi; topilmasa — 14-qadam: KKT qoidalari asosida yangi
    model yaratib bazaga yozadi. readonly_mode() ichida yaratmaydi, lekin
    default kkt_symbol/vazn'ni BARIBIR hisoblab qaytaradi — shu sabab
    tarjima natijasi (vazn asosidagi hisob-kitob) readonly rejimda ham
    o'zgarmaydi, faqat sqlite'ga yozilmaydi ("created" har doim False)."""
    try:
        conn=sqlite3.connect(db_path); cur=conn.cursor()
        row=cur.execute("SELECT kkt_symbol,v2_weight FROM pos_weight WHERE pos=?",(pos,)).fetchone()
        if row: conn.close(); return {"kkt_symbol":row[0],"weight":row[1],"created":False}
        sym=POS_KKT.get(pos,"C"); wt=POS_V2.get(pos,0.5)
        if is_readonly(): conn.close(); return {"kkt_symbol":sym,"weight":wt,"created":False}
        cur.execute("INSERT OR IGNORE INTO pos_weight(pos,kkt_symbol,v2_weight) VALUES(?,?,?)",(pos,sym,wt))
        conn.commit(); conn.close()
        return {"kkt_symbol":sym,"weight":wt,"created":True}
    except: return {"kkt_symbol":POS_KKT.get(pos,"C"),"weight":POS_V2.get(pos,0.5),"created":False}

def bm_get_or_create_affix_model(db_path, affix_text, kkt_symbol_hint="A1", default_weight=0.001):
    """13/14-qadam: BM_en_w/BM_uz_w.formal_model'dan qo'shimchaning KKT vaznini
    qidiradi; topilmasa — yangisini yaratib bazaga yozadi. readonly_mode()
    ichida yaratmaydi, lekin default qiymatlarni baribir qaytaradi (tarjima
    natijasi o'zgarmasligi uchun — izoh yuqoridagi funksiyada)."""
    try:
        conn=sqlite3.connect(db_path); cur=conn.cursor()
        row=cur.execute("SELECT kkt_symbol,v3_weight FROM formal_model WHERE affix=?",(affix_text,)).fetchone()
        if row: conn.close(); return {"kkt_symbol":row[0],"weight":row[1],"created":False}
        if is_readonly(): conn.close(); return {"kkt_symbol":kkt_symbol_hint,"weight":default_weight,"created":False}
        cur.execute("INSERT OR IGNORE INTO formal_model(affix,kkt_symbol,v3_weight) VALUES(?,?,?)",
                    (affix_text,kkt_symbol_hint,default_weight))
        conn.commit(); conn.close()
        return {"kkt_symbol":kkt_symbol_hint,"weight":default_weight,"created":True}
    except: return {"kkt_symbol":kkt_symbol_hint,"weight":default_weight,"created":False}

# ═══════════════════════════════════════════════════════════════════
#  "bazalar_ma_lumot_09.docx" — I bob (qo'shimchalar/formal belgilar)
#  va II bob (nazariy qoidalar asosidagi so'zlar) dan bazalarga yuklash
# ═══════════════════════════════════════════════════════════════════
_CYR2LAT = str.maketrans({
    "А":"A","В":"B","Е":"E","З":"3","К":"K","М":"M","Н":"H","О":"O",
    "Р":"P","С":"C","Т":"T","У":"Y","Х":"X","а":"a","е":"e","о":"o",
    "р":"p","с":"c","у":"y","х":"x",
})
def _norm_kkt(s):
    """Kirill-lotin aralash belgilarni (OCR/font xatosi) to'g'irlaydi."""
    return s.translate(_CYR2LAT).strip() if s else s

def _iter_block_items(parent):
    """docx tanasidagi paragraf va jadvallarni HUJJATDAGI TARTIBDA qaytaradi."""
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    from docx.oxml.ns import qn
    for child in parent.iterchildren():
        if child.tag == qn("w:p"): yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"): yield Table(child, parent)

def _extract_tables_in_order(docx_path):
    """Har bir jadvalni undan oldingi eng yaqin paragraf (sarlavha) bilan qaytaradi."""
    doc = Document(docx_path)
    out = []; recent = []
    for item in _iter_block_items(doc.element.body):
        if item.__class__.__name__ == "Paragraph":
            t = item.text.strip()
            if t:
                recent.append(t)
                if len(recent) > 2: recent.pop(0)
        else:
            rows = [[c.text.strip() for c in r.cells] for r in item.rows]
            out.append({"caption": recent[-1] if recent else "", "rows": rows})
    return out

def _flat_unique(rows):
    """Jadval katakchalarini tekislab, bo'sh va takrorlanganlarni olib tashlaydi."""
    vals=[]; seen=set()
    for row in rows:
        for c in row:
            c=_norm_kkt(c.strip())
            if not c or c in seen: continue
            seen.add(c); vals.append(c)
    return vals

# I bobdagi jadvallarning (0-indeksli) KKT belgisi va soʻz turkumi:
# (jadval_raqami -> (til, soʻz_turkumi, kkt_belgisi))
_CH1_TABLE_INFO = {
    1:("en","Ot","C(T)"), 2:("en","Ot","C(S)"), 3:("en","Ot","C(SF)"),
    4:("en","Sifat","P(T)"), 5:("en","Sifat","P(S)"), 6:("en","Sifat","P(SF)"),
    7:("en","Fe'l","G(T)"), 8:("en","Fe'l","G(S)"), 9:("en","Fe'l","G(SF)"),
    10:("en","Olmosh","M(S)"), 11:("en","Olmosh","M(M5)"),
    12:("en","Ravish","N(T)"), 13:("en","Ravish","N(S)"), 14:("en","Ravish","N(SF)"), 15:("en","Ravish","N(D)"),
    16:("en","Son","F(O)"), 17:("en","Umumiy","SBB-O"),
    18:("en","Predlog","D"), 19:("en","Predlog","D(E)"),
    20:("en","Bog'lovchi","Y"), 21:("en","Modal","L"), 22:("en","Taqlid","X5"),
    23:("uz","Ot","C_A1"), 24:("uz","Ot","C_AG"),
    25:("uz","Sifat","P_A1"), 26:("uz","Sifat","P_AG"),
    27:("uz","Fe'l","G_A1"), 28:("uz","Ravish","N_A4"), 29:("uz","Son","F_A4"),
    30:("uz","Olmosh","M_M3A"), 31:("uz","Olmosh","M_M4A"),
    32:("uz","Ega","X2"), 33:("uz","Kelishik","X3"), 34:("uz","Yuklama","U(A)"),
    35:("uz","Predlog","T"), 36:("uz","Taqlid","X5"), 37:("uz","Modal","L"),
}
# Bir xil soʻz turkumidagi EN va UZ jadval guruhlari — mos qoʻshimchalarga BIR XIL id beriladi
_CH1_GROUPS = [
    ("Ot",[1,2,3],[23,24]), ("Sifat",[4,5,6],[25,26]), ("Fe'l",[7,8,9],[27]),
    ("Olmosh",[10,11],[30,31]), ("Ravish",[12,13,14,15],[28]), ("Son",[16],[29]),
    ("Predlog",[17,18,19],[35]), ("Bog'lovchi",[20],[]), ("Modal",[21],[37]),
    ("Taqlid",[22],[36]), ("Ega",[],[32]), ("Kelishik",[],[33]), ("Yuklama",[],[34]),
]
# II bobdagi olmosh EVXs/EVIXs (soʻz + formal model) jadvallari
_CH2_WORD_TABLES = [88,89,90,91,92,93]

# II bobning "EVXs parsinglash" formatidagi ICHKI namuna so'zlari (avval
# o'tkazib yuborilgan, endi to'liq qo'shildi) — (en, uz, pos, model_en, model_uz)
_CH2_INLINE_WORDS = [
    # ── Ot (Noun) — §2.1 ──
    ("variable","o'zgaruvchi","Ot","C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-2]Xj","C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-1]Xj"),
    ("process","jarayon","Ot","C(C, X1) = $[i,1-h1]Ci⊕↓$[j,1-2]X1j","C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-1]Xj"),
    ("network","tarmoq","Ot","C(T1, C) = $[i,1-3]T1i⊕↓$[j,1-h1]Cj","C(C) = $[i,1-h1]Ci"),
    ("example","misol","Ot","C(T2, C) = $[i,1-3]T2i⊕↓$[j,1-h1]Cj","C(C) = $[i,1-h1]Ci"),
    ("progress","taraqqiyot","Ot","C(T3, C) = $[i,1-3]T3i⊕↓$[j,1-h1]Cj","C(C) = $[i,1-h1]Ci"),
    ("germany","Germaniya","Ot","C(T3, C, X) = $[i,1-3]T3i $[j,1-h1]Cj $[i1,1-2]Xi1","C(C, C_A1, X) = $[i,1-h1]Ci $[j,1-h1]C_A1j $[i1,1-1]Xi1"),
    ("capability","imkoniyat","Ot","C(C, X1) = $[i,1-h1]Ci⊕↓$[j,1-2]X1j","C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-1]Xj"),
    ("delay","kechikish","Ot","C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-2]Xj","C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-1]Xj"),
    ("leaf","barg","Ot","C(C, X1) = $[i,1-h1]Ci⊕↓$[j,1-2]X1j","C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-1]Xj"),
    ("man","erkak","Ot","C(C) = $[i,1-h1]Ci","C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-1]Xj"),
    ("customhouse","bojxona","Ot","C(C, C_X) = $[i,1-h1]Ci⊕↓$[j,1-h1]C_Xj","C(C, C_X) = $[i,1-h1]Ci⊕↓$[j,1-h1]C_Xj"),
    ("information","axborot","Ot","C(G, C_A1) = $[i,1-h3]Gi⊕↓$[j,1-h1]C_A1j","C(C) = $[i,1-h1]Ci"),
    ("content","mazmun","Ot","C(C_X) = $[i,1-h1]Ci⊕↓$[j,1-2]Xj","C(C) = $[i,1-h1]Ci"),
    ("chapter","bob","Ot","F(C, F) = $[i,1-h1]Ci⊕↓$[j,1-h6]Fj","F(F_A1, C) = $[i,1-h6]F_A1i⊕↓$[j,1-h1]Cj"),
    # ── Fe'l (Verb) — §2.1.1 ──
    ("analyze","tahlil qilmoq","Fe'l","$[i,1-h3]Gi","G(C, G) = $[i,1-h1]Ci⊕↓$[j,1-h3]Gj"),
    ("digitalize","raqamlashtirmoq","Fe'l","G(D, G, G_S) = $[i,1-53]Di⊕↓$[j,1-h3]Gj⊕↓$[i1,1-6]G_Si1","G(C, G(C_A1), G_A1) = $[i,1-h2]Ci⊕↓$[j,1-32]G_A1j⊕↓$[i1,1-26]G_Oi1"),
    ("whitewash","oqlamoq","Fe'l","G(D, P, G) = $[i,1-53]Di⊕↓$[j,1-h2]Pj⊕↓$[i1,1-h3]Gi1","G(P, G(P_A1), G_A1) = $[i,1-h2]Pi⊕↓$[j,1-32]G(P_A1j)⊕↓$[i1,1-62]G_A1i1"),
    ("speak","gapirmoq","Fe'l","G(G_S) = $[i,1-h3]G_Si","G(C, G_A1, G_Z) = $[i,1-h1]Ci⊕↓$[j,1-32]G_A1j⊕↓$[i1,1-3]G_Zi1"),
    ("be","bo'lmoq","Fe'l","G1(G1) = $[i,1-8]G1i","G(G, G_HA1) = $[i,1-h3]Gi⊕↓$[j,1-1]G_HA1j"),
    ("have","bor bo'lmoq","Fe'l","G(G2) = $[i,1-1]G2i","G(G, G_HA1) = $[i,1-h3]Gi⊕↓$[j,1-1]G_HA1j"),
    ("do","qilmoq","Fe'l","G(G3) = $[i,1-1]G3i","G(G_HA1) = $[i,1-32]G_HA1i"),
    ("become","bo'lmoq","Fe'l","G(G6) = $[i,1-9]G6i","G(G, G_HA1) = $[i,1-h3]Gi⊕↓$[j,1-32]G_HA1j"),
    ("can","qila olmoq","Fe'l","G(G7) = $[i,1-10]G7i","G(G, A, G_K) = $[i,1-h3]Gi⊕↓$[j,1-h3]Aj⊕↓$[i1,1-h3]G_Ki1"),
    ("ask","so'ramoq","Fe'l","G(G8) = $[i,1-h3]G8i","G(G_HA1) = $[i,1-h3]GHA1i"),
    ("follow","ergashmoq","Fe'l","G(G10) = $[i,1-h3]G10i","G(G_HA1) = $[i,1-h3]G_HA1i"),
    ("understand","tushunmoq","Fe'l","G(G12) = $[i,1-h3]G12i","G(G) = $[i,1-h3]Gi"),
    ("return","qaytmoq","Fe'l","G(G4, G) = $[i,1-h3]G4i⊕↓$[j,1-h3]Gj","G(G) = $[i,1-h3]Gi"),
    ("work","ishlamoq","Fe'l","G(G_S) = $[i,1-h3]G_Si","G(C, G_A, G_Az3) = $[i,1-h1]Ci⊕↓$[j,1-h3]G_Aj⊕↓$[i1,1-h3]G_Az3i1"),
    ("simplify","soddalashtirmoq","Fe'l","G(G13_S) = $[i,1-h3]G13_Si","G(P, G_A, G_Az3) = $[i,1-h1]Pi⊕↓$[j,1-h3]G_Aj⊕↓$[i1,1-h3]G_Ai1"),
    ("send","yubormoq","Fe'l","G(G14) = $[i,1-h3]G14i","G(G) = $[i,1-h3]Gi"),
    # ── Sifat (Adjective) — §2.2 ──
    ("big","katta","Sifat","P","P"),
    ("formal","rasmiy","Sifat","P(C, P_A1) = $[i,1-h1]Ci⊕↓$[j,1-h2]P_A1j","P(C, P_A1) = $[i,1-h1]Ci⊕↓$[j,1-h2]P_A1j"),
    ("clever","aqlli","Sifat","P(P1_S) = $[i,1-h2]P1_Si","P(P, P_A1, P1_A1) = $[i,1-h2]Pi⊕↓$[j,1-h2]P_A1j⊕↓$[i1,1-h2]P1_A1i1"),
    ("large","katta","Sifat","P5(P_S) = $[i,1-h2]P1_Si","P(P1_A1) = $[i,1-h2]P1_A1i"),
    ("busy","band","Sifat","P8(P1_S) = $[i,1-h2]P1_Si","P(P1_A1) = $[i,1-h2]P1_A1i"),
    ("gay","sho'x","Sifat","P10(P1_S) = $[i,1-h2]P1_Si","P(P1_A1) = $[i,1-h2]P1_A1i"),
    ("comfortable","qulay","Sifat","P12(T, P) = $[i,1-h2]Ti⊕↓$[j,1-h2]Pj","P(T, P) = $[i,1-3]Ti⊕↓$[j,1-h2]Pj"),
    ("good","yaxshi","Sifat","P13(P,P1_SF, P2) = $[i,1-h2]Pi⊕↓$[j,1-h2]P1_SFj⊕↓$[i1,1-h2]P2i1","P(P, P1_A1, P2_D, P) = $[i,1-h2]Pi⊕↓$[j,1-h2]P1_A1j"),
    ("interesting","qiziqarli","Sifat","P14(T, P) = $[i,1-2]Ti⊕↓$[j,1-h2]Pj","P(P1_A1, P_A1) = $[i,1-h2]P1_A1i⊕↓$[j,1-h2]P_A1j"),
    # ── Ravish (Adverb) — §2.2.1 ──
    ("very","juda","Ravish","N","N"),
    ("here","shu yerda","Ravish","N(N) = $[i,1-h4]Ni","N(M3,C, X3) = $[i,1-h5]M3i⊕↓$[j,1-h1]Cj⊕↓$[i1,1-5]X3i1"),
    ("easily","osonlik bilan","Ravish","N(N_S) = $[i,1-h4]N_Si","N(P, C_A1, Y) = $[i,1-h2]Pi⊕↓$[j,1-7]C_A1j⊕↓$[i1,1-20]Yi1"),
    ("fast","tez","Ravish","N2(N_S) = $[i,1-2]N_Si","N(N) = $[i,1-h4]Ni"),
    ("inside","ichkarida","Ravish","N5(N) = $[i,1-h4]Ni","N(N, X3) = $[i,1-h4]Ni⊕↓$[j,1-5]X3j"),
    ("today","bugun","Ravish","N6(N) = $[i,1-h4]Ni","N(N) = $[i,1-h4]Ni"),
    ("much","ko'p","Ravish","N(N) = $[i,1-h4]Ni","N(N) = $[i,1-h4]Ni"),
    ("quietly","tinchgina","Ravish","N(P, N_S) = $[i,1-h2]Pi⊕↓$[j,1-h4]N_Sj","N(P, N_A1) = $[i,1-h2]Pi⊕↓$[j,1-h4]N_A1j"),
    # ── Son (Numeral) — §2.3 ──
    ("one","bir","Son","F(F) = $[i,1-h6]Fi","F(F) = $[i,1-h6]Fi"),
    ("fifteen","o'n besh","Son","F(F_S) = $[i,1-h6]F_Si","F(F, F) = $[i,1-h6]Fi⊕↓$[j,1-h6]Fj"),
    ("eighty","sakson","Son","F(F_S) = $[i,1-h6]F_Si","F(F) = $[i,1-h6]Fi"),
    ("hundred","yuz","Son","F(F) = $[i,1-h6]Fi","F(F) = $[i,1-h6]Fi"),
    ("million","million","Son","F(F, F) = $[i,1-h6]Fi⊕↓$[j,1-h6]Fj","F(F, F) = $[i,1-h6]Fi⊕↓$[j,1-h6]Fj"),
    ("five","besh","Son","F(F) = $[i,1-h6]Fi","F(F) = $[i,1-h6]Fi"),
]
# 2.1-jadval — kishilik olmoshlari, bosh va obyekt kelishigi (jadval 86)
_CH2_PRONOUN_TABLE_WORDS = [
    ("i","men","Olmosh"), ("me","meni","Olmosh"),
    ("he","u","Olmosh"), ("him","uni","Olmosh"),
    ("she","u","Olmosh"), ("her","uni","Olmosh"),
    ("it","u","Olmosh"),
    ("we","biz","Olmosh"), ("us","bizni","Olmosh"),
    ("you","siz","Olmosh"),
    ("they","ular","Olmosh"), ("them","ularni","Olmosh"),
]

def load_bazalar_docx(docx_path):
    """
    bazalar_ma_lumot_09.docx dan:
      1) I bobning KKT belgi-funktsiya jadvali (1.1-jadval)  -> BM_en_w / BM_uz_w (kkt_symbols)
      2) I bobning ingliz/oʻzbek qoʻshimcha jadvallari       -> QM_en_w / QM_uz_w (affixes)
      3) II bobning EVXs/EVIXs soʻz+formal model jadvallari  -> UB_en_w / UB_uz_w (words)
    Mos keluvchi EN/UZ yozuvlarga BIR XIL id beriladi. Vazn (weight) ustunlari
    hozircha NULL qoldiriladi — keyinroq qiymatlar qoʻlda kiritiladi.
    Qayta ishga tushirilsa xavfsiz (UNIQUE cheklovlar tufayli takrorlanmaydi).
    """
    if not (docx_path and os.path.exists(docx_path) and HAS_DOCX):
        return {"symbols":0,"aff_en":0,"aff_uz":0,"words":0}
    init_all_databases()
    tables = _extract_tables_in_order(docx_path)

    # ── 1) KKT belgi-funktsiya jadvali (0-jadval) -> BM_en_w / BM_uz_w ──
    n_sym=0
    if tables:
        conn_en=sqlite3.connect(DB_BM_EN); cur_en=conn_en.cursor()
        conn_uz=sqlite3.connect(DB_BM_UZ); cur_uz=conn_uz.cursor()
        seen=set()
        for row in tables[0]["rows"]:
            for ci in (0,2):
                if ci+1 >= len(row): continue
                sym=_norm_kkt(row[ci].strip()); func=row[ci+1].strip()
                if not sym or sym in ("Belgi",) or sym in seen: continue
                seen.add(sym)
                cur_en.execute("INSERT OR IGNORE INTO kkt_symbols(kkt_symbol,funktsiya,weight) VALUES(?,?,NULL)",(sym,func))
                cur_uz.execute("INSERT OR IGNORE INTO kkt_symbols(kkt_symbol,funktsiya,weight) VALUES(?,?,NULL)",(sym,func))
                if cur_en.rowcount>0: n_sym+=1
        conn_en.commit(); conn_en.close(); conn_uz.commit(); conn_uz.close()

    # ── 2) I bob qoʻshimchalar jadvallari -> QM_en_w / QM_uz_w (mos id bilan) ──
    conn_qen=sqlite3.connect(DB_QM_EN); cur_qen=conn_qen.cursor()
    conn_quz=sqlite3.connect(DB_QM_UZ); cur_quz=conn_quz.cursor()
    n_aff_en=n_aff_uz=0
    shared_id = max(
        (cur_qen.execute("SELECT COALESCE(MAX(id),0) FROM affixes").fetchone()[0]),
        (cur_quz.execute("SELECT COALESCE(MAX(id),0) FROM affixes").fetchone()[0]),
    )
    for pos, en_ids, uz_ids in _CH1_GROUPS:
        en_items=[]
        for ti in en_ids:
            lang,_,sym = _CH1_TABLE_INFO[ti]
            for v in _flat_unique(tables[ti]["rows"]): en_items.append((v,sym))
        uz_items=[]
        for ti in uz_ids:
            lang,_,sym = _CH1_TABLE_INFO[ti]
            for v in _flat_unique(tables[ti]["rows"]): uz_items.append((v,sym))
        maxlen=max(len(en_items),len(uz_items))
        for i in range(maxlen):
            shared_id += 1
            if i < len(en_items):
                val,sym = en_items[i]
                cur_qen.execute("INSERT OR IGNORE INTO affixes(id,pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,?,NULL)",
                                 (shared_id,pos,sym,sym,val))
                if cur_qen.rowcount>0: n_aff_en+=1
            if i < len(uz_items):
                val,sym = uz_items[i]
                cur_quz.execute("INSERT OR IGNORE INTO affixes(id,pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,?,NULL)",
                                 (shared_id,pos,sym,sym,val))
                if cur_quz.rowcount>0: n_aff_uz+=1
    conn_qen.commit(); conn_qen.close(); conn_quz.commit(); conn_quz.close()

    # ── 3) II bob EVXs/EVIXs soʻz jadvallari -> UB_en_w / UB_uz_w (mos id bilan) ──
    conn_uen=sqlite3.connect(DB_UB_EN); cur_uen=conn_uen.cursor()
    conn_uuz=sqlite3.connect(DB_UB_UZ); cur_uuz=conn_uuz.cursor()
    n_words=0
    word_id = max(
        (cur_uen.execute("SELECT COALESCE(MAX(id),0) FROM words").fetchone()[0]),
        (cur_uuz.execute("SELECT COALESCE(MAX(id),0) FROM words").fetchone()[0]),
    )
    for ti in _CH2_WORD_TABLES:
        if ti >= len(tables): continue
        rows = tables[ti]["rows"]
        last_uz_word=""; last_uz_model=""
        for row in rows[1:]:
            if len(row) < 4: continue
            en_w,en_mm,uz_w,uz_mm = [c.strip() for c in row[:4]]
            if not en_w and not uz_w: continue
            en_list = [w.strip() for w in en_w.split("\n") if w.strip()] or [""]
            uz_list = [w.strip() for w in uz_w.split("\n") if w.strip()]
            if uz_list: last_uz_word, last_uz_model = uz_list[0], uz_mm
            for k,en1 in enumerate(en_list):
                if not en1: continue
                uz1 = uz_list[k] if k < len(uz_list) else (uz_list[0] if uz_list else last_uz_word)
                if not uz1: continue
                word_id += 1
                cur_uen.execute("""INSERT OR IGNORE INTO words(id,headword,translation,pos,source,formal_model)
                                    VALUES(?,?,?,'Olmosh','chapter2',?)""",
                                 (word_id, en1.lower(), uz1, en_mm))
                if cur_uen.rowcount>0: n_words+=1
                cur_uuz.execute("""INSERT OR IGNORE INTO words(id,headword,translation,pos,source,formal_model)
                                    VALUES(?,?,?,'Olmosh','chapter2',?)""",
                                 (word_id, uz1, en1.lower(), uz_mm or last_uz_model))
    conn_uen.commit(); conn_uen.close(); conn_uuz.commit(); conn_uuz.close()

    # ── 4) II bobning ICHKI namuna soʻzlari (38-87-jadval, "EVXs parsinglash"
    #        formatidagi so'zlar) va 2.1-jadval (kishilik olmoshi kelishiklari)
    #        -> UB_en_w / UB_uz_w (mos id bilan) ──
    conn_uen=sqlite3.connect(DB_UB_EN); cur_uen=conn_uen.cursor()
    conn_uuz=sqlite3.connect(DB_UB_UZ); cur_uuz=conn_uuz.cursor()
    word_id = max(
        (cur_uen.execute("SELECT COALESCE(MAX(id),0) FROM words").fetchone()[0]),
        (cur_uuz.execute("SELECT COALESCE(MAX(id),0) FROM words").fetchone()[0]),
    )
    n_inline=0
    for en,uz,pos,mm_en,mm_uz in _CH2_INLINE_WORDS:
        word_id += 1
        cur_uen.execute("""INSERT OR IGNORE INTO words(id,headword,translation,pos,source,formal_model)
                            VALUES(?,?,?,?,'chapter2',?)""",(word_id,en.lower(),uz,pos,mm_en))
        if cur_uen.rowcount>0: n_inline+=1
        cur_uuz.execute("""INSERT OR IGNORE INTO words(id,headword,translation,pos,source,formal_model)
                            VALUES(?,?,?,?,'chapter2',?)""",(word_id,uz,en.lower(),pos,mm_uz))
    for en,uz,pos in _CH2_PRONOUN_TABLE_WORDS:
        word_id += 1
        cur_uen.execute("""INSERT OR IGNORE INTO words(id,headword,translation,pos,source,formal_model)
                            VALUES(?,?,?,?,'chapter2',?)""",(word_id,en,uz,pos,"M(M1)"))
        if cur_uen.rowcount>0: n_inline+=1
        cur_uuz.execute("""INSERT OR IGNORE INTO words(id,headword,translation,pos,source,formal_model)
                            VALUES(?,?,?,?,'chapter2',?)""",(word_id,uz,en,pos,"M(M1)"))
    conn_uen.commit(); conn_uen.close(); conn_uuz.commit(); conn_uuz.close()
    n_words += n_inline

    return {"symbols":n_sym,"aff_en":n_aff_en,"aff_uz":n_aff_uz,"words":n_words}

# -*- coding: utf-8 -*-
"""
umumiy__to_liq_6_oid_09.pdf dan qo'lda tekshirib chiqilgan (pdfplumber orqali
ajratilgan va matn bilan o'zaro solishtirilgan) I bob ma'lumotlari.
Faqat ANIQ va sonlari matn tavsifiga (masalan "77 turdagi suffikslar") mos
kelgan jadvallar kiritildi. Kuchli buzilgan (garbled) ibora-ro'yxati
jadvallari (1.19-1.23: predlog iboralar, bog'lovchilar, modal so'zlar,
taqlid so'zlar) ANIQ EMASLIGI SABABLI KIRITILMADI.
"""

# ── KKT belgilar jadvali (1.1-jadval, 88 ta belgi) ──
KKT_SYMBOLS = [
    ("A","Affiks"),("A1","so'z yasovchi affiks"),("A2","shakl yasovchi affiks"),
    ("A3","so'z o'zgartiruvchi affiks"),("A4","boshqa affiks"),
    ("ADC","ot uchun predlog affiksi"),("AG","fe'l affiksi"),("AC","ot affiksi"),
    ("ADP","sifat uchun predlog affiksi"),("B","Postfiks"),("C","Ot"),
    ("CC","otga tegishli so'zlar bazasi"),("D","Predlog"),
    ("E","gapning yordamchi bo'laklari"),("E1","darak gaplar"),("E2","so'roq gaplar"),
    ("E3","undov gaplar"),("E4","inkor gaplar"),("E5","Ega"),("E6","Aniqlovchi"),
    ("E7","to'ldiruvchi"),("E8","Xol"),
    ("EE1","darak gaplarga tegishli so'zlar bazasi"),
    ("EE2","so'roq gaplarga tegishli so'zlar bazasi"),
    ("EE3","undov gaplarga tegishli so'zlar bazasi"),
    ("EE4","inkor gaplarga tegishli so'zlar bazasi"),
    ("EVX","kirish tili"),("EVIX","chiqish tili"),("F","Son"),
    ("FF","sonlarga tegishli so'zlar bazasi"),("G","fe'l"),("G1","Poslelog"),
    ("G2","Kesim"),("GG","fe'lga tegishli so'zlar bazasi"),("H","o'zgaruvchi"),
    ("I","o'zgaruvchi"),("J","o'zgaruvchi"),("K","o'zak"),("L","modal so'zlar"),
    ("L1","so'z"),("M","Olmosh"),("MM","olmoshga tegishli so'zlar bazasi"),
    ("M1","kishilik olmoshi"),("M2","egalik olmoshlari"),("M3","ko'rsatish olmoshi"),
    ("M3A","ko'rsatish olmoshi affikslari"),("M4","so'roq olmoshi"),
    ("M4A","so'roq olmoshi affikslari"),("M5","aniqlovchi olmosh"),
    ("M6","inkor olmoshi"),("M7","noaniq olmosh"),("N","Ravish"),
    ("NN","ravishga tegishli so'zlar bazasi"),("O","qo'shimcha"),("P","Sifat"),
    ("P1","kichraytiruvchi sifat"),("P2","kattalashtiruvchi sifat"),
    ("P3","sifatdosh I"),("P4","sifatdosh II"),
    ("PP","sifatga tegishli so'zlar bazasi"),("Q","maxsus BB"),
    ("Q1","tilning barcha o'zak so'zlari"),
    ("Q2","tilning barcha hosil bo'lgan so'zlari bazasi"),
    ("Q3","tilning gap bo'laklari bazasi"),("Q4","tilning so'z turlari bo'yicha baza"),
    ("K2","sohaga oid BB"),("R_I","sohaga oid ibora va terminlar bazasi"),
    ("S","Suffiks"),("SF","so'z yasovchi suffikslar"),("T","old qo'shimcha"),
    ("T1","ravish old qo'shimchalari"),
    ("T2","A kirish tilidagi so'zlar to'plami va ularning gapdagi vazifalari bilan"),
    ("T3","B chiqish tilidagi so'zlar to'plami va ularning gapdagi vazifalari bilan"),
    ("U","Yuklama"),("U1","inkor yuklama"),("U2","nisbat yuklama"),
    ("U3","mayl yuklama"),("U4","fe'l vaqtlarini ko'rsatuvchi yuklama"),
    ("U5","shaxs yuklama"),("V","umumiy BB"),("W","Morfema"),
    ("X","ko'plik suffiksi"),("X2","egalik suffikslari"),
    ("X3","kelishik suffikslari"),("X4","undov so'zlar"),
    ("X5","taqlid so'zlar"),("X6","xarakatni bildiruvchi so'zlar"),
    ("Y","bog'lovchi"),("Z","birlik suffikslari"),
    ("AD","Qo'shimcha ma'no beruvchi predlog"),
]

# ── I bob qo'shimcha jadvallari (jadval raqami -> (pos, kkt_symbol, [qiymatlar])) ──
# Har biri PDFdagi son bilan tasdiqlangan (masalan "43 turdagi", "77 turdagi").
AFFIX_TABLES = [
    # (jadval, pos, kkt_symbol, expected_count, values)
    ("1.2","Ot","C(T)", 43, [
        "ana-","apo-","arch-","auto-","be-","bene-","cat-","cata-","circum-","com-",
        "con-","dia-","dis-","dys-","em-","epi-","epi-","ex-","homo-","inter-",
        "mono-","neo-","para-","philo-","poly-","post-","pre-","proto-","pseudo-","re-",
        "self-","semi-","semi-","sub-","super-","syl-","sym-","syn-","tele-","trans-",
        "ultra-","under-","up-",
    ]),
    ("1.3","Ot","C(S)", 77, [
        "-acy","-age","-agogue","-anc","-ancy","-ant","-ant",
        "-ast","-ation","-cy","-dent","-dom","-ectomy","-ee",
        "-eer","-ence","-er","-ese","-ess","-eur","-hood",
        "-ian","-ics","-ics","-ie","-ier","-ine","-ion",
        "-ism","-ist","-ite","-ition","-ity","-ity","-le",
        "-le","-lessness","-let","-like","-ling","-logist","-logy",
        "-logy","-logy","-ment","-ment","-monger","-ness","-ness",
        "-oid","-on","-oon","-or","-or","-osis","-phobia",
        "-ress","-s","-scape","-ship","-ship","-sion","-sis",
        "-sure","-sy","-t","-th","-tion","-tory","-tory",
        "-tude","-ture","-ty","-ty","-wright","-y","-yer",
    ]),
    ("1.4","Ot","C(SF)", 17, [
        "-a","-ae","-ata","-el","-en","-era","-es","-ette","-i",
        "-ices","-ie","-kin","-ling","-ock","-ora","-s","-y",
    ]),
    ("1.5","Sifat","P(T)", 22, [
        "a-","ab-","ambi-","ana-","anti-","centro-","dys-","eso-",
        "ex-","extra-","il-","im-","in-","ir-","post-","pre-",
        "retro-","self-","sub-","un-","under-","whole-",
    ]),
    ("1.6","Sifat","P(S)", 46, [
        "-able","-ac","-aceous","-al","-al","-an","-ant","-ary",
        "-ative","-atory","-cal","-ed","-en","-ent","-ern","-escent",
        "-fic","-ful","-ible","-ic","-ic","-ical","-iferous","-il",
        "-ile","-ing","-ious","-ious","-ish","-ish","-ive","-less",
        "-less","-logical","-ly","-oid","-ose","-ous","-que","-sible",
        "-sive","-some","-tic","-tical","-tific","-uous",
    ]),
    ("1.7","Sifat","P(SF)", 2, ["-er","-est"]),
    ("1.9","Fe'l","G(S)", 6, ["-ate","-e","-en","-fy","-ish","-ize"]),
    ("1.10","Fe'l","G(SF)", 5, ["-ed","-t","-s","-es","-ing"]),
    ("1.11","Olmosh","M(S)", 5, ["-s","-thing","-ever","-self","-selves"]),
    ("1.14","Ravish","N(S)", 8, [
        "-ably","-ally","-ently","-long","-ly","-ward","-wards","-wise",
    ]),
    ("1.15","Ravish","N(SF)", 2, ["-est","-er"]),
    ("1.17","Son","F(O)", 4, ["-fold","-ty","-th","-teen"]),
]

# 1.18-jadval — "Umumiy prefikslar" (96 turdagi, SBB-O)
GENERAL_PREFIXES_96 = [
    "auto-","any-","eu-","im-","im-","micro-","over-","pro-","tele-","whole-",
    "apo-","com-","eso-","il-","mete-","off-","pali-","pros-","with-","dia-",
    "a-","be-","con-","ex-","in-","mid-","palin-","proto-","trans-","semi-",
    "ab-","bene-","de-","extra-","inter-","mis-","pan-","pseudo-","ultra-","syl-",
    "ad-","bi-","dis-","for-","intra-","mono-","para-","re-","un-","sym-",
    "ambi-","cat-","dys-","fore-","ir-","neo-","per-","retro-","under-","syn-",
    "an-","cata-","e-","hetero-","it-","non-","peri-","self-","unter-",
    "ana-","centro-","en-","homo-","macro-","ob-","philo-","some-","up-",
    "ant-","circum-","em-","hyper-","mal-","on-","post-","sub-","super-",
    "anti-","co-","epi-","hypo-","male-","out-","pre-","subin-","ur-",
]


def load_bazalar_affixes_docx(docx_path):
    """
    "bazalar_ma_lumot_09_07.docx" — bu fayl faqat I bobning qo'shimchalar
    jadvallarini (1.2- dan 1.38-jadvalgacha, 37 ta jadval — ingliz VA
    o'zbek tomonlari, jumladan avval PDF'da o'qib bo'lmagan 1.19-1.23
    "predlog iboralar/bog'lovchi/modal/taqlid" hamda umuman yangi 1.24-1.38
    o'zbek affikslari) o'z ichiga oladi — KKT belgilar jadvali (1.1) va
    II bob so'z jadvallari BU FAYLDA YO'Q.

    Bu asl Word jadvali bo'lgani uchun (PDF'dan farqli) hujayralar
    ANIQ va TOZA o'qiladi — taxminiy tiklashga hojat yo'q.

    Mavjud, sinovdan o'tgan _CH1_GROUPS/_CH1_TABLE_INFO xaritasidan
    foydalanadi (u "jadval[0] = KKT belgilar" deb kutadi) — shu sababli
    jadvallar ro'yxati boshiga bitta bo'sh (placeholder) jadval qo'shib,
    indekslarni to'g'ri moslashtiramiz.
    """
    if not (docx_path and os.path.exists(docx_path) and HAS_DOCX):
        return {"aff_en":0,"aff_uz":0}
    init_all_databases()
    raw_tables = _extract_tables_in_order(docx_path)
    tables = [{"caption":"","rows":[]}] + raw_tables   # index 0 = KKT belgilar o'rniga bo'sh

    conn_qen=sqlite3.connect(DB_QM_EN); cur_qen=conn_qen.cursor()
    conn_quz=sqlite3.connect(DB_QM_UZ); cur_quz=conn_quz.cursor()
    n_aff_en=n_aff_uz=0
    shared_id = max(
        (cur_qen.execute("SELECT COALESCE(MAX(id),0) FROM affixes").fetchone()[0]),
        (cur_quz.execute("SELECT COALESCE(MAX(id),0) FROM affixes").fetchone()[0]),
    )
    for pos, en_ids, uz_ids in _CH1_GROUPS:
        en_items=[]
        for ti in en_ids:
            if ti >= len(tables): continue
            lang,_,sym = _CH1_TABLE_INFO[ti]
            for v in _flat_unique(tables[ti]["rows"]): en_items.append((v,sym))
        uz_items=[]
        for ti in uz_ids:
            if ti >= len(tables): continue
            lang,_,sym = _CH1_TABLE_INFO[ti]
            for v in _flat_unique(tables[ti]["rows"]): uz_items.append((v,sym))
        maxlen=max(len(en_items),len(uz_items))
        for i in range(maxlen):
            shared_id += 1
            if i < len(en_items):
                val,sym = en_items[i]
                cur_qen.execute("INSERT OR IGNORE INTO affixes(id,pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,?,NULL)",
                                 (shared_id,pos,sym,sym,val))
                if cur_qen.rowcount>0: n_aff_en+=1
            if i < len(uz_items):
                val,sym = uz_items[i]
                cur_quz.execute("INSERT OR IGNORE INTO affixes(id,pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,?,NULL)",
                                 (shared_id,pos,sym,sym,val))
                if cur_quz.rowcount>0: n_aff_uz+=1
    conn_qen.commit(); conn_qen.close(); conn_quz.commit(); conn_quz.close()
    return {"aff_en":n_aff_en,"aff_uz":n_aff_uz}



# ═══════════════════════════════════════════════════════════════════
#  "so_zlar_bazasi_un.docx" — II bobning EVXs/EVIXs namuna soʻzlari:
#  har biri uchun INGLIZ va OʻZBEK formal modeli, tarjimasi va
#  grammatik qoida izohi (dissertatsiya matnidan qoʻlda ajratib olindi,
#  52 ta juftlik, "Ingliz tilida EVXs .../formal modeli:..." va
#  "Oʻzbek tilida EVIXs .../formal modeli:..." bandlaridan aniq
#  mos kelgan holda).
# ═══════════════════════════════════════════════════════════════════
CH2_EVX_EXAMPLES = [
    {"en":'processes',"uz":'jarayonlar',"pos":'Ot',"en_model":'C(C, X1) = $[i,1-h1]Ci⊕↓$[j,1-2]X1j',"uz_model":'C(C, X) = $[i,1-h1]Ci⊕↓$[j,1-1]Xj',"rule":"Ingliz tilidagi ko'plik affiksining ikkinchi turi aynan qaysi so'zlarda qo'llanilishiga namuna berildi. Ushbu ot turiga oid so'zlar gramamtik qoidasida so'zlarning oxirgi harflari “-s, -ss, -x, -ch, -sh”  bilan tugasa albatta “-es” ko'plik affiksi qo'shilishi natijasida birlikdagi so'zlar ko'plik manosida yasaladi. O'zbek tilida birlikdagi otlardan ko'plik otni yasashda ko'plik affiksi hamma so'zlar uchun umumiy bitta affiks “-lar” ko'plik affiksi qo'llanilishi yuqorida nazariy fikirlarda aytild"},
    {"en":'a network',"uz":'tarmoq',"pos":'Ot',"en_model":'C(T1, C) = $[i,1-3]T1i ⊕ ↓$[j,1-h1]Cj',"uz_model":'C(C) = $[i,1-h1]Ci',"rule":"Ingliz tilidagi kiruvchi so'z ot so'z turkumiga oid bo'lib, ot oldidan noaniq artikl so'z va gapda aynan “a network” deb kelganda “bitta tarmoq” haqida fikr bildirilganini bilishimiz mumkin bo'ladi. O'zbek tilida ot so'z turkumida aynan birlikni anglatadigan affikslar mavjud emas. Shu jihatlari bilan ushbu ot so'z turkumiga oid namuna misolimizda ikki til bo'yicha qurilgan formal modelimizda farq borligi yaqol seziladi."},
    {"en":'an example',"uz":'misol',"pos":'Ot',"en_model":'C(T2, C) = $[i,1-3]T2i ⊕ ↓$[j,1-h1]Cj',"uz_model":'C(C) = $[i,1-h1]Ci',"rule":"Ingliz tilidagi noaniq artikl “an” unli tovush bilan boshlanuvchi otlardan oldin qo'llaniladi. O'zbek tilining grammatikasida bunday qoida mavjud emas. Ingliz tilida berilgan ot oldidan artikl qo'llanilganligi uchun o'zbek tiliga ot bo'lib tarjima qilinsada, qurilgan modellarida farq bor. Shu bois, KT jarayonida ikki til o'rtasida grammatik va semantik jihatdan to'g'ri moslikni ta'minlash uchun aynan ushbu morfologik xususiyatlarni hisobga olish muhim ahamiyat kasb etadi. Artikllarning mavjudlig"},
    {"en":'the progress',"uz":'taraqqiyot',"pos":'Ot',"en_model":'C(T3, C) = $[i,1-3]T3i ⊕ ↓$[j,1-h1]Cj',"uz_model":'C(C) = $[i,1-h1]Ci',"rule":"Ingliz tilida aniq artikl “the” so'zlovchi va tinglovchi uchun aniq bo'lgan shaxs, narsa, hodisa kabilarni ifodalovchi otlar oldidan ishlatiladi. O'zbek tilidan farqi esa o'zbek tilida ot so'z turkumiga oid so'zlarning oldidan kelivchi bunday affikslar yo'q. Shu jihati bilan ikki til bo'yicha so'zlarning tuzilishida farq bor va bu farq formal model tuzilishida seziladi."},
    {"en":'The Germanys',"uz":'Germaniyaliklar',"pos":'Ot',"en_model":'C(T3, C, X) = $[i,1-3]T3i   $[j,1-h1]Cj   $[i1,1-2]Xi1',"uz_model":'C(C, C(A1), X) = $[i,1-h1]Ci   $[j,1-h1]C_A1j  $[i1,1-1]Xi1',"rule":"Ingliz tilida atoqli ot turidagi otlarga “-s” qo'shilganda fonetik hodisag uchramaydigan leksemalar quyidagi tamoyilga ega bo'ladi. Ingliz tilidagi atoqli otlarga ko'plik affiksini qo'llaganimizda, o'zbek tiliga quydagi 2.5- jadvalda keltirilgandek tarjima qilinadi. Ingliz tilidagi atoqli otlarda “-s” ko'plik qo'shimchasini olgan so'zlarni o'zbek tiliga tarjimasi so'z yasovchi affiks “-lik” va ko'plik affiksi “-lar” ni oladi. Ingliz tilidagi “The Germanys” so'zining o'zbek tiliga tarjimasi “Germ"},
    {"en":'capabilityies',"uz":'imkonyatlar',"pos":'Ot',"en_model":'C(C, X1) = $[i,1- h1]Ci ⊕↓$[j,1- 21X1j',"uz_model":'C(C, X) = $[i,1- h1]Ci ⊕↓$[j,1- 11Xj',"rule":"O'zbek tiliga tarjimasi ko'plik otni beradi. Biroq o'zbek tilida otga oid  bunday qoida mavjud emas. Shu jihati bilan formal modellarida farq bor."},
    {"en":'delays',"uz":'kechikishlar',"pos":'Ot',"en_model":'C(C, X) = $[i,1-h1]Ci ⊕↓$[j,1-2]Xj',"uz_model":'C(C, X) = $[i,1- h1]Ci ⊕↓$[j,1- 11Xj',"rule":"Ingliz tilidagi ot so'z turkumiga oid ba'zi so'zlar qoidaga asosan bir bo'g'inli so'zlarga “-s” ko'plik affiksi qo'llanilganda “-y” harfi o'zgarmaydi. Aynan shu qoidaga mos tushadigan so'zlar uchun ikki til bo'yicha formal modellari ishlab chiqildi."},
    {"en":'leafes',"uz":'barglar',"pos":'Ot',"en_model":'C(C, X1) = $[i,1- h1]Ci ⊕↓$[j,1- 21X1j',"uz_model":'C(C, X) = $[i,1-h1]Ci ⊕ ↓ $[j,1-1]Xj',"rule":"Morfologik tahlil: leaf – asos so'z, f → v, “es” leaf + es → leav + es. So'z ohiridagi “-f” harfi “-v” ga aylangan holda yoziladi. Ingliz tilidagi ko'plikdagi ot turining o'zbek tiliga tarjimasi ham ko'plikni beradi. Ikki til bo'yicha tahlil natijasida  formal modellari ishlab chiqildi."},
    {"en":'men',"uz":'erkaklar',"pos":'Ot',"en_model":'C(C) = $[i,1- h1]Ci',"uz_model":'C(C, X) = $[i,1-h1]Ci ⊕ ↓ $[j,1-1]Xj',"rule":"Ingliz tilida ot so'z turkumiga oid so'zlarning navbatdagi turiga kiruvchilari, asosga ko'plik affiksi qo'shilmasdan o'zagidan o'zgaradigan  so'zlar  kiradi. O'zbek tilidagi ot so'z turkumida bu qoida asosida  yasaladigan so'zlar yo'q. Ingliz tilida man → men, woman → women, foot → feet, tooth → teeth, goose → geese, mouse → mice, louse → lice 7 tani tashkil qiladi. Bu so'zlarning formal modellari otni beradi va o'zbek tiliga tarjimasi formol model va ID orqali amalga oshiriladi."},
    {"en":'customhouses',"uz":'Bojxonalar',"pos":'Ot',"en_model":'C(C, C_X) = $[i,1-h1]Ci⊕ ↓$[j,1-h1]C_Xj',"uz_model":'C(C, C_X) = $[i,1-h1]Ci⊕ ↓$[j,1-h1]C_Xj',"rule":"Ingliz tilidagi ot so'z turkumiga oid navbatdagi turini o'zbek tili bilan tahlil qilindi. Ikki til bo'yicha tahlil natijasida ingliz tilidagi bu tur otlar o'zbek tili bilan o'xshash holda ko'plik affiksini oladi. Ikki tilda ham bu so'z 2 ta asos so'zning birikishidan hosil bo'ladi. Shuning uchun ikki til bo'yicha formal modellari o'xshash."},
    {"en":'schoolboys',"uz":'Bojxonalar',"pos":'Ot',"en_model":'C(C_X) = $[i,1-h1]Ci ⊕↓$[j,1-2]Xj',"uz_model":'C(C, C_X) = $[i,1-h1]Ci⊕↓$[j,1-h1]C_Xj',"rule":"Ingliz tilida qo'shib yoziladigan otlar o'zbek tilida ikkita asosga ajratib yozilishi aniqlandi va shu jihati bilan farq qilingani uchun formal modellarida farqlar mavjud."},
    {"en":'information',"uz":'Axborot',"pos":'Ot',"en_model":'C(G, C_A1) = $[i,1-h3]Gi⊕↓$[j,1-h1]C_A1j',"uz_model":'C(C) = $[i,1-h1]Ci',"rule":"Bu yerda ingliz tilidagi asos so'z “inform” fe'l va KKTda fe'llarni G belgisi bilan belgilangan. “-ation” –  C_A1 so'zning asosiga qo'shilib ot yasovchi affiks."},
    {"en":'contents',"uz":'mazmun',"pos":'Ot',"en_model":'C(C_X) = $[i,1-h1]Ci ⊕↓$[j,1-2]Xj',"uz_model":'C(C) = $[i,1-h1]Ci',"rule":"Ingliz tilidagi ot so'z turkumiga oid ot turiga kiruvchi jamlama otlar har doim ko'plikda ishlatiladigan so'zlar kiradi. Ingliz tilidagi so'zlar ko'plikda yozilsada o'zbek tiliga faqat birlik asos bilan tarjima qilinadi."},
    {"en":"student's","uz":'studentning',"pos":'Ot',"en_model":'C(C_X) = $[i,1-h1]Ci ⊕↓$[j,1-1]X3j',"uz_model":'C(C, X3) = $[i,1-h1]Ci ⊕↓$[j,1-h1]X3j',"rule":"Ingliz tilidagi ot so'z turkumining navbatdagi turiga oid so'zlarga “ 's ” qaratqich kelishigi apostrif belgisi bilan yoziladi. Ingliz tilidagi ushbu ot turiga oid so'zni namuna siftida quyidagicha o'zbek tili bilan tahlil qilindi. “student's” student so'zi “ 's “ qaratqich kelishigini olganligi uchun o'zbek tiliga tarjimasi “student + ning“ deb tarjima qilinadi. Ushbu so'z misolida ikki til bo'yicha formal modellari quyidagicha ishlab chiqildi."},
    {"en":'to do',"uz":'qilmoq',"pos":"Fe'l","en_model":'G(G3) = $[i,1-1]G3i',"uz_model":'G( G_HA1) = $[i,1-32]G_HA1i',"rule":"Ingliz tilidagi “to do” fe'lini o'zbek tilidagi tarjimasi bilan tahlil qilindi. Ingliz tilida ikkita asosiy grammatik funksiyaga ega: Leksik fe'l sifatida –“qilmoq, bajarmoq” ma'nolarida ishlatiladi. Yordamchi fe'l sifatida-inkor, so'roq va ta'kid vazifalarini bajaradi. Shu bois, ingliz tilida “to do” fe'li nafaqat lug'aviy ma'no, balki grammatik strukturani tashkil etuvchi asosiy vositalardan biri sifatida ham muhim ahamiyat kasb etadi. “to do” fe'li aniq va majhul nisbatning barcha zamonlarida"},
    {"en":'will',"uz":'keladi',"pos":"Fe'l","en_model":'G(G4) = $[i,1-1]G4i',"uz_model":'(G, G_A1, A2) = $[i,1-h3]Gi⊕↓$[j,1-h3] Aj ⊕↓$[i1,1-6]A2i1',"rule":"Ingliz tilidagi ushbu “will” yordamchi fe'li kelasi zamonni ifodalash uchun ishlatiladi. O'zbek tiliga kelasi zamon affikslariga mos keladi. “will” fe'lining ikki til bo'yicha modellari hamda asos va affikslarning raqamli vazn qiymatlari hisoblab keltirilgani bo'yicha namuna misoli berildi."},
    {"en":'would',"uz":'keladi',"pos":"Fe'l","en_model":'G(G5) = $[i,1-1]G5i',"uz_model":'(G, G_A1, A2) = $[i,1-h3]Gi⊕↓$[j,1-h3] Aj ⊕↓$[i1,1-6]A2i1',"rule":"Ingliz tilidagi “would” yordamchi fe'li o'tkan zamonni ifodalash uchun ishlatiladi.  O'zbek tiliga tarjimasi ham o'tkan zamonni ifodalagan shakilda tarjima bo'ladi."},
    {"en":'can',"uz":'qila  olmoq',"pos":"Fe'l","en_model":'G(G7) = $[i,1-10]G7i',"uz_model":'(G, A, G_K) = $[i,1-h3]Gi⊕↓$[j,1-h3] Aj ⊕↓$[i1,1-h3]G_Ki1',"rule":"Ingliz tilida modal fe'llar bor. O'zbek tilida bunday fe'l turi yo'q. Modal fe'llar “can, could, may, might, must, ought to, need” mustaqil holda ishlatilmaydi. Fe'lga qo'shimcha ma'no yuklaydi. Modal fe'llar ish-harakatni qila olish mumkinligi, mumkin emasligi, qilish kerakligi yoki kerak emasligi kabi imkonyat va shart-sharoyitlarni anglatadi. Modal fe'llar assoiy fe'l bilan birgalikda qo'shma kesim bo'lib keladi. Ingliz tilidagi “can” modal fe'li o'zbek tilidagi ko'makchi fe'l “qila olmoq” bi"},
    {"en":'may',"uz":'mumkin',"pos":"Fe'l","en_model":'G(G7) = $[i,1-10]G7i',"uz_model":'L(L) = $[i,1-h2]Li',"rule":"Bu yerda “qil -G” fe'l asos so'zga “-a” – “A” o'tkan zamon yasashda qo'llaniladi. “GK” – ko'makchi fe'l."},
    {"en":'might',"uz":'mumkin',"pos":"Fe'l","en_model":'G(G7) = $[i,1-10]G7i',"uz_model":'P(P) = $[i,1-h2]Pi',"rule":"Bu yerda ingliz tilidagi “may” o'zbek tiliga “mumkin” modal so'z bo'ib tarjima bo'ladi."},
    {"en":'must',"uz":'shart',"pos":"Fe'l","en_model":'G(G7) = $[i,1-10]G7i',"uz_model":'C(C) = $[i,1-h2]Ci',"rule":"Bu yerda ingliz tilidagi “might” o'zbek tiliga tarjimasi “mumkin” sifat so'z turkumiga oid  so'z."},
    {"en":'ought',"uz":'zarur',"pos":"Fe'l","en_model":'G(G7) = $[i,1-10]G7i',"uz_model":'L(L) = $[i,1-h2]Li',"rule":"Bu yerda ingliz tilidagi “must” o'zbek tiliga tarjimasi “shart” ot so'z turkumiga oid."},
    {"en":'ought to',"uz":'zarur',"pos":"Fe'l","en_model":'G(G7) = $[i,1-10]G7i',"uz_model":'L(L) = $[i,1-h2]Li',"rule":"Bu yerda ingliz tilidagi “ought” o'zbek tiliga tarjimasi “zarur” modal  so'z."},
    {"en":'to ask',"uz":"so'ramoq","pos":"Fe'l","en_model":'G(G8) = $[i,1-h3]G8i',"uz_model":'G(G_HA1) = $[i,1-h3]GHA1i',"rule":"Ingliz tilidagi infinitive fe'li shaxsi noma'lum shakli bo'lib, harakatning nomini bildiradi, shaxsini va sonini ko'rsatmaydi. Infinitive fe'liga oid barcha so'zlar “to” yuklamasi bilan yoziladi. Ingliz tilidan o'zbek tiliga tarjimasi fe'lning “moq” shakliga mos keladi."},
    {"en":'reading',"uz":"o'qishni","pos":"Fe'l","en_model":'G(G9) = $[i,1-h3]G9i',"uz_model":'G(C, C_GA, X3) = $[i,1-h3]Ci ⊕↓$[j,1-h3]C_GAj⊕↓$[i1,1-h3]X3i1',"rule":"Bu yerda “so'ra -G” fe'l asos so'zga “-moq” affiksini G_HA1” harakat nomi shaklini yasovchi affiks qo'shilishi orqali yasaladi."},
    {"en":'to follow',"uz":'ergashmoq',"pos":"Fe'l","en_model":'G(G10) = $[i,1-h3]G10i',"uz_model":'G(G_HA1) = $[i,1-h3] G_HA1i',"rule":"Ingliz tilida ba'zi fe'llar o'zidan keyin vositasiz to'ldiruvchi talab qiladi. Yani fe'ldagi ish-harakat birorta shaxs yoki buyumga obektga o'tadi. Bunday fe'llar o'timli – transitive deb ataladi. Ingliz tilidagi ba'zi o'timli fe'llarga o'zbek tilida o'timsiz – intransitive fe'llar to'g'ri keladi."},
    {"en":'sent',"uz":'yuborgan',"pos":"Fe'l","en_model":'G(G14) = $[i,1-h3]G14i',"uz_model":'G(G) = $[i,1-h3]Gi',"rule":"Ingliz tilidagi noto'g'ri fe'l – bu o'tgan zamon shakli o'zagidagi tovush o'zgarishi yoki umuman “send => sent => sent” o'zbekcha tarjimasi “yubormoq => yubordi => yuborgan” shaklning o'zgarishi orqali yasalishidir. O'zbek tilida bu fe'l turi gramatikada uchramaydi."},
    {"en":'high dimensional',"uz":"ko'p o'lchovli","pos":'Sifat',"en_model":'P(P, C, P_A1) = $[i,1-h2]Pi⊕↓$[j,1-h2]Cj ⊕↓$[i1,1-h2]P_Si1',"uz_model":'P(P, C,P_A1) = $[i,1-h2]Pi⊕↓$[j,1-h2]Cj ⊕↓$[i1,1-h2]P_A1i1',"rule":"Bu yerda $ - tanlash amali, i≠j, h2 o'zgaruvchi - bu asos sifat bo'lganda so'zlar miqdori, yani [i,1-h2] - shu BBdan h2 – so'zlarning ichidan 1 tasini tanlab olishni anglatadi."},
    {"en":'cleverer',"uz":'aqilliroq',"pos":'Sifat',"en_model":'P( P1_S) = $[i,1-h2]P1_Si',"uz_model":'P(P, P_A1, P1_A1) = $[i,1-h2]Pi ⊕↓$[j,1-h2]P_A1j⊕↓$[i1,1-h2]P1_A1i1',"rule":"Ingliz va o'zbek tillarida sifat so'z turkumining uchta darajasi bor. Oddiy-positive degree, qiyosiy-comparative degree va orttirma superlative degree darajalarga bo'linadi."},
    {"en":'cleverest',"uz":'eng aqilli',"pos":'Sifat',"en_model":'P( P2_S) = $[i,1-h2]P2_Si',"uz_model":'P(P2_T, C, P_A1) = $[i,1-h2]P2_Ti ⊕↓$[j,1-h1]Cj⊕↓ $[i1,1-h2]P_A1i1',"rule":"Ingliz tilida bir ikki bo'g'inli sodda sifatlarning qiyosiy darajasi “-er”, affiksini qo'shish bilan yasaladi. Ingliz tilidagi “-er” affiksi o'zbek tilidagi qiyosiy sifatni yasovchi “-roq” affiksi bilan mos tushadi. Ikki til bo'yicha sifat so'z turkumining qiyosiy darajasiga oid formal modellari ishlab chiqildi."},
    {"en":'busier',"uz":'kattaroq',"pos":'Sifat',"en_model":'P8(P1_S) = $[i,1-h2]P1_Si',"uz_model":'P(P1_A1) = $[i,1-h2]P1_A1i',"rule":"Ingliz tilidagi sifat undoshdan keyin kelgan “y” harfi bilan tugagan bo'lsa qiyosiy va orttirma darajalarning affiksi qo'shilganida “y” harfi “i” harfiga aylanadi. Manashu nazariy keltirilgan grammatik so'z qurilishi bo'yicha ham ikki til bo'yicha  modellar yaratildi."},
    {"en":'busiest',"uz":'eng katta',"pos":'Sifat',"en_model":'P9(P2_S) = $[i,1-h2]P2_Si',"uz_model":'P(T, P) = $[i,1-10]Ti ⊕↓ $[j,1-h2]Pj',"rule":"Ingliz tilidagi sifat undoshdan keyin kelgan “y” harfi bilan tugagan bo'lsa qiyosiy va orttirma darajalarning affiksi qo'shilganida “y” harfi “i” harfiga aylanadi. Manashu nazariy keltirilgan grammatik so'z qurilishi bo'yicha ham ikki til bo'yicha  modellar yaratildi."},
    {"en":'gayer',"uz":"sho'xroq","pos":'Sifat',"en_model":'P10(P1_S) = $[i,1-h2]P1_Si',"uz_model":'P(P1_A1) = $[i,1-h2]P1_A1i',"rule":"Ingliz tilidagi sifat undoshdan keyin kelgan “y” harfi bilan tugagan bo'lsa qiyosiy va orttirma darajalarning affiksi qo'shilganida “y” harfi “i” harfiga aylanadi. Manashu nazariy keltirilgan grammatik so'z qurilishi bo'yicha ham ikki til bo'yicha  modellar yaratildi."},
    {"en":'gayer',"uz":"eng sho'x","pos":'Sifat',"en_model":'P11(P2_S) = $[i,1-h2]P2_Si',"uz_model":'P(T, P) = $[i,1-3]Ti ⊕↓$[j,1-h2]Pj',"rule":"Ingliz tilida agar sifat oxiridagi “y” harfi unli harfdan keyin kelsa sifatning qiyosiy va orttirma darajalarini yasaydigan “-er va -est” affikslari qo'shilganida “y” harfi saqlanib qolgan holda affikslar qo'shiladi."},
    {"en":'more comfortable',"uz":'eng qulay',"pos":'Sifat',"en_model":'P12(T, P) = $[i,1-h2]Ti ⊕↓$[j,1-h2]Pj',"uz_model":'P(T, P) = $[i,1-3]Ti ⊕↓$[j,1-h2]Pj',"rule":"Ingliz tilida sifatning ikki, uch va ko'p bo'g'inli sifatlarning qiyosiy darajalisini yasashda sifat oldidan “more” o'zbekchasi “-roq” va orttirma darajalini yasashda “most” o'zbekchasi “eng” so'zlarini qo'shib yozish orqali yasaladi. Ingliz tilidagi ushbu grammatik qoida asosida quriladigan sifat turi uchun ham ikki til bo'yicha formal modellar ishlab chiqildi."},
    {"en":'less interesting',"uz":"so'z kamroq qiziqarli","pos":'Sifat',"en_model":'P14(T, P) = $[i,1-2]Ti ⊕↓$[j,1-h2]Pj',"uz_model":'P(P1_A1), P_A1) = $[i,1-h2]P1_A1i⊕↓$[j,1-h2]P_A1j',"rule":"Ingliz tilida sifatlarning ozroq yoki eng oz darajasini ifodalash uchun oddiy darajadagi sifatning oldiga “less” kamroq yoki “least” eng kam so'zlari qo'yib yoziladi."},
    {"en":'here',"uz":'shu yerda',"pos":'Ravish',"en_model":'N(N) = $[i,1-h4]Ni',"uz_model":'N(M3,C, X3)=$[i,1-h5]M3i ⊕↓$[j,1-h1] Cj ⊕ ↓$[i1,1-5]X3i1',"rule":"Ingliz tilida ravishlar shakliga ko'ra ikki guruhga sodda va yasama ravishlariga bo'linadi."},
    {"en":'faster',"uz":'tezroq',"pos":'Ravish',"en_model":'N2(N_S) = $[i,1-2]N_Si',"uz_model":'N(N_A1) = $[i,1-20]N_A1i',"rule":"Ingliz tilidagi yasama ravishni quyidagicha namuna misoli orqali ikki til bo'yicha formal modeli ishlab chiqildi."},
    {"en":'fastest',"uz":'eng tez',"pos":'Ravish',"en_model":'N3(N_S) = $[i,1-2]N_Si',"uz_model":'N(T, N2) = $[i,1-h4]Ti ⊕↓$[j,1-h4]N2j',"rule":"Ingliz tilidagi ravishlar huddi sifatdek darajalarga ajratiladi. Bir, ikki bo'g'inli sodda ravishlarning qiyosiy darajasi “-er” affiksi bilan orttirma darajasi “-est” affikslarini qo'shish orqali yasaladi."},
    {"en":'inside',"uz":'ichkarida',"pos":'Ravish',"en_model":'N5(N) = $[i,1-h4]Ni',"uz_model":'N(N, X3) = $[i,1-h4]Ni⊕↓$[j,1-5]X3j',"rule":"Ingliz tilidagi ravish o'rin-joy ravishlari, vaqt ravishlari, o'lchov va daraja ravishlari hamda holat ravishlariga bo'linadi. Shu ravish turlarning har bir turi bo'yicha namuna misollari orqali modellari va raqamli vazn qiymatlarini quyidagi jadvallarda keltirildi."},
    {"en":'today',"uz":'bugun',"pos":'Ravish',"en_model":'N6(N) = $[i,1-h4]Ni',"uz_model":'N(N) = $[i,1-h4]Ni',"rule":"Ingliz tilidagi vaqt ravishlarining namuna misoli asosida ingliz - o'zbek tillaridagi formal modellari."},
    {"en":'much',"uz":"ko'p","pos":'Ravish',"en_model":'N(N) = $[i,1-h4]Ni',"uz_model":'N(N) = $[i,1-h4]Ni',"rule":"Ingliz tilidagi o'lchov va daraja ravishlari o'zbek tilidagi miqdor daraja ravishlari bilan deyarli o'xshash."},
    {"en":'quietly',"uz":'tinchgina',"pos":'Ravish',"en_model":'N(P, N_S) = $[i,1-h2]Pi ⊕↓$[j,1-h4]N_Sj',"uz_model":'N(P, N_A1)= $[i,1-h2]Pi⊕↓$[j,1-h4]N_A1j',"rule":"Holat ravishi ikki tilda ham mavjud. Ingliz tilidagi holat ravishlarining ko'pchiligi sifatga “-ly” affiksi qo'shish orqali yasaladi. O'zbek tiliga tarjimasi ham huddi ingliz tilidagidek sifatga “-gina” sifatdan ravish yasovchi affiks orqali yasaladi."},
    {"en":'one',"uz":'bir',"pos":'Son',"en_model":'F(F) = $[i,1-h6]Fi',"uz_model":'F(F) = $[i,1-h6]Fi',"rule":"Ingliz tilidagi sanoq sonlar birdan o'n ikkigacha o'zbek tilidagi sanoq songa mos keladi."},
    {"en":'fifteen',"uz":"o'n besh","pos":'Son',"en_model":'F(F_S) = $[i,1-h6]F_Si',"uz_model":'F(F, F) = $[i,1-h6]Fi ⊕↓$[j,1-h6]Fj',"rule":"Ingliz tilida o'n uchdan o'n to'qqizgacha bo'lgan sonlar “-teen” affiksi bilan yasaladi. O'zbek tilidagi sanoq sonlar o'nlikni qo'shib yozilishi va hech qanday affiks olmaganligi bilan ikki tildagi son so'z turkumiga oid formal modellarida farq bor."},
    {"en":'eighty',"uz":'sakson',"pos":'Son',"en_model":'F(F_S) = $[i,1-h6]F_Si',"uz_model":'F(F) = $[i,1-h6]Fi',"rule":"Ingliz tilida o'n uchdan o'n to'qqizgacha bo'lgan sonlar “-teen” affiksi bilan yasaladi. O'zbek tilidagi sanoq sonlar o'nlikni qo'shib yozilishi va hech qanday affiks olmaganligi bilan ikki tildagi son so'z turkumiga oid formal modellarida farq bor."},
    {"en":'eighty five',"uz":'sakson besh',"pos":'Son',"en_model":'F(F_S, F) = $[i,1-h6]F_Si⊕↓$[j,1-h6]Fj',"uz_model":'F(F, F) = $[i,1-h6]Fi ⊕↓$[j,1-h6]Fj',"rule":"Ingliz tilida o'n-ten yani o'ndan tashqari o'nlikni bildiruvchi sonlarga 20 dan 90 gacha bo'lgan sonlarga “-ty” affiksi qo'shilishi orqali yasaladi."},
    {"en":'one hundred',"uz":'bir yuz',"pos":'Son',"en_model":'F(F) = $[i,1-h6]Fi',"uz_model":'F(F) = $[i,1-h6]Fi',"rule":"Ingliz tilidagi yuzlik, minglik va millionlik sonlarining oldida one yoziladi. O'zbek tilida yuzlik, minglik va millionlik sonlarida hech qanday affikssiz, aytilishi bo'yicha yoziladi."},
    {"en":'four million',"uz":"to'rt million","pos":'Son',"en_model":'F(F, F) = $[i,1-h6]Fi ⊕↓$[j,1-h6]Fj',"uz_model":'F(F, F) = $[i,1-h6]Fi ⊕↓$[j,1-h6]Fj',"rule":"Ingliz tilidagi yuz, ming va million sonlari oldidan sanoq sonlar kelganda aniq miqdorni bildirgani uchun “-s” affiksi qo'shilmaydigan holdagi sonlar uchun ikki til bo'yicha formal modellari quyidagicha ishlab chiqildi."},
    {"en":'hundredth',"uz":'yuzinchi',"pos":'Son',"en_model":'F(F_S) = $[i,1-h6]F_Si',"uz_model":'F(F_A1) = $[i,1-h6]F_A1i',"rule":"Ingliz tilidagi tartib sonlar ham o'zbek tilidagi tartib sonlardan yozilishi bo'yicha farq qiladi. Ingliz tilida  “birinchi-first, ikkinchi-second, uchinchi-third” tartib sonlaridan boshqa sanoq sonlarga “-th” affiksi qo'shilishi bilan yasaladi. Bu o'zbek tilidagi “-inchi” affiksi bilan mos bo'lganligi uchun ikki til bo'yicha formal  modellari o'xshash."},
    {"en":'hundred and twenty first',"uz":'bir yuz yigirma birinchi',"pos":'Son',"en_model":'F1(F1) = $[i,1-h6]F1',"uz_model":'F1(F1_A1) = $[i,1-h6]F1_A1i',"rule":"Qo'shma tartib sonlarning yasalishida oxirgi son tartib son shaklida yoziladi. Qolgan sonlar sanoq son shaklida yoziladi. Ingliz tilining shu grammatik nazaryasi asosida ikki til bo'yicha formal modellari quyidagicha ishlab chiqildi."},
    {"en":'chapter five',"uz":'beshinchi bob',"pos":'Son',"en_model":'F(C, F) = $[i,1-h1]Ci ⊕↓$[j,1-h6]Fj',"uz_model":'F(F_A1, C)=$[i,1-h6]F_A1i⊕↓$[j,1-h1]Cj',"rule":"Ingliz tilida kitoblarning boblari, bo'limlari va qisimlari ko'pincha tartib sonlar sanoq songa aylanishi bo'yicha namuna misoli keltirilgan. Ingliz tilida son otdan keyin yoziladi, o'zbek tilida otdan oldin yozilishi va “-inchi” affiksi qo'llanilishi bilan bu ikki tildagi son so'z turkumiga oid qo'shma tartib sonlarda farq bor."},
]


def load_ch2_evx_examples():
    """
    CH2_EVX_EXAMPLES ro'yxatini (so_zlar_bazasi_un.docx'dan ajratib olingan,
    52 ta ingliz-o'zbek EVXs/EVIXs namuna so'z + har ikki tilning formal
    modeli + grammatik qoida izohi) quyidagilarga yozadi:
      1) UB_en_w / UB_uz_w (words)      — so'z + tarjima + formal_model ustuni
         (bu orqali smart_parse/translate_phrase_kkt AVTOMATIK ravishda shu
         tekshirilgan tarjima va modeldan foydalanadi — chunki words jadvali
         allaqachon tarjima qidiruvida ustuvor manba hisoblanadi)
      2) BM_en_w / BM_uz_w (word_models) — har bir so'zning TO'LIQ formal
         model TENGLAMASI (masalan "C(C, X1) = $[i,1-h1]Ci⊕..."), keyinchalik
         kkt_en()/kkt_uz() shundan foydalanadi (pastga qarang)
      3) BM_en_w / BM_uz_w (grammar_rules) — har bir namunaga tegishli
         grammatik qoida matni (izoh sifatida, ikkala bazada bir xil)
    Qayta ishga tushirilsa xavfsiz (UNIQUE cheklovlar tufayli takrorlanmaydi).
    """
    init_all_databases()
    conn_uen=sqlite3.connect(DB_UB_EN); cur_uen=conn_uen.cursor()
    conn_uuz=sqlite3.connect(DB_UB_UZ); cur_uuz=conn_uuz.cursor()
    conn_ben=sqlite3.connect(DB_BM_EN); cur_ben=conn_ben.cursor()
    conn_buz=sqlite3.connect(DB_BM_UZ); cur_buz=conn_buz.cursor()

    word_id = max(
        (cur_uen.execute("SELECT COALESCE(MAX(id),0) FROM words").fetchone()[0]),
        (cur_uuz.execute("SELECT COALESCE(MAX(id),0) FROM words").fetchone()[0]),
    )
    n_words=n_models=n_rules=0
    for ex in CH2_EVX_EXAMPLES:
        en,uz,pos = ex["en"].lower(), ex["uz"], ex["pos"]
        word_id += 1
        cur_uen.execute("""INSERT OR IGNORE INTO words(id,headword,translation,pos,source,formal_model)
                            VALUES(?,?,?,?,'chapter2_evx',?)""",(word_id,en,uz,pos,ex["en_model"]))
        if cur_uen.rowcount>0: n_words+=1
        cur_uuz.execute("""INSERT OR IGNORE INTO words(id,headword,translation,pos,source,formal_model)
                            VALUES(?,?,?,?,'chapter2_evx',?)""",(word_id,uz,en,pos,ex["uz_model"]))

        cur_ben.execute("INSERT OR IGNORE INTO word_models(headword,pos,kkt_model) VALUES(?,?,?)",
                         (en,pos,ex["en_model"]))
        if cur_ben.rowcount>0: n_models+=1
        cur_buz.execute("INSERT OR IGNORE INTO word_models(headword,pos,kkt_model) VALUES(?,?,?)",
                         (uz,pos,ex["uz_model"]))

        if ex.get("rule"):
            cur_ben.execute("INSERT OR IGNORE INTO grammar_rules(headword,pos,rule_text) VALUES(?,?,?)",
                             (en,pos,ex["rule"]))
            if cur_ben.rowcount>0: n_rules+=1
            cur_buz.execute("INSERT OR IGNORE INTO grammar_rules(headword,pos,rule_text) VALUES(?,?,?)",
                             (uz,pos,ex["rule"]))
    conn_uen.commit(); conn_uen.close(); conn_uuz.commit(); conn_uuz.close()
    conn_ben.commit(); conn_ben.close(); conn_buz.commit(); conn_buz.close()
    return {"words":n_words, "models":n_models, "rules":n_rules}


_WM_CACHE_EN = {}
_WM_CACHE_UZ = {}
def bm_lookup_word_model(db_path, headword):
    """word_models bazasidan SO'ZNING O'ZIGA (aniq mos kelganda) tekshirilgan
    formal model tenglamasini qaytaradi — topilmasa None."""
    cache = _WM_CACHE_EN if db_path==DB_BM_EN else (_WM_CACHE_UZ if db_path==DB_BM_UZ else None)
    key = headword.strip().lower()
    if cache is not None and key in cache:
        return cache[key]
    result=None
    try:
        conn=sqlite3.connect(db_path)
        row=conn.execute("SELECT kkt_model,pos FROM word_models WHERE lower(headword)=?",(key,)).fetchone()
        conn.close()
        if row: result={"mm":row[0],"pos":row[1]}
    except Exception:
        result=None
    if cache is not None: cache[key]=result
    return result


def load_pdf_kkt_bazalar():
    """
    "umumiy_to'liq_6_oid_09.pdf" — dissertatsiya I bobidan (KKT belgilar
    jadvali 1.1 + I bobning aniq/ishonchli o'qilgan qo'shimcha jadvallari
    1.2-1.17, 1.18) qo'lda tekshirib chiqilgan (pdfplumber orqali ajratib,
    matndagi "N turdagi" sonlariga aynan mos kelishi tasdiqlangan) holda
    BM_en_w/BM_uz_w (kkt_symbols) va QM_en_w/QM_uz_w (affixes) bazalariga
    yuklaydi.

    DIQQAT: 1.19-1.23-jadvallar (predlog iboralar, bog'lovchilar, modal
    so'zlar, taqlid so'zlar) PDFning matn qatlamida kuchli buzilgan
    (garbled/aralashgan katakchalar) bo'lgani uchun BU YERGA QO'SHILMADI —
    noto'g'ri ma'lumot bazaga yozilib qolmasligi uchun ataylab o'tkazib
    yuborildi. Bu jadvallarni kiritish uchun asl .docx (Word) manba fayl
    kerak (jadval tuzilishi PDFga qaraganda ancha ishonchli o'qiladi).

    Qayta ishga tushirilsa xavfsiz (UNIQUE cheklovlar tufayli takrorlanmaydi).
    Qaytaradi: {"symbols":n, "affixes_en":n, "new_prefixes":[...]}
    """
    init_all_databases()

    # ── 1) KKT belgilar jadvali -> BM_en_w / BM_uz_w ──
    n_sym = 0
    conn_en=sqlite3.connect(DB_BM_EN); cur_en=conn_en.cursor()
    conn_uz=sqlite3.connect(DB_BM_UZ); cur_uz=conn_uz.cursor()
    for sym,func in KKT_SYMBOLS:
        cur_en.execute("INSERT OR IGNORE INTO kkt_symbols(kkt_symbol,funktsiya,weight) VALUES(?,?,NULL)",(sym,func))
        cur_uz.execute("INSERT OR IGNORE INTO kkt_symbols(kkt_symbol,funktsiya,weight) VALUES(?,?,NULL)",(sym,func))
        if cur_en.rowcount>0: n_sym+=1
    conn_en.commit(); conn_en.close(); conn_uz.commit(); conn_uz.close()

    # ── 2) I bob affiks/prefiks jadvallari -> QM_en_w ──
    conn_qen=sqlite3.connect(DB_QM_EN); cur_qen=conn_qen.cursor()
    n_aff = 0
    next_id = cur_qen.execute("SELECT COALESCE(MAX(id),0) FROM affixes").fetchone()[0]
    for jadval,pos,sym,expected,values in AFFIX_TABLES:
        for v in values:
            next_id += 1
            cur_qen.execute(
                "INSERT OR IGNORE INTO affixes(id,pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,?,NULL)",
                (next_id,pos,sym,sym,v))
            if cur_qen.rowcount>0: n_aff+=1
    # 1.18-jadval — umumiy prefikslar (96 ta) -> QM_en_w, "T" (old qo'shimcha)
    for v in GENERAL_PREFIXES_96:
        next_id += 1
        cur_qen.execute(
            "INSERT OR IGNORE INTO affixes(id,pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,?,NULL)",
            (next_id,"Umumiy","T","T",v))
        if cur_qen.rowcount>0: n_aff+=1
    conn_qen.commit(); conn_qen.close()

    # ── 3) Jonli parserda (EN_PREFIXES) hali yo'q, lekin PDF manbada
    #        mavjud prefikslarni ANIQLAB BERISH (avtomatik QO'SHILMAYDI —
    #        qisqa prefikslar (masalan "a-","e-","on-") yolg'on-musbat
    #        so'z bo'lish xavfi yuqori, shuning uchun qo'lda ko'rib chiqish
    #        tavsiya etiladi) ──
    existing_stems = {p for p,_ in EN_PREFIXES}
    new_prefixes = sorted({p.rstrip("-") for p in GENERAL_PREFIXES_96} - existing_stems)

    return {"symbols":n_sym, "affixes_en":n_aff, "new_prefixes":new_prefixes}


def find_bazalar_docx():
    for d in SEARCH_DIRS:
        for name in DOCX2_CANDIDATES:
            p=os.path.join(d,name)
            if os.path.exists(p): return p
    return None

def find_bazalar_affixes_docx():
    for d in SEARCH_DIRS:
        for name in DOCX2B_CANDIDATES:
            p=os.path.join(d,name)
            if os.path.exists(p): return p
    return None

def find_ch2_examples_docx():
    for d in SEARCH_DIRS:
        for name in DOCX3_CANDIDATES:
            p=os.path.join(d,name)
            if os.path.exists(p): return p
    return None

# Fayllar topilmasa ham ishlashi kafolatlangan minimal lug'at — dastur hech
# qanday .docx/.xlsx topa olmagan taqdirda ham asosiy tarjima va rasmdagi
# "From our books" namunasi ishlab turishi uchun.
SEED_WORDS = [
    ("book","kitob","Ot"), ("table","stol","Ot"), ("computer","kompyuter","Ot"),
    ("student","talaba","Ot"), ("teacher","o'qituvchi","Ot"), ("house","uy","Ot"),
    ("water","suv","Ot"), ("language","til","Ot"), ("word","so'z","Ot"),
    ("system","tizim","Ot"), ("model","model","Ot"), ("number","son","Ot"),
    ("algorithm","algoritm","Ot"),
    # Predloglar — QM_en_w'da "D" tarzida ham, so'zlar bazasida ham bo'lishi
    # kerak, aks holda "from" kabi so'z yakka holda kiritilganda topilmaydi.
    ("from","dan","Predlog"), ("to","ga","Predlog"), ("of","ning","Predlog"),
    ("in","da","Predlog"), ("at","da","Predlog"), ("on","da","Predlog"),
    ("with","bilan","Predlog"), ("about","haqida","Predlog"),
    # Egalik olmoshlari
    ("my","mening","Olmosh"), ("our","bizning","Olmosh"), ("your","sizning","Olmosh"),
    ("his","uning","Olmosh"), ("her","uning","Olmosh"), ("their","ularning","Olmosh"),
    # Bog'lovchilar — IXTIYORIY (arbitrary) ko'p feʼlli / qo'shma iboralarni
    # to'g'ri SOV tartibida ajratish uchun _split_compound_clause() shu
    # so'zlarga tayanadi; bazada topilmasa ham CONJ_UZ zaxira jadvali orqali
    # ishlaydi, lekin bu yerda bo'lishi "topildi" statusini ta'minlaydi.
    ("and","va","Bog'lovchi"), ("or","yoki","Bog'lovchi"), ("but","lekin","Bog'lovchi"),
    ("because","chunki","Bog'lovchi"),
]
def _fix_mistagged_function_words():
    """Asl 1500-so'zlik lug'atda ba'zi funktsional so'zlar ("with","my","our",
    "your","his" va h.k.) NOTO'G'RI "Ot" turkumida ham uchraydi (manba
    hujjatning o'zidagi kategoriyalash xatosi). Bu funktsional so'zlar
    predlog/olmosh sifatida BIR MA'NOLI bo'lishi shart — aks holda ibora
    qayta tartiblash (PP/NP aniqlash) xato ishlaydi. Shu so'zlarning
    noto'g'ri "Ot" yozuvlarini bazadan tozalaydi.
    """
    closed_class = set(PREP_UZ_X3)|set(PREP_UZ_POSTPOSITION)|set(POSS_PRONOUN_UZ_X2)
    removed=0
    for db_path in (DB_UB_EN,):
        try:
            conn=sqlite3.connect(db_path); cur=conn.cursor()
            for w in closed_class:
                rows=cur.execute("SELECT id,pos FROM words WHERE headword=?",(w,)).fetchall()
                if len(rows)>1 and any(p!="Ot" for _,p in rows):
                    for rid,p in rows:
                        if p=="Ot":
                            cur.execute("DELETE FROM words WHERE id=?",(rid,)); removed+=1
            conn.commit(); conn.close()
        except: pass
    if removed:
        try:
            conn=sqlite3.connect(DB_UB_UZ); cur=conn.cursor()
            for w in closed_class:
                rows=cur.execute("SELECT id,translation,pos FROM words WHERE translation=?",(w,)).fetchall()
                for rid,tr,p in rows:
                    if p=="Ot" and len(cur.execute("SELECT id FROM words WHERE translation=?",(w,)).fetchall())>1:
                        cur.execute("DELETE FROM words WHERE id=?",(rid,))
            conn.commit(); conn.close()
        except: pass
    return removed

def seed_core_demo_data():
    """Hech qanday manba fayl topilmasa ham dastur ishlashi uchun minimal
    lug'at va rasmdagi namuna so'zlarni bazaga kafolatlab yozadi
    (INSERT OR IGNORE — mavjud ma'lumotni buzmaydi, faqat to'ldiradi)."""
    added=0
    for en,uz,pos in SEED_WORDS:
        if db_insert(en,uz,pos,"docx"): added+=1
    _fix_mistagged_function_words()
    # Predloglarni QM_en_w/QM_uz_w'ga ham "D" (predlog) belgisi bilan qo'shamiz
    # (predloglar affiks emas — chiziqcha qo'shilmaydi, oddiy so'z sifatida yoziladi)
    for en,uz in (("from","dan"),("to","ga"),("of","ning"),("in","da"),
                  ("at","da"),("on","da"),("with","bilan"),("about","haqida")):
        for db_path,pos,sym,val in ((DB_QM_EN,"Predlog","D",en),(DB_QM_UZ,"Predlog","X3","-"+uz)):
            try:
                conn=sqlite3.connect(db_path)
                if not conn.execute("SELECT 1 FROM affixes WHERE value=?",(val,)).fetchone():
                    conn.execute("INSERT OR IGNORE INTO affixes(pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,NULL)",
                                 (pos,sym,sym,val))
                    conn.commit()
                conn.close()
            except: pass
    return added

def set_kkt_symbol_weight(kkt_symbol, weight):
    """Keyinroq: bitta KKT belgisining vaznini BM_en_w va BM_uz_w da bir vaqtda yangilaydi."""
    ok=True
    for path in (DB_BM_EN,DB_BM_UZ):
        try:
            c=sqlite3.connect(path)
            c.execute("UPDATE kkt_symbols SET weight=? WHERE kkt_symbol=?",(weight,kkt_symbol))
            c.commit(); c.close()
        except: ok=False
    return ok

def set_affix_weight(kkt_symbol, value, weight):
    """Keyinroq: bitta qoʻshimchaning vaznini QM_en_w yoki QM_uz_w da (topilgan bazada) yangilaydi."""
    updated=0
    for path in (DB_QM_EN,DB_QM_UZ):
        try:
            c=sqlite3.connect(path)
            cur=c.execute("UPDATE affixes SET weight=? WHERE kkt_symbol=? AND value=?",(weight,kkt_symbol,value))
            updated+=cur.rowcount; c.commit(); c.close()
        except: pass
    return updated

# ═══════════════════════════════════════════════════════════════════
#  ID SINXRONLASH — UB_en_w/UB_uz_w va QM_en_w/QM_uz_w dagi
#  BARCHA (eski + yangi) yozuvlarni mos tarjima/qoʻshimcha juftligiga
#  bir xil id beradi.
# ═══════════════════════════════════════════════════════════════════
def _rewrite_words_table(conn, rows):
    cur=conn.cursor()
    cur.execute("DELETE FROM words")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='words'")
    cur.executemany("INSERT INTO words(id,headword,translation,pos,source,formal_model) VALUES(?,?,?,?,?,?)", rows)
    conn.commit()

def _rewrite_affixes_table(conn, rows):
    cur=conn.cursor()
    cur.execute("DELETE FROM affixes")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='affixes'")
    cur.executemany("INSERT INTO affixes(id,pos,category,kkt_symbol,value,weight) VALUES(?,?,?,?,?,?)", rows)
    conn.commit()

def resync_word_ids():
    """
    UB_en_w va UB_uz_w dagi HAMMA so'zni (1500 lug'at + II bob so'zlari + qo'lda
    qo'shilganlari) tekshirib, bir-birining tarjimasi bo'lgan yozuvlarga BIR XIL
    id beradi. Mos juftlik topilmagan yozuvlar ham yo'qolmaydi — faqat mustaqil
    (juftlashtirilmagan) id oladi.
    """
    conn_en=sqlite3.connect(DB_UB_EN); conn_uz=sqlite3.connect(DB_UB_UZ)
    en_rows=conn_en.execute("SELECT id,headword,translation,pos,source,formal_model FROM words ORDER BY id").fetchall()
    uz_rows=conn_uz.execute("SELECT id,headword,translation,pos,source,formal_model FROM words ORDER BY id").fetchall()

    uz_by_key={}
    for r in uz_rows:
        key=(r[2].strip().lower(), r[1].strip().lower())  # (inglizcha, o'zbekcha)
        uz_by_key.setdefault(key,[]).append(r)

    used_uz=set(); new_en=[]; new_uz=[]; next_id=1
    for r in en_rows:
        _id,hw,tr,pos,src,fm=r
        key=(hw.strip().lower(), tr.strip().lower())
        match=None
        for cand in uz_by_key.get(key,[]):
            if cand[0] not in used_uz: match=cand; break
        nid=next_id; next_id+=1
        new_en.append((nid,hw,tr,pos,src,fm))
        if match:
            used_uz.add(match[0])
            new_uz.append((nid,match[1],match[2],match[3],match[4],match[5]))
    for r in uz_rows:
        if r[0] in used_uz: continue
        nid=next_id; next_id+=1
        new_uz.append((nid,r[1],r[2],r[3],r[4],r[5]))

    _rewrite_words_table(conn_en,new_en); _rewrite_words_table(conn_uz,new_uz)
    conn_en.close(); conn_uz.close()
    return len(new_en), len(new_uz)

def resync_affix_ids():
    """
    QM_en_w va QM_uz_w dagi qoʻshimchalarni SOʻZ TURKUMI (pos) boʻyicha guruhlab,
    bir xil turkumga oid EN/UZ qoʻshimchalarga mos tartibda BIR XIL id beradi.
    (Ingliz va oʻzbek qoʻshimchalari koʻpincha turli KKT belgi yozuvidan
    foydalanadi — masalan "Ot" turkumida EN uchun C(T)/C(S)/C(SF), UZ uchun
    C_A1/C_AG — shu sababli guruhlash aniq belgi emas, pos boʻyicha olinadi;
    pos nomaʼlum ('*'/bo'sh) qatorlar uchun esa kkt_symbol boʻyicha, aks holda
    mustaqil id beriladi.)
    """
    from collections import defaultdict
    conn_en=sqlite3.connect(DB_QM_EN); conn_uz=sqlite3.connect(DB_QM_UZ)
    en_rows=conn_en.execute("SELECT id,pos,category,kkt_symbol,value,weight FROM affixes ORDER BY id").fetchall()
    uz_rows=conn_uz.execute("SELECT id,pos,category,kkt_symbol,value,weight FROM affixes ORDER BY id").fetchall()

    def _key(r):
        pos=(r[1] or "").strip()
        if pos and pos != "*": return ("pos",pos)
        sym=(r[3] or "").strip()
        if sym: return ("sym",sym)
        return None

    en_paired=defaultdict(list); en_solo=[]
    for r in en_rows:
        k=_key(r); (en_paired[k] if k else en_solo).append(r)
    uz_paired=defaultdict(list); uz_solo=[]
    for r in uz_rows:
        k=_key(r); (uz_paired[k] if k else uz_solo).append(r)

    next_id=1; new_en=[]; new_uz=[]
    for k in sorted(set(en_paired)|set(uz_paired)):
        elist=en_paired.get(k,[]); ulist=uz_paired.get(k,[])
        for i in range(max(len(elist),len(ulist))):
            nid=next_id; next_id+=1
            if i<len(elist):
                r=elist[i]; new_en.append((nid,r[1],r[2],r[3],r[4],r[5]))
            if i<len(ulist):
                r=ulist[i]; new_uz.append((nid,r[1],r[2],r[3],r[4],r[5]))
    for r in en_solo:
        nid=next_id; next_id+=1; new_en.append((nid,r[1],r[2],r[3],r[4],r[5]))
    for r in uz_solo:
        nid=next_id; next_id+=1; new_uz.append((nid,r[1],r[2],r[3],r[4],r[5]))

    _rewrite_affixes_table(conn_en,new_en); _rewrite_affixes_table(conn_uz,new_uz)
    conn_en.close(); conn_uz.close()
    return len(new_en), len(new_uz)

def resync_all_ids():
    we,wu = resync_word_ids()
    ae,au = resync_affix_ids()
    return {"words_en":we,"words_uz":wu,"aff_en":ae,"aff_uz":au}

# ═══════════════════════════════════════════════════════════════════
#  IBORANI FORMAL MODEL ASOSIDA TARJIMA QILISH
#  ("From our books" -> D+M2+C+X  ⇒  C+X+X2M+X3 -> "kitoblarimizdan")
#
#  Ingliz TT: PREDLOG(D) + EGALIK OLMOSHI(M2) + OT(C) [+ KOʻPLIK(X)]
#  Oʻzbek TT: OT(C) [+ KOʻPLIK(X)] + EGALIK QOʻSHIMCHASI(X2M) + KELISHIK(X3)
#  — SOV tartibiga oʻtishda predlog va egalik olmoshi soʻz OXIRIGA
#    qoʻshimcha sifatida koʻchadi.
# ═══════════════════════════════════════════════════════════════════
POSS_PRONOUN_UZ_X2 = {   # M2 (egalik olmoshi) -> X2 (Eganing so'z yasovchi affiks)
    "my":"im", "our":"imiz", "your":"ingiz",
    "his":"i", "her":"i", "its":"i", "their":"lari",
}
PREP_UZ_X3 = {            # D (predlog) -> X3 (Kelishik qo'shimchasi, OTga QO'SHILADI)
    "from":"dan", "of":"ning", "to":"ga", "in":"da", "at":"da", "on":"da",
}
PREP_UZ_POSTPOSITION = {  # D (predlog) -> alohida ko'makchi so'z (OTdan KEYIN, BO'SHLIQ bilan)
    "with":"bilan", "about":"haqida",
}

def _qm_lookup(db_path, kkt_symbol, value):
    """QM_en_w/QM_uz_w dan berilgan KKT belgisiga mos qatorni (case-insensitive) izlaydi."""
    try:
        conn=sqlite3.connect(db_path)
        row=conn.execute("SELECT value FROM affixes WHERE kkt_symbol=? AND LOWER(value)=?",
                          (kkt_symbol,value.lower())).fetchone()
        conn.close(); return row[0] if row else None
    except: return None

def translate_phrase_kkt(text):
    """
    Rasmdagi KKT formal model zanjiriga asosan iborani tarjima qiladi:
      D(predlog) + M2(egalik olmoshi) + C(ot) [+ X(ko'plik)]
        ⇒  C(ot) [+ X(ko'plik)] + X2M(egalik qo'shimchasi) + X3(kelishik)

    Bazalardan (QM_en_w -> D; QM_uz_w -> X2,X3; UB_en_w/UB_uz_w -> C ildizi)
    real qiymatlar olinadi. Mos kelmasa None qaytaradi (chaqiruvchi so'z-so'z
    tarjimaga o'tishi kerak).
    """
    words = re.findall(r"[A-Za-z']+", text.lower())
    if len(words) < 3: return None
    prep, poss, *rest = words
    if not rest: return None
    # MUHIM TUZATISH: bu funksiya faqat QATʼIY "predlog+egalik+OT" (D+M2+C)
    # naqshini ifodalaydi — sifat (Sifat) qatnashgan iboralar ("our OLD
    # books") uchun MO'LJALLANMAGAN. Ilgari rest[0] har doim "ot ildizi"
    # deb qabul qilinardi — agar u aslida sifat bo'lsa (masalan "old"),
    # funksiya SIFATNI ot sifatida notoʻgʻri tarjima qilib, ASL OTni
    # (bu yerda "books") butunlay TASHLAB YUBORARDI, va bu notoʻgʻri (lekin
    # None boʻlmagan) natija translate_phrase_general() ning toʻgʻriroq
    # umumiy qayta tartiblashiga yoʻl bermasdi. Endi bu funksiya faqat
    # ANIQ 3 taʼlik "predlog+egalik+ot" naqshiga mos kelgandagina ishlaydi
    # (predlog+egalik ORASIDA/OTdan OLDIN sifat boʻlsa — None qaytaradi,
    # vazifa translate_phrase_general()ga oʻtadi, u sifatlarni ham toʻgʻri
    # qoʻllab-quvvatlaydi).
    if len(rest) != 1: return None
    noun_word = rest[0]
    noun_row_check = db_lookup(noun_word)
    if noun_row_check and noun_row_check[2] not in ("Ot", None):
        return None   # rest[0] ot emas (masalan sifat) — bu naqshga mos kelmaydi

    # 1) D — predlog: PREP_UZ_X3 jadvalida borligini tekshiramiz (QM_en_w'da
    #    ham mavjud bo'lsa, bu qo'shimcha tasdiq sifatida ishlatiladi, lekin
    #    QM_en_w bo'sh/yuklanmagan bo'lsa ham funksiya ishlashda davom etadi).
    x3 = PREP_UZ_X3.get(prep)
    if not x3: return None
    x3_full = _qm_lookup(DB_QM_UZ, "X3", "-"+x3) or x3

    # 2) M2 — egalik olmoshi va X2 mosini tekshiramiz
    if poss not in POSS_PRONOUN_UZ_X2: return None
    x2 = POSS_PRONOUN_UZ_X2[poss]
    x2_full = _qm_lookup(DB_QM_UZ, "X2", "-"+x2) or x2

    # 3) C — ot ildizi: avval xavfsiz ko'plik affikslarini (-ies/-ves/-es),
    #    so'ng so'zning o'zini, oxirida oddiy "-s" ni tekshiramiz (noto'g'ri
    #    "false plural" ajratishning oldini olish uchun — masalan "access"
    #    so'zi "acces"+s emas, balki bitta ot sifatida topiladi).
    root_en=plural_sfx=None; row=None
    for sfx,restore in (("ies","y"),("ves","f"),("es","")):
        if noun_word.endswith(sfx) and len(noun_word) > len(sfx)+1:
            cand = noun_word[:-len(sfx)]+restore
            cand_row = db_lookup(cand)
            if cand_row: root_en,plural_sfx,row = cand,sfx,cand_row; break
    if not row:
        whole_rows = db_lookup_all(noun_word)
        # Faqat avtomatik keshlangan (source='auto') bo'lsa VA oddiy "-s" orqali
        # ham ajratish mumkin bo'lsa — butun so'zni EMAS, ajratilgan holatni
        # ustun qo'yamiz (X tugunini doim ko'rsatish uchun).
        is_only_auto = whole_rows and all(r[4]=="auto" for r in whole_rows)
        can_split_s = noun_word.endswith("s") and len(noun_word)>2 and db_lookup(noun_word[:-1])
        if whole_rows and not (is_only_auto and can_split_s):
            row = (whole_rows[0][1],whole_rows[0][2],whole_rows[0][3])
            root_en,plural_sfx = noun_word,""
    if not row and noun_word.endswith("s") and len(noun_word) > 2:
        cand = noun_word[:-1]; cand_row = db_lookup(cand)
        if cand_row: root_en,plural_sfx,row = cand,"s",cand_row
    if not row: return None
    uz_root = uz_stem(row[1])
    x_lar = "lar" if plural_sfx else ""

    # ── EN zanjiri (rasmning yuqori qatori) ──
    zanjir_en=[{"soz":prep,"kkt":"D"},{"soz":poss,"kkt":"M2"},{"soz":root_en,"kkt":"C"}]
    if plural_sfx: zanjir_en.append({"soz":plural_sfx,"kkt":"X"})

    # ── UZ zanjiri (rasmning pastki qatori, qayta tartiblangan: C X X2M X3) ──
    zanjir_uz=[{"soz":uz_root,"kkt":"C"}]
    if x_lar: zanjir_uz.append({"soz":x_lar,"kkt":"X"})
    zanjir_uz.append({"soz":x2,"kkt":"X2M"})
    zanjir_uz.append({"soz":x3,"kkt":"X3"})

    natija = "".join(z["soz"] for z in zanjir_uz)
    model_en = "+".join(z["kkt"] for z in zanjir_en)
    model_uz = "+".join(z["kkt"] for z in zanjir_uz)
    return {
        "kirish": " ".join(words),
        "zanjir_en": zanjir_en, "zanjir_uz": zanjir_uz,
        "natija": natija,
        "model": f"{model_en}  ⇒  {model_uz}  =  " + "+".join(z["soz"] for z in zanjir_uz),
    }


# ═══════════════════════════════════════════════════════════════════
#  UMUMIY IBORA TARJIMONI — bazadagi so'zlardan tuzilgan ISTALGAN yangi
#  ibora uchun ingliz (SVO) tartibini o'zbek (SOV) grammatik tartibiga
#  moslab qayta quradi. translate_phrase_kkt() faqat BITTA aniq naqshni
#  (predlog+egalik+ot) qamrab oladi; bu funksiya undan tashqari FE'L+
#  TO'LDIRUVCHI (obyekt) naqshini ham umumiy tarzda qayta tartiblaydi —
#  masalan "analyze the system" → "tizimni tahlil qilish", yangidan
#  kiritilgan, oldindan ko'rilmagan iboralar uchun ham ishlaydi.
# ═══════════════════════════════════════════════════════════════════
_DETERMINERS = {"the","a","an","this","that","these","those"}
# KKT spec 2.2/2.3: noaniq artikl "a"/"an" o'zbekchada "bitta" bilan beriladi
# ("a network" → "bitta tarmoq"); 2.4: aniq artikl "the" tarjima qilinmaydi
# (qolgan _DETERMINERS kabi tashlab yuboriladi).
_INDEFINITE_ARTICLE_UZ = {"a":"bitta", "an":"bitta"}
# KKT spec 2.56: "to" + FE'L — infinitiv yuklamasi, o'zbekchada alohida so'z
# bilan berilmaydi (fe'lning lug'atdagi "-moq" shakli yetarli): "to ask" →
# "so'ramoq". Faqat "to" dan KEYIN fe'l kelganda — "to the system" kabi
# predlogli iboralar (PREP_UZ_X3: to→ga) o'zgarmaydi.
INFINITIVE_PARTICLE_EN = "to"
# KKT spec 2.59: inglizchada predlog orqali to'ldiruvchi oluvchi fe'l —
# o'zbekchada vositasiz to'ldiruvchi: "listen to me" → "meni tinglamoq"
# (predlog tushadi, to'ldiruvchi fe'ldan oldin, tushum kelishigida). Qaysi
# fe'l shunday ekani LEKSIK ma'lumot: spec faqat (listen, to) juftini beradi,
# ro'yxat shu bilan cheklangan — kengaytirish faqat manbali ma'lumot bilan.
PREP_OBJECT_VERBS = {("listen","to")}
# KKT spec 3.22: kishilik olmoshining obyekt shakli (me/him/us) o'zbekchada
# allaqachon tushum kelishigida (meni/uni/bizni) — ustiga yana "-ni" qo'shilmaydi.
OBJECT_CASE_PRONOUNS = {"me","him","us"}
# KKT spec 2.31/2.32/2.34/3.5: ko'p bo'g'inli sifat va "-ly" ravishning
# ANALITIK darajasi — daraja so'zi + sifat/ravish bitta shaklga aylanadi:
#   more + X → X+roq  ("more comfortable" → "qulayroq", "more clearly" → "aniqroq")
#   most + X → eng X  ("most comfortable" → "eng qulay")
#   less + X → kamroq X ("less interesting" → "kamroq qiziqarli")
# "least" — spec tavsifida tilga olingan, lekin o'zbekcha misoli berilmagan →
# qo'shilmadi. Faqat keyingi so'z Sifat/Ravish bo'lsa ("more books" o'zgarmaydi).
ANALYTIC_DEGREE_EN = {"more", "most", "less"}

def _analytic_degree_uz(marker, uz):
    base = uz_stem(uz)
    base = base[:1].lower() + base[1:]
    if marker == "more": return make_uzbek(base, "er")     # stem+"roq" (qiyosiy jadval bilan bir xil)
    if marker == "most": return make_uzbek(base, "est")    # "eng "+stem
    return "kamroq " + base                                 # less (spec 2.34)

def _chunk_phrase(text):
    """
    Iborani KKT so'z turkumlari asosida konstituentlarga (PP/NP/VP) ajratadi.
    Har bir so'z avval parse_sentence() orqali (KONTEKST bilan) tarjima
    qilinadi, so'ng KETMA-KETLIKDAGI turkumlarga qarab guruhlanadi:

      PP (predlog iborasi):  Predlog + (egalik olmoshi)? + Sifat* + (Ot|Olmosh)[+ko'plik]
                              -> ICHKARIDA darhol qayta quriladi:
                                 [Sifat*] + Ot(+ko'plik)(+egalik)(+kelishik)
                              (predlog so'zi YO'QOLADI — o'zbek tilida
                              kelishik qo'shimchasi sifatida OT ning oxiriga
                              ko'chadi — xuddi "kitoblarimizdan" kabi).
      NP (ot iborasi):       (egalik olmoshi)? + Sifat* + (Ot|Olmosh)[+ko'plik]
      VP:                    Fe'l

    Qaytaradi: [(turkum, o'zbekcha_matn), ...] — chaqiruvchi buni SOV
    tartibiga solib chiqadi.
    """
    aa = parse_sentence(text)
    items = []; k = 0
    while k < len(aa):
        a = aa[k]; w = a["word"].lower()
        nxt = aa[k+1] if k+1 < len(aa) else None
        if w in _INDEFINITE_ARTICLE_UZ:
            # Noaniq artikl — faqat undan keyin (sifat(lar)dan so'ng) OT kelsa,
            # ot iborasiga "bitta" aniqlovchisi sifatida kiradi (spec 2.2/2.3);
            # aks holda avvalgidek tashlab yuboriladi.
            j = k + 1
            while j < len(aa) and aa[j]["found"] and aa[j]["pos"] == "Sifat": j += 1
            if j < len(aa) and aa[j]["found"] and aa[j]["pos"] == "Ot":
                items.append({**a, "found": True, "pos": "Sifat", "uz": _INDEFINITE_ARTICLE_UZ[w]})
            k += 1; continue
        if w in ANALYTIC_DEGREE_EN and nxt and nxt["found"] and nxt["pos"] in ("Sifat", "Ravish"):
            # spec 2.31/2.32/2.34/3.5: daraja so'zi + sifat/ravish → bitta shakl
            items.append({**nxt, "uz": _analytic_degree_uz(w, nxt["uz"])}); k += 2; continue
        if w in _DETERMINERS: k += 1; continue
        items.append(a); k += 1
    if not any(a["found"] for a in items): return None

    chunks=[]; i=0; n=len(items)
    while i < n:
        a = items[i]
        if not a["found"]:
            chunks.append(("?", "["+a["word"]+"?]")); i+=1; continue

        if a["pos"] == "Predlog":
            prep=a["word"].lower()
            nxt = items[i+1] if i+1<n else None
            if prep == INFINITIVE_PARTICLE_EN and nxt and nxt["found"] and nxt["pos"] == "Fe'l":
                i+=1; continue          # spec 2.56: infinitiv "to" tarjima qilinmaydi
            if i>0 and items[i-1]["found"] and items[i-1]["pos"] == "Fe'l" \
               and ((items[i-1]["root"] or "").lower(), prep) in PREP_OBJECT_VERBS:
                i+=1; continue          # spec 2.59: predlog tushadi, keyingi so'z — vositasiz to'ldiruvchi
            j=i+1; poss=None
            if j<n and items[j]["found"] and items[j]["pos"]=="Olmosh" and items[j]["word"].lower() in POSS_PRONOUN_UZ_X2:
                poss=items[j]["word"].lower(); j+=1
            mods=[]
            while j<n and items[j]["found"] and items[j]["pos"]=="Sifat":
                mods.append(items[j]["uz"]); j+=1
            if j<n and items[j]["found"] and items[j]["pos"] in ("Ot","Olmosh"):
                head=items[j]; j+=1
                x3=PREP_UZ_X3.get(prep)
                if x3:
                    head_uz=uz_stem(head["uz"])
                    if poss: head_uz += POSS_PRONOUN_UZ_X2[poss]
                    head_uz += x3
                    chunks.append(("PP"," ".join(mods+[head_uz]))); i=j; continue
                post=PREP_UZ_POSTPOSITION.get(prep)
                if post:
                    head_uz=uz_stem(head["uz"])
                    if poss: head_uz += POSS_PRONOUN_UZ_X2[poss]
                    chunks.append(("PP"," ".join(mods+[head_uz,post]))); i=j; continue
            # predlog uchun kelishik topilmadi — so'zma-so'z qoldiramiz
            chunks.append(("Predlog",a["uz"])); i+=1; continue

        if a["pos"] == "Fe'l":
            chunks.append(("VP", a["uz"])); i+=1; continue

        if a["pos"] == "Sifat":
            mods=[a["uz"]]; j=i+1
            while j<n and items[j]["found"] and items[j]["pos"]=="Sifat":
                mods.append(items[j]["uz"]); j+=1
            if j<n and items[j]["found"] and items[j]["pos"] in ("Ot","Olmosh"):
                mods.append(items[j]["uz"]); j+=1
                chunks.append(("NP"," ".join(mods))); i=j; continue
            chunks.append(("Sifat"," ".join(mods))); i=j; continue

        if a["pos"]=="Olmosh" and a["word"].lower() in POSS_PRONOUN_UZ_X2 and i+1<n \
           and items[i+1]["found"] and items[i+1]["pos"] in ("Ot","Sifat"):
            j=i+1; mods=[]
            while j<n and items[j]["found"] and items[j]["pos"]=="Sifat":
                mods.append(items[j]["uz"]); j+=1
            if j<n and items[j]["found"] and items[j]["pos"]=="Ot":
                head_uz=uz_stem(items[j]["uz"])+POSS_PRONOUN_UZ_X2[a["word"].lower()]
                chunks.append(("NP"," ".join(mods+[head_uz]))); i=j+1; continue

        if a["word"].lower() in OBJECT_CASE_PRONOUNS:
            # spec 3.22: obyekt shakli (meni/uni/bizni) — "M1" bo'lagi,
            # translate_phrase_general() unga qayta "-ni" qo'shmaydi.
            chunks.append(("M1", uz_stem(a["uz"]))); i+=1; continue

        chunks.append((a["pos"] or "X", a["uz"])); i+=1
    return chunks

def translate_phrase_general(text):
    """
    KKT ASOSIDA UMUMIY GRAMMATIK QAYTA TARTIBLASH — oldindan belgilangan
    bitta naqshga bog'liq emas, bazadagi so'zlardan tuzilgan IXTIYORIY yangi
    iborani _chunk_phrase() orqali PP/NP/VP konstituentlarga ajratib, so'ng
    ularni o'zbek SOV tartibiga (Predlog-ibora endi kelishikli OT, Fe'l esa
    ibora OXIRIGA) qayta joylashtiradi:
      - VP (fe'l) — har doim ENG OXIRGA ko'chadi (SOV);
      - fe'ldan keyin (inglizcha) kelgan birinchi ODDIY Ot/Olmosh (predlogsiz)
        — TO'G'RIDAN-TO'G'RI TO'LDIRUVCHI hisoblanadi va "-ni" (tushum
        kelishigi) qo'shiladi;
      - PP (predlog+ot) konstituentlari ICHKARIDA allaqachon to'g'ri
        qurilgan (masalan "to the system" -> "tizimga"), shunchaki tartibda
        qoladi.
    Hech qanday tarjima qilingan so'z topilmasa yoki natija mazmunsiz bo'lsa
    None qaytaradi (chaqiruvchi so'zma-so'z tarjimaga o'tadi).
    """
    chunks = _chunk_phrase(text)
    if not chunks: return None
    found_chunks = [c for c in chunks if c[0]!="?"]
    if len(found_chunks) < 1: return None

    vp_idx = [i for i,(t,_) in enumerate(chunks) if t=="VP"]
    if len(vp_idx) == 1:
        vi = vp_idx[0]
        before, verb, after = chunks[:vi], chunks[vi], chunks[vi+1:]
        # Fe'ldan keyingi HAR BIR oddiy Ot/Olmosh/NP — to'g'ridan-to'g'ri
        # to'ldiruvchi (obyekt) hisoblanadi va tushum kelishigi "-ni"
        # qo'shiladi. Avval faqat BIRINCHISI belgilanardi (break bilan) —
        # bu "clean the table and the chair" kabi "va" bilan bog'langan
        # BIR NECHTA obyektli iboralarda ikkinchi (uchinchi, ...) obyektga
        # "-ni" qo'shilmay qolishiga olib kelardi. Endi "and/or"(Bog'lovchi)
        # bilan ajratilgan HAMMA bare Ot/Olmosh/NP obyekt sifatida belgilanadi.
        for k,(t,val) in enumerate(after):
            if t in ("Ot","Olmosh","NP"):
                after[k] = (t, uz_stem(val)+"ni")
        rest = [c for c in (before+after) if c[0] != "?"]
        if not rest:
            # Faqat fe'l qoldi. Bitta so'zli kirish (yoki noma'lum so'z bor) —
            # avvalgidek None (GUI so'zma-so'z natijani ko'rsatadi). Bir necha
            # so'zdan faqat fe'l qolgan bo'lsa (spec 2.56 "to ask" — infinitiv
            # "to" ataylab tashlangan), natija — fe'lning o'zi; aks holda
            # so'zma-so'z zaxira tashlangan "to" ni "ga" qilib qaytarardi.
            if len(re.findall(r"[A-Za-z']+", text)) < 2 or any(c[0] == "?" for c in chunks):
                return None
        seq = [c[1] for c in rest] + [verb[1]]
        model_syms = "+".join((POS_KKT.get(t,t) if t not in ("PP","NP","VP") else t) for t,_ in rest + [("G","")])
    elif len(vp_idx) == 0:
        rest = [c for c in chunks if c[0] != "?"]
        # Ilgari faqat PP/NP boʻlsa oʻtardi — feʼlsiz, lekin sof Ot/Olmosh
        # (sifatsiz, predlogsiz) boʻlaklardan tuzilgan iboralar (masalan
        # koʻp soʻzli ot birikmalari) shu tekshiruv sabab umuman qayta
        # tartiblanmasdan soʻzma-soʻz zaxiraga tushib qolardi. Endi kamida
        # BITTA topilgan (bazada bor) boʻlak boʻlsa yetarli.
        if len(rest) < 1: return None
        seq = [c[1] for c in rest]
        model_syms = "+".join((POS_KKT.get(t,t) if t not in ("PP","NP") else t) for t,_ in rest)
    else:
        return None   # bir nechta fe'l — murakkab gap, hozircha so'zma-so'zga o'tadi

    if not seq: return None
    seq=[s[0].lower()+s[1:] if s else s for s in seq]
    seq[0]=seq[0][0].upper()+seq[0][1:] if seq[0] else seq[0]
    natija=" ".join(seq)
    return {"natija":natija,
            "model":f"KKT qayta tartiblash ({model_syms})  =  {natija}",
            "kirish":text}



# ═══════════════════════════════════════════════════════════════════
#  QO'SHMA GAP / KO'P FE'LLI IBORALAR — "and"/"or"/"but" kabi
#  bog'lovchi bilan bog'langan, HAR BIRI O'Z FE'LIGA ega bo'lgan ikki
#  (yoki undan ortiq) mustaqil boʻlakni topib, HAR BIRINI ALOHIDA SOV
#  tartibiga soladi, so'ng mos o'zbekcha bog'lovchi bilan qayta
#  birlashtiradi. Bu — translate_phrase_general() ning "bitta feʼl"
#  cheklovini chetlab o'tib, IXTIYORIY (koʻp feʼlli) iboralarni ham
#  toʻgʻri soʻz tartibida tarjima qilish imkonini beradi. Diqqat: bu
#  faqat bog'lovchining HAR IKKI tomonida ham kamida bittadan feʼl
#  bo'lgandagina ishga tushadi — aks holda (masalan "books and
#  articles" — bitta feʼlga tegishli ikkita obyekt) bu funksiya jim
#  qaytadi va vazifa translate_phrase_general() dagi "obyektlar
#  ro'yxati" mantig'iga (yuqoridagi tuzatish) qoladi.
# ═══════════════════════════════════════════════════════════════════
CONJ_UZ = {"and":"va", "or":"yoki", "but":"lekin", "because":"chunki"}

def _translate_compound_clauses(text):
    aa_all = parse_sentence(text)
    verb_count = sum(1 for a in aa_all if a.get("found") and a.get("pos")=="Fe'l")
    if verb_count < 2:
        return None   # bitta (yoki nolta) feʼl — bo'lish shart emas
    tokens = re.findall(r"[A-Za-z']+", text)
    lower = [t.lower() for t in tokens]
    for idx, tok in enumerate(lower):
        if tok not in CONJ_UZ or idx == 0 or idx == len(tokens)-1:
            continue
        left_txt  = " ".join(tokens[:idx])
        right_txt = " ".join(tokens[idx+1:])
        left_v  = sum(1 for a in parse_sentence(left_txt)  if a.get("found") and a.get("pos")=="Fe'l")
        right_v = sum(1 for a in parse_sentence(right_txt) if a.get("found") and a.get("pos")=="Fe'l")
        if left_v < 1 or right_v < 1:
            continue   # bu bog'lovchi ikkita mustaqil FEʼLLI boʻlakni ajratmayapti
        left_r  = translate_phrase_kkt(left_txt)  or translate_phrase_general(left_txt)
        right_r = translate_phrase_kkt(right_txt) or translate_phrase_general(right_txt)
        if not left_r or not right_r:
            continue
        uz_conj = CONJ_UZ[tok]
        # Har ikki boʻlak ALOHIDA translate_phrase_*() orqali oʻtganida
        # OʻZINING birinchi harfini bosh harf qilib qoʻyadi (mustaqil
        # gap sifatida ishlab chiqilgani uchun). Ular BIR gapga
        # birlashtirilganda faqat ENG BIRINCHI soʻz bosh harfli qolishi
        # kerak — ikkinchi boʻlak endi gap ICHIDA, shu sabab kichik
        # harfga qaytariladi.
        right_natija = right_r["natija"]
        if right_natija:
            right_natija = right_natija[0].lower() + right_natija[1:]
        natija = f"{left_r['natija']} {uz_conj} {right_natija}"
        model = f"[{left_r.get('model','')}]  +{uz_conj.upper()}+  [{right_r.get('model','')}]"
        return {"natija": natija, "model": model, "kirish": text}
    return None


def translate_phrase(text, allow_write=True):
    """
    Ibora tarjimasining YAGONA kirish nuqtasi — GUI shu funksiyani chaqiradi.
    Tartib:
      1) _translate_compound_clauses — ikki (yoki undan ortiq) mustaqil
         feʼlli boʻlakdan tuzilgan qoʻshma iboralarni (masalan "... and ...")
         ikkiga ajratib, HAR BIRINI ALOHIDA toʻgʻri SOV tartibiga soladi;
      2) translate_phrase_kkt — ANIQ KKT naqshi (predlog+egalik+ot, formal
         belgilari bazadan ID orqali olingan);
      3) translate_phrase_general — UMUMIY grammatik qayta tartiblash
         (fe'l+obyekt(lar) SVO→SOV, PP/NP predlogli birikmalar va h.k.) —
         oldindan koʻrilmagan, IXTIYORIY yangi iboralar uchun ham ishlaydi.
    Uchalasi ham mos kelmasa None — GUI so'zma-so'z (parse_sentence)
    natijasini ko'rsatadi.

    allow_write=False (standart: True) — readonly_mode() ning qulay yorlig'i:
    ichki chaqiruv zanjiri (translate_phrase_general -> _chunk_phrase ->
    parse_sentence -> smart_parse) noma'lum so'z/qo'shimchani avtomatik
    xulosa qilsa ham, natijani .db fayllarga YOZMAYDI. Tarjima natijasi
    (matn) allow_write qiymatidan qat'i nazar bir xil bo'ladi — faqat
    yon ta'sir (bazaga yozish) farq qiladi. O'lchov/audit skriptlari
    (scripts/audit_examples.py va h.k.) shu bilan chaqirishi kerak:
    `translate_phrase(matn, allow_write=False)`.
    """
    if not allow_write:
        with readonly_mode():
            return (_translate_compound_clauses(text)
                    or translate_phrase_kkt(text)
                    or translate_phrase_general(text))
    return (_translate_compound_clauses(text)
            or translate_phrase_kkt(text)
            or translate_phrase_general(text))


# ═══════════════════════════════════════════════════════════════════
#  MORFOLOGIK TAHLIL — 5 BOSQICH ALGORITM
#
#  Bosqich 1: To'g'ridan baza → C(C) yoki G(G) modeli
#  Bosqich 2: Apostrof belgisi → student's
#  Bosqich 3: NLTK lemmatizatsiya → grammatik shakl aniqlash
#  Bosqich 4: MORPH_RULES → imlo qoidalari bilan ildiz + affiks
#  Bosqich 5a: Prefiks + ildiz → C(T,C) modeli
#  Bosqich 5b: Prefiks + ildiz + affiks → C(T,C,A1) modeli
# ═══════════════════════════════════════════════════════════════════
def _try_suffix(w):
    """
    MORPH_RULES orqali so'zdan ildiz va affiksni ajratadi.

    MUHIM QOIDA:
      -es uchun FAQAT fn1=w[:-2] ishlatiladi (w[:-1] YO'Q).
      Sababi: "variables"→fn2=w[:-1]="variable" bor → -es deb topadi.
      Lekin to'g'risi -s! Chunki -es faqat {s,ss,x,ch,sh} dan keyin qo'shiladi.
      Shuning uchun -es qoidasida w[:-1] yo'q — bu -s ning ishi.

    NATIJA:
      - "variables": -es fn1="variabl"(yo'q) → -s fn1="variable"(bor) → -s ✓
      - "processes": -es fn1="process"(bor) → -es ✓

    MUHIM: derived_pos — MORPH_RULES dan olingan to'g'ri turkum.
      Masalan: "quickly" → "-ly" → pos="Ravish" (bazadagi "quick"→"Sifat" emas!)
    """
    for rule in MORPH_RULES:
        sfx, fns, derived_pos, label = rule[0], rule[1], rule[2], rule[3]
        req_root_pos = rule[4] if len(rule) > 4 else None
        if not w.endswith(sfx): continue
        if len(w) <= len(sfx)+1: continue
        for fn in fns:
            try: cand = fn(w)
            except: continue
            if len(cand) < 2: continue
            row = db_lookup(cand)
            if row:
                if req_root_pos and row[2] != req_root_pos: continue
                return row, cand, sfx, derived_pos, label
    return None


def _try_suffix_chain(w):
    """_try_suffix'ning IKKI QATLAMLI qo'shimchali so'zlar uchun kengaytmasi
    (masalan "work+er+s" — ish + bajaruvchi + ko'plik). Avval bitta qatlamni
    sinaydi; agar lug'atda topilmasa, tashqi qo'shimchani (lug'at tekshiruvisiz)
    ajratib, qolgan qismni yana bir marta _try_suffix'ga yuboradi.
    Qaytaradi: (row, root, tashqi_sfx, derived_pos, label, ichki_sfx, ichki_label)
    ichki_sfx/ichki_label bitta qatlam bo'lsa None."""
    res = _try_suffix(w)
    if res:
        row,cand,sfx,derived_pos,label = res
        return row,cand,sfx,derived_pos,label,None,None
    for rule in MORPH_RULES:
        sfx, fns, derived_pos, label = rule[0], rule[1], rule[2], rule[3]
        req_root_pos = rule[4] if len(rule) > 4 else None
        if not w.endswith(sfx) or len(w) <= len(sfx)+2: continue
        for fn in fns:
            try: mid = fn(w)
            except: continue
            if len(mid) < 3: continue
            inner = _try_suffix(mid)
            if inner:
                irow,icand,isfx,ipos,ilabel = inner
                # Tashqi qoida ildiz turkumini talab qilsa (masalan Fe'l "-s"),
                # u oraliq so'zning ANIQLANGAN turkumiga (ipos) qo'llanadi —
                # aks holda "work+er+s" (Ot) fe'l 3-shaxs deb olinib qolardi.
                if req_root_pos and ipos != req_root_pos: continue
                return irow,icand,sfx,derived_pos,label,isfx,ilabel
    return None


def _detect_structure(w):
    """
    Bazadan topilgan so'zning ichki morfologik tarkibini aniqlaydi.
    DB talab etmaydi — faqat affikslar ro'yxati asosida ishlaydi.

    Algoritm:
      1. Suffiks → ildiz topiladi (masalan: abduction → -tion → "abduct")
      2. Ildizdan prefiks ajratiladi (masalan: abduct → ab- → "duct")

    Qaytaradi: (prefix, prefix_label, root, suffix, suffix_pos, suffix_label)
    Masalan: "abduction" → ("ab","uzoqlashtirish","duct","tion","Ot","C←G(-tion:...)")
    """
    # 1-qadam: Suffiksni topamiz (MORPH_RULES, uzundan qisqaga)
    sfx_found = sfx_pos = sfx_lbl = ""
    for sfx, fns, s_pos, s_label in sorted(MORPH_RULES, key=lambda x:-len(x[0])):
        if w.endswith(sfx) and len(w) > len(sfx)+2:
            # Ildiz kandidatini hisoblaymiz
            for fn in fns:
                try:
                    cand = fn(w)
                    if len(cand) >= 2:
                        sfx_found = sfx; sfx_pos = s_pos; sfx_lbl = s_label
                        w = cand  # ildiz (prefiks tekshirish uchun)
                        break
                except: continue
            if sfx_found: break

    # 2-qadam: Ildizdan prefiksni ajratamiz
    pfx_found = pfx_lbl = ""
    for pfx, lbl in EN_PREFIXES:
        if w.startswith(pfx) and len(w) > len(pfx)+2:
            pfx_found = pfx; pfx_lbl = lbl
            w = w[len(pfx):]  # toza ildiz
            break

    root = w
    return pfx_found, pfx_lbl, root, sfx_found, sfx_pos, sfx_lbl


# ═══════════════════════════════════════════════════════════════════
#  FORMAL MODELNI OLDINDAN QURISH + KONTEKST ASOSIDA MA'NO TANLASH
# ═══════════════════════════════════════════════════════════════════
def build_formal_model(word):
    """
    So'zning FORMAL MODELINI KKT belgilari asosida SURFACE SHAKLIDAN quradi —
    so'z lug'atda to'g'ridan-to'g'ri topilgan-topilmaganidan qat'i nazar
    (o'ngdan-chapga parsing: prefiks/ildiz/suffiks + BM_en_w'dan vaznlar).
    Bu:
      (a) ko'p ma'noli so'zni turkum vazni bo'yicha farqlashda,
      (b) BM bazasida mos model topilmasa — parsing orqali YANGISINI qurishda
    ishlatiladi.

    Qaytaradi: {"pos","weight","kkt_symbol","sfx","pfx","root"}
    yoki hech qanday model qurib bo'lmasa None.
    """
    w = word.strip().lower()
    res = _try_suffix_chain(w)
    pfx=""; sfx=""; derived_pos=None; cand=w; inner_sfx=None
    if res:
        row,cand,sfx,derived_pos,sfx_label,inner_sfx,_ilabel = res
    else:
        for p,plbl in EN_PREFIXES:
            if not w.startswith(p) or len(w)<=len(p)+2: continue
            stem=w[len(p):]
            r2=_try_suffix(stem)
            if r2:
                _row2,cand2,sfx2,dp2,_lbl2 = r2
                pfx,cand,sfx,derived_pos = p,cand2,sfx2,dp2; break
            stem_row=db_lookup(stem)
            if stem_row:
                pfx,cand,derived_pos = p,stem,stem_row[2]; break
    if not derived_pos:
        direct=db_lookup(w)          # so'zning o'zi lug'atda bo'lsa — o'sha turkum
        if direct: derived_pos=direct[2]
    if not derived_pos:
        return None
    # 13/14-qadam: BM_en_w'dan MODEL QIDIRISH; topilmasa — KKT asosida yaratish
    pos_m = bm_get_or_create_pos_model(DB_BM_EN, derived_pos)
    sfx_w = 0.0
    if sfx:
        sm = bm_get_or_create_affix_model(DB_BM_EN, sfx, EN_AFF_V3.get(sfx,("A1",0))[0])
        sfx_w += sm["weight"] if sm else 0.0
    if inner_sfx:
        im = bm_get_or_create_affix_model(DB_BM_EN, inner_sfx, EN_AFF_V3.get(inner_sfx,("A1",0))[0])
        sfx_w += im["weight"] if im else 0.0
    pfx_w = 0.01 if pfx else 0.0
    return {"pos":derived_pos,"weight":pos_m["weight"]+sfx_w+pfx_w,
            "kkt_symbol":pos_m["kkt_symbol"],"sfx":sfx,"pfx":pfx,"root":cand}

# Grammatik kontekst: oldingi so'z turkumidan keyin qaysi turkum ko'proq
# ehtimolli (ibora ichida "yonidagi so'zga qarab" tarjima qilish uchun).
POS_CONTEXT_NEXT = {
    "Olmosh":     {"Ot":1.0, "Sifat":0.55},
    "Predlog":    {"Ot":1.0, "Olmosh":0.85, "Sifat":0.5},
    "Son":        {"Ot":1.0},
    "Bog'lovchi": {"Ot":0.7, "Fe'l":0.7, "Sifat":0.65, "Ravish":0.6},
}
INFINITIVE_MARKERS = {"to","will","would","can","could","may","might","must","shall","should"}

def select_meaning_contextual(rows, word, prev_pos=None, prev_raw=None):
    """
    Ko'p ma'noli so'zni tanlashning ASOSIY funksiyasi — ikki bosqichda:
      1) KONTEKST: oldingi so'z (uning turkumi yoki "to" kabi infinitiv
         belgisi) qaysi turkumni kutishini POS_CONTEXT_NEXT jadvali orqali
         tekshiradi — mos turkumdagi ma'no topilsa, o'sha tanlanadi.
      2) VAZN FARQI: kontekst hal qilmasa — so'zning SURFACE shaklidan
         build_formal_model() orqali qurilgan formal model vazni bilan har
         bir ma'no turkumining BM_en_w vazni orasidagi FARQI eng kichkina
         bo'lgan ma'no tanlanadi.
    Ikkalasi ham hal qilmasa (masalan hamma ma'no bir xil turkumda —
    "bank": Ot/Ot/Ot) — None qaytaradi, chaqiruvchi psb_select_meaning'ga
    (yoki birinchi ma'noga) o'tadi.
    """
    if not rows: return None
    distinct_pos = {r[3] for r in rows}
    if len(distinct_pos) <= 1:
        return None                       # turkum bo'yicha farqlab bo'lmaydi

    # 1) KONTEKST orqali
    expect_pos = None
    if prev_raw and prev_raw.lower() in INFINITIVE_MARKERS:
        expect_pos = "Fe'l"
    elif prev_pos and prev_pos in POS_CONTEXT_NEXT:
        prefs = POS_CONTEXT_NEXT[prev_pos]
        best_p=None; best_s=-1
        for p in distinct_pos:
            s = prefs.get(p, 0.0)
            if s > best_s: best_s, best_p = s, p
        if best_s > 0: expect_pos = best_p
    if expect_pos:
        for r in rows:
            if r[3] == expect_pos: return r

    # 2) VAZN FARQI orqali (formal model surface shakldan qurilib solishtiriladi)
    fm = build_formal_model(word)
    if not fm: return None
    target_w = fm["weight"]
    best=None; best_diff=None
    for r in rows:
        pm = bm_get_or_create_pos_model(DB_BM_EN, r[3])
        diff = abs(pm["weight"] - target_w)
        if best_diff is None or diff < best_diff:
            best, best_diff = r, diff
    return best


# ═══════════════════════════════════════════════════════════════════
#  SSM METRIKASI + MDB_uz_w  —  BLOK-SXEMANING 8-13-QADAMLARI
#  (M. Xakimov, "Metric for evaluating mathematical models natural
#   language words for machine translation", IJIRSS 8(6) 2025, 2430-2447,
#   DOI:10.53894/ijirss.v8i6.10125 — formula (1)-(6) asosida)
# ═══════════════════════════════════════════════════════════════════
DB_MDB_UZ = os.path.join(SCRIPT_DIR, "MDB_uz_w.db")
ALL_DBS.append(DB_MDB_UZ)

_SSM_ROOT_SYMBOLS = {"C", "P", "G", "M", "N", "F", "K", "D", "Y", "U", "L"}
# MUHIM TUZATISH (KKT spec, vazn jadvali: "Yordamchi so'z turkumlari (U, L) –
# 0.07"): U (yuklama) va L (modal so'zlar) — spec bo'yicha alohida SO'Z
# TURKUMI belgilari, ya'ni ildiz. Ilgari ro'yxatda yo'q edi — "may"/"might"
# (CH2 modeli "L(L) = $[i,1-h2]Li", SSM=0.989) "root topilmadi" deb
# hisoblanib, lug'atdagi to'g'ri "mumkin" MDB_uz_w'dagi tasodifiy
# "Ajratib ko'rsatmoq" bilan almashtirilardi (spec 2.51/2.52). Quyidagi
# D/Y tuzatishi bilan bir xil turdagi xato.
# MUHIM TUZATISH: "D" (Predlog) va "Y" (Bog'lovchi) ilgari bu ro'yxatda
# yo'q edi. Natijada _ssm_is_root() predlog/bog'lovchi so'zlar uchun
# doim False qaytarardi -> evaluate_and_refine_ssm() ularni HAR DOIM
# "root topilmadi" deb hisoblab, 10-QADAM (MDB_uz_w'dan eng yaqin vaznli
# nomzod qidirish) orqali TARJIMANI ALMASHTIRARDI. Predlog/bog'lovchilar
# soni cheklangan yopiq turkum bo'lib, ularning ko'pchiligi BIR XIL V2
# vazniga ega (masalan barcha oddiy predloglar 0.40) — shu sabab bu
# "yaqin nomzod" qidiruvi ko'pincha BUTUNLAY BOSHQA (lekin bir xil
# vaznli) predlog/bog'lovchi bilan almashtirib qo'yardi (masalan "from"
# so'zi "dan" o'rniga "with"ning tarjimasi "bilan" bilan almashardi).
# Bu esa ibora qayta tartiblash (PP/ibora aniqlash) natijasini ham
# buzardi. "D"/"Y" endi "root" sifatida tan olingani uchun bunday
# noto'g'ri almashtirish endi yuz bermaydi.
_SSM_TOKEN_RE = re.compile(r"^([A-Z]+[0-9]*)")


def _ssm_split_segments(mm):
    """MM satrini '⊕' bo'yicha segmentlarga ajratadi."""
    rhs = mm.split("=", 1)[1] if "=" in mm else mm
    parts = re.split(r"⊕", rhs)
    segs = []
    for p in parts:
        p = p.strip()
        if not p: continue
        optional = p.startswith("↓")
        p_clean = p.lstrip("↓").strip()
        has_dollar = "$" in p_clean
        after_bracket = re.sub(r"\$\[[^\]]*\]", "", p_clean).strip()
        is_paren = "(" in after_bracket
        m = _SSM_TOKEN_RE.match(after_bracket)
        base_symbol = m.group(1) if m else after_bracket[:1]
        segs.append({"raw":p, "optional":optional, "has_dollar":has_dollar,
                     "base":base_symbol, "is_paren":is_paren})
    return segs


def _ssm_is_root(seg):
    if seg["base"] == "K" and seg["is_paren"]:
        return True
    if not seg["is_paren"] and seg["base"].rstrip("0123456789") in _SSM_ROOT_SYMBOLS:
        return True
    return False


def ssm_score(mm, language="uz"):
    """
    SSM = (Mor+Sq+Mav+Qb+Muk)/Count - Penalty  — formula (1).
    Qaytaradi: dict {mor,sq,mav,qb,muk,count,penalty,ssm,grade,root_found}.
    DIQQAT: maqolaning o'z Jadval 2'sida bir xil model satri (Model-1/9)
    turli natija bergani kabi ichki nomuvofiqliklar bor; shu sabab bu
    funksiya formulani MATNDA YOZILGANIDEK amalga oshiradi. PENALTY qismi
    (Qs, alpha=0.055/0.015) maqolaning barcha o'zbekcha jadval qiymatlari
    bilan sinovdan o'tkazilib, ANIQ mos kelgani tasdiqlangan.
    """
    agglutinative = (language.lower() == "uz")
    segs = _ssm_split_segments(mm)
    if not segs:
        return {"mor":0,"sq":0,"mav":0,"qb":0,"muk":0,"count":0,
                "penalty":0.0,"ssm":0.0,"grade":"Qoniqarsiz","root_found":False}

    mor = 1.0 if any(_ssm_is_root(s) for s in segs) else 0.0

    additions = [s for s in segs if not _ssm_is_root(s)]
    n_add = len(additions)
    if n_add == 0:
        sq = 0.0
    elif agglutinative:
        sq = sum(1.00 + 0.05*k for k in range(n_add)) / n_add
    else:
        sq = 0.65

    m = sum(1 for s in segs if s["has_dollar"])
    if m == 0:
        mav, qb = 1.0, 1.0
    else:
        mav = (1.00 + 1.05*m) / (m+1)
        qb = sum(1.00 + 0.05*k for k in range(1, m+1)) / m

    roots = [s for s in segs if _ssm_is_root(s)]
    muk = float(max(1, len(roots)))

    qs = n_add
    alpha = 0.055 if agglutinative else 0.015
    computed = alpha * max(0, qs-3)
    penalty = computed if computed > 0 else (0.03 if agglutinative else 0.015)

    params = [mor, sq, mav, qb, muk]
    count = sum(1 for p in params if p != 0)
    ssm_final = (sum(params)/count - penalty) if count else 0.0
    ssm_final = max(0.0, min(1.0, ssm_final))

    if ssm_final >= 0.90: grade = "Aniq"
    elif ssm_final >= 0.80: grade = "Yaxshi"
    elif ssm_final >= 0.75: grade = "O'rtacha"
    elif ssm_final >= 0.65: grade = "Zaif"
    else: grade = "Qoniqarsiz"

    return {"mor":round(mor,5),"sq":round(sq,5),"mav":round(mav,5),
            "qb":round(qb,5),"muk":round(muk,5),"count":count,
            "penalty":round(penalty,5),"ssm":round(ssm_final,5),
            "grade":grade,"root_found":mor>0}


def _create_mdb_tables(conn):
    """MDB_uz_w — EVIX uchun alternativ rasmiy model nomzodlari bazasi
    (10-qadam: EVX vazniga yaqin qiymat bo'yicha qidirish uchun)."""
    conn.execute("""CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uz_word TEXT NOT NULL, pos TEXT NOT NULL,
        mm TEXT NOT NULL, weight REAL NOT NULL,
        source TEXT DEFAULT 'auto')""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mdb_pos_w ON candidates(pos,weight)")
    conn.commit()


def mdb_seed_if_empty():
    """MDB_uz_w bo'sh bo'lsa, UB_uz_w + BM_uz_w'dagi mavjud so'zlardan
    (POS vazni asosida) boshlang'ich nomzodlar bilan to'ldiradi."""
    conn = sqlite3.connect(DB_MDB_UZ); _create_mdb_tables(conn)
    n = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    if n > 0:
        conn.close(); return 0
    try:
        src = sqlite3.connect(DB_UB_UZ)
        rows = src.execute("SELECT DISTINCT headword,pos,formal_model FROM words "
                            "WHERE pos IS NOT NULL").fetchall()
        src.close()
    except Exception:
        rows = []
    added = 0
    for headword, pos, fm in rows:
        pos = pos or "Ot"
        pos_m = bm_get_or_create_pos_model(DB_BM_UZ, pos)
        mm = fm if fm else f"{pos_m['kkt_symbol']}(root) = $[i,1-h]{pos_m['kkt_symbol']}i"
        w = ssm_score(mm, "uz")  # faqat mm to'g'ri ishlashini tekshirish uchun emas, vazn uchun kkt_uz ishlatiladi pastda
        conn.execute("INSERT INTO candidates(uz_word,pos,mm,weight,source) VALUES(?,?,?,?,?)",
                     (headword, pos, mm, pos_m["weight"], "bootstrap"))
        added += 1
    conn.commit(); conn.close()
    return added


def mdb_nearest(target_weight, pos=None, thresh=0.23):
    """10-qadam: |farq|<=thresh ichidagi eng yaqin nomzodni qaytaradi."""
    if not os.path.exists(DB_MDB_UZ):
        return None
    conn = sqlite3.connect(DB_MDB_UZ)
    try:
        if pos:
            rows = conn.execute("SELECT uz_word,pos,mm,weight FROM candidates WHERE pos=?", (pos,)).fetchall()
        else:
            rows = conn.execute("SELECT uz_word,pos,mm,weight FROM candidates").fetchall()
    except Exception:
        rows = []
    conn.close()
    best = None
    for uz_word, r_pos, mm, weight in rows:
        diff = abs(weight - target_weight)
        if best is None or diff < best["diff"]:
            best = {"uz_word":uz_word,"pos":r_pos,"mm":mm,"weight":weight,"diff":diff}
    if best and best["diff"] <= thresh:
        return best
    return None


def qm_uz_try_alternative_suffix(analysis, target_weight):
    """
    11-12-qadam: EVIXni «QM_uz_w» bazasidan YANGI (hozirgi ishlatilganidan
    BOSHQA) qo'shimcha bilan, EVX vazniga (target_weight) ENG YAQIN
    natija beradigan tarzda BIR MARTA qayta tanlaydi.
    Qaytaradi: {"uz":yangi_soz,"total":yangi_vazn,"suffix":...} yoki None
    (agar mos POS uchun QM_uz_w'da boshqa hech qanday qo'shimcha topilmasa).
    """
    pos = analysis.get("pos") or "Ot"
    uz = analysis.get("uz") or ""
    us, uk, uv, root = _detect_uz_affix(uz)
    if not root:
        return None
    pos_m = bm_get_or_create_pos_model(DB_BM_UZ, pos)
    v2 = pos_m["weight"]
    try:
        conn = sqlite3.connect(DB_QM_UZ)
        rows = conn.execute(
            "SELECT value,kkt_symbol,weight FROM affixes "
            "WHERE pos=? AND weight IS NOT NULL", (pos,)
        ).fetchall()
        conn.close()
    except Exception:
        rows = []
    best = None
    for value, kkt_symbol, weight in rows:
        suffix_text = value.lstrip("-").rstrip("-")
        if not suffix_text or suffix_text == us:
            continue                      # hozirgi qo'shimchaning o'zi emas — "yangi" bo'lishi shart
        cand_total = v2 + weight
        diff = abs(target_weight - cand_total)
        if best is None or diff < best["diff"]:
            best = {"suffix":suffix_text, "kkt_symbol":kkt_symbol, "weight":weight,
                     "uz": root + suffix_text, "total": cand_total, "diff": diff}
    return best


def evaluate_and_refine_ssm(analysis, quality_threshold=0.80):
    """
    Blok-sxemaning 8→9→10→11→12→13-QADAMLARI:
      8:  SSM metrikasi asosida EVIX (o'zbek) rasmiy modeli baholanadi.
      9:  SSM >= 0.80 ("yaxshi"+) -> quality_flag='green', o'zgarishsiz.
          Aks holda -> 'red' (pastda 'orange'ga ko'tarilishga harakat qilinadi).
      10: MDB_uz_w'dan |farq|<=0.23 ichida eng yaqin nomzod izlanadi.
          Topilsa -> shu nomzod qabul qilinadi (quality_flag='orange').
      11: Topilmasa va |farq|<0.3 bo'lsa -> QM_uz_w'dan YANGI qo'shimcha
          bilan BIR MARTA qayta sintez qilishga ruxsat beriladi
          (qm_uz_try_alternative_suffix orqali).
      12: Qayta sintez qilingan so'zning yangi umumiy vazni hisoblanadi.
      13: |EVX-yangi_EVIX| < 0.26 shartimi tekshiriladi — bajarilsa qabul
          qilinadi (quality_flag='orange'), aks holda asl natija 'red'
          holida qoldiriladi.
    `analysis` lug'atiga qo'shiladigan yangi kalitlar:
      ssm_uz (float), ssm_grade (str), quality_flag ('green'|'orange'|'red'),
      mdb_used (bool), mdb_diff (float|None), resuffixed (bool)
    """
    analysis.setdefault("quality_flag", "green")
    analysis.setdefault("mdb_used", False)
    analysis.setdefault("mdb_diff", None)
    analysis.setdefault("resuffixed", False)
    if not analysis.get("found"):
        analysis["ssm_uz"] = 0.0; analysis["ssm_grade"] = "—"
        analysis["quality_flag"] = "red"
        return analysis

    try:
        mdb_seed_if_empty()
        uz_mm = kkt_uz(analysis)["mm"]
        res = ssm_score(uz_mm, "uz")
        analysis["ssm_uz"] = res["ssm"]; analysis["ssm_grade"] = res["grade"]

        if res["root_found"] and res["ssm"] >= quality_threshold:
            analysis["quality_flag"] = "green"
            return analysis

        analysis["quality_flag"] = "red"
        en_total = kkt_en(analysis)["total"]
        uz_total = kkt_uz(analysis)["total"]

        # ── 10-QADAM: MDB_uz_w'dan |farq|<=0.23 qidirish ──
        cand = mdb_nearest(en_total, pos=analysis.get("pos"), thresh=0.23)
        if cand:
            analysis["uz"] = cand["uz_word"]
            analysis["method"] = analysis.get("method","") + " → MDB_uz_w[|farq|≤0.23]"
            analysis["quality_flag"] = "orange"
            analysis["mdb_used"] = True
            analysis["mdb_diff"] = round(cand["diff"], 5)
            return analysis

        # ── 11-QADAM: |farq|<0.3 -> QM_uz_w orqali bir martalik qayta urinish ──
        diff = abs(en_total - uz_total)
        if diff < 0.3:
            refined = qm_uz_try_alternative_suffix(analysis, en_total)
            if refined:
                # ── 12-QADAM: yangi vazn allaqachon refined["total"] da ──
                # ── 13-QADAM: yakuniy farqni tekshirish ──
                final_diff = abs(en_total - refined["total"])
                if final_diff < 0.26:
                    analysis["uz"] = refined["uz"]
                    analysis["method"] = analysis.get("method","") + \
                        f" → QM_uz_w[qayta urinish: -{refined['suffix']}, |farq|<0.26]"
                    analysis["quality_flag"] = "orange"
                    analysis["mdb_diff"] = round(final_diff, 5)
                    analysis["resuffixed"] = True
    except Exception as e:
        # SSM/MDB bosqichida kutilmagan xatolik bo'lsa ham, tarjimaning
        # o'zi (asosiy natija) HECH QACHON yo'qolmasligi kerak — faqat
        # sifat belgisi qo'yilmay qoladi.
        analysis.setdefault("ssm_uz", 0.0)
        analysis.setdefault("ssm_grade", "—")
        analysis["quality_flag"] = analysis.get("quality_flag","green")
        print(f"  [SSM/MDB ogohlantirish] {analysis.get('word','')}: {e}")
    return analysis


def _smart_parse_core(word, prev_pos=None, prev_raw=None):
    """
    KKT 21-QADAMLI RASMIY ALGORITM (blok-sxema asosida, to'liq bazadan ishlaydi).

      4-6-qadam:   UB_en_w'dan TO'G'RIDAN-TO'G'RI (ID orqali) qidirish;
                   ko'p ma'noli bo'lsa — barcha ma'nolar yig'iladi, PSB
                   asosida ustuvori tanlanadi.
      7-qadam:     Topilmasa — o'ngdan-chapga parsinglash boshlanadi.
      8-9-qadam:   QM_en_w'dan suffiks qidiriladi/tasdiqlanadi (topilmasa —
                   yangisi sifatida bazaga yoziladi).
      10-11-qadam: QM_en_w'dan prefiks qidiriladi/tasdiqlanadi.
      12-qadam:    O'zak ajratiladi va UB_en_w'dan qidiriladi.
      13-14-qadam: BM_en_w'dan asos so'zning formal modeli (POS+affiks
                   vaznlari) qidiriladi; topilmasa — KKT qoidalari asosida
                   yangisi yaratilib BM_en_w'ga yoziladi.
      15-qadam:    Umumiy formal model vazni hisoblanadi.
      16-qadam:    BM_uz_w'dan mos formal model qidiriladi.
      17-qadam:    UB_uz_w'dan mos o'zak ID orqali qidiriladi.
      18-qadam:    QM_uz_w'dan mos qo'shimcha ID orqali qidiriladi (topilmasa
                   — statik KKT-jadval zaxira sifatida ishlatiladi).
      19-qadam:    EVIX (o'zbekcha so'z) sintez qilinadi.
      20-qadam:    Ko'p ma'nolilik yakuniy natijada ham saqlanadi.

    Qaytaradi: {word, root, prefix, suffix, pos, uz, conf, found, meanings, ...}
    """
    w = word.strip().lower()
    empty = {
        "word":w,"root":w,"prefix":"","prefix_label":"","suffix":"",
        "conf":0.0,"uz":None,"pos":None,"pos_label":"Topilmadi",
        "method":"Topilmadi","found":False,"auto_saved":False,"meanings":[],
        "bm_pos_kkt_en":"C","bm_pos_v2_en":0.0,"bm_sfx_kkt_en":"","bm_sfx_v3_en":0.0,
        "bm_pfx_kkt_en":"","bm_pfx_v3_en":0.0,
        "bm_pos_kkt_uz":"C","bm_pos_v2_uz":0.0,
    }

    # ══ 4-5-6-QADAM: UB_en_w'dan TO'G'RIDAN-TO'G'RI (ID orqali) qidirish ══
    rows = db_lookup_all(w)
    # MUHIM: agar so'zning BARCHA yozuvlari avval avtomatik keshlangan bo'lsa
    # (source='auto' — ya'ni asl lug'at emas, balki oldingi tarjimada
    # o'zi hosil qilingan shakl) VA so'z hozir ham morfologik ajratilishi
    # mumkin bo'lsa — to'g'ridan-to'g'ri natijani EMAS, balki har doim yangi
    # (7-12-qadam) ajratishni ishlatamiz. Aks holda "books" bir marta
    # keshlangandan keyin doim "affikssiz" ko'rinib qolaveradi.
    if rows and all(r[4]=="auto" for r in rows) and _try_suffix_chain(w):
        rows = []
    if rows:
        chosen = (select_meaning_contextual(rows, w, prev_pos, prev_raw)   # kontekst + vazn farqi
                  or psb_select_meaning(rows))                              # 6-qadam zaxira: PSB/birinchi
        _id,hw,tr,pos,src,fm = chosen
        pos_en = bm_get_or_create_pos_model(DB_BM_EN,pos)   # 13/14-qadam (asos so'z)
        pos_uz = bm_get_or_create_pos_model(DB_BM_UZ,pos)   # 16-qadam
        uz_row = db_lookup_by_id(DB_UB_UZ,_id)              # 17-qadam — ID orqali
        uz_final = uz_row[1] if uz_row else tr
        n=len(rows)
        return {**empty,"conf":0.999,"uz":uz_final,"pos":pos,"root":w,
                "pos_label": f"To'g'ridan (ID:{_id}, {n} ma'no)" if n>1 else f"To'g'ridan (ID:{_id})",
                "method":"UB_en_w[ID]→UB_uz_w[ID]",
                "meanings":[{"id":r[0],"uz":r[2],"pos":r[3]} for r in rows],   # 20-qadam
                "bm_pos_kkt_en":pos_en["kkt_symbol"],"bm_pos_v2_en":pos_en["weight"],
                "bm_pos_kkt_uz":pos_uz["kkt_symbol"],"bm_pos_v2_uz":pos_uz["weight"],
                "found":True}

    # ── Egalik 's (X3) — bazadagi o'zakka qo'shilgan alohida holat ──
    if w.endswith("'s"):
        wc=w[:-2]; rows=db_lookup_all(wc)
        if rows:
            chosen=psb_select_meaning(rows); _id,hw,tr,pos,src,fm=chosen
            qm_confirm_or_add(DB_QM_EN,"'s",pos,is_prefix=False,kkt_symbol_hint="X3")
            uz=make_uzbek(tr,"'s"); saved=db_insert(w,uz,pos,"auto")
            pos_en=bm_get_or_create_pos_model(DB_BM_EN,pos); pos_uz=bm_get_or_create_pos_model(DB_BM_UZ,pos)
            return {**empty,"root":wc,"suffix":"'s","conf":0.970,
                    "uz":uz,"pos":pos,"pos_label":"Egalik(X3)","method":"QM_en_w:'s→X3",
                    "found":True,"auto_saved":saved,"meanings":[{"id":r[0],"uz":r[2],"pos":r[3]} for r in rows],
                    "bm_pos_kkt_en":pos_en["kkt_symbol"],"bm_pos_v2_en":pos_en["weight"],
                    "bm_pos_kkt_uz":pos_uz["kkt_symbol"],"bm_pos_v2_uz":pos_uz["weight"]}

    # ══ 7-QADAM: O'ngdan-chapga parsinglash boshlanadi ══
    # 8-9-qadam: suffiks (MORPH_RULES imlo qoidalari + QM_en_w tasdig'i/ro'yxati)
    # Ikki qatlamli qo'shimchalar ham qo'llab-quvvatlanadi (work+er+s).
    pfx=""; pfx_lbl=""; sfx=""; sfx_label=""; derived_pos=None; cand=w; root_rows=[]
    inner_sfx=None; inner_label=None
    res = _try_suffix_chain(w)
    if res:
        row,cand,sfx,derived_pos,sfx_label,inner_sfx,inner_label = res
        qm_confirm_or_add(DB_QM_EN, sfx, derived_pos, is_prefix=False,
                           kkt_symbol_hint=EN_AFF_V3.get(sfx,("A1",0))[0])
        if inner_sfx:
            qm_confirm_or_add(DB_QM_EN, inner_sfx, row[2], is_prefix=False,
                               kkt_symbol_hint=EN_AFF_V3.get(inner_sfx,("A1",0))[0])
        root_rows = db_lookup_all(cand)

    if not root_rows:
        # 10-11-qadam: prefiks (QM_en_w tasdig'i bilan)
        for p,plbl in EN_PREFIXES:
            if not w.startswith(p) or len(w)<=len(p)+2: continue
            stem=w[len(p):]
            r2=_try_suffix(stem)
            if r2:
                row2,cand2,sfx2,dp2,lbl2 = r2
                rr=db_lookup_all(cand2)
                if rr:
                    pfx,pfx_lbl,cand,sfx,derived_pos,sfx_label = p,plbl,cand2,sfx2,dp2,lbl2
                    root_rows=rr
                    qm_confirm_or_add(DB_QM_EN,p,dp2,is_prefix=True)
                    qm_confirm_or_add(DB_QM_EN,sfx2,dp2,is_prefix=False,
                                       kkt_symbol_hint=EN_AFF_V3.get(sfx2,("A1",0))[0])
                    break
            rr=db_lookup_all(stem)
            if rr:
                pfx,pfx_lbl,cand,root_rows = p,plbl,stem,rr
                qm_confirm_or_add(DB_QM_EN,p,rr[0][3],is_prefix=True)
                break

    # ── 12-qadamdan keyin ham topilmasa: NLTK lemmatizatsiya (qo'shimcha zaxira,
    #    nomuntazam shakllar — went, children — uchun) ──
    if not root_rows:
        _nltk_pos_map={"n":"Ot","v":"Fe'l","a":"Sifat","s":"Sifat","r":"Ravish"}
        if USE_LEMMA and _lemmatizer:
            for pt in ("n","v","a","r","s"):
                lemma=_lemmatizer.lemmatize(w,pt)
                if lemma!=w:
                    rr=db_lookup_all(lemma)
                    if rr:
                        sfx=w[len(lemma):] if w.startswith(lemma) else ""
                        derived_pos=_nltk_pos_map.get(pt)
                        cand=lemma; root_rows=rr
                        if sfx: qm_confirm_or_add(DB_QM_EN,sfx,derived_pos,is_prefix=False)
                        break
    if not root_rows:
        return empty

    chosen = psb_select_meaning(root_rows)              # 6/20-qadam (o'zak uchun)
    _id,hw,tr,pos_db,src,fm = chosen
    pos = derived_pos or pos_db

    # ══ 13-14-QADAM: BM_en_w'dan formal model qidirish / yaratish ══
    pos_m_en = bm_get_or_create_pos_model(DB_BM_EN, pos)
    # Ayrim qo'shimchalar (masalan "-er"/"-or") ikki xil ma'noda bo'ladi:
    # qiyosiy sifat (P1_SF: bigger) yoki ish bajaruvchi ot (C_A1: worker).
    # Matn bir xil bo'lgani uchun BM_en_w'da chalkashmasligi uchun turkum
    # bilan birga noyob kalit sifatida saqlaymiz.
    AGENTIVE_ER_SYM = {"er":"C_A1","or":"C_A1"}
    # Xuddi shunday "-s": Ot ko'plik (X) yoki Fe'l 3-shaxs birlik (spec 2.37).
    # Fe'l ma'nosi alohida kalit bilan, kodning fe'l zamon affikslari uchun
    # ishlatadigan belgisi (EN_AFF_V3: ing/ed/ied → G_A1) bilan saqlanadi.
    verb_3sg = (sfx == "s" and pos == "Fe'l")
    if sfx in AGENTIVE_ER_SYM and pos=="Ot":
        sfx_bm_key = sfx+"#Ot"; default_sym = AGENTIVE_ER_SYM[sfx]
    elif verb_3sg:
        sfx_bm_key = "s#Fe'l"; default_sym = "G_A1"
    else:
        sfx_bm_key = sfx; default_sym = EN_AFF_V3.get(sfx,("A1",0))[0]
    sfx_m_en = bm_get_or_create_affix_model(DB_BM_EN, sfx_bm_key, default_sym) if sfx else None
    pfx_m_en = bm_get_or_create_affix_model(DB_BM_EN, pfx, "T", 0.01) if pfx else None
    inner_sfx_bm_key = (inner_sfx+"#Ot") if (inner_sfx in AGENTIVE_ER_SYM) else inner_sfx
    inner_default_sym = AGENTIVE_ER_SYM.get(inner_sfx, EN_AFF_V3.get(inner_sfx,("A1",0))[0]) if inner_sfx else None
    inner_m_en = bm_get_or_create_affix_model(DB_BM_EN, inner_sfx_bm_key, inner_default_sym) if inner_sfx else None

    # ══ 15-QADAM: umumiy formal model vazni ══
    v2_en = pos_m_en["weight"]
    v3_en = (sfx_m_en["weight"] if sfx_m_en else 0.0) + (pfx_m_en["weight"] if pfx_m_en else 0.0) \
            + (inner_m_en["weight"] if inner_m_en else 0.0)

    # ══ 16-QADAM: BM_uz_w'dan mos formal model ══
    pos_m_uz = bm_get_or_create_pos_model(DB_BM_UZ, pos)

    # ══ 17-QADAM: UB_uz_w'dan mos o'zakni ID orqali qidirish ══
    uz_row = db_lookup_by_id(DB_UB_UZ, _id)
    uz_root_raw = uz_row[1] if uz_row else tr

    # ══ 18-QADAM: QM_uz_w'dan mos qo'shimchani ID orqali qidirish ══
    # (ichki qo'shimcha — masalan "work+ER+s" dagi "-er" — avval o'zakka
    #  qo'shiladi, so'ng tashqi qo'shimcha ustiga qo'shiladi)
    if inner_sfx and inner_m_en and not (pos=="Sifat" and inner_sfx in ("er","est","ier","iest")):
        inner_qm_row = qm_confirm_or_add(DB_QM_EN, inner_sfx, pos, is_prefix=False,
                                          kkt_symbol_hint=inner_default_sym)
        inner_uz_aff = qm_uz_equivalent(inner_qm_row[0], pos) if inner_qm_row else None
        if inner_uz_aff:
            uz_root_raw = uz_stem(uz_root_raw) + inner_uz_aff[1].lstrip("-")
        else:
            uz_root_raw = make_uzbek(uz_root_raw, inner_sfx)

    uz_suffix_text = ""
    _DEGREE_SFX = {"er","est","ier","iest"}  # qiyosiy/orttirma daraja — ID moslash ishonchsiz, doim zaxira jadval ishlatiladi
    # Fe'l "-s" uchun ham ID moslash ishlatilmaydi: QM_en_w'dagi "-s" yozuvi
    # ko'plik affiksi, uning ID-jufti fe'l shaklini bermaydi.
    if sfx and sfx_m_en and sfx not in _DEGREE_SFX and not verb_3sg:
        qm_en_row = qm_confirm_or_add(DB_QM_EN, sfx, pos, is_prefix=False,
                                       kkt_symbol_hint=EN_AFF_V3.get(sfx,("A1",0))[0])
        uz_aff = qm_uz_equivalent(qm_en_row[0], pos) if qm_en_row else None
        if uz_aff: uz_suffix_text = uz_aff[1].lstrip("-")

    # ══ 19-QADAM: EVIX (o'zbekcha so'z) sintez qilish ══
    if uz_suffix_text:
        uz = uz_stem(uz_root_raw) + uz_suffix_text          # bazadan (QM_uz_w)
        method_tag = "QM_en_w→QM_uz_w[ID]"
    elif sfx:
        uz = make_uzbek(uz_root_raw, sfx, pos)               # zaxira: statik KKT jadval
        method_tag = "QM_en_w + zaxira-jadval"
    else:
        uz = uz_root_raw
        method_tag = "UB_en_w→UB_uz_w[ID]"

    if pfx:
        tmpl = EN_PREFIX_UZ.get(pfx, pfx+" ...")
        uz = tmpl.replace("...", uz) if "..." in tmpl else tmpl+" "+uz

    saved = db_insert(w, uz, pos, "auto")
    kkt_en_sym = pos_m_en["kkt_symbol"]
    skkt_en = sfx_m_en["kkt_symbol"] if sfx_m_en else ""
    ikkt_en = inner_m_en["kkt_symbol"] if inner_m_en else ""
    pkkt_en = "T" if pfx else ""
    display_sfx = f"{inner_sfx}+{sfx}" if inner_sfx else sfx
    label = (f"T+{sfx_label}" if (pfx and sfx_label) else sfx_label) if sfx_label else \
            ("T+Ildiz" if pfx else "Ildiz")
    if inner_label: label = f"{inner_label}+{label}"
    sym_parts = [x for x in (pkkt_en,kkt_en_sym,ikkt_en,skkt_en) if x]

    return {**empty,"root":cand,"prefix":pfx,"prefix_label":pfx_lbl,"suffix":display_sfx,
            "conf":0.93 if not pfx else 0.895,
            "uz":uz,"pos":pos,"pos_label":label,
            "method":f"{method_tag}: {kkt_en_sym}({','.join(sym_parts)})",
            "found":True,"auto_saved":saved,
            "meanings":[{"id":r[0],"uz":r[2],"pos":r[3]} for r in root_rows],
            "bm_pos_kkt_en":kkt_en_sym,"bm_pos_v2_en":v2_en,
            "bm_sfx_kkt_en":skkt_en,"bm_sfx_v3_en":(sfx_m_en["weight"] if sfx_m_en else 0.0)+(inner_m_en["weight"] if inner_m_en else 0.0),
            "bm_pfx_kkt_en":pkkt_en,"bm_pfx_v3_en":(pfx_m_en["weight"] if pfx_m_en else 0.0),
            "bm_pos_kkt_uz":pos_m_uz["kkt_symbol"],"bm_pos_v2_uz":pos_m_uz["weight"]}


def smart_parse(word, prev_pos=None, prev_raw=None):
    """
    _smart_parse_core() (21-qadamli asosiy tahlil) natijasini oladi va unga
    blok-sxemaning 8-13-QADAMLARINI (SSM baholash + MDB_uz_w orqali qayta
    izlash zanjiri) qo'llaydi. _smart_parse_core ning o'zi o'zgartirilmagan —
    bu qatlam faqat UNING USTIGA qo'shiladi (surgical, xavfsiz integratsiya).
    """
    a = _smart_parse_core(word, prev_pos=prev_pos, prev_raw=prev_raw)
    return evaluate_and_refine_ssm(a)


def parse_sentence(text):
    """Iborani so'zlarga ajratib, HAR BIRINI OLDINGI SO'Z KONTEKSTI bilan
    birga tarjima qiladi (ko'p ma'noli so'zlarni to'g'ri tanlash uchun —
    select_meaning_contextual orqali)."""
    words = re.findall(r"[a-zA-Z']+", text)
    results=[]; prev_pos=None; prev_raw=None
    for w in words:
        if not w.strip("'"): continue
        a = smart_parse(w, prev_pos=prev_pos, prev_raw=prev_raw)
        results.append(a)
        prev_pos = a.get("pos"); prev_raw = w
    return results


def find_docx():
    for d in SEARCH_DIRS:
        for name in DOCX_CANDIDATES:
            path=os.path.join(d,name)
            if os.path.exists(path): return path
    for d in SEARCH_DIRS:
        try:
            for fname in os.listdir(d):
                if fname.lower().endswith(".docx") and "1500" in fname:
                    return os.path.join(d,fname)
        except: pass
    return None

# ═══════════════════════════════════════════════════════════════════
#  RANGLAR VA SHRIFTLAR — aslidagidek
# ═══════════════════════════════════════════════════════════════════
BG    ="#f0f4f8"; WHITE="#ffffff"; DARK  ="#1a2332"
GREEN ="#00a651"; GRN_DK="#008c44"; TEAL="#00796b"
BLUE  ="#1565c0"; ORANGE="#e65100"; RED_C="#c62828"
GRAY  ="#546e7a"; GRAY_LT="#eceff1"; BORDER="#cfd8dc"
AUTO_C="#ff6f00"; GOLD="#e67e00"
CARD1="#00897b"; CARD2="#0288d1"; CARD3="#7b1fa2"; CARD4="#e65100"
F_LABEL=("Segoe UI",18,"bold"); F_NORMAL=("Segoe UI",18)
F_INPUT=("Segoe UI",18);        F_RESULT=("Segoe UI",18,"bold")
F_MONO =("Consolas",12);        F_MONO_B=("Consolas",12,"bold")
F_SMALL=("Segoe UI",18);        F_CARD_N=("Segoe UI",16,"bold")
F_CARD_L=("Segoe UI",11);       F_BTN  =("Segoe UI",18,"bold")
F_HDR  =("Segoe UI",18,"bold");  F_CARD_NOTE=("Segoe UI",8)

# ═══════════════════════════════════════════════════════════════════
#  GUI YORLIG'I — "aniqlik" chalkashuvi (Faza 2, Ustuvorlik 0.2)
#  Batafsil dalil/audit: reports/faza_2_confidence_audit.md
# ═══════════════════════════════════════════════════════════════════
# DIQQAT: bu ikki matn ilgari "O'rtacha aniqlik"/"Aniqlik" deb nomlangan
# edi va shu nom bilan (hatto dissertatsiya skrinshotlarida ham) TARJIMA
# TO'G'RILIGI sifatida o'qilgan. Aslida bu — `conf` maydonining (qattiq
# kodlangan konstanta: 0.999/0.970/0.93/0.895/0.0, qarang
# `_smart_parse_core`) o'rtachasi/o'zi — so'z qaysi morfologik kod
# yo'lidan o'tganini bildiradi, TARJIMA MAZMUNAN TO'G'RILIGINI EMAS.
# Bu yerda FAQAT NOM/IZOH o'zgartirildi — `avg_c`/`conf` HISOBLASH
# MANTIG'IGA HECH NARSA TEGMAGAN (Qoida: natijaga qarab kod tuzatilmaydi,
# vazn/konstantalar o'zgartirilmaydi). Modul darajasida konstanta
# sifatida chiqarilgan, chunki CI'da (Ubuntu, displeysiz) haqiqiy Tk
# oynasi ochib bo'lmaydi — test shu matnni Tk'siz tekshiradi
# (tests/test_gui_labels.py).
ACC_CARD_LABEL = "Parse ishonchi (morfologik)"
ACC_CARD_NOTE = ("Tarjima to'g'riligini EMAS — so'z lug'at/affiks "
                  "bazasida qanday topilganini bildiradi.")
ACC_INLINE_LABEL = "Parse ishonchi"

if HAS_TK:

    # ═══════════════════════════════════════════════════════════════════
    #  ASOSIY ILOVA — GUI
    # ═══════════════════════════════════════════════════════════════════
    class MTSystem(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Kengayuvchi kirish tili asosida rasmiy modellar bilan kompyuter tarjimasi")
            # Sarlavha panelidan belgichani (qush pati ikonkasini) olib tashlash
            try:
                self.iconbitmap(default='')
            except Exception:
                pass
            # ── Ekranga moslashuvchi oyna o'lchami ──────────────────────
            # Eski kodda oyna doim "1100x700" qilib ochilardi. Agar
            # foydalanuvchi ekrani (yoki Windows displey masshtabi/DPI
            # scaling) buning uchun torroq bo'lsa, oynaning pastki/o'ng
            # qismi ekrandan tashqarida qolib, "yarmi ko'rinmaydi" edi.
            # Endi ekran o'lchami so'raladi va oyna shunga qarab (hamda
            # taskbar uchun joy qoldirib) markazlashtirilib ochiladi.
            self.update_idletasks()
            scr_w = self.winfo_screenwidth(); scr_h = self.winfo_screenheight()
            win_w = min(1100, scr_w - 60)
            win_h = min(700, scr_h - 90)   # taskbar/oyna sarlavhasi uchun joy
            pos_x = max(0, (scr_w - win_w) // 2)
            pos_y = max(0, (scr_h - win_h) // 2)
            self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
            self.minsize(min(920, win_w), min(600, win_h))
            self.configure(bg=BG); self.resizable(True,True)
            self._last_analyses=[]; self._build_ui(); self._show_welcome()

        def report_callback_exception(self, exc, val, tb):
            """Tkinter'ning standart xatti-harakati — tugma bosish, matn
            kiritish va boshqa har qanday GUI hodisasi (callback) ichida
            yuzaga kelgan xatolikni faqat konsolga chop etadi. Bu yerda
            UNI QAYTA ANIQLAB, har qanday shunday xatolik ENDI foydalanuvchiga
            tushunarli xabar oynasi (dialog) sifatida ham ko'rsatiladi."""
            import traceback
            traceback.print_exception(exc, val, tb)
            show_error_dialog("Kutilmagan xatolik", str(val) or exc.__name__)

        def _build_ui(self):
            self._build_header(); self._build_io_section()
            self._build_stats_cards(); self._build_phrase_model_bar()
            self._build_parse_panels()
            self._build_status_bar()

        def _build_phrase_model_bar(self):
            # Butun IBORANING (bir nechta so'zdan tuzilgan zanjirning) rasmiy
            # KKT modeli — har bir so'zning o'z alohida KKT MM qutisidan farqli
            # o'laroq, shu yerda D+M2+C+X kabi TO'LIQ zanjir ko'rinadi.
            bar=tk.Frame(self,bg=GOLD,padx=14,pady=1); bar.pack(fill="x")
            self._phrase_model_var=tk.StringVar(value="")
            self._phrase_model_lbl=tk.Label(bar,textvariable=self._phrase_model_var,
                font=("Consolas",13,"bold"),bg=GOLD,fg=DARK,anchor="w",justify="left",
                wraplength=1400)
            self._phrase_model_lbl.pack(fill="x",padx=6,pady=2)

        def _build_header(self):
            hdr=tk.Frame(self,bg=DARK,pady=14); hdr.pack(fill="x")
            tk.Label(hdr,
                text="INGLIZ TILIDAN O'ZBEK TILIGA RASMIY MODELLAR ASOSIDA TARJIMA MODULI",
                font=("Segoe UI",18,"bold"),bg=DARK,fg=WHITE).pack()

        def _build_io_section(self):
            outer=tk.Frame(self,bg=BG,padx=14,pady=8); outer.pack(fill="x")
            outer.columnconfigure(0,weight=1); outer.columnconfigure(1,weight=1)
            left=self._card(outer); left.grid(row=0,column=0,sticky="nsew",padx=(0,7))
            tk.Label(left,text="Ingliz tilida so'zni kiritish:",
                     font=F_LABEL,bg=WHITE,fg=DARK).pack(anchor="w",padx=10,pady=(7,3))
            iw=tk.Frame(left,bg=GREEN,padx=2,pady=2); iw.pack(fill="x",padx=10,pady=(0,5))
            self.input_box=tk.Text(iw,height=2,font=F_INPUT,bg=WHITE,fg=DARK,
                                   relief="flat",wrap="word",padx=7,pady=5,insertbackground=GREEN)
            self.input_box.pack(fill="x")
            def _ret(e): self._translate(); return "break"
            self.input_box.bind("<Return>",_ret); self.input_box.focus()
            br=tk.Frame(left,bg=WHITE); br.pack(anchor="w",padx=10,pady=(0,8))
            self._btn(br,"  OK  ",self._translate,GREEN).pack(side="left",padx=(0,7))
            self._btn(br," Tozala ",self._clear,GRAY).pack(side="left")
            right=self._card(outer); right.grid(row=0,column=1,sticky="nsew",padx=(7,0))
            tk.Label(right,text="O'zbekcha tarjima (KKT asosida):",
                     font=F_LABEL,bg=WHITE,fg=DARK).pack(anchor="w",padx=10,pady=(7,3))
            rw=tk.Frame(right,bg=GREEN,padx=2,pady=2); rw.pack(fill="x",padx=10,pady=(0,5))
            self.result_box=tk.Text(rw,height=2,font=F_RESULT,bg=WHITE,fg=GRN_DK,
                                    relief="flat",wrap="word",padx=7,pady=5,state="disabled")
            self.result_box.pack(fill="x")
            ar=tk.Frame(right,bg=WHITE); ar.pack(anchor="e",padx=10,pady=(0,8))
            self._btn(ar,"+ Yangi so'z",self._open_add_dialog,TEAL).pack()

        def _build_stats_cards(self):
            row=tk.Frame(self,bg=BG,padx=14,pady=1); row.pack(fill="x")
            self._sc_words =self._stat_card(row,"-","So'zlar soni",CARD1)
            self._sc_affiks=self._stat_card(row,"-","Affiks/Prefiks",CARD2)
            self._sc_acc   =self._stat_card(row,"-",ACC_CARD_LABEL,CARD3,note=ACC_CARD_NOTE)
            self._sc_auto  =self._stat_card(row,"-","Jami(V2+V3)",CARD4)
            for sc in (self._sc_words,self._sc_affiks,self._sc_acc,self._sc_auto):
                sc["frame"].pack(side="left",expand=True,fill="x",padx=2)

        def _build_parse_panels(self):
            row=tk.Frame(self,bg=BG,padx=14,pady=4); row.pack(fill="both",expand=True)
            row.columnconfigure(0,weight=1); row.columnconfigure(1,weight=1)
            L=self._card(row); L.grid(row=0,column=0,sticky="nsew",padx=(0,7))
            lhdr=tk.Frame(L,bg=GREEN,pady=7,padx=10); lhdr.pack(fill="x")
            tk.Label(lhdr,text="Ingliz tili so'zni Parsinglash",
                     font=F_HDR,bg=GREEN,fg=WHITE).pack(anchor="w")
            self.in_tree=tk.Text(L,font=F_MONO,bg=WHITE,fg=DARK,
                                 relief="flat",padx=6,pady=5,wrap="word",state="disabled")
            sb_l=ttk.Scrollbar(L,command=self.in_tree.yview)
            self.in_tree.config(yscrollcommand=sb_l.set)
            sb_l.pack(side="right",fill="y")
            self.in_tree.pack(fill="both",expand=True)
            self._setup_tags(self.in_tree)
            R=self._card(row); R.grid(row=0,column=1,sticky="nsew",padx=(7,0))
            rhdr=tk.Frame(R,bg=BLUE,pady=7,padx=10); rhdr.pack(fill="x")
            tk.Label(rhdr,text="O'zbek tili so'zni Parsinglash",
                     font=F_HDR,bg=BLUE,fg=WHITE).pack(anchor="w")
            self.out_tree=tk.Text(R,font=F_MONO,bg=WHITE,fg=DARK,
                                  relief="flat",padx=6,pady=5,wrap="word",state="disabled")
            sb_r=ttk.Scrollbar(R,command=self.out_tree.yview)
            self.out_tree.config(yscrollcommand=sb_r.set)
            sb_r.pack(side="right",fill="y")
            self.out_tree.pack(fill="both",expand=True)
            self._setup_tags(self.out_tree)

        def _build_status_bar(self):
            bar=tk.Frame(self,bg=DARK,pady=4); bar.pack(fill="x",side="bottom")
            self._status=tk.StringVar(value="  Tayyor. Inglizcha so'z yozing va OK tugmasini bosing.")
            tk.Label(bar,textvariable=self._status,font=F_SMALL,bg=DARK,fg=WHITE,anchor="w").pack(side="left",padx=10)
            self._bar_right=tk.Label(bar,text="",font=F_SMALL,bg=DARK,fg=WHITE)
            self._bar_right.pack(side="right",padx=10); self._refresh_bar()

        def _translate(self):
            raw=self.input_box.get("1.0","end").strip()
            if not raw: return
            kkt_r = translate_phrase(raw)
            aa=parse_sentence(raw)
            if not aa: return
            self._last_analyses=aa
            parts=[a["uz"] if a["found"] else "["+a["word"]+"?]" for a in aa]
            self._set_text(self.result_box,"  "+"   ".join(parts))
            total=len(aa); affixed=sum(1 for a in aa if a["suffix"] or a.get("prefix"))
            avg_c=(sum(a["conf"] for a in aa)/total*100) if total else 0
            fl=[a for a in aa if a["found"]]
            avg_t=sum(kkt_en(a)["total"] for a in fl)/len(fl) if fl else 0.0
            self._sc_words["lbl"].config(text=str(total))
            self._sc_affiks["lbl"].config(text=str(affixed))
            self._sc_acc["lbl"].config(text=str(round(avg_c,1))+"%")
            self._sc_auto["lbl"].config(text=f"{avg_t:.4f}")
            self._draw_en_parse(aa); self._draw_uz_parse(aa)
            found=sum(1 for a in aa if a["found"])
            if kkt_r:
                self._set_text(self.result_box,"  "+kkt_r["natija"])
                self._status.set(f"  KKT formal model: {kkt_r['model']}")
                self._phrase_model_var.set("  IBORANING RASMIY MODELI:  "+kkt_r["model"])
            else:
                self._status.set(f"  '{raw[:45]}' → {found}/{total} so'z, {affixed} ta affiks/prefiks.")
                self._phrase_model_var.set("")
            self._refresh_bar()

        def _draw_en_parse(self,aa):
            t=self.in_tree; t.config(state="normal"); t.delete("1.0","end")
            for i,a in enumerate(aa,1):
                found=a["found"]; pfx=a.get("prefix",""); sfx=a.get("suffix",""); em=kkt_en(a)
                t.insert("end",f"\n  {i}. ","dim")
                t.insert("end",a["word"].upper()+"\n","bold_green" if found else "red")
                if found:
                    pos=a.get("pos","Ot"); ks=POS_KKT.get(pos,"C")
                    t.insert("end","  ├─ Ildiz:   ","dim"); t.insert("end",a["root"].capitalize()+"\n","green")
                    t.insert("end","  ├─ Prefiks: ","dim")
                    if pfx: t.insert("end",pfx+"-","orange"); t.insert("end","  [T, V3=0.01]\n","dim")
                    else:   t.insert("end","yo'q\n","dim")
                    t.insert("end","  ├─ Suffiks: ","dim")
                    if sfx:
                        sk=em["sfx_kkt"]; sv=EN_AFF_V3.get(sfx,("",0))[1]
                        t.insert("end",f"-{sfx}  ","orange"); t.insert("end",f"[{sk}, V3={sv:.5f}]\n","dim")
                    else:   t.insert("end","yo'q\n","dim")
                    t.insert("end","  ├─ Turkum:  ","dim"); t.insert("end",f"{pos}  [{ks}]\n","blue")
                    meanings=a.get("meanings") or []
                    if len(meanings)>1:
                        alts=", ".join(m["uz"] for m in meanings)
                        t.insert("end","  ├─ Ma'nolar:","dim"); t.insert("end",f" {alts}  ({len(meanings)} ta)\n","orange")
                    t.insert("end",f"  ├─ {ACC_INLINE_LABEL}: ","dim")
                    t.insert("end",f"{round(a['conf']*100,1)}%\n","orange" if (sfx or pfx) else "green")
                    t.insert("end","  │\n","dim")
                    t.insert("end","  ╔══ KKT MM (INGLIZ) ═══════════════╗\n","gold")
                    t.insert("end","  ║  ","gold"); t.insert("end",f"MM: {em['mm']}\n","kkt")
                    t.insert("end","  ╠═══════════════════════════════════╣\n","gold")
                    t.insert("end","  ║  ","gold"); t.insert("end",f"V2  = {em['v2']:.5f}","bold_green")
                    t.insert("end",f"  [{pos}={ks}]\n","dim")
                    t.insert("end","  ║  ","gold"); t.insert("end",f"V3  = {em['v3']:.5f}","orange")
                    if sfx:   t.insert("end",f"  [-{sfx}={em['sfx_kkt']}]\n","dim")
                    elif pfx: t.insert("end",f"  [{pfx}-=T]\n","dim")
                    else:     t.insert("end","  [affiksiz]\n","dim")
                    t.insert("end","  ╠═══════════════════════════════════╣\n","gold")
                    t.insert("end","  ║  ","gold"); t.insert("end",f"V2+V3 = {em['total']:.5f}\n","gold")
                    t.insert("end","  ╚═══════════════════════════════════╝\n","gold")
                else:
                    t.insert("end","  └─ Bazada topilmadi\n","red")
            t.config(state="disabled")

        def _draw_uz_parse(self,aa):
            t=self.out_tree; t.config(state="normal"); t.delete("1.0","end")
            for i,a in enumerate(aa,1):
                found=a["found"]; em=kkt_en(a); um=kkt_uz(a)
                t.insert("end",f"\n  {i}. ","dim")
                ud=(a.get("uz") or a["word"]).upper() if found else "["+a["word"]+"?]"
                t.insert("end",ud+"\n","bold_blue" if found else "red")
                if found:
                    us=um["sfx"]; uk=um["sfx_kkt"]
                    t.insert("end","  ├─ O'z ildiz:","dim"); t.insert("end"," "+um["root"]+"\n","blue")
                    t.insert("end","  ├─ O'z affiks:","dim")
                    if us and us!="eng":
                        t.insert("end",f" -{us}  ","orange"); t.insert("end",f"[{uk}, V3={um['v3']:.5f}]\n","dim")
                    elif us=="eng":
                        t.insert("end"," eng  [P2_D=0.07]\n","orange")
                    else: t.insert("end"," yo'q\n","dim")
                    t.insert("end","  ├─ Turkum:   ","dim"); t.insert("end",f"{a.get('pos','Ot')}  [{um['kkt']}]\n","blue")
                    t.insert("end","  │\n","dim")
                    t.insert("end","  ╔══ KKT MM (O'ZBEK) ══════════════╗\n","bold_blue")
                    t.insert("end","  ║  ","bold_blue"); t.insert("end",f"MM: {um['mm']}\n","kkt")
                    t.insert("end","  ╠══════════════════════════════════╣\n","bold_blue")
                    t.insert("end","  ║  ","bold_blue"); t.insert("end",f"V2_1 = {um['v2']:.5f}","bold_green")
                    t.insert("end",f"  [{a.get('pos','Ot')}={um['kkt']}]\n","dim")
                    t.insert("end","  ║  ","bold_blue"); t.insert("end",f"V3_1 = {um['v3']:.5f}","orange")
                    if us and us!="eng": t.insert("end",f"  [-{us}={uk}]\n","dim")
                    else: t.insert("end","  [affiksiz]\n","dim")
                    t.insert("end","  ╠══════════════════════════════════╣\n","bold_blue")
                    t.insert("end","  ║  ","bold_blue"); t.insert("end",f"V2_1+V3_1 = {um['total']:.5f}\n","bold_blue")
                    t.insert("end","  ╠══════════════════════════════════╣\n","bold_blue")
                    diff=abs(em["total"]-um["total"])
                    dt="green" if diff<0.001 else ("orange" if diff<=0.26 else "red")
                    t.insert("end","  ║  ","bold_blue")
                    t.insert("end",f"FARQ = |{em['total']:.5f}-{um['total']:.5f}| = {diff:.5f}  ",dt)
                    if diff<0.00001:  t.insert("end","✓ Bir xil\n","green")
                    elif diff<=0.26:  t.insert("end","≈ Maqbul\n","orange")
                    else:             t.insert("end","✗ Katta farq!\n","red")
                    t.insert("end","  ╠══════════════════════════════════╣\n","bold_blue")
                    # 8-9-QADAM: SSM metrikasi asosida sifat baholash
                    ssm_v = a.get("ssm_uz"); ssm_g = a.get("ssm_grade","—")
                    qflag = a.get("quality_flag","green")
                    qtag = {"green":"green","orange":"orange","red":"red"}.get(qflag,"dim")
                    t.insert("end","  ║  ","bold_blue")
                    if ssm_v is not None:
                        t.insert("end",f"SSM = {ssm_v:.5f}  ({ssm_g})",qtag)
                    else:
                        t.insert("end","SSM = —","dim")
                    if a.get("mdb_used"):
                        t.insert("end",f"   [MDB_uz_w, |farq|={a.get('mdb_diff')}]","orange")
                    t.insert("end","\n")
                    t.insert("end","  ╚══════════════════════════════════╝\n","bold_blue")
                else:
                    t.insert("end","  └─ Topilmadi\n","red")
            t.config(state="disabled")

        def _open_add_dialog(self):
            dlg=tk.Toplevel(self); dlg.title("Yangi so'z qo'shish")
            dlg.geometry("480x310"); dlg.configure(bg=WHITE)
            dlg.resizable(False,False); dlg.grab_set()
            hdr=tk.Frame(dlg,bg=TEAL,pady=10); hdr.pack(fill="x")
            tk.Label(hdr,text="  + Bazaga yangi so'z qo'shish",
                     font=F_LABEL,bg=TEAL,fg=WHITE).pack(anchor="w")
            body=tk.Frame(dlg,bg=WHITE,padx=20,pady=14); body.pack(fill="both",expand=True)
            for lbl,attr in [("Inglizcha:","_en"),("O'zbekcha:","_uz")]:
                tk.Label(body,text=lbl,font=F_LABEL,bg=WHITE,fg=DARK).pack(anchor="w",pady=(5,2))
                v=tk.StringVar(); setattr(self,"_dlg"+attr,v)
                tk.Entry(body,textvariable=v,font=F_INPUT,bg=GRAY_LT,fg=DARK,relief="flat",bd=3).pack(fill="x",ipady=5)
            tk.Label(body,text="So'z turkumi:",font=F_LABEL,bg=WHITE,fg=DARK).pack(anchor="w",pady=(7,2))
            pv=tk.StringVar(value="Ot"); self._dlg_pos=pv
            ttk.Combobox(body,textvariable=pv,values=list(POS_MAP.values()),
                         state="readonly",font=F_NORMAL,width=28).pack(anchor="w")
            mv=tk.StringVar(); tk.Label(body,textvariable=mv,font=F_SMALL,bg=WHITE,fg=GRN_DK).pack(pady=(6,0))
            def do():
                en=self._dlg_en.get().strip(); uz=self._dlg_uz.get().strip()
                if not en or not uz: mv.set("Ikkala maydon to'ldirilsin!"); return
                if db_insert(en,uz,pv.get(),"user"):
                    mv.set(f"'{en}' [{POS_KKT.get(pv.get(),'?')}] qo'shildi!")
                    self._dlg_en.set(""); self._dlg_uz.set(""); self._refresh_bar()
                else: mv.set(f"'{en}' allaqachon mavjud.")
            br=tk.Frame(body,bg=WHITE); br.pack(pady=(8,0))
            self._btn(br," Qo'shish ",do,TEAL).pack(side="left",padx=5)
            self._btn(br," Yopish ",dlg.destroy,GRAY).pack(side="left")

        def _show_welcome(self):
            for t in (self.in_tree,self.out_tree):
                t.config(state="normal"); t.delete("1.0","end"); t.config(state="disabled")

        def _clear(self):
            self.input_box.delete("1.0","end"); self._set_text(self.result_box,"")
            for sc in (self._sc_words,self._sc_affiks,self._sc_acc,self._sc_auto):
                sc["lbl"].config(text="-")
            self._show_welcome(); self._status.set("  Maydon tozalandi."); self.input_box.focus()

        def _refresh_bar(self):
            s=db_stats()
            self._bar_right.config(text=f"Baza: {s['total']} so'z  |  Affiks en:{s['aff_en']} uz:{s['aff_uz']}  ")

        def _setup_tags(self,w):
            w.tag_config("dim",       foreground=GRAY,   font=F_MONO)
            w.tag_config("green",     foreground=GREEN,  font=F_MONO)
            w.tag_config("bold_green",foreground=GRN_DK, font=F_MONO_B)
            w.tag_config("blue",      foreground=BLUE,   font=F_MONO)
            w.tag_config("bold_blue", foreground=BLUE,   font=F_MONO_B)
            w.tag_config("orange",    foreground=ORANGE, font=F_MONO)
            w.tag_config("red",       foreground=RED_C,  font=F_MONO)
            w.tag_config("gold",      foreground=GOLD,   font=F_MONO_B)
            w.tag_config("kkt",       foreground="#1a6b00",font=F_MONO_B)

        @staticmethod
        def _card(p):
            return tk.Frame(p,bg=WHITE,highlightbackground=BORDER,highlightthickness=1)
        @staticmethod
        def _btn(p,text,cmd,color):
            return tk.Button(p,text=text,command=cmd,font=F_BTN,bg=color,fg=WHITE,
                             relief="flat",padx=12,pady=6,cursor="hand2",
                             activebackground=color,activeforeground=WHITE)
        def _stat_card(self,p,value,label,color,note=None):
            frame=tk.Frame(p,bg=color,pady=3,padx=5)
            lbl=tk.Label(frame,text=value,font=F_CARD_N,bg=color,fg=WHITE); lbl.pack()
            tk.Label(frame,text=label,font=F_CARD_L,bg=color,fg=WHITE).pack()
            if note:
                # Faza 2 / Ustuvorlik 0.2 — ko'rsatkich nimani o'lchamasligini
                # doim ko'rinadigan izoh sifatida bildiradi (qarang ACC_CARD_NOTE).
                tk.Label(frame,text=note,font=F_CARD_NOTE,bg=color,fg=WHITE,
                         wraplength=150,justify="center").pack()
            return {"frame":frame,"lbl":lbl}
        @staticmethod
        def _set_text(widget,text):
            widget.config(state="normal"); widget.delete("1.0","end")
            if text: widget.insert("1.0",text)
            widget.config(state="disabled")

# ═══════════════════════════════════════════════════════════════════
def _safe_step(label, fn, *args, **kwargs):
    """
    Har bir YUKLASH bosqichini (docx/xlsx/pdf o'qish, baza to'ldirish)
    o'zining "xavfsiz konvertida" ishga tushiradi: agar shu BITTA bosqich
    (masalan eskirgan/yo'q fayl, buzilgan docx, sxema nomuvofiqligi
    sababli) xatolik bersa — faqat OGOHLANTIRISH chop etiladi va DASTUR
    KEYINGI bosqichga, oxir-oqibat GUI OCHILISHIGA davom etadi.
    Bu — "GUI ishga tushmadi" muammosining old oldini oluvchi asosiy tuzatish.
    """
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        show_error_dialog("Yuklash bosqichi xatosi",
            f"{label}:\n{e}\n\n(bu bosqich o'tkazib yuborildi, dastur davom etadi)")
        return None


def main():
    print("="*65)
    print("  MT System v5.0  —  KKT 6-POS To'liq Morfologik Tahlil")
    print("="*65)
    print("  Skript papkasi: "+SCRIPT_DIR)
    print("  Bazalar: BM_en_w, BM_uz_w, UB_en_w, UB_uz_w, QM_en_w, QM_uz_w, PSB_en_w, PSB_uz_w, MDB_uz_w")

    _safe_step("Bazalarni ishga tushirish (init_all_databases)", init_all_databases)

    need_rebuild = not all(os.path.exists(p) for p in (DB_UB_EN,DB_UB_UZ,DB_QM_EN,DB_QM_UZ))
    if not need_rebuild:
        s = _safe_step("Baza statistikasi (db_stats)", db_stats) or {"total":0}
        if s.get("total",0)==0: need_rebuild=True
        else: print(f"  UB_en_w/UB_uz_w: {s['total']} so'z | QM_en_w:{s['aff_en']} QM_uz_w:{s['aff_uz']}")
    if need_rebuild:
        docx_path = _safe_step("DOCX qidirish (find_docx)", find_docx) if HAS_DOCX else None
        if docx_path:
            print("  Topildi: "+os.path.basename(docx_path))
        else:
            print(f"  DIQQAT: {DOCX_CANDIDATES[0]} topilmadi (skript bilan bir papkada bo'lishi kerak).")
            print("          Faqat zaxira (minimal) lug'at bilan ishlaydi.")
        print("  Bazalar yaratilmoqda ...")
        n = _safe_step("Baza to'ldirish (setup_database)", setup_database, docx_path) or 0
        if n>0: print(f"  DOCX dan {n} ta so'z UB_en_w/UB_uz_w ga yuklandi.")
        print("  Excel affikslari yuklanmoqda ...")
        n2 = _safe_step("Excel affikslari (load_xlsx_affixes)", load_xlsx_affixes) or 0
        print(f"  Excel dan {n2} ta affiks QM_en_w ga yuklandi.")
        s = _safe_step("Baza statistikasi (db_stats)", db_stats) or {"aff_en":0,"aff_uz":0}
        print(f"  QM_en_w:{s['aff_en']}  QM_uz_w:{s['aff_uz']}")

    bz_path = _safe_step("bazalar_ma_lumot_09.docx qidirish", find_bazalar_docx)
    if bz_path:
        print("  bazalar_ma_lumot_09.docx topildi — I/II bob maʼlumotlari yuklanmoqda ...")
        r = _safe_step("bazalar_ma_lumot_09.docx yuklash", load_bazalar_docx, bz_path)
        if r:
            print(f"  BM belgilar:+{r['symbols']}  QM_en_w:+{r['aff_en']}  QM_uz_w:+{r['aff_uz']}  UB soʻzlar:+{r['words']}")
    else:
        print(f"  DIQQAT: {DOCX2_CANDIDATES[0]} topilmadi — I/II bob ma'lumotlari (89 KKT")
        print("          belgisi, 1041 qo'shimcha) yuklanmadi.")

    n3 = _safe_step("Zaxira lug'at (seed_core_demo_data)", seed_core_demo_data) or 0
    if n3: print(f"  Zaxira lug'at: {n3} ta asosiy so'z kafolatlab qo'shildi (fayl topilmasa ham ishlashi uchun).")

    bazalar2_path = _safe_step("bazalar_ma_lumot_09_07.docx qidirish", find_bazalar_affixes_docx)
    if bazalar2_path:
        r_aff = _safe_step("bazalar_ma_lumot_09_07.docx yuklash", load_bazalar_affixes_docx, bazalar2_path)
        if r_aff:
            print(f"  {os.path.basename(bazalar2_path)}: QM_en_w affikslar +{r_aff['aff_en']}, "
                  f"QM_uz_w affikslar +{r_aff['aff_uz']} (1.2-1.38-jadval, I bob to'liq)")

    pdf_r = _safe_step("PDF manba (load_pdf_kkt_bazalar)", load_pdf_kkt_bazalar)
    if pdf_r:
        print(f"  PDF manbadan (umumiy_to'liq_6_oid_09): KKT belgilar +{pdf_r['symbols']}, "
              f"QM_en_w affikslar +{pdf_r['affixes_en']}")
        if pdf_r.get("new_prefixes"):
            print(f"  DIQQAT: PDF manbada topilgan, lekin jonli parserda (EN_PREFIXES) hali "
                  f"faollashtirilmagan {len(pdf_r['new_prefixes'])} ta prefiks bor — "
                  f"qo'lda ko'rib chiqish tavsiya etiladi:")
            print("    " + ", ".join(pdf_r["new_prefixes"]))

    ch2_r = _safe_step("II bob EVXs/EVIXs namunalari (load_ch2_evx_examples)", load_ch2_evx_examples)
    if ch2_r:
        print(f"  so_zlar_bazasi_un.docx (II bob EVXs/EVIXs namunalari): "
              f"UB so'zlar +{ch2_r['words']}, BM formal modellar +{ch2_r['models']}, "
              f"grammatik qoidalar +{ch2_r['rules']}")

    rr = _safe_step("ID sinxronlash (resync_all_ids)", resync_all_ids)
    if rr:
        print(f"  ID sinxronlandi — soʻzlar EN:{rr['words_en']} UZ:{rr['words_uz']} | "
              f"qoʻshimchalar EN:{rr['aff_en']} UZ:{rr['aff_uz']}")

    mdb_added = _safe_step("MDB_uz_w boshlang'ich to'ldirish (mdb_seed_if_empty)", mdb_seed_if_empty) or 0
    if mdb_added: print(f"  MDB_uz_w: {mdb_added} ta boshlang'ich nomzod qo'shildi (SSM-asosidagi qayta izlash uchun).")

    if not HAS_TK:
        print("  DIQQAT: tkinter bu muhitda mavjud emas — GUI ochilmaydi.")
        print("          Bazalar/tarjima mantig'i baribir tayyor (scripts/build_db.py,")
        print("          translate_phrase() import qilib ishlatilishi mumkin).")
        print("="*65)
        return

    print("  Interfeys ochilmoqda ..."); print("="*65)

    # ── GUI OCHILISHI — BU QATOR HECH QACHON YUQORIDAGI (ixtiyoriy
    #    boyitish) bosqichlaridagi xatolik sababli o'tkazib yuborilmaydi ──
    app = MTSystem()
    app.mainloop()

if __name__=="__main__":
    try:
        main()
    except Exception as e:
        # Dasturni ishga tushirishda GUI ochilishidan OLDIN yuzaga kelgan
        # (masalan _safe_step qamrab olmagan) har qanday kutilmagan
        # xatolik ham jim konsolga tushib qolmasin — dialog ko'rsatiladi.
        import traceback
        traceback.print_exc()
        show_error_dialog("Dasturni ishga tushirish xatosi", str(e))
