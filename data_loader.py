"""
data_loader.py
================
`data/` papkasidagi 3 ta JSON faylni (dastlab .docx/.xlsx fayllardan
konvertatsiya qilingan) o'qib, dastur ichida qulay ishlatish uchun
Python obyektlariga aylantiradi.

Manba fayllar:
  data/Table_English 1-7 Vazn Type 2 14.02.2024.json   -> ingliz affikslari (og'irlik bilan)
  data/Lotinda Table_Uzbek 1-7 Vazn 11.02.2025.json    -> o'zbek affikslari
  data/1500_EN_UZ_6_POS_sorted.20.json                 -> 1500 ta EN-UZ so'z jufti (POS bo'yicha)

Ishlatish:
    from data_loader import load_english_affixes, load_uzbek_affixes, load_word_pairs

    en_affixes = load_english_affixes()
    uz_affixes = load_uzbek_affixes()
    words      = load_word_pairs()

    # Masalan: "Ot" (NOUNS) so'z turkumidagi barcha juftlar
    nouns = words.by_category("NOUNS (OTLAR)")

    # Masalan: 1-OT varag'idagi "C-T" kodli affikslar ro'yxati
    ct = en_affixes.by_code("1-OT", "C-T")

Har bir funksiya natijani xotirada keshlab qo'yadi (lru_cache), shuning
uchun bir necha marta chaqirilsa ham fayl qayta o'qilmaydi.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

ENGLISH_AFFIXES_JSON = os.path.join(DATA_DIR, "Table_English 1-7 Vazn Type 2 14.02.2024.json")
UZBEK_AFFIXES_JSON = os.path.join(DATA_DIR, "Lotinda Table_Uzbek 1-7 Vazn 11.02.2025.json")
WORD_PAIRS_JSON = os.path.join(DATA_DIR, "1500_EN_UZ_6_POS_sorted.20.json")


def _read_json(path: str) -> Any:
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON fayl topilmadi: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────
#  Affiks fayllari (ingliz / o'zbek) uchun umumiy konteyner
# ─────────────────────────────────────────────────────────────────

@dataclass
class AffixItem:
    value: str
    weight: Optional[float] = None


@dataclass
class AffixGroup:
    sheet: str
    code: Optional[str]
    label: Any  # ingliz faylda group raqami (int), o'zbek faylda "Jadval-N"
    items: List[AffixItem] = field(default_factory=list)

    def values(self) -> List[str]:
        return [it.value for it in self.items]


class AffixTable:
    """Bitta xlsx-dan konvertatsiya qilingan barcha varaqlar/guruhlarni ushlab turadi."""

    def __init__(self, sheets: Dict[str, List[AffixGroup]]):
        self._sheets = sheets

    @property
    def sheet_names(self) -> List[str]:
        return list(self._sheets.keys())

    def groups(self, sheet: str) -> List[AffixGroup]:
        return self._sheets.get(sheet, [])

    def by_code(self, sheet: str, code: str) -> List[AffixItem]:
        """Berilgan varaq va kod (masalan 'C-T', 'P-A1') bo'yicha affikslar ro'yxati."""
        for g in self.groups(sheet):
            if g.code == code:
                return g.items
        return []

    def all_codes(self, sheet: str) -> List[str]:
        return [g.code for g in self.groups(sheet) if g.code]

    def find_code(self, code: str) -> List[AffixItem]:
        """Barcha varaqlar bo'ylab kodni qidiradi (varaq nomi muhim bo'lmasa)."""
        for sheet in self._sheets:
            items = self.by_code(sheet, code)
            if items:
                return items
        return []


def _build_affix_table(raw: Dict[str, List[dict]], label_key: str) -> AffixTable:
    sheets: Dict[str, List[AffixGroup]] = {}
    for sheet_name, groups in raw.items():
        parsed_groups = []
        for g in groups:
            items = [
                AffixItem(value=it["value"], weight=it.get("weight"))
                if isinstance(it, dict) and "weight" in it
                else AffixItem(value=it if isinstance(it, str) else it.get("value") if isinstance(it, dict) else it)
                for it in g.get("items", [])
            ]
            parsed_groups.append(
                AffixGroup(sheet=sheet_name, code=g.get("code"), label=g.get(label_key), items=items)
            )
        sheets[sheet_name] = parsed_groups
    return AffixTable(sheets)


@lru_cache(maxsize=1)
def load_english_affixes() -> AffixTable:
    """Table_English ...json -> AffixTable (har bir item: value + weight)."""
    raw = _read_json(ENGLISH_AFFIXES_JSON)
    return _build_affix_table(raw, label_key="group")


@lru_cache(maxsize=1)
def load_uzbek_affixes() -> AffixTable:
    """Lotinda Table_Uzbek ...json -> AffixTable (har bir item: faqat value, weight=None)."""
    raw = _read_json(UZBEK_AFFIXES_JSON)
    return _build_affix_table(raw, label_key="table")


# ─────────────────────────────────────────────────────────────────
#  1500 EN-UZ so'z juftlari
# ─────────────────────────────────────────────────────────────────

@dataclass
class WordPair:
    no: int
    english: str
    uzbek: str
    category: str


class WordPairTable:
    def __init__(self, title: Optional[str], categories: Dict[str, List[WordPair]]):
        self.title = title
        self._categories = categories
        self._all: List[WordPair] = [wp for lst in categories.values() for wp in lst]

    @property
    def category_names(self) -> List[str]:
        return list(self._categories.keys())

    def by_category(self, category: str) -> List[WordPair]:
        return self._categories.get(category, [])

    def all(self) -> List[WordPair]:
        return self._all

    def find_english(self, word: str) -> List[WordPair]:
        word = word.strip().lower()
        return [wp for wp in self._all if wp.english.strip().lower() == word]

    def find_uzbek(self, word: str) -> List[WordPair]:
        word = word.strip().lower()
        return [wp for wp in self._all if wp.uzbek.strip().lower() == word]

    def __len__(self) -> int:
        return len(self._all)


@lru_cache(maxsize=1)
def load_word_pairs() -> WordPairTable:
    """1500_EN_UZ_6_POS_sorted.20.json -> WordPairTable."""
    raw = _read_json(WORD_PAIRS_JSON)
    categories: Dict[str, List[WordPair]] = {}
    for cat, entries in raw.get("categories", {}).items():
        pairs = []
        for e in entries:
            if "english" in e and "uzbek" in e:
                pairs.append(WordPair(no=e.get("no", -1), english=e["english"], uzbek=e["uzbek"], category=cat))
        categories[cat] = pairs
    return WordPairTable(title=raw.get("title"), categories=categories)


# ─────────────────────────────────────────────────────────────────
#  Tezkor o'z-o'zini tekshirish
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    en = load_english_affixes()
    uz = load_uzbek_affixes()
    words = load_word_pairs()

    print("Ingliz affikslar varaqlari:", en.sheet_names)
    print("  1-OT / C-T:", [i.value for i in en.by_code("1-OT", "C-T")][:5])

    print("O'zbek affikslar varaqlari:", uz.sheet_names)
    print("  1-OT / C-A1:", [i.value for i in uz.by_code("1-OT", "C-A1")][:5])

    print("So'z juftlari:", words.category_names, "jami:", len(words))
    print("  NOUNS namuna:", words.by_category("NOUNS (OTLAR)")[:3])
    print("  'ability' tarjimasi:", words.find_english("ability"))
