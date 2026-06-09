import pandas as pd
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TOA5Data:
    fmt: str
    station_name: str
    datalogger_type: str
    sn: str
    os_version: str
    dld_name: str
    dld_signature: str
    table_name: str
    field_names: list[str]
    units: list[str]
    processing: list[str]
    data: pd.DataFrame

def read_toa5(file_path: Path, timestamp_index: bool = True) -> TOA5Data:
    with open(file_path, "r") as f:
        header_1 = f.readline().strip().split(',')
        varnames = f.readline().strip().split(',')
        units = f.readline().strip().split(',')
        statistics = f.readline().strip().split(',')
    data = pd.read_csv(file_path, skiprows=[0, 2, 3], na_values=[-9999, "NAN", "NA", "NaN"], parse_dates=["TIMESTAMP"])

    if timestamp_index:
        data.set_index("TIMESTAMP", inplace=True)
        varnames = varnames[1:]
        units = units[1:]
        statistics = statistics[1:]
    toa5_data = TOA5Data(
        fmt=header_1[0],
        station_name=header_1[1],
        datalogger_type=header_1[2],
        sn=header_1[3],
        os_version=header_1[4],
        dld_name=header_1[5],
        dld_signature=header_1[6],
        table_name=header_1[7],
        field_names=varnames,
        units=units,
        processing=statistics,
        data=data
    )

    return toa5_data