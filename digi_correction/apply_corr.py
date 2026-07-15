import uproot
import numpy as np


corr_file = uproot.open("h_slices.root")

nchannels = 225

corrections = []

for ch in range(225):
    p = corr_file[f"h_{ch}_1"]
    corrections.append((p.values(), p.axis().edges()))


# Apri il file di input
fin = uproot.open("cat_435_10GeV_new_template.root")
tree = fin["tree"]

# Leggi tutti i branch
arrays = tree.arrays(library="np")

# ----------------------------------------------------
# Calcola amp_corr (come nel codice precedente)
# ----------------------------------------------------

startcell = arrays["StartCell"][:, 7, 2]

amp = arrays["crilin_lsfit_amp"]
gain = arrays["crilin_one_over_gain_over_ADC_per_mV"]
mpv = arrays["crilin_one_over_mpv"]

scale = gain * mpv

amp_corr = amp.copy()

for ch in range(225):

    values, edges = corrections[ch]

    bins = np.searchsorted(edges, startcell, side="right") - 1
    bins = np.clip(bins, 0, len(values)-1)

    amp_corr[:, ch] -= values[bins] * scale[:, ch]

# ----------------------------------------------------
# Aggiungi nuovi branch
# ----------------------------------------------------

arrays["crilin_lsfit_amp_corr"] = amp_corr

arrays["SumCorr"] = np.sum(
    amp_corr * (amp_corr/(gain*mpv) > 3.5),
    axis=1
)

mask = (
    ~((startcell >= 100) & (startcell <= 160))
    &
    ~((startcell >= 640) & (startcell <= 700))
)

arrays["PassStartCellCut"] = mask



import ROOT

# ----------------------------------------------------
# 2-fold residual correction with TH2::FitSlicesY
# ----------------------------------------------------

ROOT.gROOT.SetBatch(True)

nsc = 1024

nbins_sc = 50
xmin_sc = 0.
xmax_sc = 1000.

h_even = ROOT.TH2F(
    "h_even", "",
    nbins_sc, xmin_sc, xmax_sc,
    80, 180, 220
)

h_odd = ROOT.TH2F(
    "h_odd", "",
    nbins_sc, xmin_sc, xmax_sc,
    80, 180, 220
)

entries = np.arange(len(startcell))

even = (entries % 2) == 0
odd  = ~even

# fill TH2

for sc, s in zip(startcell[mask & even], arrays["SumCorr"][mask & even]):
    h_even.Fill(float(sc), float(s))

for sc, s in zip(startcell[mask & odd], arrays["SumCorr"][mask & odd]):
    h_odd.Fill(float(sc), float(s))

# Gaussian fits in each StartCell bin

ROOT.gROOT.cd()

h_even.FitSlicesY()
h_odd.FitSlicesY()

mean_even = ROOT.gDirectory.Get("h_even_1")
mean_odd  = ROOT.gDirectory.Get("h_odd_1")

# ----------------------------------------------------
# Save h_even + FitSlicesY mean points
# ----------------------------------------------------
mean_even = ROOT.gDirectory.Get("h_even_1")
mean_odd  = ROOT.gDirectory.Get("h_odd_1")


# EVEN

c1 = ROOT.TCanvas("c1", "even", 900, 700)

h_even.Draw("COLZ")

mean_even.SetMarkerStyle(7)
mean_even.SetMarkerColor(ROOT.kRed)
mean_even.SetLineColor(ROOT.kRed)

mean_even.Draw("P SAME")

c1.SaveAs("SumCorr_vs_StartCell_even.pdf")
c1.SaveAs("SumCorr_vs_StartCell_even.root")


# ODD

c2 = ROOT.TCanvas("c2", "odd", 900, 700)

h_odd.Draw("COLZ")

mean_odd.SetMarkerStyle(7)
mean_odd.SetMarkerColor(ROOT.kRed)
mean_odd.SetLineColor(ROOT.kRed)

mean_odd.Draw("P SAME")

c2.SaveAs("SumCorr_vs_StartCell_odd.pdf")
c2.SaveAs("SumCorr_vs_StartCell_odd.root")

# convert to numpy

# subtract inclusive mean
corr_even = np.array([mean_even.GetBinContent(i+1) for i in range(nbins_sc)])
corr_odd  = np.array([mean_odd.GetBinContent(i+1) for i in range(nbins_sc)])

corr_even -= np.mean(corr_even[corr_even != 0])
corr_odd  -= np.mean(corr_odd[corr_odd != 0])

# event-by-event correction
residual = np.zeros(len(startcell))

binwidth = (xmax_sc - xmin_sc) / nbins_sc

# Bin ROOT (0-based)
bin_idx = ((startcell - xmin_sc) / binwidth).astype(np.int32)
bin_idx = np.clip(bin_idx, 0, nbins_sc - 1)

residual = np.empty(len(startcell), dtype=np.float64)

residual[even] = corr_odd[bin_idx[even]]
residual[odd]  = corr_even[bin_idx[odd]]


# ----------------------------------------------------
# Scrivi il nuovo ROOT file
# ----------------------------------------------------

arrays["ResidualGlobalCorrection"] = residual

arrays["SumCorrResidualCorrected"] = (
    arrays["SumCorr"] - residual
)

with uproot.recreate("data_corrected.root") as fout:
    fout["tree"] = arrays
