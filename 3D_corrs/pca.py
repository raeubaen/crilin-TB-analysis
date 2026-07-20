#!/usr/bin/env python3

import uproot
import numpy as np
from sklearn.decomposition import PCA


# ==========================================================
# Input / output
# ==========================================================

input_file = "data_corrected.root"
tree_name = "tree"

output_file = "pca_latent_selected.root"
output_tree = "tree"


# ==========================================================
# Read input
# ==========================================================

tree = uproot.open(input_file)[tree_name]

data = tree.arrays(
    [
        "SumCorrResidualCorrected",
        "crilin_lsfit_amp",
        "PassStartCellCut"
    ],
    library="np"
)


# ==========================================================
# Basic variables
# ==========================================================

E_all = data["SumCorrResidualCorrected"]

pass_cut = data["PassStartCellCut"].astype(bool)


# ==========================================================
# Event selection
#
# PassStartCellCut == True
# Energy > 1800
# ==========================================================

selection = (
    pass_cut &
    (E_all > 1800)
)


print("Total events :", len(E_all))
print("Selected     :", np.sum(selection))


# apply selection

E = E_all[selection]

amp = data["crilin_lsfit_amp"][selection]


# ==========================================================
# Five central crystals
# ==========================================================

central = np.column_stack(
    [
        amp[:,220],
        amp[:,221],
        amp[:,222],
        amp[:,223],
        amp[:,224],
    ]
)


# ==========================================================
# Shower-shape variables
# ==========================================================

features = central / E[:,None]


# ==========================================================
# PCA
# ==========================================================

pca = PCA(n_components=5)

latent = pca.fit_transform(features)


# ==========================================================
# PCA information
# ==========================================================

print("\nExplained variance:")

for i,v in enumerate(pca.explained_variance_ratio_):
    print(f"PC{i+1}: {v:.6f}")


print("\nEigenvectors:")
print(pca.components_)


# ==========================================================
# Write output tree
# ==========================================================

outfile = uproot.recreate(output_file)

outfile[output_tree] = {

    "EnergyTotal":
        E.astype(np.float32),

    "feature_220":
        features[:,0].astype(np.float32),

    "feature_221":
        features[:,1].astype(np.float32),

    "feature_222":
        features[:,2].astype(np.float32),

    "feature_223":
        features[:,3].astype(np.float32),

    "feature_224":
        features[:,4].astype(np.float32),


    "PC1":
        latent[:,0].astype(np.float32),

    "PC2":
        latent[:,1].astype(np.float32),

    "PC3":
        latent[:,2].astype(np.float32),

    "PC4":
        latent[:,3].astype(np.float32),

    "PC5":
        latent[:,4].astype(np.float32),

    "PassStartCellCut":
        data["PassStartCellCut"][selection]
}


outfile.close()

print("\nWritten:", output_file)
