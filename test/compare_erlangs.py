import pandas as pd
import numpy as np


import math


def round_decimals_up(number:float, decimals:int=2):
    """
    Returns a value rounded up to a specific number of decimal places.
    author:https://kodify.net/python/math/round-decimals/
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.ceil(number)

    factor = 10 ** decimals
    return math.ceil(number * factor) / factor




if __name__ == '__main__':
    loads = np.arange(.01,.96,.01)

    T = 100 - 22.1
    #T = 50
    reliab = .99999
    #reliab = .999
    #reliab = .99

    print(f'T={T}, reliability={reliab}')

    for I in [2**i for i in range(8)]:
    #for I in range(61):
        min_c_sim, min_c_apr = 10000, 10000

        if I/40 > .95:
            continue

        for c in list(range(1,41))[::-1]:
            if round_decimals_up(I/c,2) > .95:
                continue
            rho = max(round_decimals_up(I/c,2), .01)

            # Exact M/G/k CDF
            f_sim = f'../results/cdf-simu/rho-{rho:.2f}_c-{c}.csv'
            df_sim = pd.read_csv(f_sim)
            df_sim.columns = ['x', 'cdf']

            # Approx M/G/k CDF
            f_apr = f'../results/MGkapprox/cdf-sweep/rho-{rho:.2f}_c-{c}.csv'
            df_apr = pd.read_csv(f_apr)
            df_apr.columns = ['x', 'cdf']

            # Filter .99999
            df_sim = df_sim[df_sim['cdf']>=reliab]
            df_apr = df_apr[df_apr['cdf']>=reliab]

            if len(df_sim) > 0:
                x_sim = df_sim['x'].values[0]
                if x_sim <= T and c < min_c_sim:
                    min_c_sim = c
            if len(df_apr) > 0:
                x_apr = df_apr['x'].values[0]
                if x_apr <= T and c < min_c_apr:
                    min_c_apr = c

        print(f'I={I}, (c_apr,c_sim)={(min_c_apr,min_c_sim)}')


