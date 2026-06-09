"""
Process raw data files from L0b_ingested to prepare them for analysis and intake by eddypro

Also perform some basic cleaning on the data

Contains lots of business logic for how to handle, name, combine, and clean data from different sources and time periods.
"""

from pathlib import Path
import argparse

import pandas as pd
import numpy as np

def preprocess_biomet_data(f: Path, args) -> None:
    biomet = (
        pd.read_feather(f)
        .replace([-9999, -7999, 7999, np.inf, -np.inf], np.nan)
        .reset_index(names="TIMESTAMP")
        .drop_duplicates(subset=["TIMESTAMP"], keep="last")
        .set_index("TIMESTAMP")
        .sort_index()
    )

    out_cols = [
        "TIMESTAMP_1", "Ta_0_0_1", "Ta_0_1_1", "Pa_0_0_1", "Pa_0_1_1", "RH_0_0_1", "Tc_0_0_1", "Rn_0_0_1", "Rg_0_0_1", "Rr_0_0_1", "LWin_0_0_1", "LWout_0_0_1", "SWin_0_0_1", "SWout_0_0_1", "PPFD_0_0_1", "MWS_0_0_1", "WD_0_0_1",
        "Ts_0_0_1", "Ts_0_1_1", "Ts_0_2_1", "Ts_1_0_1", "Ts_1_1_1", "Ts_1_2_1", "SWC_0_0_1", "SWC_0_1_1", "SWC_0_2_1", "SWC_1_0_1", "SWC_1_1_1", "SWC_1_2_1", "SHF_0_0_1", "SHF_1_0_1", "SHF_2_0_1"
    ]
    out_units = [
        "yyyy-mm-dd HHMM", "C", "C", "kPa", "kPa", "%", "C", "W+1m-2", "W+1m-2", "W+1m-2", "W+1m-2", "W+1m-2", "W+1m-2", "W+1m-2", "umol+1m-2s-1", "m+1s-1", "degrees",
        "C", "C", "C", "C", "C", "C", "m+3m-3", "m+3m-3", "m+3m-3", "m+3m-3", "m+3m-3", "m+3m-3", "W+1m-2", "W+1m-2", "W+1m-2"
    ]

    # VAR_X_Y_Z codes
    # from https://www.europe-fluxdata.eu/home/guidelines/how-to-submit-data/variables-codes:
    # X (0-indexed): horizontal ID
    # Y (0-indexed): vertical ID (numeration increases downwards into the ground and upwards into the atmosphere)
    # Z: (1-indexed): replicate ID
    # this differs from Ameriflux naming, where the vertical ID always increases downwards, and IDs are always 1-indexed
    biomet_for_eddypro = biomet.copy()
    biomet_for_eddypro["TIMESTAMP_1"] = biomet_for_eddypro.index.strftime(r"%Y-%m-%d %H%M")
    biomet_for_eddypro["Ta_0_0_1"] = biomet_for_eddypro.get("irgason_temp_Avg", np.nan)
    biomet_for_eddypro["Ta_0_1_1"] = biomet_for_eddypro.get("temp_Avg", np.nan)
    biomet_for_eddypro["Pa_0_0_1"] = biomet_for_eddypro.get("irgason_press_Avg", np.nan)
    biomet_for_eddypro["Pa_0_1_1"] = biomet_for_eddypro.get("press_Avg", np.nan)
    biomet_for_eddypro["RH_0_0_1"] = biomet_for_eddypro.get("rh_Avg", np.nan)
    biomet_for_eddypro["Tc_0_0_1"] = biomet_for_eddypro.get("T_CANOPY_Avg", np.nan)
    biomet_for_eddypro["Rn_0_0_1"] = biomet_for_eddypro.get("sw_in_Avg", np.nan) - biomet_for_eddypro.get("sw_out_Avg", np.nan) + biomet_for_eddypro.get("lw_in_Avg", np.nan) - biomet_for_eddypro.get("lw_out_Avg", np.nan)
    biomet_for_eddypro["Rg_0_0_1"] = biomet_for_eddypro.get("sw_in_Avg", np.nan)
    biomet_for_eddypro["Rr_0_0_1"] = biomet_for_eddypro.get("sw_out_Avg", np.nan)
    biomet_for_eddypro["LWin_0_0_1"] = biomet_for_eddypro.get("lw_in_Avg", np.nan)
    biomet_for_eddypro["LWout_0_0_1"] = biomet_for_eddypro.get("lw_out_Avg", np.nan)
    biomet_for_eddypro["SWin_0_0_1"] = biomet_for_eddypro.get("sw_in_Avg", np.nan)
    biomet_for_eddypro["SWout_0_0_1"] = biomet_for_eddypro.get("sw_out_Avg", np.nan)
    biomet_for_eddypro["PPFD_0_0_1"] = biomet_for_eddypro.get("ppfd_Avg", np.nan)
    biomet_for_eddypro["MWS_0_0_1"] = biomet_for_eddypro.get("irgason_ws_Max", np.nan)
    biomet_for_eddypro["WD_0_0_1"] = biomet_for_eddypro.get("irgason_wd_Avg", np.nan)

    biomet_for_eddypro["Ts_0_0_1"] = biomet_for_eddypro.get("soil_temp_A_5cm_Avg", np.nan)
    biomet_for_eddypro["Ts_0_1_1"] = biomet_for_eddypro.get("soil_temp_A_10cm_Avg", np.nan)
    biomet_for_eddypro["Ts_0_2_1"] = biomet_for_eddypro.get("soil_temp_A_30cm_Avg", np.nan)
    biomet_for_eddypro["Ts_1_0_1"] = biomet_for_eddypro.get("soil_temp_B_5cm_Avg", np.nan)
    biomet_for_eddypro["Ts_1_1_1"] = biomet_for_eddypro.get("soil_temp_B_10cm_Avg", np.nan)
    biomet_for_eddypro["Ts_1_2_1"] = biomet_for_eddypro.get("soil_temp_B_30cm_Avg", np.nan)

    biomet_for_eddypro["SWC_0_0_1"] = biomet_for_eddypro.get("vwc_A_5cm_Avg", np.nan)
    biomet_for_eddypro["SWC_0_1_1"] = biomet_for_eddypro.get("vwc_A_10cm_Avg", np.nan)
    biomet_for_eddypro["SWC_0_2_1"] = biomet_for_eddypro.get("vwc_A_30cm_Avg", np.nan)
    biomet_for_eddypro["SWC_1_0_1"] = biomet_for_eddypro.get("vwc_B_5cm_Avg", np.nan)
    biomet_for_eddypro["SWC_1_1_1"] = biomet_for_eddypro.get("vwc_B_10cm_Avg", np.nan)
    biomet_for_eddypro["SWC_1_2_1"] = biomet_for_eddypro.get("vwc_B_30cm_Avg", np.nan)

    biomet_for_eddypro["SHF_0_0_1"] = biomet_for_eddypro.get("G_A_5cm_Avg", np.nan)
    biomet_for_eddypro["SHF_1_0_1"] = biomet_for_eddypro.get("G_B_5cm_Avg", np.nan)
    biomet_for_eddypro["SHF_2_0_1"] = biomet_for_eddypro.get("G_C_5cm_Avg", np.nan)

    biomet_for_eddypro = biomet_for_eddypro[out_cols]
    biomet_for_eddypro = biomet_for_eddypro.replace([np.inf, -np.inf, np.nan], np.nan)

    with open(args.output_file, "w") as file:
        file.write(",".join(out_cols) + "\n")
        file.write(",".join(out_units) + "\n")
    biomet_for_eddypro.to_csv(args.output_file, mode="a", header=False, index=False, float_format="%.5f", na_rep="-9999")

    return

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_file", type=Path)
    parser.add_argument("--stats_file", type=Path, default=None)
    parser.add_argument("--output_file", type=Path)
    args = parser.parse_args()

    preprocess_biomet_data(args.stats_file, args)

if __name__ == "__main__":
    main()
    

        