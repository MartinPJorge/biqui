from math import exp,log
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import scipy


# def epsilon(mu,lam,theta,d,sigma=0):
#     try:
#         eps = exp(-theta*(sigma+mu*d)) * exp(lam*d*(exp(theta)-1))
#     except OverflowError as err:
#         eps = float('nan')
#     return eps


def delay(mu,lam,theta,epsilon,sigma=0):
    return (log(epsilon) + theta*sigma) / (-theta*mu +lam*exp(theta) -lam)

def delay2(mu,lam,theta,epsilon,sigma=0):
    A = lam*exp(theta)-1-theta*mu
    print('log inside', epsilon*A*exp(theta*sigma)+1)
    result = 1/A * log(epsilon*A*exp(theta*sigma)+1)

    return result





mu = 250/21.42  # Kb/ms
nu = 1/22.5
t = 100000 # in ms 
x = 100 # in ms
infty=20
alpha = shape = 16.39974 # Kbit
theta_gamma =  1.35
beta =  1/theta_gamma # Kbit
theta = 0
nthetas=100
tmax = 100
epsilon=1e-6
#epsilon=1e-1


for c in range(1,40):
    prior_eps = 100
    #for rho in np.arange(.1,.96,.1):
    for rho in np.arange(.1,.96,.1):
        lam = c*mu*rho
        
        thetas = np.arange(.01,10,.01)

        f = lambda thetas: [delay(mu,lam,theta,epsilon,sigma=0) for theta in
                thetas]
        min_f = scipy.optimize.minimize(f, x0=thetas[0],
                bounds=[[thetas[0],thetas[-1]]]).x
        sol = scipy.optimize.minimize(f, x0=thetas[0],
                bounds=[[thetas[0],min_f]])
        theta_min, delay_min = sol.x[0], sol.fun


        # plt.plot(thetas,[delay(mu,lam,theta,epsilon,sigma=0) for theta in
        #     thetas],label=f'rho={rho}')

        # MALAKIA
        plt.plot(thetas,[delay2(mu,lam,theta,epsilon,sigma=0) for theta in
            thetas],label=f'rho={rho}',ls='dashed')


        #plt.plot(theta_min,delay_min,label=f'rho={rho}',ls='dashed')
        #plt.scatter(theta_min,delay_min,label=f'rho={rho}',ls='dashed')
        print(f'c={c},rho={rho},theta_min={theta_min},delay_min={delay_min}')



    plt.legend()
    plt.xlabel('theta')
    plt.ylabel('delay')
    #plt.ylim(0,100)
    #plt.ylim(0)
    plt.title(f'c={c},')
    plt.show()


