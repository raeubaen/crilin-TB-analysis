import sys
import uproot
import ROOT
import pandas as pd
import numpy as np

# ======================================================
# Files
# ======================================================


dummy = False

root_file = sys.argv[1] #"../cat_386_100GeV_v3.0.root"
energy = sys.argv[2]

tree_name = "tree"


# ======================================================
# Read calibration coefficients
# ======================================================

if not dummy:
    df = pd.read_csv("/home/ruben/Downloads/calibfile_fullstatistics.csv")

    nx = df["ix"].max() + 1
    ny = df["iy"].max() + 1
    nz = df["layer"].max() + 1

    coeff = np.ones((nx, ny, nz), dtype=np.float32)

    coeff[
        df["ix"].to_numpy(np.int32),
        df["iy"].to_numpy(np.int32),
        df["layer"].to_numpy(np.int32),
    ] = 32.7709/26.2086*42.0224/df["mpv"].to_numpy(np.float32)

# ======================================================
# Read ROOT tree
# ======================================================


print("starting to open")

event_sum_all = []

branches = [
    "crilin_ix",
    "crilin_iy",
    "crilin_layer",
    "crilin_peak",
    "beamcatcher_peak",
    #"crilin_ix_centroid",
    #"crilin_iy_centroid",
]

coeffs = []
with uproot.open(root_file) as f:
    tree = f[tree_name]

    for arr in tree.iterate(branches, library="np", step_size="100 MB"):

        arr["crilin_gain"] = np.ones_like(arr["crilin_layer"])
        arr["crilin_gain"][arr["crilin_layer"] == 4] *= 6
        arr["crilin_gain"][arr["crilin_layer"] == 3] *= 4
        arr["crilin_gain"][arr["crilin_layer"] == 0] *= 4

        print("new step")
        ix = np.stack(arr["crilin_ix"]).astype(int)
        iy = np.stack(arr["crilin_iy"]).astype(int)
        layer = np.stack(arr["crilin_layer"]).astype(int)
        peak = np.stack(arr["crilin_peak"])
        thr = peak > np.stack(3/arr["crilin_gain"])

        if dummy:
            peak *= thr
            #pass
        else:
            peak *= coeff[ix, iy, layer]
            peak *= thr

        coeffs.append(coeff[ix, iy, layer])

        print(arr["beamcatcher_peak"].shape)

        mask = (
            (arr["beamcatcher_peak"][:, 0] > -10) #was < 10
            & (peak[:, 223]*4 < 1400) & (peak[:, 224]*6 < 1400)
            #& (np.abs(14 * arr["crilin_ix_centroid"]) < 2)
            #& (np.abs(14 * arr["crilin_iy_centroid"]) < 2)
        )

        print(mask.shape)
        print(peak.shape)
        event_sum = peak.sum(axis=1)

        print("shape peak sum per chunk: ", event_sum.shape)
        event_sum_all.append(event_sum)

event_sum = np.concatenate(event_sum_all)/1e3

coeffs_array = np.concatenate(coeffs)

#with uproot.recreate("calib_coeff_for_friendship.root") as f:
#  f["calib_tree"] = coeffs_array


print(event_sum)

# ======================================================
# Histogram
# ======================================================

h = ROOT.TH1D(
    "hEventSum",
    "Calibrated Event Sum;Calibrated Sum;Events",
    15000,
    0,
    150
)

weights = np.ones(event_sum.size, dtype=np.float64)

h.FillN(event_sum.size, event_sum.astype(np.float64), weights)

c = ROOT.TCanvas("c", "Event Sum", 800, 600)
h.Draw("HIST")

h.SaveAs(f"histo_energy_sum_{energy}.root")
c.SaveAs(f"canvas_energy_sum_{energy}.root")
