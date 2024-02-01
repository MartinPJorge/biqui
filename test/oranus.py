import argparse
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







if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, required=False,
                        help="output directory to store the CDFs",
                        default='../results/cdf-oranus')
    parser.add_argument("--out_pref", type=str, required=False,
                        help="CDFs name prefix",
                        default='')
    args = parser.parse_args()





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

    def W(alpha,beta,lam,mu,eps,delta,theta,rho_s):
        return ( -alpha/beta*log(1-theta/beta/mu)
            -2/theta*(log(eps/2)+log(1-exp(-theta*delta))) )/(rho_s-delta)

    rho_s=1
    eps=1e-6


    epsilons = [1e-1,1e-2,1e-3,1e-4,1e-5,1e-6]
    
    for c in range(1,41):
        last_W=0
        for rho in np.arange(.01,.96,.01):
            lam = c*mu*rho

            # Stores the min delays for eps=1e-1,1e-2,...
            min_delays = []

            for eps in epsilons:
                theta_min,delta_min,delay_min = 1000,1000,1000

                thetas = np.linspace(.01,beta*mu-.01, 100)
                for theta in thetas:
                    deltas = np.linspace(.01,rho_s/2-lam/2*(exp(theta)-1),100)
                    deltas = deltas[deltas>0]
                    # print(deltas)
                    for delta in deltas:
                        # print(f'theta={theta},delta={delta}')
                        # print(f'theta/beta/mu={theta/beta/mu}')
                        W_ = W(alpha,beta,lam,mu*c,eps,delta,theta,rho_s)
                        #print(f'c={c},rho={rho},theta={theta},delta={delta},W={W_}')

                        #print(f'c={c},rho={rho},W_={W_},delay_min={delay_min}')
                        if W_ < delay_min and W_ > last_W + 1:
                            theta_min,delta_min,delay_min = theta,delta,W_
                            #print('found min', delay_min)

                # Store the minimum delay
                min_delays += [delay_min]



            out_f = f'{args.out_dir}/{args.out_pref}rho-{rho:.2f}_c-{c}.csv'
            last_W = delay_min
            pd.DataFrame(data={
                'delay': [0] + min_delays,
                'cdf': [0] + [1-eps for eps in epsilons],
            }).to_csv(out_f, header=None, index=False)

            print(f'c={c},rho={rho},W={delay_min}')
            
