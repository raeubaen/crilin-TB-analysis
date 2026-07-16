# crilin-TB-calib

Info sparse:

Elog: https://drd6-crilin-logbook.cern.ch/elisa/display

Excel elog: https://drd6-crilin-logbook.cern.ch/elisa/display/14?logbook=CRILIN

Ultima reco con calibrazione 1/MPV(MIP) e template fit linearizzato dentro: [https://github.com/raeubaen/crilin_reco_from_padme_daq/releases/tag/crilin-on-ferrari-v1.1-mip-calib-in_ALL_WORKING](https://github.com/raeubaen/crilin_reco_from_padme_daq/releases/tag/crilin-on-ferrari-v2-linearized_fitON)

Run usati qui: https://rgargiul.web.cern.ch/crilin_hadded_runs_tb-h2-2026/ (re-reco iniziale, filtro + picco), meno quello a 65 GeV

File nuovi ricostruiti qui:
/eos/experiment/muoncollider/data/crilin/h2-2026/re-reco_dqm_template

Profili per correggere i canali vs. startCell:
https://rgargiul.web.cern.ch/digi_corr_crilin_pedestal_profiles_checks/


Tabella run buoni per energia:
| Run | Energia |
|-------:|-------:|
| 386    | 100    |
| 395    | 20     |
| 401    | 34     |
| 403    | 52     |
| 404    | 74     |
| 413    | 120    |
| 435    | 10     |
| 429    | 65     |

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
