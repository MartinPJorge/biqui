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


    # Subscription cost ratio
    if args.subs_ratio == None:
        args.subs_ratio = args.cost_ratio

    
    found, cc = False, 1
    while not found and cc < args.cloud_max:
        rho_c = args.lambda_ / (cc*args.mu)

        if rho_c < 0.01:
            rho_c = 0.01
        if rho_c > 0.95:
            cc += 1
            continue

        # read the edge cdf csv file for new load
        f = f'cdf-sweep/rho-{rho_c:.2f}_c-{cc}.csv'
        print('  loading', f)
        df_next = pd.read_csv(f, names=['x', 'cdf'], header=None)
        df_next = df_next.dropna()
        perc_c = df_next[df_next['x']<=args.target_d-args.cloud_d].tail(1)['cdf'].values[0]
        # & compute avg_del_c
        if args.cost_fn == 'avg_delay':
            cdfs = {('a','a'): df_next}
            avg_del_c = avg_delay(cdfs, 'a', 'a')

        if perc_c >= args.percentile:
            found = True
        else:
            cc += 1

    if not found:
        # Find max rho_c admitted w/ cloud_max
        perc_c, rho_c = 0, 0.96
        rho_step = 0.01
        while perc_c < args.percentile:
            rho_c -= rho_step

            # read the edge cdf csv file for new load
            f = f'cdf-sweep/rho-{rho_c:.2f}_c-{cc}.csv'
            print('  loading', f)
            df_next = pd.read_csv(f, names=['x', 'cdf'], header=None)
            df_next = df_next.dropna()
            perc_c = df_next[df_next['x']<=args.target_d-args.cloud_d].tail(1)['cdf'].values[0]
            # & compute avg_del_c
            if args.cost_fn == 'avg_delay':
                cdfs = {('a','a'): df_next}
                avg_del_c = avg_delay(cdfs, 'a', 'a')


        # Send the remaining load to the Edge
        lambda_c = rho_c * args.cloud_max * args.mu

        # lambda_c = z * lambda
        z = lambda_c / args.lambda_

        lambda_e = (1-z) * args.lambda_

        # Find feasible setup for edge offload
        found, ce = False, 1
        while not found and ce < args.edge_max:
            rho_e = lambda_e / (ce*args.mu)

            if rho_e < 0.01:
                rho_e = 0.01
            if rho_e > 0.95:
                ce += 1
                continue

            # Read the edge CDF CSV file for new load
            f = f'cdf-sweep/rho-{rho_e:.2f}_c-{ce}.csv'
            print('  Loading', f)
            df_next = pd.read_csv(f, names=['x', 'cdf'], header=None)
            df_next = df_next.dropna()
            perc_e = df_next[df_next['x']<=args.target_d-args.edge_d].tail(1)['cdf'].values[0]
            # & compute avg_del
            if args.cost_fn == 'avg_delay':
                cdfs = {('a','a'): df_next}
                avg_del_e = avg_delay(cdfs, 'a', 'a')

            if perc_e >= args.percentile:
                found = True
            else:
                ce += 1

        if not found:
            print('Not found!')
        else:
            if args.cost_fn == 'money':
                min_cost = cost(x=ce, y=args.cloud_max,
                                z=z, lam=args.lambda_,
                                mu=args.mu, 
                                c0e=args.cost_ratio*args.c0c,
                                c0c=args.c0c,
                                c1e=args.subs_ratio*args.c1c,
                                c1c=args.c1c)
            else: # 'avg_delay':
                min_cost = avg_delay_cost(z=z,
                        avg_del_c=avg_del_c, avg_del_e=avg_del_e)

            # print(ce, cc, z, cost, args.lambda_, args.mu,
            #         args.edge_d, args.cloud_d, args.target_d,
            #         args.percentile, args.cost_ratio)

            print(ce, args.cloud_max, z, min_cost, args.lambda_, args.mu,
                    args.edge_d, args.cloud_d, args.target_d,
                    args.percentile, args.cost_ratio)

    else:
        if args.cost_fn == 'money':
            min_cost = cost(x=0, y=cc, z=1, lam=args.lambda_,
                            mu=args.mu, 
                            c0e=args.cost_ratio*args.c0c,
                            c0c=args.c0c,
                            c1e=args.subs_ratio*args.c1c,
                            c1c=args.c1c)
        # & compute avg_del_e
        else: #args.cost_fn == 'avg_delay':
            cdfs = {('a','a'): df_next}
            avg_del_e = avg_delay(cdfs, 'a', 'a')
            min_cost = avg_delay_cost(z=1, avg_del_e=0,
                        avg_del_c=avg_del_c)

        # print(ce, cc, z, cost, args.lambda_, args.mu,
        #         args.edge_d, args.cloud_d, args.target_d,
        #         args.percentile, args.cost_ratio)

        print(0, cc, 1, min_cost, args.lambda_, args.mu,
                args.edge_d, args.cloud_d, args.target_d,
                args.percentile, args.cost_ratio)

