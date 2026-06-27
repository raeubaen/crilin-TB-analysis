import ROOT

import tensorflow as tf
import numpy as np

import argparse

ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()

parser.add_argument("x", type=int, help="x value")
parser.add_argument("y", type=int, help="y value")
parser.add_argument("z", type=int, help="z value")

args = parser.parse_args()

x = args.x
y = args.y
z = args.z

print(x, y, z)

f_data = ROOT.TFile.Open(f"data_x_{x}_y_{y}_z_{z}.root")
f_mc   = ROOT.TFile.Open(f"mc_x_{x}_y_{y}_z_{z}.root")


h_data = f_data.Get(f"histo_data_x_{x}_y_{y}_z_{z}")
h_mc   = f_mc.Get(f"histo_mc_x_{x}_y_{y}_z_{z}")


assert h_data
assert h_mc


nbins = h_data.GetNbinsX()

data_counts = np.array(
    [h_data.GetBinContent(i) for i in range(1, nbins+1)],
    dtype=np.float32
)

nom_counts = np.array(
    [h_mc.GetBinContent(i) for i in range(1, nbins+1)],
    dtype=np.float32
)

bin_centers = np.array(
    [h_data.GetBinCenter(i) for i in range(1, nbins+1)],
    dtype=np.float32
)


bin_width = h_data.GetBinWidth(1)


print("nbins =", nbins)
print("data integral =", data_counts.sum())
print("mc integral   =", nom_counts.sum())


# ----------------------------
# Inputs from ROOT
# ----------------------------

# bin centers in GeV
bin_centers = bin_centers.astype(np.float32)

# bin width
bw = float(bin_centers[1] - bin_centers[0])

print("here1")
nom_counts_tf = tf.constant(nom_counts)
print("here2")

data_counts_tf = tf.constant(data_counts)
print("here3")

E = tf.constant(bin_centers)

print("here4")

fine_factor = 1

print("here5")

fine_E = np.linspace(
    bin_centers[0],
    bin_centers[-1],
    fine_factor * len(bin_centers)
).astype(np.float32)

print("here6")

fine_nom = np.maximum(
    np.interp(
        fine_E,
        bin_centers,
        nom_counts
    ),
    0.
).astype(np.float32)

print("here7")

fine_bw = fine_E[1] - fine_E[0]
print("here8")

Nfine = len(fine_E)

SQRT2PI = tf.constant(
    np.sqrt(2.0*np.pi),
    dtype=tf.float32
)

print(fine_E.shape)

print(fine_nom.shape)

fine_E_tf = tf.constant(fine_E)
print("here9")
fine_nom_tf = tf.constant(fine_nom)

n_coarse = len(bin_centers)


log_alpha = tf.Variable(np.log(1), dtype=tf.float32)

logS = tf.Variable(np.log(0.6e3), dtype=tf.float32)
#logC = tf.Variable(np.log(0.02), dtype=tf.float32)
logN = tf.Variable(np.log(0.02), dtype=tf.float32)


def make_prediction():

    alpha = tf.exp(log_alpha)

    S = tf.exp(logS)      # pe/GeV
    #C = tf.exp(logC)      # relative constant term
    N = tf.exp(logN)      # MeV

    Etrue = fine_E_tf

    mu = alpha * Etrue

    sigma = tf.sqrt(
        #(C * mu)**2 +
        mu / tf.maximum(S, 100)
    )

    sigma = tf.clip_by_value(
        sigma,
        1e-4,
        100.0
    )


    # ----------------------------------------
    # Banded Gaussian response
    # ----------------------------------------

    max_sigma = tf.reduce_max(sigma)

    W = tf.cast(
        tf.math.ceil(
            5.0 * max_sigma / fine_bw
        ),
        tf.int32
    )

    offsets = tf.range(
        -W,
        W + 1,
        dtype=tf.int32
    )

    # shape: (Nfine, 1)
    off = offsets[None, :]

    center = tf.cast(
        tf.round(
            (mu - fine_E[0]) / fine_bw
        ),
        tf.int32
    )[:, None]

    i = center + off

    valid = (
        (i >= 0)
        &
        (i < Nfine)
    )


    Ereco = (
        fine_E[0]
        + tf.cast(i, tf.float32) * fine_bw
    )

    deltaE = Ereco - mu[:, None]


    # shape: (Nfine, 2W+1)
    sig = sigma[:, None]

    g = tf.exp(
        -0.5 * (deltaE / sig)**2
    )

    g /= (
        SQRT2PI
        * sig
    )

    g *= fine_bw

    Ej = fine_E_tf[:, None]

    reco_energy = Ereco

    g *= tf.cast(
        valid,
        tf.float32
    )

    # multiply by truth spectrum
    contrib = (
        g
        * fine_nom_tf[:, None]
    )

    # scatter into reco spectrum
    pred_fine = tf.math.unsorted_segment_sum(
        tf.reshape(
            contrib,
            [-1]
        ),
        tf.reshape(
            tf.where(
                valid,
                i,
                tf.zeros_like(i)
            ),
            [-1]
        ),
        Nfine
    )

    pred_fine = tf.where(
        tf.math.is_finite(pred_fine),
        pred_fine,
        tf.zeros_like(pred_fine)
    )



    Wn = tf.cast(
        tf.math.ceil(
            5.0 * N / fine_bw
        ),
        tf.int32
    )

    noise_offsets = tf.range(
        -Wn,
        Wn + 1,
        dtype=tf.int32
    )

    noise_x = (
        tf.cast(noise_offsets, tf.float32)
        * fine_bw
    )

    noise_kernel = tf.exp(
        -0.5 * (noise_x / N)**2
    )

    noise_kernel /= tf.reduce_sum(noise_kernel)

    noise_kernel = tf.reshape(
        noise_kernel,
        [-1, 1, 1]
    )

    pred_fine = tf.nn.conv1d(
        tf.reshape(pred_fine, [1, -1, 1]),
        noise_kernel,
        stride=1,
        padding="SAME"
    )

    pred_fine = tf.reshape(
        pred_fine,
        [-1]
    )

    pred_fine *= tf.cast(
        fine_E_tf >= 0.06,
        tf.float32
    )

    pred = tf.reshape(
        pred_fine,
        (n_coarse, fine_factor)
    )

    pred = tf.reduce_sum(
        pred,
        axis=1
    )

    pred *= (
        tf.reduce_sum(data_counts_tf)
        /
        tf.maximum(
            tf.reduce_sum(pred),
            1e-12
        )
    )

    print("Nfine =", Nfine)
    print("fine_bw =", fine_bw)
    print("max sigma =", max_sigma.numpy())
    print("W =", W.numpy())

    return pred

