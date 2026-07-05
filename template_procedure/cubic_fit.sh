root $1.root << EOF

  gSystem->AddIncludePath("-I/usr/include/eigen3");
  .L resample.C+

  resample_prof($1, 0, 1/2.5, "coeffs_${1}", true)

EOF

