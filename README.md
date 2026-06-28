# crilin-TB-calib

parallel -j6 'bash save_hit_histos_data.sh {1} {2} {3}'     ::: $(seq -3 3)     ::: $(seq -3 3)     ::: $(seq 0 4)

parallel -j6 'python3 tf_calibrate.py {1} {2} {3}'     ::: $(seq -3 3)     ::: $(seq -3 3)     ::: $(seq 0 4)

Missing thresholds on MC... taking only the good ones

waves filter / no filter
https://rgargiul.web.cern.ch/waves_filter_wrt_nofilter.root

