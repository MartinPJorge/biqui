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

# def mgf_service(theta,t,alpha,beta,mu_ser,inf=10):
#     # mgf for gamma distribution
#     return integrate.quad(lambda x: exp(theta*mu_ser*t/x)
#         * stats.gamma.pdf(x, a=alpha, scale=1/beta), 0, inf )[0]


def mgf_service(theta,t,alpha,beta,mu_ser,inf=10):
    # mgf for gamma distribution
    return integrate.quad(lambda x: exp(theta*x)
        *mu_ser*t/ stats.gamma.pdf(x, a=alpha, scale=1/beta), 0.1, inf )[0]



if __name__ == '__main__':
    ## mu_frame = 250/21.42*1e3  # Kbps
    ## t = 10 # in seconds
    ## x = .1 # in seconds

    mu_frame = 250/21.42  # Kb/ms
    t = 10 # in ms 
    x = 100 # in ms
    infty=20
    alpha = shape = 16.39974 # Kbit
    theta_gamma =  1.35
    beta =  1/theta_gamma # Kbit
    theta = 0


    for c in range(1, 41):
        for rho in np.arange(.01, 0.96, .01):
            lambda_ = rho*c*mu_frame

            viol_prob_bound = sum([
                mgf_service(-theta,s+x,alpha,beta,mu_frame*c)\
                * mgf_arrival(theta,s,lambda_)\
                for s in np.linspace(0,t,200)])

            print(f't={t},c={c},lam={lambda_:.2f},eps={viol_prob_bound:.2e}',
                    f'cdf={1-viol_prob_bound}')



