import numpy as np
import pandas as pd
import hesseflux as hf
from pathlib import Path
import argparse

def ustar_filter(fullout: pd.DataFrame) -> pd.Series:
    hesseflux_df = (
        fullout
        [["u*", "co2_flux", "air_temperature"]]
        .rename(columns={"u*":"USTAR", "co2_flux":"NEE", "air_temperature":"TA"})
        .assign(
            TA = lambda df: df["TA"] - 273.15,
        )
    )

    hesseflux_flag = (
        fullout[["qc_co2_flux", "qc_Tau"]]
        .rename(columns={"qc_co2_flux":"NEE", "qc_Tau":"USTAR"})
    )
    hesseflux_flag["NEE"] = np.where(hesseflux_flag["NEE"] < 2, 0, 2)  # convert to 0 for good data and 2 for bad data
    hesseflux_flag["USTAR"] = np.where(hesseflux_flag["USTAR"] < 2, 0, 2)  # convert to 0 for good data and 2 for bad data
    hesseflux_flag["TA"] = 0  # no TA flag, so just add a dummy one with all good values
    hesseflux_flag = hesseflux_flag

    hesseflux_isday = fullout[["daytime"]].rename(columns={"daytime":"isday"}).astype(bool)

    _, ustar_flag = hf.ustarfilter(
        hesseflux_df, 
        isday=hesseflux_isday,
        flag=hesseflux_flag,
        nboot=20,
        nmon=3,
        randomstate=8472,
        mindaysperyear=360,
        minseasondata=100,
        seasonout=True,
        ustardefault=0.2
    )

    ustar_flag = ustar_flag.astype(bool)

    return ustar_flag


def main():
    parser = argparse.ArgumentParser(description="Ingest raw data files from L0_raw and organize them into L0_ingested.")
    parser.add_argument("--L2_eddypro_outputs_dir", type=Path, help="Directory containing eddypro output files.")
    parser.add_argument("--eddypro_project_name", type=str, help="Name of the eddypro project to use.")
    parser.add_argument("--eddypro_run_id", type=str, help="ID of the eddypro run to use.")
    parser.add_argument("--L3a_filtered_dir", type=Path, help="Directory to save filtered data files.")
    args = parser.parse_args()

    ep_out_dir = args.L2_eddypro_outputs_dir / args.eddypro_project_name 
    
    # get the most recent run
    fullout_file = sorted(ep_out_dir.glob(f"eddypro_{args.eddypro_run_id}_full_output_*.csv"))[-1]
    fullout = pd.read_csv(fullout_file, skiprows=[0, 2], na_values=["-9999.00", "-9999"])
    # with open(fullout_file, "r") as f:
    #     f.readline()
    #     f.readline()
    #     units = f.readline().strip().split(",")
    #     units = {c:u.strip('[]') for c, u in zip(fullout.columns, units)}
    fullout["TIMESTAMP"] = pd.to_datetime(fullout["date"] + " " + fullout["time"])
    fullout = fullout.set_index("TIMESTAMP").sort_index()

    # filter out bad data based on QC flags
    # 0 = best, 1 = aggregate, 2 = bad
    fullout["H"] = np.where(fullout["qc_H"] < 2, fullout["H"], np.nan)
    fullout["LE"] = np.where(fullout["qc_LE"] < 2, fullout["LE"], np.nan)
    fullout["ET"] = np.where(fullout["qc_LE"] < 2, fullout["ET"], np.nan)
    fullout["co2_flux"] = np.where(fullout["qc_co2_flux"] < 2, fullout["co2_flux"], np.nan)
    fullout["h2o_flux"] = np.where(fullout["qc_h2o_flux"] < 2, fullout["h2o_flux"], np.nan)
    fullout["Tau"] = np.where(fullout["qc_Tau"] < 2, fullout["Tau"], np.nan)
    fullout["u*"] = np.where(fullout["qc_Tau"] < 2, fullout["u*"], np.nan)

    # U* filtering with hesseflux
    ustar_flag = ustar_filter(fullout)

    # update fluxes to reflect U* filtering (set to NaN if U* is below threshold)
    fullout["H_ustar"] = np.where(ustar_flag, fullout["H"], np.nan)
    fullout["LE_ustar"] = np.where(ustar_flag, fullout["LE"], np.nan)
    fullout["ET_ustar"] = np.where(ustar_flag, fullout["ET"], np.nan)
    fullout["co2_flux_ustar"] = np.where(ustar_flag, fullout["co2_flux"], np.nan)
    fullout["h2o_flux_ustar"] = np.where(ustar_flag, fullout["h2o_flux"], np.nan)

    # update QC flags to reflect U* filtering
    fullout["ustar_filter"] = ustar_flag
    
    # despike the data using MAD filter
    fullout.to_parquet(args.L3a_filtered_dir / f"filtered_{args.eddypro_project_name}_{args.eddypro_run_id}.parquet")

if __name__ == "__main__":
    main()