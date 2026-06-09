import re
import datetime
import numpy as np
from dataclasses import dataclass


@dataclass
class PlanarFitResult:
    n_sectors: int
    min_data_per_sector: int
    max_wbar: float
    min_ubar: float
    start: datetime.date
    end: datetime.date
    sectors: list[tuple[int, int]]   # (start_deg, end_deg) for each sector
    coef: list[tuple[float, float, float]]  # (B0, B1, B2) for each sector
    n_data: list[int]                # sector numerosity
    R: list[np.ndarray]           # 3x3 rotation matrices

def _parse_colon_separated_line(line: str) -> str:
    return line.strip().split(":")[-1].strip()


def parse_planar_fit(path: str) -> PlanarFitResult:
    with open(path) as f:
        while f.readline().strip() != "Planar_fit_results":
            pass
        n_sectors = int(_parse_colon_separated_line(f.readline()))
        min_data_per_sector = int(_parse_colon_separated_line(f.readline()))
        max_wbar = float(_parse_colon_separated_line(f.readline()))
        min_ubar = float(_parse_colon_separated_line(f.readline()))
        start = datetime.datetime.strptime(_parse_colon_separated_line(f.readline()), r"%Y-%m-%d").date()
        end = datetime.datetime.strptime(_parse_colon_separated_line(f.readline()), r"%Y-%m-%d").date()

        sectors = []
        coef = []
        n_data = []
        R = []
        
        while f.readline().strip() != "Fitting planes coefficients":
            pass
        f.readline()  # skip header
        for _ in range(n_sectors):
            line = f.readline().strip()
            _, start_deg, end_deg, B0, B1, B2 = re.split(r"\s+", line)
            start_deg = start_deg[:-1]
            sectors.append((int(start_deg), int(end_deg)))
            coef.append((float(B0), float(B1), float(B2)))

        while f.readline().strip() != "Rotation matrices":
            pass

        for _ in range(n_sectors):    
            n_data.append(int(_parse_colon_separated_line(f.readline())))
            R1 = re.split(r"\s+", f.readline().strip())
            R2 = re.split(r"\s+", f.readline().strip())
            R3 = re.split(r"\s+", f.readline().strip())
            R.append(np.array([
                [float(R1[0]), float(R1[1]), float(R1[2])],
                [float(R2[0]), float(R2[1]), float(R2[2])],
                [float(R3[0]), float(R3[1]), float(R3[2])]
            ]))

    for i in range(n_sectors):
        R[i] = np.where(R[i] == -9999, np.nan, R[i])
        for j in range(3):
            if coef[i][j] == -9999:
                coef[i][j] = np.nan
    
        
    return PlanarFitResult(
        n_sectors=n_sectors,
        min_data_per_sector=min_data_per_sector,
        max_wbar=max_wbar,
        min_ubar=min_ubar,
        start=start,
        end=end,
        sectors=sectors,
        coef=coef,
        n_data=n_data,
        R=R
    )

if __name__ == "__main__":
    pf_result = parse_planar_fit("/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi/code/tests/pf_issues_20260329/eddypro_pf_issue_20260329_planar_fit_2026-06-09T101639_adv.txt")
    print(pf_result)


       