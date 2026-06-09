from pathlib import Path
from configparser import ConfigParser
from datetime import datetime, timedelta
import subprocess
import tempfile
import shutil
from tqdm import trange
from time import sleep
from multiprocessing import Pool

runno = 4

def run_eddypro(days_offset):
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ConfigParser()
        wd = Path("/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi")
        config.read(wd / "code/configs/wrtbi-template.eddypro")
        
        pf_start_date = datetime(2026, 4, 20)
        pf_end_date = pf_start_date + timedelta(days=days_offset)

        # copy the input files for this run to a temp directory to avoid issues with file locking across runs
        in_path = Path(tmpdir) / "pf_issue_input"
        in_path.mkdir(exist_ok=True)
        (in_path / "fast_for_eddypro").mkdir(exist_ok=True)
        (in_path / "biomet_for_eddypro").mkdir(exist_ok=True)
        template_in_path = config.get("RawProcess_General", "data_path")
        print(f"Copying input files...{template_in_path} to {in_path / 'fast_for_eddypro'}, days_offset={days_offset}")
        for file in Path(template_in_path).glob("*"):
            shutil.copy(file, in_path / "fast_for_eddypro" / file.name)
        template_biomet_path = config.get("Project", "biom_dir")
        for file in Path(template_biomet_path).glob("*"):
            shutil.copy(file, in_path / "biomet_for_eddypro" / file.name)
        config.set("RawProcess_General", "data_path", str(in_path / "fast_for_eddypro"))
        config.set("Project", "biom_dir", str(in_path / "biomet_for_eddypro"))
        # also copy the executable file
        shutil.copy("/opt/eddypro-engine-master/bin/mac/eddypro_rp", tmpdir)

        # change the length of the planar fit run        
        config.set("RawProcess_TiltCorrection_Settings", "pf_start_date", pf_start_date.strftime(r"%Y-%m-%d"))
        config.set("RawProcess_TiltCorrection_Settings", "pf_end_date", pf_end_date.strftime(r"%Y-%m-%d"))
        config.set("RawProcess_TiltCorrection_Settings", "pf_subset", "1")
        config.set("RawProcess_TiltCorrection_Settings", "pf_mode", "1")

        # make the project start and end dates be super short to speed up the run: we only care about the planar fit
        config.set("Project", "pr_start_date", pf_start_date.strftime(r"%Y-%m-%d"))
        config.set("Project", "pr_end_date", (pf_start_date).strftime(r"%Y-%m-%d"))
        config.set("Project", "pr_start_time", "00:00")
        config.set("Project", "pr_end_time", "06:00")
        config.set("Project", "pr_subset", "1")

        out_path = wd / f"code/tests/pf_issues_{runno}_{pf_end_date.strftime(r'%Y%m%d')}"
        out_path.mkdir(exist_ok=True)

        config.set("Project", "out_path", str(out_path))
        config.set("Project", "project_id", f"pf_issue_{runno}_{pf_end_date.strftime(r'%Y%m%d')}")
        project_file = out_path / f"pf_issue_{runno}_{pf_end_date.strftime(r'%Y%m%d')}.eddypro"
        with open(project_file, "w") as f:
            f.write(";EDDYPRO_PROCESSING\n")
            config.write(f, space_around_delimiters=False)

        (out_path / "tmp").mkdir(exist_ok=True)
        with open(out_path / f"pf_issue_{runno}_{pf_end_date.strftime(r'%Y%m%d')}.log", "w") as logf:
                subprocess.run([
                    str(Path(tmpdir) / "eddypro_rp"),
                    "-s", "mac",
                    "-m", "desktop",
                    "-c", "console",
                    "-e", str(out_path),
                    str(project_file)
                ], stdout=logf, stderr=subprocess.STDOUT)

if __name__ == "__main__":
    wd = Path("/Users/alex/Library/CloudStorage/OneDrive-UniversityofWyoming/Work/UWyo/Research/WyACT/wrtbi")
    days_offsets = list(range(1, 4))

    with Pool() as pool:
        pool.map(run_eddypro, days_offsets)