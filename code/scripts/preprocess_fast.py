"""
Process raw data files from L0b_ingested to prepare them for analysis and intake by eddypro

Also perform some basic cleaning on the data

Contains lots of business logic for how to handle, name, combine, and clean data from different sources and time periods.
"""

from pathlib import Path
import argparse

import pandas as pd
import numpy as np
def preprocess_fast_data(f: Path, args) -> None:
    fast = (
        pd.read_feather(f)
        .replace([-9999, -7999, 7999, np.inf, -np.inf], np.nan)
        .reset_index(names="TIMESTAMP")
        .drop_duplicates(subset=["TIMESTAMP"], keep="last")
        .drop(columns=["RECORD", "TIMESTAMP"], errors="ignore")
    )

    fast["irga_diag"] = fast["irga_diag"].replace([np.nan, np.inf, -np.inf], -9999).astype(int).astype(str).replace("-9999", "")
    fast["sonic_diag"] = fast["sonic_diag"].replace([np.nan, np.inf, -np.inf], -9999).astype(int).astype(str).replace("-9999", "")

    fast.to_csv(args.output_file, index=False, header=False, sep=",", float_format="%.5g")

    return

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=Path)
    parser.add_argument("--output_file", type=Path)
    args = parser.parse_args()
    preprocess_fast_data(args.input_file, args)

    # for f in Path("/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi/L0c_ingested/Fast").glob("*.parquet"):
    #     args = argparse.Namespace(
    #         output_file=Path("/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi/L1_preprocessed/fast_for_eddypro") / f"{f.stem}.csv"
    #     )
    #     preprocess_fast_data(f, args)

if __name__ == "__main__":
    main()
    

        