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

for lambda_ in list(lambdas.keys())[10:]:
    print('lambda', lambda_, 'sols', lambdas[lambda_])
    # min cost setups for such lambda
    min_cost = min([c for (ce,cc,z),c in lambdas[lambda_].items()])
    max_cost = max([c for (ce,cc,z),c in lambdas[lambda_].items()])

    # Obtain the configuration with min cost
    min_confs = [(ce,cc,z) for (ce,cc,z),c in lambdas[lambda_].items()\
            if c==min_cost]



    #print(f'costs lam={lambda_}: ', list(lambdas[lambda_].values()))
    #print('lambda[lam]=', lambdas[lambda_])

    print(f'lam={lambda_} min cost: {min_cost}')
    print(f'   min confs: {min_confs}')
    print(f'   ratio={abs(min_cost-max_cost)/max_cost}')
    bests[lambda_] = {cc:ce
        for (ce,cc,z),cost in lambdas[lambda_].items()
        if cost==min_cost}

    uniq_cpu_pairs = {}
    for ce,cc,z in lambdas[lambda_].keys():
        if cc not in uniq_cpu_pairs:
            uniq_cpu_pairs[cc] = ce
        else:
            uniq_cpu_pairs[cc] = min(uniq_cpu_pairs[cc], ce)

    uniq_cpu_pairs = dict(sorted(uniq_cpu_pairs.items()))
    plt.plot(uniq_cpu_pairs.keys(), uniq_cpu_pairs.values(),
            '-o', markersize=3,
            label=r'$\lambda=$' + f'{lambda_:.2f}')

    plt.scatter(bests[lambda_].keys(),
            bests[lambda_].values(), marker='*',  s=100)


plt.title(f'Dc=22.8 [ms], De={del_edge} [ms], ce/cc=1')
plt.xlabel('Cloud CPUs')
plt.ylabel('Edge CPUs')
plt.legend(loc='lower left')


plt.show()
