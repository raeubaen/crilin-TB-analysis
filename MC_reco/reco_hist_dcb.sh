en=$1

root electrons_${en}GeV.root << EOF
  events->SetAlias("rng", "sin(2*pi*rndm)*sqrt(-2*log(rndm))")
  events->SetAlias("Hit_CE", "Hit_NCherenkov/24.37")
  events->SetAlias("Hit_layer", "4 - Hit_iz")
  events->SetAlias("gain", "( (Hit_layer == 1) || (Hit_layer == 2)) ? 1 : ( (Hit_layer == 4) ? 6 : 4 )")
  events->SetAlias("noise_per_layer", "8/gain")
  events->SetAlias("noise_per_ch", "noise_per_layer * ( ((Hit_ix==3) && (Hit_iy==3)) ? 2 : 1)")
  .L ../dcb.cxx
  events->Draw("Sum\$((Hit_CE * (1 + rng/sqrt(Hit_CE * 0.6/1.4)) + rng*noise_per_ch > 25/8*noise_per_ch) * (Hit_CE * (1 + rng/sqrt(Hit_CE * 0.6/1.4)) + rng*noise_per_ch ))/1e3>>h_$1(2000, 0.88 * $en*0.95, 0.88 * $en*1.05)")

  ofstream outf("out_electrons_final.csv", std::ios::app);
  h_${en}->Draw()
  h_$en->GetXaxis()->SetRangeUser(0.88 * $en*0.95, 0.88 * $en*1.05);
  h_$en->GetXaxis()->SetRangeUser(h_$en->GetMean() - 4*h_$en->GetRMS(), h_$en->GetMean() + 4*h_$en->GetRMS())
  h_$en->GetXaxis()->SetRangeUser(h_$en->GetMean() - 2.5*h_$en->GetRMS(), h_$en->GetMean() + 2.5*h_$en->GetRMS())
  dcb(h_$en)
  dcb(h_$en)
  dcb(h_$en)
  auto *f = h_$en->GetFunction("dcb")
  outf << ${en} << "," << f->GetParameter(5) << ",0," << f->GetParError(5) << "," << f->GetParameter(4) << "," << f->GetParError(4) << endl;
  outf.close()
  h_$en->SaveAs("histo_${en}_fitted.root");

EOF
