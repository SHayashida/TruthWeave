.PHONY: run assets paper check

run:
	snakemake -j 1 run_example

assets:
	snakemake -j 1 aggregate

paper:
	snakemake -j 1 paper

check:
	snakemake -j 1 check
