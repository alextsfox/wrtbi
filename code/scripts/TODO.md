## Make parallel

modify `ingest.py` and split it into two files:
* `ingest.py`: handles conversion from TOB3 to parquet, takes only one input file and one output file. This lets us use snakemake's native parallelism. We will need to enumerate the output files in advance for snakemake. 
* `concat_files_by_time_interval.py`: move this into a separate script. Much harder to parallelize: we will have to run 1 script that prints the starting and ending timestamps for each file and creates a mapping of input files to output files. Then once we have an idea of that mapping, we can run a separate script/rule that applies the mapping in parallel.

many .dat files -> camp2ascii -> many intermediate .parquet
many intermediate .parquet files -> concat -> files ready for preprocessing

likewise, we can make `preprocess.py` take one input file and one output file, and then use snakemake to parallelize it across the files produced by the previous step.

Snakemake parallelizes rules that have independent outputs per wildcard.

Example:
```
rule preprocess_fast:
    input:  "L0b_ingested/fast/{date}.parquet"
    output: "L1_preprocessed/fast/{date}.csv"
    shell:  "python preprocess.py --input {input} --output {output}"
```

`{date}` might expand to `2026_03_26`, `2026_03_27`, etc. Since the input and output wildcards match, snakemake can run multiple instances of `preprocess.py` in parallel, each processing a different date's file.

Counterexample:
```
rule preprocess_fast:
    input:  "L0b_ingested/fast/{filename}.parquet"
    output: "L1_preprocessed/fast/{date}.csv"
    shell:  "python preprocess.py --input {input} --output {output}"
```
In this case, the input wildcard is `{filename}` while the output wildcard is `{date}`. Since snakemake cannot determine which input files correspond to which output files based on the wildcards, it cannot parallelize this rule effectively. It would likely run the preprocessing sequentially or require additional logic to match inputs to outputs, defeating the purpose of using snakemake for parallelization.

## Archive outputs after each step
Whenever a step completes, move the input files into an "arfhive" directory.
This way we don't need to keep track of which files have been processed in a separate text file. instead we just never look at the archive directory when searching for files to process. This also makes it easy to reprocess files if needed, since we can just move them back from the archive. We should include an "unarchive" option in the config that allows us to move files back from the archive to the raw directory if we need to reprocess them.

## Delete intermediate files
Add a config option to delete intermediate files after downstream steps complete successfully. This will save disk space, but we should be careful to only delete files that are truly intermediate and not needed for debugging or reprocessing. The only files that remain will be files in L0a_raw and the files in L3 and beyond.

This step would involve adding a cleanup step: instead of moving intermediate files to an archive directory, we can just delete them after the next step completes successfully. We can use snakemake's `on_success` hook to do this. For example:
```
rule preprocess_fast:
    input:  "L0b_ingested/fast/{date}.parquet"
    output: "L1_preprocessed/fast/{date}.csv"
    shell:  "python preprocess.py --input {input} --output {output}"
    on_success: "rm {input}"
```


