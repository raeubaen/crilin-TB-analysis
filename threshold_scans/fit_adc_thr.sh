root $1 << EOF
  .L dcb.cxx
  for (int i=0; i<60; i++){
    tree->Draw(Form("Sum\$(crilin_lsfit_amp*(crilin_lsfit_amp/(crilin_one_over_gain_over_ADC_per_mV*crilin_one_over_mpv) >-3+ 0.1*%i))>>h_%i(400, 100, 500)", i, i), "StartCell[7][2] < 20", "zcol goff");
    dcb((TH1F*)(gROOT->FindObject(Form("h_%i", i))));
    cout << "FIT: " << -3+ 0.1*i << " " << ((TH1F*)gROOT->FindObject(Form("h_%i", i)))->GetFunction("dcb")->GetParameter(5) << " " << ((TH1F*)gROOT->FindObject(Form("h_%i", i)))->GetFunction("dcb")->GetParError(5) << " " << ((TH1F*)gROOT->FindObject(Form("h_%i", i)))->GetFunction("dcb")->GetParameter(4) << " " << ((TH1F*)gROOT->FindObject(Form("h_%i", i)))->GetFunction("dcb")->GetParError(4) << endl;
  }
EOF
