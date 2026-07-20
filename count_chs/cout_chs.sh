root $1 << EOF

  tree->Draw("Sum\$(crilin_lsfit_amp_corr/(crilin_one_over_mpv*crilin_one_over_gain_over_ADC_per_mV) > 3.5)>>h_$2(250, 0, 250)")
  h_$2->SaveAs("h_$2.root")

EOF
