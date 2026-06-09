from dataclasses import dataclass
from pathlib import Path
import json
import argparse

import pandas as pd


@dataclass
class StartEnd:
    start: pd.Timestamp
    end: pd.Timestamp

def main():
    parser = argparse.ArgumentParser(description="Compute the mapping from output file names to input file names for the concat step of the pipeline.")
    parser.add_argument("--input_files", nargs="+", type=Path, required=True, help="List of input files to consider for concatenation.")
    parser.add_argument("--output_file", type=Path, required=True, help="Path to the output pickle file that will contain the concat mapping.")
    parser.add_argument("--file_time_span", type=str, required=True, help="Time span for each output file (e.g., '1D' for daily files).")
    parser.add_argument("--aq_freq", type=str, required=True, help="Frequency of data points in the output files (e.g., '30min' for 30 minute intervals).")
    args = parser.parse_args()

    raw_start_end: dict[Path, StartEnd] = {}
    target_start_end: dict[str, StartEnd] = {}

    for file in args.input_files:
        tmp = pd.read_feather(file, columns=["TIMESTAMP"]).set_index("TIMESTAMP")
        fstart, fend = tmp.index.min(), tmp.index.max()
        raw_start_end[file] = StartEnd(fstart, fend)
    raw_start_end = dict(sorted(raw_start_end.items(), key=lambda item: item[1].start))

    record_start = list(raw_start_end.values())[0].start.floor(args.file_time_span)
    record_end = list(raw_start_end.values())[-1].end.ceil(args.file_time_span)
    target_start_end = {
        intvl.left.strftime(r"%Y_%m_%d_%Hh%Mm"): StartEnd(intvl.left, intvl.right - pd.Timedelta(args.aq_freq))
        for intvl in pd.interval_range(start=record_start, end=record_end, freq=args.file_time_span)
    }

    # we now have the start and end times for each raw file and for each output file
    # next, we must determine the overlap between each raw file and each output file, and use that to 
    # determine which raw files should be combined to create each output file
    # the result will be a dict that maps each output file name to a list of raw files that should be concatenated to create it, which can then be used as the input to the next step of the pipeline
    # {output_file_name: [raw_file1, raw_file2, ...], ...}
    # our problem boils down to:
    # given an interval [a1, a2] and a set of intervals{[b1, b2], [b2, b3], [b4, b5],...], find all intervals that overlap with [a, b]
    concat_mapping: dict[str, list[Path]] = {}
    for tgt_name, tgt_intvl in target_start_end.items():
        # print(f"Searching for files that overlap with target interval {tgt_name} ({tgt_intvl.start} to {tgt_intvl.end})")
        cover = []
        for fp, cand_intvl in raw_start_end.items():
            # print(f"\tChecking candidate file {fp} ({cand_intvl.start} to {cand_intvl.end})")
            if tgt_intvl.start <= cand_intvl.end and tgt_intvl.end > cand_intvl.start:
                # print(f"\t\tSuccess.")
                cover.append(fp)
        concat_mapping[tgt_name] = cover

    # for k, v in concat_mapping.items():
    #     print(k)
    #     print(f"\t{v}")

    with open(args.output_file, "w") as f:
        json.dump({k: [str(fp) for fp in v] for k, v in concat_mapping.items()}, f)


if __name__ == "__main__":
    main()