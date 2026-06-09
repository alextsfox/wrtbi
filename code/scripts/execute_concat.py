import argparse
from pathlib import Path

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Concatenate parquet files by time interval.")
    parser.add_argument("--input_files", type=Path, nargs="*", default=[], help="Path to the input parquet files.")
    parser.add_argument("--out_file", type=Path, required=True, help="Path to the output parquet file (e.g., '2023_01_01_00h00m.parquet').")
    parser.add_argument("--file_timespan", type=str, required=True, help="Time interval for averaging data (e.g., '1D' for 1 day).")
    parser.add_argument("--aq_freq", type=str, required=True, help="Frequency of data points in the output files (e.g., '30min' for 30 minute intervals).")
    args = parser.parse_args()

    if not args.input_files:
        print(f"No input files found for output stem {args.out_file.stem}. Skipping.")
        return
    
    df = pd.concat([pd.read_feather(file) for file in args.input_files]).set_index("TIMESTAMP")

    tstart = pd.to_datetime(args.out_file.stem, format=r"%Y_%m_%d_%Hh%Mm")
    tend = tstart + pd.Timedelta(args.file_timespan) - pd.Timedelta(args.aq_freq)
    new_idx = pd.date_range(start=tstart, end=tend, freq=args.aq_freq)

    df = df.reindex(new_idx).sort_index()

    df.to_feather(args.out_file)

    return

if __name__ == "__main__":
    main()

    
    
