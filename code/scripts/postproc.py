import argparse
from pathlib import Path

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Post-process EddyPro output files to prepare them for analysis.")
    parser.add_argument("--ep_out_dir", type=Path, required=True, help="Path to the input EddyPro output directory.")
    parser.add_argument("--run_id", type=str, required=True, help="Run ID for the EddyPro project.")
    parser.add_argument("--output_file", type=Path, required=True, help="Path to the output post-processed parquet file.")
    args = parser.parse_args()

    fullout_files = sorted(args.ep_out_dir.glob(f"eddypro_{args.run_id}_full_output_*_adv.csv"))
    dfs = []
    for f in fullout_files:
        df = pd.read_csv(f, skiprows=[0, 2], na_values=["-9999.00", "-9999"])
        df["TIMESTAMP"] = pd.to_datetime(df["date"] + " " + df["time"])
        df = df.set_index("TIMESTAMP").sort_index()
        float_cols = df.select_dtypes(include=["float"]).columns
        df[float_cols] = df[float_cols].astype("float32")
        dfs.append(df)
    dfs = pd.concat(dfs).sort_index()
    dfs = dfs[~dfs.index.duplicated(keep="last")]

    dfs.to_parquet(args.output_file)

if __name__ == "__main__":
    main()