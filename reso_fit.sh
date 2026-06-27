resofile=$1

root << EOF
  new TCanvas("c")
  new TTree("t", "t")
  t->ReadFile("$resofile")
  t->Draw("en:sigma_abs/peak_abs:0:sigma_abs/peak_abs * sqrt( pow(err_sigma_abs/sigma_abs,2) + pow(err_peak_abs/peak_abs, 2) ) ")
  auto *ge = new TGraphErrors(t->GetSelectedRows(), t->GetV1(), t->GetV2(), t->GetV3(), t->GetV4())
  ge->Draw("AP")
  new TF1("f", "sqrt(pow([N(GeV)]/x, 2) + pow([S(%)]/sqrt(x) * 1e-2, 2) + pow([C(%)]*1e-2, 2))", 0, 200)
  ge->Fit(f);
  ge->GetXaxis()->SetTitle("Beam energy [GeV]")
  ge->GetYaxis()->SetTitle("Resolution")
  TLatex l(80, 0.02, "#frac{#sigma_{E}}{E} = #frac{N}{E} #oplus #frac{S}{#sqrt{E[GeV]}} #oplus C")
  l.Draw()
  c->SaveAs("reso_canvas_crilin.root")
EOF
