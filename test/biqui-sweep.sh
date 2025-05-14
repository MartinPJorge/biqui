#!/bin/bash - 
#===============================================================================
#
#          FILE: biqui-sweep.sh
# 
#         USAGE: ./biqui-sweep.sh target_d reliab mode\
#                   [results cloud_mu_mult cloudMHz]
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: results and mu_mult must be given together
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 25/07/23 16:11
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

target_d=$1
reliab=$2
mode=$3
# results=$4 # optional
# cloud_mu_mult=$5 # optional
# cloudMHz=$6 # optional


#
# AWS prices for EC2 w/ calculator 26/07/2023 @18:02
#   https://calculator.aws/#/addService/ec2-enhancement
#
# g4dn.2xlarge instance 8vCPUs,32GiB,25Gbps,225GB-NVME SSD
#
# Edge=Local(Hamburg)
# Cloud=Regional(Francfurt)
#
#  dedicated price: 1.452 $/h @Edge and 1.001 $/h @Cloud
#  shared price:    1.363 $/h @Edge and 0.94   $/h @Cloud
#
dedica_edge=`echo "scale=10; 1.452 / 8" | bc`
dedica_cloud=`echo "scale=10; 1.001 / 8" | bc`
shared_edge=`echo "scale=10; 1.363 / 8" | bc`
shared_cloud=`echo "scale=10; 0.94 / 8" | bc`



del_edge=18.1
del_cloud=22.8
cost_fn="money"
if [[ "$mode" == "dedicated" ]]; then
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=`echo "scale=10; $dedica_edge/$dedica_cloud" | bc`    
    subsratio=$ecratio
elif [[ "$mode" == "shared" ]]; then
    c0c=0
    c1c=$shared_cloud
    ecratio=`echo "scale=10; $shared_edge/$shared_cloud" | bc`    
    subsratio=$ecratio
elif [[ "$mode" == "dedicatedhour" ]]; then
    c0c=0
    c1c=$dedica_cloud
    ecratio=`echo "scale=10; $dedica_edge/$dedica_cloud" | bc`    
    subsratio=$ecratio
elif [[ "$mode" == "dedicatedhour5p" ]]; then
    c0c=0
    c1c=$dedica_cloud
    ecratio=1.05 # edge 5p more expensive
    subsratio=$ecratio
elif [[ "$mode" == "dedicatedhour0p" ]]; then
    c0c=0
    c1c=$dedica_cloud
    ecratio=1.00 # edge 0% more expensive
    subsratio=$ecratio
elif [[ "$mode" == "dedicatedhourNear5p" ]]; then
    c0c=0
    c1c=$dedica_cloud
    ecratio=1.05    
    subsratio=$ecratio
    del_edge=9.05
elif [[ "$mode" == "dedicatedhour200p" ]]; then
    c0c=0
    c1c=$dedica_cloud
    ecratio=2
    subsratio=$ecratio
elif [[ "$mode" == "default" ]]; then
    c0c=5
    c1c=2
    ecratio=2
    subsratio=$ecratio
elif [[ "$mode" == "avg_delay" ]]; then
    c0c=0
    c1c=0
    ecratio=1    
    subsratio=$ecratio
    cost_fn="avg_delay"
