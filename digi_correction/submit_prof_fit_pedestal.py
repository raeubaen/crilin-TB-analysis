#!/usr/bin/env python3

import argparse
import csv
import glob
import subprocess
from pathlib import Path

DEFAULT_RUNS = {
    #386: 100,
    #395: 20,
    #401: 34,
    #403: 52,
    #404: 74,
    413: 120,
    429: 65,
    #435: 10,
}

RERECO = Path("/eos/experiment/muoncollider/data/crilin/h2-2026/re-reco_dqm_template")
OUTBASE = Path.home() / "pedestals_digi_corr"
WWW = "/eos/user/r/rgargiul/www/digi_corr_crilin_pedestal_profiles_checks"


def sh(cmd, dry):
    print(cmd)
    if not dry:
        subprocess.run(["bash", "-lc", cmd], check=True)


def read_runs(csvfile):
    if csvfile is None:
        return DEFAULT_RUNS

    runs = {}
    with open(csvfile) as f:
        for r in csv.DictReader(f):
            runs[int(r["run"])] = int(r["energy"])
    return runs


parser = argparse.ArgumentParser()
parser.add_argument("--dry", action="store_true",
                    help="Print commands without executing them")
parser.add_argument("--csv",
                    help="CSV file with columns: run,energy")
args = parser.parse_args()


for run, energy in read_runs(args.csv).items():

    matches = glob.glob(f"{RERECO}/run_{run:07d}_*")
    if len(matches) != 1:
        raise RuntimeError(f"Run {run}: trovati {len(matches)} match")

    rundir = Path(matches[0])
    runname = rundir.name.replace("run_", "", 1)

    infile = next(
        rundir.glob(f"cat_{runname}_{energy}GeV_pedestals.root"),
        None,
    )
    if infile is None:
        raise RuntimeError(f"File non trovato in {rundir}")

    outdir = OUTBASE / f"run{run}_{energy}GeV"
    prefix = outdir / f"run{run}_{energy}GeV_pedestal_corr"

    print(f"\n=== run {run} ({energy} GeV) ===")

    sh(f"mkdir -p {outdir}", args.dry)

    sh(
        f'source ~/crilin-TB-calib/digi_correction/prof_fit_pedestal.sh '
        f'{infile} "{prefix}"',
        args.dry,
    )

    sh(
        f"cd {outdir} && "
        f"hadd -f run{run}_{energy}GeV_pedestal_corr_all.root *.root",
        args.dry,
    )

    sh(
        f"cd {outdir} && "
        f"pdfunite *.pdf run{run}_{energy}GeV_pedestal_corr_prof_corr_all.pdf",
        args.dry,
    )

    sh(
        f"cp {outdir}/run{run}_{energy}GeV_pedestal_corr_prof_corr_all.pdf {WWW}/",
        args.dry,
    )

    sh(
        f"cd {outdir} && "
        f"find . -maxdepth 1 -name '*.root' "
        f"! -name 'run{run}_{energy}GeV_pedestal_corr_all.root' -delete",
        args.dry,
    )

    sh(
        f"cd {outdir} && "
        f"find . -maxdepth 1 -name '*.pdf' "
        f"! -name 'run{run}_{energy}GeV_pedestal_corr_prof_corr_all.pdf' -delete",
        args.dry,
    )

print("\nDone.")
