import numpy as np
import pandas as pd
import hesseflux as hf
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(description="Ingest raw data files from L0_raw and organize them into L0_ingested.")
    parser.add_argument("--L3a_filtered_dir", type=Path, help="Directory containing filtered data files.")
    parser.add_argument("--eddypro_project_name", type=str, help="Name of the eddypro project to use.")
    parser.add_argument("--eddypro_run_id", type=str, help="ID of the eddypro run to use.")
    parser.add_argument("--L3b_gapfill_dir", type=Path, help="Directory to save gap-filled data files.")
    args = parser.parse_args()

    filtered = pd.read_parquet(args.L3a_filtered_dir / f"filtered_{args.eddypro_project_name}_{args.eddypro_run_id}.parquet")

    # gapfill
    # TODO: add this bit

    filtered.to_parquet(args.L3b_gapfill_dir / f"gapfilled_{args.eddypro_project_name}_{args.eddypro_run_id}.parquet")

if __name__ == "__main__":
    main()
