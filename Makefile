PYTHON ?= python3

.PHONY: install db test check100 audit ergap ch2leakage spec conformance leakage lexsources specdiss clean

install:
	$(PYTHON) -m pip install -r requirements.txt

## Barcha .db bazalarni data/ dagi manba fayllardan noldan quradi
## (GUI ochmaydi). Qarang: scripts/build_db.py, reports/db_reproducibility.md.
db:
	$(PYTHON) scripts/build_db.py

test:
	$(PYTHON) -m pytest tests/ -v

## 100_soz.docx gold-set natijasini qayta hisoblaydi (reports/faza_1_100soz_baseline.md).
check100:
	$(PYTHON) scripts/check_100_soz.py

## II bob (CH2_EVX_EXAMPLES) auditini qayta hisoblaydi (reports/faza_1_audit_examples.md).
audit:
	$(PYTHON) scripts/audit_examples.py

## "-er" so'zlarini sifat+er (qiyosiy) / fe'l+er (agentiv) ga ajratib,
## sonlarini hisoblaydi (reports/faza_2_er_gap.md) — hech narsani hal
## qilmaydi, faqat professor muhokamasi uchun dalil tayyorlaydi.
ergap:
	$(PYTHON) scripts/audit_er_gap.py

## CH2_EVX_EXAMPLES ni asl dissertatsiya (data/desertatsiya.docx, shaxsiy
## fayl — .gitignore'da) bilan solishtiradi (reports/ch2_leakage_check.md).
## Fayl mavjud bo'lmasa xato bilan to'xtaydi.
ch2leakage:
	$(PYTHON) scripts/check_ch2_leakage.py

## data/kkt_qoidalari.docx -> data/kkt_spec.json (rasmiy KKT spesifikatsiyasi,
## matn aynan ko'chiriladi). `--check` bilan faqat sinxronlikni tekshiradi.
spec:
	$(PYTHON) scripts/extract_kkt_spec.py

## 87 ta spec qoidasini kod bilan solishtiradi (conformance matrix,
## reports/faza_2_kkt_spec_conformance.md) — kodni o'zgartirmaydi.
conformance:
	$(PYTHON) scripts/audit_kkt_spec_conformance.py

## kkt_spec.json misollari va gold/test to'plamlar kesishmasi — faqat
## ogohlantirish, leakage emas (reports/faza_2_kkt_spec_leakage.md).
leakage:
	$(PYTHON) scripts/check_leakage.py

## KKT_Terminologik va 100_soz qatorlari lug'atda qayerda ishlatiladi (ablatsiya
## bilan) — reports/faza_2_lexicon_sources.md.
lexsources:
	$(PYTHON) scripts/audit_lexicon_sources.py

## Spec (kkt_spec.json) ↔ dissertatsiya II bobi ↔ CH2_EVX_EXAMPLES barcha
## nomuvofiqliklari (reports/faza_2_spec_vs_dissertation.md). data/desertatsiya.docx
## (shaxsiy fayl) talab qilinadi.
specdiss:
	$(PYTHON) scripts/compare_spec_dissertation.py

## Generatsiya qilingan bazalarni tozalaydi (data/ dagi manba fayllarga
## tegmaydi — qayta `make db` bilan tiklanadi).
clean:
	rm -f *.db
	rm -rf __pycache__ tests/__pycache__ scripts/__pycache__ .pytest_cache
