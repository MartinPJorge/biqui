import pandas as pd
from math import ceil

def closest_l(setups, l):
    return sorted([l_ for l_ in setups.keys() if l_>=l])[0]

def avg_delay(df):
    # https://stats.stackexchange.com/a/13377
    # Riemman sum w/ dx=x[1]-x[0]
    dx = df['x'].values[1] - df['x'].values[0]
    return sum(1-df['cdf'].values) * dx

biqui_results='biqui-targetd_100-reliab_0.99999-mode_18-22-0-x1.45-1690737649.csv'
del_e=18.2
del_c=22.8

df_biqui = pd.read_csv(biqui_results, sep=' ').dropna()

setups = {
    r['lambda']: (int(r['ce']),int(r['cc']),float(r['z']))\
    for _,r in df_biqui.iterrows()
}

df_traffic = pd.read_csv('traffic_torino.csv').dropna()

roads = df_traffic.columns

lambda_ = df_traffic[roads[0]].values
for r in roads[1:-1]:
    lambda_ += df_traffic[r].values


cache_cdfs = {}

data = []
for l in lambda_:
    l_ = closest_l(setups, l)
    ce, cc, z = setups[l_]

    mu = 1/22.5
    rho_e = l_ * (1-z) / (ce * 1/mu) if ce > 0 else 0
    rho_c = l_ * z / (cc * 1/mu) if cc > 0 else 0


    pe, dpe, avge = 1, 0, 0
    if rho_e > 0 and rho_e <= 0.95:
        rho_e = ceil(rho_e*100)/100
        f = f'cdf-sweep/rho-{rho_e:.2f}_c-{ce}.csv'
        cdf = pd.read_csv(f, names=['x', 'cdf'], header=None).dropna()
        #dpe, pe = cdf[cdf['cdf']>=0.99999].head(1).values[0]
        dpe, pe = cdf[cdf['x']<=100-del_e].tail(1).values[0]
        avge = avg_delay(cdf) + del_e

    pc, dpc, avgc = 1, 0, 0
    if rho_c > 0 and rho_c <= 0.95:
        rho_c = ceil(rho_c*100)/100
        f = f'cdf-sweep/rho-{rho_c:.2f}_c-{cc}.csv'
        cdf = pd.read_csv(f, names=['x', 'cdf'], header=None).dropna()
        #dpc, pc = cdf[cdf['cdf']>=0.99999].head(1).values[0]
        dpc, pc = cdf[cdf['x']<=100-del_c].tail(1).values[0]

        avgc = avg_delay(cdf) + del_c

    data.append([
        l_, ce, cc, z, pe, pc, dpe, dpc, avge, avgc,
        (1-z)*avge + z*avgc])
    print(data[-1])

pd.DataFrame(data, columns=\
        ['l_', 'ce', 'cc', 'z', 'pe', 'pc', 'dpe', 'dpc', 'avge',
            'avgc','tot_avg']).to_csv('BiQui-aggregated_traffic-torino_v08.csv', index=False)






