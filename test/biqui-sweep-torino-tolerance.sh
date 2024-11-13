#!/bin/bash - 
#===============================================================================
#
#          FILE: biqui-sweep-torino-tolerance.sh
# 
#         USAGE: ./biqui-sweep-torino-tolerance.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: we assume equal edge/cloud pricing
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 29/10/24 18:40
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

target_d=$1
reliab=$2
deleratio=$3 # 2 to have 2/10 delay to cloud. 18.2 to fix it
biqui=$4 # 1|0 to issue/not BiQui
opt=$5 # 1|0 to issue/not OPT



del_cloud=22.8 # ms
# Compute delay to the edge
#dels_edge="18.2"
if [[ $deleratio =~ "." ]]; then
    dels_edge=$deleratio
else
    dels_edge=`echo "scale=10; $del_cloud * $deleratio / 10" | bc`
fi




mu=`echo "scale=10; 1/22.5" | bc`
lam_min=$mu
lam_step=$mu
lam_max=`echo "scale=10; 100*$mu" | bc`

# To use . decimal delimiter
LANG=C

now=`date +%s`


mkdir /tmp/logs


# Ratio between the usage (c1.) and subscription (c0.) cost
# r=c1./c0.={10^0, 10^1, 10^2, 10^3}
r=0

# Ratio between the edge (c.e) and cloud (c.c) costs
# rec=c.e/c.c={1/10,1/9,...,1,2,...,10}
# in this case we fix it to be the same
recs="1"


# Iterate over each ratio 
for rec in $recs; do
    recn=`echo "scale=10; $rec" | bc`
    # Compute the costs
    c0e=1
    c1e=`echo "scale=10; $c0e * 10^$r" | bc`
    c0c=`echo "scale=10; $c0e / ($rec)" | bc`
    c1c=`echo "scale=10; $c1e / ($rec)" | bc`
    cost_ratio=`echo "scale=10; $rec" | bc`


    # Iterate over every possible edge delay
    for del_edge in `echo $dels_edge`; do

        for tolerance in `seq 0.00 0.01 0.12`; do


            # Check if flag is set to issue BiQui
            if [ $biqui -eq 1 ]; then
                cd ..
                # Create file for BiQui (M/G/k approx)
                experiment="biqui-targetd_$target_d-reliab_$reliab-use_subs_ratio_10p$r-edge_cloud_ratio_$recn-del_edge_$del_edge-del_cloud_$del_cloud-tolerance_$tolerance-$now"
                res_dir="results/journal-extension/tolerance-change-torino"
                results="$res_dir/$experiment.csv"
                results_cf="$res_dir/cloud_first-$experiment.csv"
                echo "ce cc z cost lambda mu edge_d cloud_d target_d percentile cost_ratio" > $results
                echo "ce cc z cost lambda mu edge_d cloud_d target_d percentile cost_ratio" > $results_cf

                # Keep track of last used #CPUs
                ce_prev=0
                cc_prev=0
                ce_prev_cf=0
                cc_prev_cf=0

                for lam in `awk -F, 'NR>1{printf "%f\n",$8}' data/traffic_torino_v02.csv`; do
                    # Issue M/G/k approx
                    log_f="/tmp/logs/$experiment.log"
                    explo="$res_dir/explo-lam_$lam-$experiment.json"
                    echo Working on $log_f
                    python3 biqui.py\
                        --mu $mu --lambda_ $lam\
                        --exploration $explo\
                        --target_d $target_d --percentile $reliab\
                        --c0c $c0c --c1c $c1c --cost_ratio $cost_ratio\
                        --edge_d $del_edge --cloud_d $del_cloud\
                        --ce_prev $ce_prev --cc_prev $cc_prev\
                        --tolerance $tolerance &> $log_f
                    tail -n1 $log_f >> $results

                    ce_prev=`tail -n1 $results | cut -d' ' -f1`
                    cc_prev=`tail -n1 $results | cut -d' ' -f2`


                    ####################
                    # Now CLOUD FIRST!
                    ####################
                    # Issue M/G/k approx
                    log_f="/tmp/logs/cloud_first-$experiment.log"
                    explo="$res_dir/cloud_first-explo-lam_$lam-$experiment.json"
                    echo Working on $log_f
                    python3 biqui.py\
                        --mu $mu --lambda_ $lam -cf\
                        --exploration $explo\
                        --target_d $target_d --percentile $reliab\
                        --c0c $c0c --c1c $c1c --cost_ratio $cost_ratio\
                        --edge_d $del_edge --cloud_d $del_cloud\
                        --ce_prev $ce_prev_cf --cc_prev $cc_prev_cf\
                        --tolerance $tolerance &> $log_f
                    tail -n1 $log_f >> $results_cf


                    ce_prev_cf=`tail -n1 $results_cf | cut -d' ' -f1`
                    cc_prev_cf=`tail -n1 $results_cf | cut -d' ' -f2`
                done

                cd test
            fi


            # Check if flag is set to issue OPT
            if [ $opt -eq 1 ]; then
                # Create file for BiQui + simu CDF
                experiment_opt="opt-targetd_$target_d-reliab_$reliab-use_subs_ratio_10p$r-edge_cloud_ratio_$recn-del_edge_$del_edge-del_cloud_$del_cloud-$now"
                res_dir="../results/journal-extension/tolerance-change-torino"
                results_opt="$res_dir/$experiment_opt.csv"
                echo "ce cc z cost lambda mu edge_d cloud_d target_d percentile cost_ratio" > $results_opt

                for lam in `awk -F, 'NR>1{printf "%f\n",$8}' data/traffic_torino_v02.csv`; do
                    # Issue M/G/k simulation
                    log_opt_f="/tmp/logs/$experiment_opt.log"
                    explo="$res_dir/explo-lam_$lam-$experiment_opt.json"
                    echo Working on $log_opt_f
                    python3 exhaustive_search_simuapp.py\
                        --mu $mu --lambda_ $lam -cf\
                        --exploration $explo\
                        --target_d $target_d --percentile $reliab\
                        --c0c $c0c --c1c $c1c --cost_ratio $cost_ratio\
                        --edge_d $del_edge --cloud_d $del_cloud &> $log_opt_f
                    tail -n1 $log_opt_f >> $results_opt
                done
            fi







        done # tolerance



    done # del_edge
done




