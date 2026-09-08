PYTHON ?= python3

.PHONY: install db test check100 audit clean

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

## Generatsiya qilingan bazalarni tozalaydi (data/ dagi manba fayllarga
## tegmaydi — qayta `make db` bilan tiklanadi).
clean:
	rm -f *.db
	rm -rf __pycache__ tests/__pycache__ scripts/__pycache__ .pytest_cache
