PYTHON ?= python3

.PHONY: install db test clean

install:
	$(PYTHON) -m pip install -r requirements.txt

## Barcha .db bazalarni data/ dagi manba fayllardan noldan quradi
## (GUI ochmaydi). Qarang: scripts/build_db.py, reports/db_reproducibility.md.
db:
	$(PYTHON) scripts/build_db.py

test:
	$(PYTHON) -m pytest tests/ -v

## Generatsiya qilingan bazalarni tozalaydi (data/ dagi manba fayllarga
## tegmaydi — qayta `make db` bilan tiklanadi).
clean:
	rm -f *.db
	rm -rf __pycache__ tests/__pycache__ scripts/__pycache__ .pytest_cache
