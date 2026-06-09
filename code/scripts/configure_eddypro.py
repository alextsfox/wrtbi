from pathlib import Path
from configparser import ConfigParser
import argparse

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Generate EddyPro project files based on the preprocessed biomet data.")
    parser.add_argument("--fast_files", type=Path, nargs='*', default=[], help="List of preprocessed fast data files for EddyPro.")
    parser.add_argument("--biomet_files", type=Path, nargs='*', default=[], help="List of preprocessed biomet data files for EddyPro.")
    parser.add_argument("--output_file", type=Path, required=True, help="Path to the output .eddypro project file.")
    parser.add_argument("--template", type=Path, required=True, help="Path to the EddyPro project template file.")
    parser.add_argument("--run_id", type=str, required=True, help="Run ID for the EddyPro project.")
    parser.add_argument("--project_title", type=str, required=True, help="Title for the EddyPro project.")
    args = parser.parse_args()

    config = ConfigParser()
    config.read(args.template)

    file_dates = [pd.to_datetime(file.stem, format=r"%Y_%m_%d_%Hh%Mm") for file in args.fast_files]
    start_date = min(file_dates)
    end_date = max(file_dates)
    config.set("Project", "pr_start_date", start_date.strftime(r"%Y-%m-%d"))
    config.set("Project", "pr_end_date", end_date.strftime(r"%Y-%m-%d"))
    config.set("Project", "pr_start_time", "00:00")
    config.set("Project", "pr_end_time", "23:30")
    config.set("Project", "pr_subset", "1")

    config.set("Project", "project_id", args.run_id)
    config.set("Project", "project_title", args.project_title)

    with open(args.output_file, "w") as f:
        f.write(";EDDYPRO_PROCESSING\n")
        config.write(f, space_around_delimiters=False)

if __name__ == "__main__":
    main()