enlist=$1
outf=$2
outd=$3

echo "en,sigma_abs,zero,err_sigma_abs,peak_abs,err_peak_abs" > $outf

for en in $(cat $enlist);
do
  root /eos/experiment/muoncollider/data/crilin/h2-2026/re-reco_dqm_template/cat_digi_corrected/data_corrected_$en.root << EOF

    ofstream outf("$outf", std::ios::app);
    .L ../dcb.cxx
    tree->Draw("SumCorrResidualCorrected>>h_$en(3000, 0, 3000)")
    h_${en}->Draw()
    h_$en->GetXaxis()->SetRangeUser(1940/100. * $en*0.95, 1940/100. * $en*1.05);
    h_$en->GetXaxis()->SetRangeUser(h_$en->GetMean() - 4*h_$en->GetRMS(), h_$en->GetMean() + 4*h_$en->GetRMS())
    h_$en->GetXaxis()->SetRangeUser(h_$en->GetMean() - 4*h_$en->GetRMS(), h_$en->GetMean() + 4*h_$en->GetRMS())
    dcb(h_$en)
    dcb(h_$en)
    dcb(h_$en)
    auto *f = h_$en->GetFunction("dcb")
    outf << ${en} << "," << f->GetParameter(5) << ",0," << f->GetParError(5) << "," << f->GetParameter(4) << "," << f->GetParError(4) << endl;
    outf.close()
    h_$en->SaveAs("$outd/histo_${en}_fitted.root");
EOF
done
