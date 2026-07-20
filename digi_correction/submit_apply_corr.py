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
    #413: 120,
    #429: 65,
    435: 10,
}

RERECO = Path("/eos/experiment/muoncollider/data/crilin/h2-2026/re-reco_dqm_template")
PED = Path.home() / "pedestals_digi_corr"
WORKDIR = Path("/root/crilin-TB-analysis/digi_correction")


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
                    help="CSV file with columns run,energy")
args = parser.parse_args()


for run, energy in read_runs(args.csv).items():

    matches = glob.glob(f"{RERECO}/run_{run:07d}_*")
    if len(matches) != 1:
        raise RuntimeError(f"Run {run}: trovati {len(matches)} match")

    rundir = Path(matches[0])
    runname = rundir.name.replace("run_", "", 1)

    electrons = next(
        rundir.glob(f"cat_{runname}_{energy}GeV_electrons.root"),
        None,
    )
    if electrons is None:
        raise RuntimeError(f"File electrons non trovato in {rundir}")

    pedestal = (
        PED
        / f"run{run}_{energy}GeV"
        / f"run{run}_{energy}GeV_pedestal_corr_all.root"
    )

    if not pedestal.exists() and not args.dry:
        raise RuntimeError(f"Pedestal corretto non trovato: {pedestal}")

    print(f"\n=== run {run} ({energy} GeV) ===")

    sh(
        f"cd {WORKDIR} && "
        f"python3 apply_corr.py "
        f"{electrons} "
        f"{pedestal} "
        f"{rundir} "
        f"{energy}",
        args.dry,
    )

print("\nDone.")
