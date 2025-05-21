import os
import json
import pandas as pd
from matplotlib import pyplot as plt

explore_path='../results/journal-extension/tolerance-change/'
tolerance = 'tolerance_0.12'
delayc = 'del_cloud_22.8'
delaye = 'del_edge_11.4'

lambdas = {}
for fname in os.listdir(explore_path):
    if 'json' not in fname:
        continue

    if delayc not in fname:
        continue

    if delaye not in fname:
        continue

    if tolerance not in fname:
        continue

    if 'cloud_first' in fname:
        continue

    print('file ', fname)
    lambda_ = float(fname.split('-')[1].split('_')[1])

    # Open and read the JSON file
    with open(explore_path + '/' + fname, 'r') as f:
        explo = json.load(f)
        lambdas[lambda_] = {
            (explo[i]['ce'], explo[i]['cc'], explo[i]['z']):\
                explo[i]['cost']
            for i in explo.keys()
        }


# Sort dict by lambdas
lambdas = dict(sorted(lambdas.items()))

# Mark the best solution
bests = {}

taus = [0,0.05,0.1]
taus = [0.02,0.06,0.12] # Skype
taus = [0.03, 0.06, 0.12]
taus = [0.03, 0.12]

print('there are ', len(lambdas), 'lambdas')
lam_idx = 16
print('lam at', lam_idx, 'is', list(lambdas.keys())[lam_idx])
print('lam at', lam_idx+1, 'is', list(lambdas.keys())[lam_idx+1])
tau_setups = {}



lam_keys = list(lambdas.keys())
lam_idx = 16 # lambda=0.7555555548
lam_idx = 17 # lambda=0.7999999992
print('lam_keus', lam_keys)
print('at ', lambdas[lam_keys[lam_idx]])
cost_best = min([c for (ce,cc,z),c in lambdas[lam_keys[lam_idx]].items()])
ce_best, cc_best, z_best = 0, 0, 0
for (ce,cc,z),c in lambdas[lam_keys[lam_idx]].items():
    if c == cost_best:
        ce_best, cc_best, z_best = ce,cc,z


for lambda_ in [list(lambdas.keys())[lam_idx+1]]:
    # print('lambda', lambda_, 'sols', lambdas[lambda_])
    # min cost setups for such lambda
    min_cost = min([c for (ce,cc,z),c in lambdas[lambda_].items()])
    max_cost = max([c for (ce,cc,z),c in lambdas[lambda_].items()])

    # Obtain the configuration with min cost
    min_confs = [(ce,cc,z) for (ce,cc,z),c in lambdas[lambda_].items()\
            if c==min_cost]

    tau_setups[lambda_] = {tau: {} for tau in taus}
    for tau in taus:
        tau_setups[lambda_][tau] = {
            (ce,cc,z):c for (ce,cc,z),c in lambdas[lambda_].items()
            if (c-min_cost)/c <= tau
        }


print(tau_setups[lambda_][0.03])
for tau in taus:
    out = f'/tmp/lam_{lambda_}_tau_{tau}_sameCosts_boundary.csv'
    pd.DataFrame.from_dict({
        'ce': [ce for ce,cc,z in tau_setups[lambda_][tau]],
        'cc': [cc for ce,cc,z in tau_setups[lambda_][tau]],
        'z': [z for ce,cc,z in tau_setups[lambda_][tau]],
        'c': [c for c in tau_setups[lambda_][tau].values()],
    }).sort_values(by='z').to_csv(out)



markers = ['o', '^', 'x']
for lambda_ in tau_setups:
    for s,tau in enumerate(tau_setups[lambda_]):
        xs = [cc for ce,cc,z in tau_setups[lambda_][tau]]
        ys = [ce for ce,cc,z in tau_setups[lambda_][tau]]
        plt.scatter(xs,ys,label='$\\tau='+str(tau)+'$', s=50-2*s,
                marker=markers[s])
    plt.legend()
    plt.xlabel('cloud')
    plt.ylabel('edge')
    plt.show()

###    #print(f'costs lam={lambda_}: ', list(lambdas[lambda_].values()))
###    #print('lambda[lam]=', lambdas[lambda_])
###
###    print(f'lam={lambda_} min cost: {min_cost}')
###    print(f'   min confs: {min_confs}')
###    print(f'   ratio={abs(min_cost-max_cost)/max_cost}')
###    bests[lambda_] = {cc:ce
###        for (ce,cc,z),cost in lambdas[lambda_].items()
###        if cost==min_cost}
###
###    uniq_cpu_pairs = {}
###    for ce,cc,z in lambdas[lambda_].keys():
###        if cc not in uniq_cpu_pairs:
###            uniq_cpu_pairs[cc] = ce
###        else:
###            uniq_cpu_pairs[cc] = min(uniq_cpu_pairs[cc], ce)
###
###    uniq_cpu_pairs = dict(sorted(uniq_cpu_pairs.items()))
###    plt.plot(uniq_cpu_pairs.keys(), uniq_cpu_pairs.values(),
###            '-o', markersize=3,
###            label=r'$\lambda=$' + f'{lambda_:.2f}')
###
###    plt.scatter(bests[lambda_].keys(),
###            bests[lambda_].values(), marker='*',  s=100)
###
###
###plt.title(f'Dc=22.8 [ms], De={del_edge} [ms], ce/cc=1')
###plt.xlabel('Cloud CPUs')
###plt.ylabel('Edge CPUs')
###plt.legend(loc='lower left')
###
###
###plt.show()
