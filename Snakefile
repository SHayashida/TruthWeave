rule run_example:
    output:
        directory("runs")
    shell:
        "uv run paperops run exp=example"

rule aggregate:
    output:
        "paper/auto/variables.tex",
        "paper/auto/MANIFEST.json",
    shell:
        "uv run paperops build-paper-assets"

rule paper:
    input:
        "paper/main.tex",
        "paper/auto/variables.tex",
    shell:
        "latexmk -pdf -interaction=nonstopmode -halt-on-error -output-directory=paper paper/main.tex"

rule check:
    shell:
        "uv run paperops check"
