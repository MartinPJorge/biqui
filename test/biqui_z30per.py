import time
import pandas as pd
import numpy as np
import os
import sys
import argparse
from matplotlib import pyplot as plt
import matplotlib as mpl
from math import ceil
import json

def cost(x, y, z, lam, mu, c0e=10, c0c=5, c1e=4, c1c=2):
    return c0e*x + c0c*y + c1e*lam/mu*(1-z) + c1c*lam/mu*z


def avg_delay(cdfs, rho, c):
    df = cdfs[rho,c]
    # https://stats.stackexchange.com/a/13377
    # Riemman sum w/ dx=x[1]-x[0]
    dx = df['x'].values[1] - df['x'].values[0]
    return sum(1-df['cdf'].values) * dx

def avg_delay_cost(z, avg_del_c, avg_del_e):
    return z*avg_del_c + (1-z)*avg_del_e


def bin_search(c, lambda_, mu, percentile, tgt, delay, avg_d=False):
    percentiles = {}
    avg_del = -1 # in case latter no solution found

    lost_df = 0

    # Init: check max value
    c_init = c
    rho = lambda_ / (mu*c)
    #print('c_init', c,  'rho_init', rho)
    if not float(f'{rho:.2f}') > 0:
        avd = avg_del if avg_d else -1
        return 0, 1, avd, lost_df if tgt<delay else 0
    if float(f'{rho:.2f}') <= 0.95:
        f = f'../results/MGkapprox/cdf-sweep/rho-{rho:.2f}_c-{c}.csv'
        tic_h = time.time()
        df = pd.read_csv(f, names=['x', 'cdf'], header=None)
        df = df.dropna()
        lost_df += time.time() - tic_h
        #print(f'tgt-delay={tgt-delay}')
        perc = df[df['x']<=tgt-delay].tail(1)['cdf'].values[0]
        percentiles[c] = perc
        #print('c_init', c,  'rho_init', rho, 'perc', perc)

        if avg_d:
            #print('enter avg_d')
            cdfs = {('a','a'): df}
            avg_del = avg_delay(cdfs, 'a', 'a')


    c_next = c//2


    while c != c_next:
        rho_next = lambda_ / (mu*c_next)
        #print('c', c, ' c_next=', c_next, 'rho_next', rho_next)

        if rho_next <= 0.95:
            # Round 0.001 to 0.01
            if rho_next < 0.01:
                rho_next = ceil( rho_next * 100 ) / 100
            f = f'../results/MGkapprox/cdf-sweep/rho-{rho_next:.2f}_c-{c_next}.csv'
            tic_h = time.time()
            df_next = pd.read_csv(f, names=['x', 'cdf'], header=None)
            df_next = df_next.dropna()
            lost_df += time.time() - tic_h
            #print(f'tgt-delay={tgt-delay}')
            perc_next = df_next[df_next['x']<=tgt-delay].tail(1)['cdf'].values[0]
            percentiles[c_next] = perc_next
            #print('loaded', f, 'percentile:', perc_next)
            #print('prev c:', c)
            if avg_d:
                cdfs = {('a','a'): df_next}
                avg_del = avg_delay(cdfs, 'a', 'a')

            # Update values
            swap_c = c_next
            c_next = ceil((c + c_next) / 2)\
                    if perc_next < percentile else c_next // 2
            c = swap_c if perc_next >= percentile else c

        # If c_next is unfeasible c_next = c//4
        else:
            c_next = ceil((c + c_next) / 2)
            

    # Get the average delay if required
    avd = avg_del if avg_d else -1
    #print('exit binary search with avd:', avd)

    return (c, percentiles[c], avd, lost_df) if len(percentiles)>0 else (c, 0, avd, lost_df)





