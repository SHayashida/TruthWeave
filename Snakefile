import json
import subprocess
from pathlib import Path

index_path = Path("artifacts/manifests/papers_index.json")
if not index_path.exists():
    subprocess.run(["uv", "run", "paperops", "discover"], check=True)

papers = []
if index_path.exists():
    data = json.loads(index_path.read_text())
    papers = [p["paper_id"] for p in data.get("papers", [])]


rule run_example:
    output:
        directory("runs")
    shell:
        "uv run truthweave run exp=example"


rule discover:
    output:
        "artifacts/manifests/papers_index.json"
    shell:
        "uv run truthweave discover"


rule assets_per_paper:
    input:
        "artifacts/manifests/papers_index.json"
    output:
        "papers/{paper}/auto/variables.tex",
        "papers/{paper}/auto/MANIFEST.json"
    shell:
        "uv run truthweave build-paper-assets --paper {wildcards.paper}"


rule assets_all:
    input:
        expand("papers/{paper}/auto/variables.tex", paper=papers),
        expand("papers/{paper}/auto/MANIFEST.json", paper=papers),
    output:
        "artifacts/manifests/assets_all.done"
    shell:
        "touch {output}"


rule paper_per_paper:
    input:
        "artifacts/manifests/papers_index.json"
    output:
        "papers/{paper}/build/main.pdf"
    shell:
        "uv run truthweave build-paper --paper {wildcards.paper}"


rule paper_all:
    input:
        expand("papers/{paper}/build/main.pdf", paper=papers),
    output:
        "artifacts/manifests/paper_all.done"
    shell:
        "touch {output}"


rule check:
    shell:
        "uv run truthweave check"
