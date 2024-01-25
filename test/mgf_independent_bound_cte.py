from math import exp,ceil
import scipy.integrate as integrate
import scipy.special as special
import numpy as np
from scipy.special import gamma, factorial, gammainc
import scipy.stats as stats
import pandas as pd


def mgf_arrival(theta,t,lam):
    # MGF for poiss(lambda*t)
    return exp(lam*t*(exp(theta)-1))

def mgf_service(theta,t,alpha,beta,mu_ser):
    # MGF for gamma distribution
    return 1/(mu_ser*t) 





if __name__ == '__main__':
    ## mu_frame = 250/21.42*1e3  # Kbps
    ## t = 10 # in seconds
    ## x = .1 # in seconds

    mu_frame = 250/21.42  # Kb/ms
    t = 100000 # in ms 
    x = 100 # in ms
    infty=20
    alpha = shape = 16.39974 # Kbit
    theta_gamma =  1.35
    beta =  1/theta_gamma # Kbit
    theta = 0


    for c in range(1, 41):
        for rho in np.arange(.01, 0.96, .01):


            delays = []
            cdf = []
            for t in np.arange(.1,400.1,.1):
                lambda_ = rho * mu_frame * c

                viol_prob_bound = sum([
                    mgf_service(-theta,s+x,alpha,beta,mu_frame*c)\
                    * mgf_arrival(theta,s,lambda_)\
                    for s in np.linspace(0,t,200)])

                delays += [t]
                cdf += [1-viol_prob_bound]

                #print(f't={t},c={c},lam={lambda_:.2f},eps={viol_prob_bound:.2e}',
                #        f'cdf={1-viol_prob_bound}')

            pd.DataFrame.from_dict({
                'delays': delays,
                'cdf': cdf
            }).to_csv(f'/tmp/rho-{rho:.2f}_c-{c}.csv', index=None,
                    header=False)


