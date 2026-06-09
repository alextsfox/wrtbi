"""
Ingest raw data files from L0a_raw and organize them into L0b_ingested.

1. Convert .dat files to intermediate .parquet files using camp2ascii and save them in a temporary directory.
2. Restructure intermediate files into files of fixed time intervals (e.g., 1 day for fast data, 7 days for slow data)
3. Fill missing timestamps with NaN values to ensure consistent time intervals.
4. Save the restructured files to L0b_ingested
5. Keep track of processed files in a .processed_files text file to avoid reprocessing the same files in future runs.
"""

import argparse
from pathlib import Path
import tempfile


import camp2ascii as c2a

def main():
    parser = argparse.ArgumentParser(description="Ingest raw data files from L0_raw and organize them into L0_ingested.")
    parser.add_argument("--file", type=Path, help="Input .dat file to convert.")
    parser.add_argument("--output", type=Path, help="Output .parquet file path.")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="convert_") as tmp:
        converted_file = next(c2a.camp2ascii([args.file], Path(tmp), pbar=True, verbose=1, n_invalid=10, output_format=2))
        converted_file.rename(args.output)

if __name__ == "__main__":
    main()