if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--edge_max", type=int, required=False,
                        help="max CPUs @edge",
                        default=20)
    parser.add_argument("--cloud_max", type=int, required=False,
                        help="max CPUs @cloud",
                        default=40)
    parser.add_argument("--mu", type=float, required=False,
                        help="service rate [pkt/ms]",
                        default=1/22.5)
    parser.add_argument("--lambda_", type=float, required=False,
                        help="arrival rate [pkt/ms]",
                        default=50*1/22.5) # TODO: change
    parser.add_argument("--cloud_d", type=float, required=False,
                        help="delay towards cloud [ms]",
                        default=22.8) 
    # cloud delays from IMC =  22.8, 49.5, 60.8
    parser.add_argument("--edge_d", type=float, required=False,
                        help="delay towards edge [ms]",
                        default=18.1) 
    parser.add_argument("--target_d", type=float, required=False,
                        help="target service delay [ms]",
                        default=100) 
    parser.add_argument("--percentile", type=float, required=False,
                        help="reliability percentile",
                        default=.99999) 
    parser.add_argument("--cost_ratio", type=float, required=False,
                        help="cost_edge = cost_ratio*cost_cloud",
                        default=2) 
    parser.add_argument("--subs_ratio", type=float, required=False,
                        help="subscription cost ratio",
                        default=None) 
    parser.add_argument("--c0c", type=float, required=False,
                        help="c0c",
                        default=15) 
    parser.add_argument("--c1c", type=float, required=False,
                        help="c1c",
                        default=2) 
    parser.add_argument("--cost_fn", type=str, required=False,
                        help="money|avg_delay",
                        default='money') 
    args = parser.parse_args()


    # Matplotlib color map
    cmap = mpl.colormaps['magma']

    # Subscription cost ratio
    if args.subs_ratio == None:
        args.subs_ratio = args.cost_ratio

    # First check the minimum offloading required
    # rho = lambda / (c·mu); max_rho=0.95
    rho = args.lambda_ / (args.cloud_max*args.mu)
    if rho <= 0.95:
        z = 1
    else:
        z = 0.95 * args.cloud_max * args.mu / args.lambda_
    z = round(z, 2)
    z = 1 # This line is necessary to about advantage at start

    # Binary search @Cloud
    z_step = 0.3
    z += z_step
    perc_c = 0
    main_tic = time.time()
    losts_df = 0
    while perc_c < args.percentile and z-z_step > 0:
        z -= z_step
        #print(f'== ENTERING CLOUD BINARY SEARCH @z={z}')
        cc_min, perc_c, avg_del_c, lost_df = bin_search(c=args.cloud_max,
                                        lambda_=z*args.lambda_,
                                        mu=args.mu,
                                        percentile=args.percentile,
                                        tgt=args.target_d,
                                        delay=args.cloud_d,
                                        avg_d=args.cost_fn=='avg_delay')
        losts_df += lost_df
        #print(f'== CLOUD BIN @z={z} cc={cc_min} perc={perc_c}')

    if 0 < z < z_step:
        z = max(z-z_step, 0)

    # Only feasible setup is no offloading to cloud
    if z == 0:
        cc_min, perc_c = 0,1


    # The only feasible solution w/ z<1 => search min_edge setup
    if z < 1:
        #print(f'== ENTERING EDGE BINARY SEARCH @z={z}')
        ce_min, perc_e, avg_del_e, lost_df = bin_search(c=args.edge_max,
                                        lambda_=(1-z)*args.lambda_,
                                        mu=args.mu,
                                        percentile=args.percentile,
                                        tgt=args.target_d,
                                        delay=args.edge_d,
                                        avg_d=args.cost_fn=='avg_delay')
        losts_df += lost_df
        #print(f'== EDGE BIN @z={z} ce={ce_min} perc={perc_e}')
    else:
        ce_min, perc_e = 0, 1


    # Store the minimum setup at starting offloading z
    if args.cost_fn == 'money':
        min_cost = cost(x=ce_min, y=cc_min, lam=args.lambda_,
                        mu=args.mu, z=z,
                        c0e=args.cost_ratio*args.c0c,
                        c0c=args.c0c,
                        c1e=args.subs_ratio*args.c1c,
                        c1c=args.c1c)
    else:
        avg_del_c = 0 if z==0 else avg_del_c
        avg_del_e = 0 if z==1 else avg_del_e
        #print(f'the delay @z={z} is del_e={avg_del_e}, del_c={avg_del_c}')
        min_cost = avg_delay_cost(z, avg_del_c=avg_del_c,
                        avg_del_e=avg_del_e)


    #print(f'== MIN SETUP @z={z} is (ce,cc)={(ce_min,cc_min)}')
    #print(f'== with perc_e={perc_e} perc_c={perc_c}')
    #print(f'== and cost {min_cost}')


    # Check feasibility
    if z == 1 and perc_c < args.percentile:
        #print('No feasible solution')
        sys.exit(1)
    if z == 0 and perc_e < args.percentile:
        #print('No feasible solution')
        sys.exit(1)
    if 0<z<1 and (perc_e < args.percentile or perc_c < args.percentile):
        #print('No feasible solution')
        sys.exit(1)


    # Keep a dictionary of explored setups
    explored = {(ce_min, cc_min, z): min_cost}

    # Do AAAAAAAll the way up! :D
    #print('== ENTERING THE CLIMB UP! ==')
    cpu_increase = False
    cc, cur_cost = cc_min, explored[ce_min,cc_min,z]
    ce = ce_min if z<1 else 1 # put 1CPU@Edge if z starts at 1
    while z>0:
        z = max(z-z_step, 0)
        #print(f'Iter climb @z={z}')

        rho_e = (1-z) * args.lambda_ / (ce*args.mu) if ce>0 else 10000
        rho_c =    z  * args.lambda_ / (cc*args.mu) if cc>0 else 10000
    
        # Overloaded Edge, increase +1 CPU
        while rho_e > 0.95:
            #print(f'  z={z}, need to increase +1 CPU @Edge w ce={ce}')
            ce += 1
            rho_e = (1-z) * args.lambda_ / (ce*args.mu) if ce>0 else 10000
        # Cannot 
        if ce > args.edge_max:
            #print('  z={z} quit! I need more CPUs@Edge than available')
            perc_e = 0
            break

        # Read the edge CDF CSV file for new load
        f = f'../results/MGkapprox/cdf-sweep/rho-{rho_e:.2f}_c-{ce}.csv'
        #print('  Loading', f)
        tic_h = time.time()
        df_next = pd.read_csv(f, names=['x', 'cdf'], header=None)
        df_next = df_next.dropna()
        losts_df += time.time() - tic_h
        perc_e = df_next[df_next['x']<=args.target_d-args.edge_d].tail(1)['cdf'].values[0]
        if args.cost_fn == 'avg_delay':
            cdfs = {('a','a'): df_next}
            avg_del_e = avg_delay(cdfs, 'a', 'a')

        
        # Edge cannot assume current (1-z), increase until it can
        while perc_e < args.percentile and ce < args.edge_max:
            #print(f'  z={z}, need to increase +1 CPU @Edge')
            ce += 1
            rho_e = (1-z) * args.lambda_ / (ce*args.mu)
            #print(f'     CPU increase@edge:: ce={ce}')

            if rho_e>0 and float(f'{rho_e:.2f}')==0:
                rho_e = ceil(0.001*100)/100
            f = f'../results/MGkapprox/cdf-sweep/rho-{rho_e:.2f}_c-{ce}.csv'
            #print('  Loading', f)
            tic_h = time.time()
            df_next = pd.read_csv(f, names=['x', 'cdf'], header=None)
            df_next = df_next.dropna()
            losts_df += time.time() - tic_h
            perc_e = df_next[df_next['x']<=args.target_d-args.edge_d].tail(1)['cdf'].values[0]
            if args.cost_fn == 'avg_delay':
                cdfs = {('a','a'): df_next}
                avg_del_e = avg_delay(cdfs, 'a', 'a')


        # Impossible to meet with max_edge CPUs
        if perc_e < args.percentile:
            #print('    maximum Edge CPUs reached! need more CPUs!')
            break

        perc_c = 1
        while perc_c >= args.percentile and cc > 0:
            # Try to decrease by one CPU @Cloud
            cc -= 1
            #print(f'  Try to decrease -1 CPU @Cloud, i.e. cc={cc}')

            # Cannot handle 0 cloud CPUs with offloading
            if (cc == 0 and z > 0) or (cc == z == 0):
                #print(f'    cannot! because cc={0} z={z}')
                continue
            #print(f'cc={cc}, z={z}')

            # Comute new rho with -1 CPU@Cloud
            rho_c = z  * args.lambda_ / (cc*args.mu)

            # If rho>0.95 accuracy low, skip
            if rho_c > 0.95:
                #print(f'    cannot! because rho_c={rho_c}>0.95')
                perc_c = 0
                continue
            
            # If rho_c=0 => no cpus required
            if not float(f'{rho_c:.2f}') > 0:
                cc = 0
                continue

            # Read the cloud CDF CSV file for new load and -1 CPU
            f = f'../results/MGkapprox/cdf-sweep/rho-{rho_c:.2f}_c-{cc}.csv'
            #print('  Loading', f)
            tic_h = time.time()
            df_next = pd.read_csv(f, names=['x', 'cdf'], header=None)
            df_next = df_next.dropna()
            losts_df += time.time() - tic_h
            perc_c = df_next[df_next['x']<=args.target_d-args.cloud_d].tail(1)['cdf'].values[0]
            if args.cost_fn == 'avg_delay':
                cdfs = {('a','a'): df_next}
                avg_del_c = avg_delay(cdfs, 'a', 'a')

            #print(f'   z={z} with cc={cc} CPUs@Cloud, percentile={perc_c}')
        # Loop exits because with cc @Cloud does not hold
        # so go back to +1 CPU @Cloud
        cc += 1

        # If there is no load@cloud, fix 0 CPUs
        if z == 0:
            cc = 0

        # If we exit because rho_c=0 => cc=0
        if not float(f'{rho_c:2f}') > 0:
            cc, perc_c = 0, 1 if args.target_d>args.cloud_d else 0


        #print(f'  invoking cost with ce={ce},cc={cc},z={z}')
        if args.cost_fn == 'money':
            explored[ce,cc,z] = cost(x=ce, y=cc, lam=args.lambda_,
                                    mu=args.mu, z=z,
                                    c0e=args.cost_ratio*args.c0c,
                                    c0c=args.c0c,
                                    c1e=args.subs_ratio*args.c1c,
                                    c1c=args.c1c)
        else:
            avg_del_c = 0 if z==0 else avg_del_c
            avg_del_e = 0 if z==1 else avg_del_e
            #print(f'the delay @z={z} is del_e={avg_del_e}, del_c={avg_del_c}')
            explored[ce,cc,z] =\
                avg_delay_cost(z, avg_del_c=avg_del_c,
                            avg_del_e=avg_del_e)

        cur_cost = explored[ce,cc,z]
        #print(f'@climb up w z={z:.2f} (ce,cc)={(ce,cc)} cost={cur_cost}')


    #print(json.dumps({str(k): v for k,v in explored.items()},
        #indent=4))
    #print('DDDDDDDDONE')

    # Get the minimum cost
    #(ce,cc,z), cost = min(explored.items(), key=lambda kv: kv[1])

    #min_ce, min_cc, min_z, min_cost = 0,0,10,1000000000000
    #for (ce,cc,z), cost in explored.items():
    #    if round(cost,4) <= round(min_cost,4) and z <= min_z:
    #        min_ce, min_cc, min_z, min_cost = ce, cc, z, cost
    #ce, cc, z = min_ce, min_cc, min_z

    explored = dict(sorted(explored.items(),
        key=lambda kv: (round(kv[1],4), kv[0][2]))) # sort (value, z)
    #print('sorted costs', explored.items())
    (ce,cc,z), cost = list(explored.items())[0]

    z = 0 if cc==0 else z


    # Last check
    # In some cases the rounding thinks it works with, e.g
    # 12 CPUs @Edge and z=0, when it needs 13
    if z == 0:
        rho_e = args.lambda_ * (1-z) / (ce*args.mu)
        f = f'../results/MGkapprox/cdf-sweep/rho-{rho_e:.2f}_c-{ce}.csv'
        tic_h = time.time()
        df = pd.read_csv(f, names=['x', 'cdf'], header=None)
        df = df.dropna()
        losts_df += time.time() - tic_h
        perc_e = df[df['x']<=args.target_d-args.edge_d].tail(1)['cdf'].values[0]
        #print('rho_e', rho_e, perc_e)
        if perc_e < args.percentile:
            ce += 1


    main_tac = time.time()
    print(f'Ellapsed time: {main_tac-main_tic-losts_df}sec')
    print(ce, cc, z, cost, args.lambda_, args.mu,
            args.edge_d, args.cloud_d, args.target_d,
            args.percentile, args.cost_ratio)

