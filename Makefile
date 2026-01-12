.PHONY: run discover assets assets-all paper paper-all check check-all

run:
	snakemake -j 1 run_example

discover:
	uv run paperops discover

assets: discover
	@if [ -z "$(PAPER)" ]; then echo "Set PAPER=<paper_id>"; exit 1; fi
	uv run paperops build-paper-assets --paper $(PAPER)

assets-all: discover
	@for paper in $$(uv run python -c 'import json;print(" ".join([p["paper_id"] for p in json.load(open("artifacts/manifests/papers_index.json"))["papers"]]))'); do \
		echo "Building assets for $$paper"; \
		uv run paperops build-paper-assets --paper $$paper; \
	done

paper: discover
	@if [ -z "$(PAPER)" ]; then echo "Set PAPER=<paper_id>"; exit 1; fi
	uv run paperops build-paper --paper $(PAPER)

paper-all: discover
	@for paper in $$(uv run python -c 'import json;print(" ".join([p["paper_id"] for p in json.load(open("artifacts/manifests/papers_index.json"))["papers"]]))'); do \
		echo "Building paper for $$paper"; \
		uv run paperops build-paper --paper $$paper; \
	done

check: discover
	@if [ -n "$(PAPER)" ]; then uv run paperops check --paper $(PAPER); else uv run paperops check; fi

check-all: discover
	@for paper in $$(uv run python -c 'import json;print(" ".join([p["paper_id"] for p in json.load(open("artifacts/manifests/papers_index.json"))["papers"]]))'); do \
		echo "Checking $$paper"; \
		uv run paperops check --paper $$paper; \
	done
