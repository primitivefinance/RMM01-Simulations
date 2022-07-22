import numpy as np
from scipy.stats import norm

def nonnegative(x):
    if isinstance(x, np.ndarray):
        return (x >= 0).all()
    return x >= 0

def wiener(w0, dt, steps):
    '''
    Generator function for a simple 
    Wiener process aka Brownian motion.
    '''
    wi = w0
    i = 0
    yield wi
    while i < steps:
        yi = np.random.normal()
        dw = np.sqrt(dt)*yi
        yield wi + dw
        wi = wi + dw
        i += 1

def gbm(s0, dt, time_horizon, sigma, mu):
    '''
    Generator function to get a GBM with prescribed 
    parameters. 
    Time must be in unit of years. 
    Sigma is annualized volatility.
    Mu is annualized drift.
    '''
    si = s0
    i = 0
    t = 0
    steps = round(time_horizon/dt)
    for w in wiener(0, dt, steps):
        si = s0*np.exp((mu - 0.5*sigma**2)*t+sigma*w)
        yield si
        t = i*dt
        i += 1

def getInitialYGivenInitialXRMM(x, strike, volatility, tau):
    return strike*norm.cdf(norm.ppf(1-x)-volatility*np.sqrt(tau))

def getInitialXGivenReferencePriceRMM(ref_price, strike, volatility, tau):
    return 1 - norm.cdf((1/(volatility*np.sqrt(tau)))*(np.log(ref_price/strike) + 0.5*tau*volatility**2))

