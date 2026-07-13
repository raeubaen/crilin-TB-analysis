import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt


# =====================================================
# File
# =====================================================

filename = "cat_435_10GeV_pedestals_only_peak412_electrons_like_sw_fitON.root"

tree = uproot.open(filename)["tree"]


# =====================================================
# Read branches
# =====================================================

arrays = tree.arrays(
    [
        "crilin_pre_processed_waves",
        "crilin_board",
        "crilin_digi_ch",
        "StartCell",
        "crilin_one_over_gain_over_ADC_per_mV", "crilin_one_over_mpv", "crilin_layer"
    ],
    library="ak"
)


# =====================================================
# Waveforms
# =====================================================

waves = ak.to_numpy(
    arrays["crilin_pre_processed_waves"]
)

Nevt, Nch, Nsamp = waves.shape

print("Waveforms:", waves.shape)

# =====================================================
# Physical channel
# physical_channel = board*32 + digi_ch
# =====================================================

board = ak.to_numpy(arrays["crilin_board"][0]).astype(int)
digi_ch = ak.to_numpy(arrays["crilin_digi_ch"][0]).astype(int)

physical_channel = board * 32 + digi_ch

print("Physical channels:")
print(physical_channel)

print(
    "Number of unique physical channels:",
    len(np.unique(physical_channel))
)


# sort waveform channels according to physical channel

order = np.argsort(physical_channel)

physical_channel = physical_channel[order]

waves = waves[:, order, :]


# =====================================================
# Align samples
#
# sample_corrected = sample - StartCell[7][2]
#
# no loop
# =====================================================

sample_cell = ak.to_numpy(
    arrays["StartCell"][:, 7, 2]
).astype(int)


idx = (
    1024 + np.arange(Nsamp)[None, :]
    + sample_cell[:, None]
) % 1024


# =====================================================
# Estimate drift for each physical channel
# =====================================================

#drift = aligned.mean(axis=0)
#
sample = np.tile(np.arange(Nsamp), Nevt)

# -------------------------------------------------------
# Before drift subtraction
# -------------------------------------------------------

Ncap = 1024

drift_sum = np.zeros((Nch, Ncap), dtype=np.float64)
drift_count = np.zeros((Nch, Ncap), dtype=np.int64)


# Loop only over channels (225), not events
# This is fast and keeps memory reasonable

for ch in range(Nch):

    np.add.at(
        drift_sum[ch],
        idx,
        waves[:, ch, :]
    )

    np.add.at(
        drift_count[ch],
        idx,
        1
    )


drift = drift_sum / np.maximum(drift_count, 1)

print("drift shape:", drift.shape)
# (225,1024)

ich = 221

plt.figure(figsize=(10,6))

plt.hist2d(
    idx.ravel(),
    waves[:, ich, :].ravel(),
    bins=[1024, 2000],
    cmap="viridis"
)

plt.plot(
    np.arange(1024),
    drift[ich],
    color="red",
    lw=2,
    label="Estimated drift"
)

plt.colorbar(label="Counts")
plt.xlabel("Aligned sample")
plt.ylabel("ADC")
plt.title(f"Channel {physical_channel[ich]} (aligned)")
plt.legend()

plt.tight_layout()
plt.show()


# =====================================================
# Subtract capacitor-dependent drift
# =====================================================

noise = np.empty_like(waves, dtype=float)

for ch in range(Nch):
    noise[:, ch, :] = (
        waves[:, ch, :]
        - drift[ch, idx]
    )


ich = 221

print("Drift shape:", drift.shape)

plt.figure(figsize=(12,6))

for i in range(2):
    plt.plot(
        drift[i],
        lw=0.8,
        alpha=0.5,
        label=str(physical_channel[i])
    )

plt.xlabel("Aligned sample")
plt.ylabel("ADC")
plt.title("Estimated drift for all channels")

plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()


# =====================================================
# Correlation matrix
# =====================================================

X = noise.transpose(1, 0, 2).reshape(Nch, -1)

X -= X.mean(axis=1, keepdims=True)

corr_active = np.corrcoef(X)


# =====================================================
# Expand to physical channel numbering
# with voids for missing channels
# =====================================================

max_channel = int(physical_channel.max())

corr_phys = np.full(
    (max_channel + 1, max_channel + 1),
    np.nan
)

corr_phys[
    np.ix_(physical_channel, physical_channel)
] = corr_active


# =====================================================
# Plot
# =====================================================

plt.figure(figsize=(10,10))

plt.imshow(
    corr_phys,
    origin="lower",
    cmap="coolwarm",
    vmin=-1,
    vmax=1
)

plt.colorbar(
    label="Noise correlation coefficient"
)

plt.xlabel(
    "Physical channel = crilin_board*32 + crilin_digi_ch"
)

plt.ylabel(
    "Physical channel = crilin_board*32 + crilin_digi_ch"
)

plt.title(
    "CRILIN pedestal noise correlation matrix"
)

plt.tight_layout()
plt.show()

sigma_E = np.sqrt(np.ones((Nch,)) @ np.cov(X) @ np.ones((Nch,)) ) * 32.7709/24.3*42.0224

print("sigma_E: ", sigma_E)

crilin_one_over_gain_over_ADC_per_mV = ak.to_numpy(arrays["crilin_one_over_gain_over_ADC_per_mV"][0])
crilin_one_over_mpv = ak.to_numpy(arrays["crilin_one_over_mpv"][0]).astype(float)

ene_noise = np.sqrt( np.diagonal(np.cov(X))) * 32.7709/24.3*42.0224

adc_noise = np.sqrt( np.diagonal(np.cov(X)) ) / crilin_one_over_mpv/crilin_one_over_gain_over_ADC_per_mV

np.savetxt(
    "adc_noise.csv",
    adc_noise,
    delimiter=",",
    header="adc_noise",
    comments="",
    fmt="%f"
)

np.savetxt(
    "ene_noise.csv",
    np.column_stack((ene_noise, arrays["crilin_layer"][0]) ),
    delimiter=",",
    header="ene_noise_MeV,layer",
    comments="",
    fmt="%f"
)


print(f"Noise on energy sum = {sigma_E:.3f}")


# =====================================================
# Optional: show one channel drift
# =====================================================

# =====================================================
# Residual noise for one channel
# =====================================================

ich = 220   # channel index after sorting

plt.figure(figsize=(10,6))

plt.hist2d(
    np.tile(np.arange(Nsamp), Nevt),
    noise[:, ich, :].ravel(),
    bins=[Nsamp, 200],
    cmap="viridis"
)

plt.colorbar(label="Counts")

plt.xlabel("Aligned sample")
plt.ylabel("ADC residual")
plt.title(f"Channel {physical_channel[ich]} after drift subtraction")

plt.tight_layout()
plt.show()
