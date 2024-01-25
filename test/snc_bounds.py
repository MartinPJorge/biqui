from math import factorial as fac
from math import exp,ceil
import scipy.integrate as integrate
import scipy.special as special
import numpy as np




if __name__ == '__main__':
    mu = 1/22.5 # in seconds
    sigma = 0.1 # bounding service curve burst
    T = .1 # in seconds
    infty=20

    for c in range(1, 41):
        for rho in np.arange(.01, 0.96, .01):
            lambda_ = rho * mu * c

            result = integrate.quad(lambda t:\
                sum([exp(-mu*c*t) * (lambda_*t)**k / fac(k)\
                for k in range(ceil(sigma+mu*c*t),infty)]), 0, T)

            print(f'c={c},rho={rho:.2f},CDF={1-result[0]:.10f}')


