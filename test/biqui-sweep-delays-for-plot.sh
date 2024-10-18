#!/bin/bash - 
#===============================================================================
#
#          FILE: biqui-sweep-delays-for-plots.sh
# 
#         USAGE: ./biqui-sweep-delays-for-plots.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 17/10/24 16:23
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

target_d=$1
reliab=$2
recnum=$3
biqui=$4 # 1|0 to issue/not BiQui
opt=$5 # 1|0 to issue/not OPT



del_cloud=22.8 # ms
# Compute delays to the edge
dels_edge="18.2"
for i in `seq 10`; do
    del_edge=`echo "scale=10; $del_cloud * $i / 10" | bc`
    dels_edge="$dels_edge $del_edge"
done



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
lim=10
recs=`echo "scale=10;1.363/0.94" | bc`
recs=( $recs 1/3 1 3 )
recs="${recs[recnum]}"


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


        # Check if flag is set to issue BiQui
        if [ $biqui -eq 1 ]; then
            cd ..
            # Create file for BiQui (M/G/k approx)
            experiment="biqui-targetd_$target_d-reliab_$reliab-use_subs_ratio_10p$r-edge_cloud_ratio_$recn-del_edge_$del_edge-del_cloud_$del_cloud-$now"
            res_dir="results/journal-extension/delay-change"
            results="$res_dir/$experiment.csv"
            echo "ce cc z cost lambda mu edge_d cloud_d target_d percentile cost_ratio" > $results

            for lam in `seq $lam_min $lam_step $lam_max`; do
                # Issue M/G/k approx
                log_f="/tmp/logs/$experiment.log"
                explo="$res_dir/explo-lam_$lam-$experiment.json"
                echo Working on $log_f
                python3 biqui.py\
                    --mu $mu --lambda_ $lam -cf\
                    --exploration $explo\
                    --target_d $target_d --percentile $reliab\
                    --c0c $c0c --c1c $c1c --cost_ratio $cost_ratio\
                    --edge_d $del_edge --cloud_d $del_cloud &> $log_f
                tail -n1 $log_f >> $results
            done

            cd test
        fi


        # Check if flag is set to issue OPT
        if [ $opt -eq 1 ]; then
            # Create file for BiQui + simu CDF
            experiment_opt="opt-targetd_$target_d-reliab_$reliab-use_subs_ratio_10p$r-edge_cloud_ratio_$recn-del_edge_$del_edge-del_cloud_$del_cloud-$now"
            res_dir="../results/journal-extension/delay-change"
            results_opt="$res_dir/$experiment_opt.csv"
            echo "ce cc z cost lambda mu edge_d cloud_d target_d percentile cost_ratio" > $results_opt

            for lam in `seq $lam_min $lam_step $lam_max`; do
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


    done
done




