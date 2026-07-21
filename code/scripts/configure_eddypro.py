from pathlib import Path
from configparser import ConfigParser
import argparse
from datetime import datetime

import pandas as pd

PROC_PERIODS = [
    {
        "start": None,                      
        "end":   pd.Timestamp("2026-06-04"),
        "pfit_file": "/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi/code/configs/eddypro_configs/2026-03-25_2026-06-04.pfit",
        "spec_file": "/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi/code/configs/eddypro_configs/2026-03-25_2026-06-04.spec",
    },
    {
        "start": pd.Timestamp("2026-06-04"),
        "end":   None,                      
        "pfit_file": "/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi/code/configs/eddypro_configs/2026-06-04.pfit",
        "spec_file": "/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi/code/configs/eddypro_configs/2026-06-04.spec",
    },
]


def get_overlapping_periods(start_date: pd.Timestamp, end_date: pd.Timestamp) -> list:
    """Return the subset of TILT_PERIODS that overlap with [start_date, end_date]."""
    overlapping = []
    for period in PROC_PERIODS:
        p_start = period["start"] if period["start"] is not None else start_date
        p_end   = period["end"]   if period["end"]   is not None else end_date
        if p_start < end_date and p_end > start_date:
            overlapping.append(period)
    return overlapping


def build_config(template: Path, period: dict,
                 eff_start: pd.Timestamp, eff_end: pd.Timestamp,
                 run_id: str, project_title: str, eddypro_output_path: str) -> ConfigParser:
    config = ConfigParser()
    config.read(template)
    config.set("Project", "pr_start_date", eff_start.strftime(r"%Y-%m-%d"))
    config.set("Project", "pr_end_date",   eff_end.strftime(r"%Y-%m-%d"))
    config.set("Project", "pr_start_time", "00:00")
    config.set("Project", "pr_end_time",   "23:30")
    config.set("Project", "pr_subset",     "1")

    config.set("RawProcess_TiltCorrection_Settings", "pf_file", period["pfit_file"])
    config.set("RawProcess_TiltCorrection_Settings", "pf_mode", "0")

    config.set("FluxCorrection_SpectralAnalysis_General", "sa_file", period["spec_file"])
    config.set("FluxCorrection_SpectralAnalysis_General", "sa_mode", "0")

    config.set("Project", "project_id",    run_id)
    config.set("Project", "project_title", project_title)

    config.set("Project", "out_path", eddypro_output_path)
    return config


def write_config(config: ConfigParser, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(";EDDYPRO_PROCESSING\n")
        config.write(f, space_around_delimiters=False)
    print(f"Written: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate EddyPro project files based on the preprocessed data.")
    parser.add_argument("--fast_files", type=Path, nargs='*', default=[], help="List of preprocessed fast data files for EddyPro.")
    parser.add_argument("--biomet_files", type=Path, nargs='*', default=[], help="List of preprocessed biomet data files for EddyPro.")
    parser.add_argument("--output_dir", type=Path, required=True, help="Base path for the output .eddypro project file(s).")
    parser.add_argument("--template", type=Path, required=True, help="Path to the EddyPro project template file.")
    parser.add_argument("--run_id", type=str, required=True, help="Run ID for the EddyPro project.")
    parser.add_argument("--project_title", type=str, required=True, help="Title for the EddyPro project.")
    parser.add_argument("--eddypro_output_path", type=Path, required=True, help="Output path for the EddyPro project files.")
    args = parser.parse_args()

    file_dates = [pd.to_datetime(f.stem, format=r"%Y_%m_%d_%Hh%Mm") for f in args.fast_files]
    start_date = min(file_dates)
    end_date   = max(file_dates)

    periods = get_overlapping_periods(start_date, end_date)
    if not periods:
        raise ValueError(f"No tilt-correction period found covering {start_date} - {end_date}. "
                         "Add an entry to TILT_PERIODS.")

    if not args.output_dir.exists():
        args.output_dir.mkdir(parents=True, exist_ok=True)

    for period in periods:
        p_start = period["start"] if period["start"] is not None else start_date
        p_end   = period["end"]   if period["end"]   is not None else end_date
        out_path = args.output_dir / f"{args.project_title}_{args.run_id}_{p_start.strftime(r'%Y-%m-%d')}_{p_end.strftime(r'%Y-%m-%d')}.eddypro"
        eff_start = max(start_date, p_start)
        eff_end   = min(end_date,   p_end)
        config = build_config(args.template, period, eff_start, eff_end,
                               args.run_id, args.project_title, str(args.eddypro_output_path))
        write_config(config, out_path)

    with open(args.output_dir / ".sentinel", "w") as f:
        f.write("")

if __name__ == "__main__":
    main()