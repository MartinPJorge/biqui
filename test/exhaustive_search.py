import pandas as pd
import numpy as np
import os
import argparse
from matplotlib import pyplot as plt
import matplotlib as mpl
from math import ceil


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
    parser.add_argument("--plot", type=bool, required=False,
                        help="Whether to plot the search",
                        default=False) 
    parser.add_argument("--cost_fn", type=str, required=False,
                        help="money|avg_delay",
                        default='money') 
    parser.add_argument("--plot_all", type=str, required=False,
                        help="plot all feasible points",
                        default=False) 
    parser.add_argument("--z_step", type=float, required=False,
                        help="z sweep step",
                        default=0.01) 
    args = parser.parse_args()


    # Matplotlib color map
    cmap = mpl.colormaps['magma']

    # Subscription cost ratio
    if args.subs_ratio == None:
        args.subs_ratio = args.cost_ratio
    print(args.subs_ratio)


    # Load all the CDF files
    print('Loading CDFs')
    cdfs, avg_dels = {}, {}
    for f in os.listdir('cdf-sweep'):
        rho = float(f.split('_')[0][-4:])
        c = int(f.split('_')[1].split('-')[1].split('.')[0])
        print(f'cdf-sweep/{f}')
        cdfs[rho,c] =\
            pd.read_csv(f'cdf-sweep/{f}', names=['x', 'cdf'], header=None)
        cdfs[rho,c] = cdfs[rho,c].dropna()

        # Precompute avg. telays if that's the cost fn
        if args.cost_fn == 'avg_delay':
            avg_dels[rho,c] =\
                avg_delay(cdfs, rho, c)
            print(f'avg_delay: {avg_dels[rho,c]}')

    # Get the rhos and cs available in data
    rhos = set(k[0] for k in cdfs.keys())
    cs = set(k[1] for k in cdfs.keys())


    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')


    # Store minimum setups for each z
    min_setup = {}

    # Store the cost grid
    cost_grid = {}

    # Plot the cost of feasible points
    for z in np.arange(0, 1.01, args.z_step):
        lamE = args.lambda_ * (1-z)
        lamC = args.lambda_ * z

        # (ce, cc) combinations
        cpu_combis = np.array(np.meshgrid(
            range(0, args.edge_max+1),
            range(0, args.cloud_max+1))).T.reshape(-1, 2)

        for ce, cc in cpu_combis:
            if ce == 0 and cc == 0:
                continue

            # Get edge rho
            if lamE == 0:
                rhoE = 0
            else:
                rhoE = lamE / (ce*args.mu) if ce > 0 else -1
                if 0 < rhoE < 0.01: # to prevent 0.001 being 0
                    rhoE = ceil( rhoE * 100 ) / 100
                else:
                    rhoE = round(rhoE, 2)

            # Get cloud rho
            if lamC == 0:
                rhoC = 0
            else:
                rhoC = lamC / (cc*args.mu) if cc > 0 else -1
                if 0 < rhoC < 0.01: # to prevent 0.001 being 0
                    rhoC = ceil( rhoC * 100 ) / 100
                else:
                    print(f'rhoC_before={rhoC}')
                    rhoC = round(rhoC, 2)
                    print(f'rhoC_after={rhoC}')

            
            print(f'ce={ce},cc={cc},z={z}:: rhoE={rhoE:.7f}, rhoC={rhoC:.7f}')

            if rhoE > 0.95 or rhoC > 0.95 or rhoE < 0 or rhoC < 0:
                continue


            # Obtain the edge delay percentile, 100% if rhoE=0
            if rhoE > 0:
                dfE = cdfs[rhoE,ce]
                percE =\
                    dfE[dfE['x']<=args.target_d-args.edge_d].tail(1)['cdf'].values[0]
            else: #rhoE=0
                percE = 0 if args.edge_d > args.target_d else 1

            # Obtain the cloud delay percentile, 100% if rhoC=0
            if rhoC > 0:
                # Get the dataframes @edge and @cloud
                dfC = cdfs[rhoC,cc]
                # Obtain the target latency percentiles
                percC =\
                    dfC[dfC['x']<=args.target_d-args.cloud_d].tail(1)['cdf'].values[0]
            else: #rhoC=0
                percC = 0 if args.cloud_d > args.target_d else 1

            # Check feasibility & include point
            print('percE', percE, 'percC', percC)
            if percE >= args.percentile and percC >= args.percentile:
                print('ENTROOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
                if args.cost_fn == 'money':
                    cost_grid[ce,cc,z] =\
                        cost(x=ce, y=cc, lam=args.lambda_,
                            mu=args.mu, z=z,
                            c0e=args.cost_ratio*args.c0c,
                            c0c=args.c0c,
                            c1e=args.subs_ratio*args.c1c,
                            c1c=args.c1c)
                else:
                    avg_del_c = avg_dels[rhoC,cc] if z>0 else 0
                    avg_del_e = avg_dels[rhoE,ce] if z<1 else 0
                    cost_grid[ce,cc,z] =\
                        avg_delay_cost(z=z,
                            avg_del_c=avg_del_c,
                            avg_del_e=avg_del_e)

                    if args.plot and args.plot_all:
                        sc = ax.scatter(ce, cc, z,
                            c=cost_grid[ce,cc,z], cmap=cmap)

                print(f'costgrid[{ce,cc,z}]={cost_grid[ce,cc,z]}')
            else:
                print(f'ce={ce},cc={cc},z={z} is UNFEASIBLE')
                print(f'  rhoE={rhoE},rhoC={rhoC}')
                pass # unfeasible point, don't add




        if len(cost_grid) < 1:
            continue

        #max_cost = max(cost_grid.values())
        #for k in cost_grid.keys():
        #    cost_grid[k] /= max_cost

        x = [k[0] for k in cost_grid.keys()]
        y = [k[1] for k in cost_grid.keys()]
        colors = [cost_grid[k] for k in cost_grid.keys()]

        print(x[:5])
        print(y[:5])
        print(colors[:5])

        z_cost_grid = [(k,v) for k,v in cost_grid.items() if k[2]==z]
        # No feasible solution for this z
        if not len(z_cost_grid) > 0:
            continue

        # Find min config for this z
        (cemin,ccmin,_),min_cost =\
            min(z_cost_grid, key=lambda kv: kv[1])
        min_setup[z] = (cemin, ccmin, min_cost)
        print(f'setup z={z} has min cost {min_cost} @{(cemin,ccmin)}')

        if args.plot:
            # Cost color
            #sc = ax.scatter(x, y, z, c=colors, cmap=cmap)
            sc = ax.scatter(cemin, ccmin, z, c=min_cost, cmap=cmap)

            # Z color
            #sc = ax.scatter(x, y, z, c=colors, cmap=cmap)
            # sc = ax.scatter(cemin, ccmin, min_cost, c=z, cmap=cmap)

    if args.plot:
        #plt.title(f'z={z:.2f}, lambda={args.lambda_:.2f}, mu={args.mu:.2f}')
        plt.title(f'lambda={args.lambda_:.2f}, mu={args.mu:.2f}')
        plt.xlabel('Edge')
        plt.ylabel('Cloud')
        ax.set_zlabel('z')
        plt.xlim(0,)
        plt.ylim(0,)
        fig.colorbar(sc)
        #cbar = plt.colorbar(ax)
        #cbar.ax.set_ylabel('cost', rotation=270)
        plt.show()


        #########################################
        ###### Plot cost vs. offloading for many setups #########
        #########################################
        # fig = plt.figure()
        # markers = ['o', '^', 's']
        # m = 0
        # for z,(ce,cc,_) in list(min_setup.items()):
        #     values = np.array([[z_,cost]\
        #             for (ce_,cc_,z_),cost in cost_grid.items()\
        #             if ce == ce_ and cc == cc_])
        #     print(f'setup z={z}, (ce,cc)={(ce,cc)} has', values)
        #     plt.plot(values[:,0], values[:,1], marker=markers[m],
        #             label=f'z={z:.2f},ce={ce},cc={cc}')
        #     m = (m+1) % len(markers)
        # plt.xlabel('offloading - z')
        # plt.ylabel('cost')
        # plt.legend(ncol=4)
        # plt.show()
        

        #########################################################
        ###### Plot cost vs. offloading for best setups #########
        #########################################################
        fig = plt.figure()
        markers = ['o', '^', 's']
        m = 0
        for z,(ce,cc,_) in list(min_setup.items()):
            plt.plot(z, cost_grid[ce,cc,z], marker=markers[m],
                    label=f'z={z:.2f},ce={ce},cc={cc}')
            m = (m+1) % len(markers)
        plt.xlabel('offloading - z')
        plt.ylabel('cost')
        plt.legend(ncol=5)
        plt.title(f'lambda={args.lambda_:.2f}')
        #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

        # Create a df for the min setup
        data = []
        for z,(ce,cc,min_cost) in list(min_setup.items()):
            data.append( [ce,cc,z,min_cost] )
        f = f'pareto-bound-lam_{args.lambda_}.csv'
        pd.DataFrame(data,
                columns=['ce', 'cc', 'z', 'cost']
                ).to_csv(f, sep=' ', index=False)


        # Plot the offloading for all feasible points
        fig = plt.figure()
        for (ce,cc,z), cost_ in cost_grid.items():
            plt.plot(z, cost_, marker='o',
                    label=f'z={z:.2f},ce={ce},cc={cc}')
        plt.xlabel('offloading - z')
        plt.ylabel('cost')
        #plt.legend(ncol=5)
        plt.title(f'lambda={args.lambda_:.2f}')
        #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()



    # Get the minimum cost
    #(ce,cc,z), cost = min(cost_grid.items(), key=lambda kv: kv[1])
    cost_grid = dict(sorted(cost_grid.items(),
        key=lambda kv: (round(kv[1],4), kv[0][2]))) # sort (value, z)
    print('sorted costs', cost_grid.items())
    if len(cost_grid) > 0:
        (ce,cc,z), cost = list(cost_grid.items())[0]
        print(ce, cc, z, cost, args.lambda_, args.mu,
                args.edge_d, args.cloud_d, args.target_d,
                args.percentile, args.cost_ratio)
    else:
        print('No solution!')


