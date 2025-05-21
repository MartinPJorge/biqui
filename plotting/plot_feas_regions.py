import os
import json
from matplotlib import pyplot as plt

explore_path='../results/journal-extension/delay-change/'
del_edge = '15.96'
ecr = 'edge_cloud_ratio_1-'


lambdas = {}
for fname in os.listdir(explore_path):
    if 'json' not in fname:
        continue

    if del_edge not in fname:
        continue

    if ecr not in fname:
        continue

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
taus = [0.01, 0.02, 0.03]

print('there are ', len(lambdas), 'lambdas')
lambdas_ = [list(lambdas.keys())[10]] # SKype
lambdas_ = [list(lambdas.keys())[9]] 
lambdas_ = [list(lambdas.keys())[38]] 
tau_setups = {}

for lambda_ in lambdas_:
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
out = f'/tmp/lam_{lambda_}_tau_{taus[-1]}_sameCosts_boundary.csv'
#df.Dataframe.from_dict({
#    'ce': [ce for ce,cc,z in tau_setups[lambda_][taus[-1]]],
#    'cc': [cc for ce,cc,z in tau_setups[lambda_][taus[-1]]],
#    'z': [z for ce,cc,z in tau_setups[lambda_][taus[-1]]],
#    'c': [c for c in tau_setups[lambda_][taus[-1]].values()],
#}).sort_values(by='z').to_csv(out)



markers = ['o', '^', 'x']
for lambda_ in tau_setups:
    for s,tau in enumerate(tau_setups[lambda_]):
        xs = [z for ce,cc,z in tau_setups[lambda_][tau]]
        ys = [c for c in tau_setups[lambda_][tau].values()]
        plt.scatter(xs,ys,label='$\\tau='+str(tau)+'$', s=50-2*s,
                marker=markers[s])
    plt.legend()
    plt.xlabel('z')
    plt.ylabel('K(x,y,z)')
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