print("here10")
pred0 = make_prediction().numpy()

c = ROOT.TCanvas("c","c",800,600)

h_pred = ROOT.TH1F(
    "h_pred",
    ";Energy;Counts",
    nbins,
    h_data.GetXaxis().GetXmin(),
    h_data.GetXaxis().GetXmax()
)

for i in range(nbins):
    h_pred.SetBinContent(i+1, pred0[i])

h_pred.SetLineColor(ROOT.kRed)
h_pred.SetLineWidth(2)

h_data.SetLineColor(ROOT.kBlack)
h_data.SetMarkerStyle(20)

h_data.Draw("E")
h_pred.Draw("HIST SAMES")

c.SaveAs(f"prediction_initial_x_{x}_y_{y}_z_{z}.pdf")
c.SaveAs(f"prediction_initial_x_{x}_y_{y}_z_{z}.root")


def nll():

    pred = make_prediction()

    pred = tf.maximum(
        pred,
        1e-12
    )

    d = data_counts_tf

    return tf.reduce_sum(
        pred
        - d*tf.math.log(pred)
    )

# ----------------------------
# Fit
# ----------------------------

opt = tf.keras.optimizers.Adam(
    learning_rate=0.005
)

import pandas as pd

history = {
    "step": [],
    "loss": [],
    "alpha": [],
    "S": [],
    "N": []
}

print("Here11")

for step in range(200):

    with tf.GradientTape() as tape:

        loss = nll()

    grads = tape.gradient(
        loss,
        [
            log_alpha,
            logS,
            #logC,
            logN
        ]
    )

    opt.apply_gradients(
        zip(
            grads,
            [
                log_alpha,
                logS,
                #logC,
                logN
            ]
        )
    )


    history["step"].append(step)
    history["loss"].append(float(loss))
    history["alpha"].append(float(tf.exp(log_alpha)))
    history["S"].append(float(tf.exp(logS)))
    history["N"].append(float(tf.exp(logN)))


    if step > 0:

        print(
            "step: ", step,
            "loss: ", float(loss),
            "alpha =", float(tf.exp(log_alpha)),
            "S =", float(tf.exp(logS)),
            "N =", float(tf.exp(logN))
        )


df = pd.DataFrame(history)

df.to_csv(
    f"fit_history_x_{x}_y_{y}_z_{z}.csv",
    index=False
)

print(df.head())
print(f"Saved fit history to fit_history_x_{x}_y_{y}_z_{z}.csv")

print()
print("===== FIT RESULT =====")
print("Scale =", float(tf.exp(log_alpha)))
print("S     =", float(tf.exp(logS)))
print("N     =", float(tf.exp(logN)))

with open(f"result_x_{x}_y_{y}_z_{z}.csv", "w") as f:
  f.write(f"alpha,S,N\n{float(tf.exp(log_alpha))},{float(tf.exp(logS))},{float(tf.exp(logN))}")

pred0 = make_prediction().numpy()

c = ROOT.TCanvas("cc","cc",800,600)

h_pred = ROOT.TH1F(
    "h_pred",
    ";Energy;Counts",
    nbins,
    h_data.GetXaxis().GetXmin(),
    h_data.GetXaxis().GetXmax()
)

for i in range(nbins):
    h_pred.SetBinContent(i+1, pred0[i])

h_pred.SetLineColor(ROOT.kRed)
h_pred.SetLineWidth(2)

h_data.SetLineColor(ROOT.kBlack)
h_data.SetMarkerStyle(20)

h_data.Draw("E")
h_pred.Draw("HIST SAMES")

c.SaveAs(f"prediction_final_x_{x}_y_{y}_z_{z}.pdf")
c.SaveAs(f"prediction_final_x_{x}_y_{y}_z_{z}.root")

