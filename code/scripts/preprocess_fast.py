"""
Process raw data files from L0b_ingested to prepare them for analysis and intake by eddypro

Also perform some basic cleaning on the data

Contains lots of business logic for how to handle, name, combine, and clean data from different sources and time periods.
"""

from pathlib import Path
import argparse

import pandas as pd
import numpy as np

import sys
sys.path.append("/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/PostProc")
from FluxFox.hf import despike_hf

def preprocess_fast_data(f: Path, args) -> None:
    fast = pd.read_feather(f)
    if fast.empty:
        pd.DataFrame().to_csv(args.output_file, index=False, header=False, sep=",", float_format="%.5g")
        return

    fast = (
        fast
        .replace([-9999, -7999, 7999, np.inf, -np.inf], np.nan)
        .reset_index(names="TIMESTAMP")
        .drop_duplicates(subset=["TIMESTAMP"], keep="last")
        .drop(columns=["RECORD", "TIMESTAMP"], errors="ignore")
    )

    numeric_cols = ["ux", "uy", "uz", "sonic_temp", "rho_co2", "rho_h2o"]

    # despike and fill gaps smaller than 2 datapoints
    keep = despike_hf(fast[numeric_cols], z_thresh=7, chunksize=20*300)
    fast[numeric_cols] = fast[numeric_cols].where(keep)
    fast[numeric_cols] = fast[numeric_cols].interpolate(method="linear", limit_direction="both", limit_area='inside', limit=2)

    # remove obviously bad values
    fast[["ux", "uy", "uz"]] = fast[["ux", "uy", "uz"]].where(fast[["ux", "uy", "uz"]].abs() < 100)
    fast["sonic_temp"] = fast["sonic_temp"].where(fast["sonic_temp"].abs() < 60)
    fast["rho_co2"] = fast["rho_co2"].where(fast["rho_co2"].between(0, 5000))
    fast["rho_h2o"] = fast["rho_h2o"].where(fast["rho_h2o"].between(-10, 100))

    # filter out values based on diagnostic flags
    fast[["rho_co2", "rho_h2o"]] = fast[["rho_co2", "rho_h2o"]].where(fast["irga_diag"] == 0)
    fast[["ux", "uy", "uz", "sonic_temp"]] = fast[["ux", "uy", "uz", "sonic_temp"]].where(fast["sonic_diag"] == 0)

    # drop diagnostic columns
    fast = fast.drop(columns=["irga_diag", "sonic_diag"], errors="ignore")

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
    

        