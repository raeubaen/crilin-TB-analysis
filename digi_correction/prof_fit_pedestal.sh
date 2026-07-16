root $1 << EOF
  cout << "init" << endl;
  for (int i=0; i<225; i++) {
    cout << i << endl;
    tree->Draw(Form("crilin_lsfit_amp[%i]/(crilin_one_over_gain_over_ADC_per_mV[%i]*crilin_one_over_mpv[%i]):StartCell[7][2]>>h_%i(20, 0, 1000, 120, -20, 40)", i, i, i, i), "", "zcol goff");
    auto *h = (TH2F*)gROOT->FindObject(Form("h_%i", i));
    //h->SaveAs(Form("h_%i_1.root", i));
    //h->FitSlicesY();
    auto *h_mean = h->ProfileX();
    h_mean->SaveAs(Form("${2}_h_%i_1.root", i));
    auto *c = new TCanvas(Form("c_%i", i));
    h->Draw();
    h_mean->Draw("same");
    h_mean->SetMarkerStyle(7);
    h_mean->SetMarkerColor(kRed);
    c->SaveAs(Form("${2}_prof_corr_c_%i.pdf", i));
    delete c;
    delete h;
    delete h_mean;
  }
EOF
