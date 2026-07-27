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
    print(f"Preprocessing {f}")


    fast = pd.read_feather(f)

    if fast.empty:
        print(f"\t{args.output_file} is empty before preprocessing")
        pd.DataFrame().to_csv(args.output_file, index=False, header=False, sep=",", float_format="%.5g")
        return
    
    fast = (
        fast
        .replace([-9999, -7999, 7999, np.inf, -np.inf], np.nan)
        .reset_index(names="TIMESTAMP")
        .drop_duplicates(subset=["TIMESTAMP"], keep="last")
        .drop(columns=["RECORD", "TIMESTAMP"], errors="ignore")
    )

    print(f"\tInitial Data Integrity")
    for c in fast.columns:
        print(f"\t\t{c}: {fast[c].count()/fast.shape[0]*100:.3f}%")

    # despike and fill gaps smaller than 4 datapoints. Use a relatively permissive spike threshold
    # use 5 minute chunks for despiking
    keep = despike_hf(fast[["rho_co2", "rho_h2o"]], z_thresh=7, chunksize=20*300)
    fast[["rho_co2", "rho_h2o"]] = fast[["rho_co2", "rho_h2o"]].where(keep)
    fast[["rho_co2", "rho_h2o"]] = fast[["rho_co2", "rho_h2o"]].interpolate(method="linear", limit_direction="both", limit_area='inside', limit=4)
    print(f"\tData Integrity After Despiking")
    for c in fast.columns:
        print(f"\t\t{c}: {fast[c].count()/fast.shape[0]*100:.3f}%")

    # remove obviously bad values
    fast[["ux", "uy", "uz"]] = fast[["ux", "uy", "uz"]].where(fast[["ux", "uy", "uz"]].abs() < 100)
    fast["sonic_temp"] = fast["sonic_temp"].where(fast["sonic_temp"].abs() < 60)
    fast["rho_co2"] = fast["rho_co2"].where(fast["rho_co2"].between(0, 5000))
    fast["rho_h2o"] = fast["rho_h2o"].where(fast["rho_h2o"].between(-10, 100))
    print(f"\tData Integrity After Diagnostic and Bounds Filtering")

    # filter out values based on diagnostic flags
    fast[["rho_co2", "rho_h2o"]] = fast[["rho_co2", "rho_h2o"]].where(fast["irga_diag"] == 0)
    fast[["ux", "uy", "uz", "sonic_temp"]] = fast[["ux", "uy", "uz", "sonic_temp"]].where(fast["sonic_diag"] == 0)
    # drop diagnostic columns
    fast = fast.drop(columns=["irga_diag", "sonic_diag"], errors="ignore")
    for c in fast.columns:
        print(f"\t\t{c}: {fast[c].count()/fast.shape[0]*100:.3f}%")

    # skewness and kurtosis filter
    thirty_minutes = 20*1800
    kurt_min, kurt_max = -3, 6
    skew_max = 3
    kurt = (
        fast
        .groupby((fast.index // thirty_minutes)*thirty_minutes)
        .apply(lambda x: x.kurtosis())
        .astype(np.float32)
        .reindex(fast.index).ffill()
        .astype(np.float16)
    )
    skew = (
        fast
        .groupby((fast.index // thirty_minutes)*thirty_minutes)
        .skew()
        .astype(np.float32)
        .reindex(fast.index).ffill()
        .astype(np.float16)
        .abs()
    )
    fast = fast.where(skew < skew_max)
    fast = fast.where((kurt > kurt_min) & (kurt < kurt_max)) # equivalent to regular kurtosis between 0 and 9

    print(f"\tData Integrity After Skewness and Kurtosis Filtering")
    for c in fast.columns:
        print(f"\t\t{c}: {fast[c].count()/fast.shape[0]*100:.3f}%")

    # remove periods with not enough data
    min_integrity = 0.9
    integrity = (
        fast
        .groupby((fast.index // thirty_minutes)*thirty_minutes)
        .apply(lambda x: x.notna().sum()/thirty_minutes)
        .astype(np.float32)
        .reindex(fast.index).ffill()
    )
    fast = fast.where(integrity >= min_integrity)
    print(f"\tData Integrity After Minimum Integrity Filtering")
    for c in fast.columns:
        print(f"\t\t{c}: {fast[c].count()/fast.shape[0]*100:.3f}%")

    if fast.isna().all().all():
        print(f"\t{args.output_file} is all nans after preprocessing")
        pd.DataFrame().to_csv(args.output_file, index=False, header=False, sep=",", float_format="%.5g")
        return
    print(f"\t{args.output_file} written successfully")
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
    

        