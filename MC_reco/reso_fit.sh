resofile=$1

root << EOF
  new TCanvas("c")
  new TTree("t", "t")
  t->ReadFile("$resofile")
  t->Draw("en:sigma_abs/peak_abs:0:sigma_abs/peak_abs*0.01")
  //t->Draw("en:1e-2*sqrt(pow(1e2*sigma_abs/peak_abs, 2) - pow(bes, 2) - pow(syst_a, 2) - pow(syst_b, 2)):en*5e-3:1e-2*sqrt( pow(1e2*sigma_abs/peak_abs, 2) + syst_a*syst_a + syst_b*syst_b ) - sigma_abs/peak_abs")
  auto *ge = new TGraphErrors(t->GetSelectedRows(), t->GetV1(), t->GetV2(), t->GetV3(), t->GetV4())
  ge->Draw("AP")
  new TF1("f", "sqrt(pow([N(GeV)]/x, 2) + pow(1e-2*[S(%)]/sqrt(x), 2) + pow(1e-2*[C(%)], 2))", 0, 110)
  ge->Fit(f, "R");
  ge->GetXaxis()->SetTitle("Beam energy [GeV]")
  ge->GetYaxis()->SetTitle("Resolution (%)")
  TLatex l(80, 0.02, "#frac{#sigma_{E}}{E} = #frac{N}{E} #oplus #frac{S}{#sqrt{E[GeV]}} #oplus C")
  l.Draw()
  c->SaveAs("$2")
EOF
