import argparse
from pathlib import Path

import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Post-process EddyPro output files to prepare them for analysis.")
    parser.add_argument("--ep_out_dir", type=Path, required=True, help="Path to the input EddyPro output directory.")
    parser.add_argument("--run_id", type=str, required=True, help="Run ID for the EddyPro project.")
    parser.add_argument("--output_file", type=Path, required=True, help="Path to the output post-processed parquet file.")
    args = parser.parse_args()

    import sys
    sys.path.append("/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/PostProc")
    from FluxFox import postproc

    fullout_files = sorted(args.ep_out_dir.glob(f"eddypro_{args.run_id}_full_output_*_adv.csv"))
    fullout = []
    for f in fullout_files:
        df = pd.read_csv(f, skiprows=[0, 2], na_values=["-9999.00", "-9999"])
        df["TIMESTAMP"] = pd.to_datetime(df["date"] + " " + df["time"])
        df = df.set_index("TIMESTAMP").sort_index()
        float_cols = df.select_dtypes(include=["float"]).columns
        df[float_cols] = df[float_cols].astype("float32")
        fullout.append(df)
    fullout = pd.concat(fullout).sort_index()
    fullout = fullout[~fullout.index.duplicated(keep="last")]

    biomet = pd.concat([pd.read_feather(f) for f in Path("/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi/L0c_ingested/SlowRaw").glob("*.feather")])

    
    # isday = postproc.compute_isday(df.index, lat=43.200, lon=-108.8134, elev=1654, sw_thresh=20)
    # cols_to_despike = ["H", "LE", "ET", "FC", "CO2", "H2O"]

    # cols_to_keep = [
    #     "H", "LE", "ET", "FC", 
    #     "CO2", "H2O", 
    #     "T_SONIC", "USTAR", "U", "V", "W", "U_VAR", "V_VAR", "W_VAR",   
    # ]

    # keep = postproc.despike_mad_papale_2006(
    #     df=fullout[cols_to_despike],
    #     isday=isday,
    #     cols_to_despike=cols_to_despike,
    #     z=6,
    #     chunksize_days=13,
    # )
    # fullout[cols_to_despike] = fullout[cols_to_despike].where(keep)

    # fullout.loc[keep].to_parquet(args.output_file)

if __name__ == "__main__":
    main()