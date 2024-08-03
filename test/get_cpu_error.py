import pandas as pd
import os

#rho-0.95_c-9.csv

approx_dir = '../results/MGkapprox/cdf-sweep'
simu_dir = '../results/cdf-simu'
perc = 0.99999

def get_cpu_vs_I(soj_dir):
    cpus_dict = {} # I: [CPUs satisfying ]

    for f in os.listdir(soj_dir):
        rho = float(f.split('-')[1].split('_')[0])
        c = int(f.split('-')[2].split('.')[0])
        df = pd.read_csv(soj_dir + '/' + f, header=None)
        df.columns = ['delay', 'cdf']
        df = df[(df['cdf'] >= perc) & (df['delay'] <= 100)]
        if len(df)>0:
            if rho*c not in cpus_dict:
                cpus_dict[rho*c] = c
            else:
                cpus_dict[rho*c] = min(c, cpus_dict[rho*c])


    return cpus_dict



approx_cpu = get_cpu_vs_I(approx_dir)
simu_cpu = get_cpu_vs_I(simu_dir)


approx_cpu = dict(sorted(approx_cpu.items()))

for (rhoc),cpu in approx_cpu.items():
    if (rhoc) in simu_cpu:
        print(rhoc,cpu-simu_cpu[rhoc])

# Compute the errors and store them
soj_err = {I: approx_cpu[I] - simu_cpu[I]
        for I in [I for I in approx_cpu.keys() if I in simu_cpu]}

pd.DataFrame.from_dict({
    'I': soj_err.keys(),
    f'{perc}-cpu-100ms': soj_err.values()
}).sort_values(by=f'{perc}-cpu-100ms').to_csv('/tmp/cpu-err.csv',
    index=False)

pd.DataFrame.from_dict({
    'I': soj_err.keys(),
    f'{perc}-cpu-100ms': soj_err.values()
}).sort_values(by='I').to_csv('/tmp/cpu-err-vs-I.csv',
    index=False)
