from math import factorial as fac
from math import exp,ceil
import scipy.integrate as integrate
import scipy.special as special





if __name__ == '__main__':
    lambda_ = 4
    mu = 5
    sigma = 0.5
    T = 100
    infty=20

    result = integrate.quad(lambda t:\
        sum([exp(-mu*t) * (lambda_*t)**k / fac(k)\
        for k in range(ceil(sigma+mu*t),infty)]), 0, T)

    print(result)

