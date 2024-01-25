from math import exp
import numpy as np
import pandas as pd


def epsilon(alpha,beta,mu,lam,theta,t,x):
    try:
        eps = (1+alpha/beta)**(-alpha)/mu*sum([exp(lam*s*(exp(theta)-1))/(s+x)\
            for s in range(t)])
    except OverflowError as err:
        eps = float('nan')

    return eps


mu = 250/21.42  # Kb/ms
t = 100000 # in ms 
x = 100 # in ms
infty=20
alpha = shape = 16.39974 # Kbit
theta_gamma =  1.35
beta =  1/theta_gamma # Kbit
theta = 0
nthetas=100
tmax = 100


for x in np.arange(.1,400,.1):
    for c in range(1,40):
        prior_eps = 100
        prior_t = None
        for rho in np.arange(.1,.96,.1):
            lam = c*mu*rho
            
            # Search meshgrid
            thetas = np.linspace(0, 10, nthetas)
            ts = np.array(range(1,tmax))
            thetav, tv = np.meshgrid(thetas, ts)


            # Create meshgrid dataframe
            NT = np.product(tv.shape)
            data = {
                "theta": np.reshape(thetav,NT),
                "t": np.reshape(tv,NT)
            }
            df = pd.DataFrame(data=data)

            # Compute the epsilon bound for each pair
            eps_col = [epsilon(alpha,beta,mu,lam,theta,int(t),x)\
                for theta,t in df[['theta','t']].values]


            # Obtain the minimum setup
            df['epsilon'] = eps_col
            df.dropna(inplace=True)
            df_interval = df[(df['epsilon']<=1) & (df['epsilon']>=0)]
            df_interval = df_interval[df_interval['epsilon']<=prior_eps]
            if prior_t != None:
                df_interval = df_interval[df_interval['t']==prior_t]
            df_interval.reset_index(inplace=True)
            _,theta_min, t_min, eps_min =\
                df_interval.iloc[df_interval['epsilon'].idxmax()].values

            print(f'x={x},c={c},rho={rho},theta_min={theta_min},t_min={t_min},eps_min={eps_min}')

            prior_eps = eps_min
            if prior_t == None:
                prior_t = t_min



