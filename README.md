# crilin-TB-calib

parallel -j6 'bash save_hit_histos_data.sh {1} {2} {3}'     ::: $(seq -3 3)     ::: $(seq -3 3)     ::: $(seq 0 4)

parallel -j6 'python3 tf_calibrate.py {1} {2} {3}'     ::: $(seq -3 3)     ::: $(seq -3 3)     ::: $(seq 0 4)

Missing thresholds on MC... taking only the good ones

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

1.39 * 1.168 / ( 1.6e-19 * 3.2e5 * 1e12) / 42 / 1.25 = 0.6 p.e./ MeV


con mip solo per intercalibrare (peak *= media MIP / MIP-singolo-canale):
picco a 100 GeV: 2353.72 mV

2353.72 * 1.168 / (91e3 * 3.2e5 * 1.16e-19 * 1e12) / 1.25 = 0.65 p.e. / MeV


noise:
3.3 ADC in all channels, so we multiply for one_over_adc_per_mV_over_gain

proviamo a capire effetto noise correlato:
/eos/user/r/rgargiul/www/noise_studies

