.PHONY: test selftest static acceptance qa manifest

test:
	python -m pytest -q

selftest:
	python run.py selftest

static:
	python tools/static_audit.py

acceptance:
	python tools/acceptance.py

qa: test selftest static acceptance

manifest:
	python tools/build_manifest.py
