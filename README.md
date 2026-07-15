# crilin-TB-calib

Info sparse:

Elog: https://drd6-crilin-logbook.cern.ch/elisa/display

Excel elog: https://drd6-crilin-logbook.cern.ch/elisa/display/14?logbook=CRILIN

Ultima reco con calibrazione 1/MPV(MIP) e template fit linearizzato dentro: [https://github.com/raeubaen/crilin_reco_from_padme_daq/releases/tag/crilin-on-ferrari-v1.1-mip-calib-in_ALL_WORKING](https://github.com/raeubaen/crilin_reco_from_padme_daq/releases/tag/crilin-on-ferrari-v2-linearized_fitON)

Run usati qui: https://rgargiul.web.cern.ch/crilin_hadded_runs_tb-h2-2026/ (re-reco iniziale, filtro + picco), meno quello a 65 GeV

Tabella run buoni per energia:
386 100
395 20
401 34
403 52
404 74
413 120
435 10
429 65

MC:
https://github.com/raeubaen/CrilinSim/releases/tag/MC-for_TB

MC file: 
/eos/home-r/rgargiul/www/electrons_g4_crilin/fixed99GeV_2.5mmsquared_30_100GeV_4mmAldesign/fixed99GeV_2.5mmsquared_30_100GeV_4mmAldesign.root



Calibrazione MC
```
parallel -j6 'bash save_hit_histos_data.sh {1} {2} {3}'     ::: $(seq -3 3)     ::: $(seq -3 3)     ::: $(seq 0 4)

parallel -j6 'python3 tf_calibrate.py {1} {2} {3}'     ::: $(seq -3 3)     ::: $(seq -3 3)     ::: $(seq 0 4)
```

waves filter / no filter
https://rgargiul.web.cern.ch/waves_filter_wrt_nofilter.root


calib light yield:
con MIP:
media mpv mip (mV): 1.39 mV
media pC/mV: 1.168 pc/mV
mpv landau muoni 150 GeV: 42 MeV
gain SiPM: 3.2e5

LY elettroni / LY muoni (da G4 cherenkov): 32.7709/26.2086 = 1.25
RICONTROLLARE 26.2,... dipende dal canale
```
1.39 * 1.168 / ( 1.6e-19 * 3.2e5 * 1e12) / 42 / 1.25 = 0.6 p.e./ MeV
```

con mip solo per intercalibrare (peak *= media MIP / MIP-singolo-canale):
picco a 100 GeV: 2353.72 mV
```
2353.72 * 1.168 / (91e3 * 3.2e5 * 1.16e-19 * 1e12) / 1.25 = 0.65 p.e. / MeV
```

noise:
3.3 ADC in all channels, so we multiply for one_over_adc_per_mV_over_gain

proviamo a capire effetto noise correlato:
/eos/user/r/rgargiul/www/noise_studies

