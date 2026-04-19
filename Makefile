PYTHON ?= python3

.PHONY: test demo formal paper-check

test:
	$(PYTHON) -m pytest -q tests

demo:
	$(PYTHON) scripts/run_demo.py

formal:
	$(PYTHON) formal/bounded_model.py

paper-check:
	! rg -n "placeholder|TODO|TBD|lorem ipsum|minimal LaTeX paper" README.md spec docs paper ietf
