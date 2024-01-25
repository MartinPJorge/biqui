from math import exp,ceil
import scipy.integrate as integrate
import scipy.special as special
import numpy as np
from scipy.special import gamma, factorial, gammainc
import scipy.stats as stats


def mgf_arrival(theta,t,lam):
    # MGF for poiss(lambda*t)
    return exp(lam*t*(exp(theta)-1))

def mgf_service(theta,t,alpha,beta,mu_ser,inf=20):
    # MGF for a gamma based processing
    return sum([exp(theta*k)\
            * integrate.quad(lambda x:\
            stats.gamma.pdf(x, a=alpha, scale=1/beta),\
            k*mu_ser*t, (k+1)*mu_ser*t)[0]
            for k in range(inf)])


def backlog_bound_all(t,x,lam,alpha,beta,mu_ser,theta,inf=20):
    return integrate.quad(lambda s:\
            mgf_arrival(theta,s,lam)\
            * mgf_service(-theta,t,alpha,beta,mu_ser,inf),
        0, t)[0]


def backlog_bound(t,x,lam,alpha,beta,mu,theta,inf=20):
    # using Poisson arrival with rate lam
    # and gamma(alpha,beta) packet size, mu processing rate
    # P( B(t)>x ) <= bound(theta)

    return integrate.quad(lambda s:\
            mgf_arrival(theta,s,lam)\
            * sum( np.array([exp(-theta*k) for k in range(inf)])\
            * (gammainc(alpha,[beta*(k+1)*mu*s for k in range(inf)])
            - gammainc(alpha,[beta*k*mu*s for k in range(inf)])) ),
        0, T)[0] / gamma(alpha)



if __name__ == '__main__':
    mu = 1/22.5 # in seconds
    mu_frame = 250/21.42*1e3  # Kbps
    T = .1 # in seconds
    infty=20
    alpha = shape = 16.39974 # Kbit
    theta =  1.35
    beta =  1/theta # Kbit


    for c in range(1, 41):
        for rho in np.arange(.01, 0.96, .01):
            lambda_ = rho * mu_frame * c
            print( backlog_bound(t=1,x=T,lam=lambda_,alpha=alpha,
                beta=beta,mu=mu_frame*c,theta=0,inf=20) )
            print( backlog_bound_all(t=1,x=T,lam=lambda_,alpha=alpha,
                beta=beta,mu_ser=mu_frame*c,theta=0,inf=20) )

