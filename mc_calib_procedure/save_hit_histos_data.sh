#!/bin/bash

data_file="/home/ruben/Downloads/cat_386_100GeV_v3.0.root"
mc_file="/home/ruben/Downloads/sestini_data/fixed99GeV_2.5mmsquared_30_100GeV_4mmAldesign.root"

x=$1
y=$2
z=$3

data_branch="45*crilin_peak*(crilin_peak>3)"
mc_branch="Hit_NCherenkov/24.3"

root -l -b $data_file $mc_file << EOF

TTree *events_data = (TTree*)_file0->Get("tree");
TTree *events_mc   = (TTree*)_file1->Get("events");

auto htmp = new TH1D("htmp","",2000,0,200);

// --------------------
// 1. BINNING FROM DATA
// --------------------
events_data->Draw(
    Form("Sum\$(${data_branch}*(crilin_ix==%d)*(crilin_iy==%d)*(crilin_layer==%d))/1e3>>htmp",
         $x, $y, $z),
    "crilin_peak_sum_all_layers > 2000",
    ""
);


double probs[5] = {0.001, 0.25, 0.50, 0.75, 0.999};
double q[5];

htmp->GetQuantiles(5, q, probs);

double xmin = q[0]*0.5;
double xmax = q[4]*1.5;

double iqr = q[3] - q[1];
double N   = htmp->GetEntries();

double bw = 2.0 * iqr / std::cbrt(N);
int nbins = std::max(50, std::min(2000, int((xmax - xmin)/bw)));

std::cout << "IQR   = " << iqr << std::endl;
std::cout << "N     = " << N << std::endl;
std::cout << "bw    = " << bw << std::endl;
std::cout << "nbins = " << nbins << std::endl;

// --------------------
// 2. HISTOGRAMS
// --------------------
auto sc1  = new TH1D("sc1","data",nbins,xmin,xmax);
auto nom1 = new TH1D("nom1","mc",nbins,xmin,xmax);

// --------------------
// 3. FILL DATA
// --------------------
events_data->Draw(
    Form("Sum\$(${data_branch}*(crilin_ix==%d)*(crilin_iy==%d)*(crilin_layer==%d))/1e3>>sc1",
         $x, $y, $z),
    "crilin_peak_sum_all_layers > 2000",
    "goff"
);

// --------------------
// 4. FILL MC (same bins)
// --------------------
events_mc->Draw(
    Form("Sum\$(${mc_branch}*( (Hit_ix - 3) ==%d)*( (Hit_iy - 3) ==%d)*( (4 - Hit_iz) ==%d))/1e3>>nom1",
         $x, $y, $z),
    "",
    "goff"
);

nom1->Scale(sc1->Integral() / nom1->Integral())

// --------------------
// 5. SAVE
// --------------------
sc1->SetName(Form("histo_data_x_%d_y_%d_z_%d",$x,$y,$z));
nom1->SetName(Form("histo_mc_x_%d_y_%d_z_%d",$x,$y,$z));

sc1->SaveAs(Form("data_x_%d_y_%d_z_%d.root",$x,$y,$z));
nom1->SaveAs(Form("mc_x_%d_y_%d_z_%d.root",$x,$y,$z));

EOF
