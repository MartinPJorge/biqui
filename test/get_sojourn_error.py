import pandas as pd
import os

#rho-0.95_c-9.csv

approx_dir = '../results/MGkapprox/cdf-sweep'
simu_dir = '../results/cdf-simu'
perc = 0.99999

def get_soj_vs_I(soj_dir):
    soj_dict = {}

    for f in os.listdir(soj_dir):
        rho = float(f.split('-')[1].split('_')[0])
        c = int(f.split('-')[2].split('.')[0])
        df = pd.read_csv(soj_dir + '/' + f, header=None)
        df.columns = ['delay', 'cdf']
        df = df[df['cdf'] >= perc]
        if len(df)>0:
            soj_dict[rho*c] = df['delay'].values[0]

    return soj_dict



approx_soj = get_soj_vs_I(approx_dir)
simu_soj = get_soj_vs_I(simu_dir)


approx_soj = dict(sorted(approx_soj.items()))

for (rhoc),delay in approx_soj.items():
    if (rhoc) in simu_soj:
        print(rhoc,delay-simu_soj[rhoc])

# Compute the errors and store them
soj_err = {I: approx_soj[I] - simu_soj[I]
        for I in [I for I in approx_soj.keys() if I in simu_soj]}

pd.DataFrame.from_dict({
    'I': soj_err.keys(),
    f'{perc}-delay': soj_err.values()
}).sort_values(by=f'{perc}-delay').to_csv('/tmp/soj-err.csv',
    index=False)

