L0_raw/  # raw data presented exactly as it was collected from the datalogger, without any processing, along with some metadata
├── yyyy_mm_dd/  # date of data collection
│   ├── data/ # data files collected on that date
|   │   ├── 20Hz_1.dat
|   │   ├── 20Hz_2.dat
|   │   ├── Summary_1.dat
|   │   ├── Summary_2.dat
│   ├── fieldnotes/ # field notes taken on that date
|   │   ├── fieldnotes_1.txt
|   │   ├── fieldnotes_2.txt
|   │   ├── image_1.jpg
|   │   ├── image_2.jpg

```shell
snakemake -s ./code/Snakefile --cores 6  # or however many cores you want to use
```

how to run up to a specific step:
```shell
snakemake -s ./code/Snakefile --cores 6 preprocess  # or whatever step you want to run up to
```