elif [[ "$mode" == "18-22-x2-0" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=0
    ecratio=2
    subsratio=0
elif [[ "$mode" == "18-22-x1-0" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=0
    ecratio=1
    subsratio=0
elif [[ "$mode" == "18-22-0-x1.45" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=0
    c1c=$shared_cloud
    ecratio=0
    subsratio=1.45
elif [[ "$mode" == "18-22-x2-x1.45" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=2
    subsratio=1.45
elif [[ "$mode" == "18-22-x1-x1.45" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=1
    subsratio=1.45
# Divide by 2 the edge costs in the 18-22-x1-x1.45 scenario
elif [[ "$mode" == "18-22-x1-x1.45-div2" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=`echo "scale=10; 1 / 2" | bc`
    subsratio=`echo "scale=10; 1.45 / 2" | bc`
# Divide by 4 the edge costs in the 18-22-x1-x1.45 scenario
elif [[ "$mode" == "18-22-x1-x1.45-div4" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=`echo "scale=10; 1 / 4" | bc`
    subsratio=`echo "scale=10; 1.45 / 4" | bc`
# Divide by 8 the edge costs in the 18-22-x1-x1.45 scenario
elif [[ "$mode" == "18-22-x1-x1.45-div8" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=`echo "scale=10; 1 / 8" | bc`
    subsratio=`echo "scale=10; 1.45 / 8" | bc`
# Divide by 16 the edge costs in the 18-22-x1-x1.45 scenario
elif [[ "$mode" == "18-22-x1-x1.45-div16" ]]; then
    del_edge=18.1
    del_cloud=22.8
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=`echo "scale=10; 1 / 16" | bc`
    subsratio=`echo "scale=10; 1.45 / 16" | bc`
#
elif [[ "$mode" == "15-30-x2-0" ]]; then
    del_edge=15
    del_cloud=30
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=0
    ecratio=2
    subsratio=0
elif [[ "$mode" == "15-30-x1-0" ]]; then
    del_edge=15
    del_cloud=30
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=0
    ecratio=1
    subsratio=0
elif [[ "$mode" == "15-30-0-x1.45" ]]; then
    del_edge=15
    del_cloud=30
    c0c=0
    c1c=$shared_cloud
    ecratio=0
    subsratio=1.45
elif [[ "$mode" == "15-30-x2-x1.45" ]]; then
    del_edge=15
    del_cloud=30
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=2
    subsratio=1.45
elif [[ "$mode" == "15-30-x1-x1.45" ]]; then
    del_edge=15
    del_cloud=30
    c0c=`echo "scale=10; $dedica_cloud-$shared_cloud" | bc`    
    c1c=$shared_cloud
    ecratio=1
    subsratio=1.45
elif [[ "$mode" == "18-49-0-x1.45" ]]; then
    del_edge=18.1
    del_cloud=49.5
    c0c=0
    c1c=$shared_cloud
    ecratio=0
    subsratio=1.45
else
    c0c=15
    c1c=2
    ecratio=2
    subsratio=$ecratio
fi



mu=`echo "scale=10; 1/22.5" | bc`
lam_min=$mu
lam_step=$mu
lam_max=`echo "scale=10; 100*$mu" | bc`

# To use . decimal delimiter
LANG=C

now=`date +%s`

# Set results path
if [ -z "$4" ]; then
    results="results/sigmetrics2024/biqui-targetd_$target_d-reliab_$reliab-mode_$mode-$now.csv"
else
    results=$4
fi


# Specify the mu multiplier for the cloud
cloud_mu_flag=""
cloud_mu_mult="1"
if [ -z "$5" ]; then
    echo '' > /dev/null
else
    cloud_mu=`echo "scale=10; $mu * $5" | bc`
    cloud_mu_mult=$5
    cloud_mu_flag="--cloudmu $cloud_mu"
fi


# Specify the cloud speed in MHz
cloudMHz=""
if [ -z "$6" ]; then
    echo '' > /dev/null
else
    cloudMHz=$6
fi



echo "ce cc z cost lambda mu edge_d cloud_d target_d percentile cost_ratio" > $results




cd ..
mkdir /tmp/logs
for lam in `seq $lam_min $lam_step $lam_max`; do
    log_f="/tmp/logs/biqui-reliab-$reliab-targetdel-$target_d-lambda-`printf '%.2f' $lam`-mu-`printf '%.2f' $mu`-mode_$mode-cloud_mu_mult_$cloud_mu_mult-cloudMHz_$cloudMHz.log"
    echo Working on $log_f
    python3 biqui.py\
        --mu $mu --lambda_ $lam\
        --target_d $target_d --percentile $reliab\
        --c0c $c0c --c1c $c1c --cost_ratio $ecratio\
        --edge_d $del_edge --cost_fn $cost_fn\
        --cloud_d $del_cloud\
        --subs_ratio $subsratio\
        $cloud_mu_flag\
        --cloudMHz $cloudMHz &> $log_f
    tail -n1 $log_f >> $results
done


