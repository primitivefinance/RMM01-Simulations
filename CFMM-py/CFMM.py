from bdb import effective
import numpy as np
from scipy.stats import norm
from utils import nonnegative

class CFMM:
    def __init__(self, x, y, xbounds, ybounds, fee):
        self.x = x
        self.y = y
        self.xbounds = xbounds
        self.ybounds = ybounds
        self.gamma = 1 - fee


class UniV2(CFMM):
    def __init__(self, x, y, fee):
        super().__init__(x, y, np.inf, np.inf, fee)

    def TradingFunction(self):
        k = self.x * self.y
        return k

    def swapXforY(self, deltax):
        assert nonnegative(deltax)
        deltay = self.y - self.TradingFunction()/(self.x + self.gamma * deltax)
        assert nonnegative(deltay)
        self.x += deltax
        self.y -= deltay
        effective_price = deltay/deltax
        return deltay, effective_price

    def swapYforX(self, deltay):
        assert nonnegative(deltay)
        deltax = self.x - self.TradingFunction()/(self.y + self.gamma * deltay)
        assert nonnegative(deltax)
        self.y += deltay
        self.x -= deltax
        effective_price = deltay/deltax
        return deltax, effective_price

    def getMarginalPriceAfterXTrade(self, deltax, numeraire):
        assert nonnegative(deltax)
        assert numeraire == 'y' or numeraire == 'x'
        if numeraire == 'y':
            return self.gamma*self.TradingFunction()/(self.x + self.gamma*deltax)**2
        elif numeraire == 'x':
            return 1/(self.gamma*self.TradingFunction()/(self.x + self.gamma*deltax)**2)

    def getMarginalPriceAfterYTrade(self, deltay, numeraire):
        assert nonnegative(deltay)
        assert numeraire == 'y' or numeraire == 'x'
        if numeraire == 'y':
            return 1/(self.gamma*self.TradingFunction()/(self.y + self.gamma*deltay)**2)
        elif numeraire == 'x':
            return self.gamma*self.TradingFunction()/(self.y + self.gamma*deltay)**2

    def findArbitrageAmountYIn(self, m):
        '''
        Given a reference price denominated in y, find the amount of y to swap in
        in order to align the price of the pool with the reference market.
        '''
        assert m > self.getMarginalPriceAfterYTrade(0, "y")
        def inverseG(price):
            return np.sqrt(self.TradingFunction()/price) - self.y
        # print("inverG", inverseG(1/m))
        # For this inverG formula, the target price must be in x.y-1
        m = 1/m
        return (1/self.gamma)*inverseG(m/self.gamma)

    def findArbitrageAmountXIn(self, m):
        '''
        Given a reference price denominated in y, find the amount of x to swap in
        in order to align the price of the pool with the reference market.
        '''
        assert m < self.getMarginalPriceAfterXTrade(0, "y")
        def inverseG(price):
            return np.sqrt(self.TradingFunction()/price) - self.x
        # print("inverseG", inverseG(m))
        return (1/self.gamma)*inverseG(m/self.gamma)


class RMM01(CFMM):
    def __init__(self, x, y, fee, strike, vol, duration, env, timescale):
        super().__init__(x, y, 1, np.inf, fee)
        self.K = strike
        self.vol= vol
        self.T = duration
        self.env = env
        self.timescale = timescale

    def TradingFunction(self):
        tau = self.T - self.timescale*self.env.now
        k = self.y - self.K*norm.cdf(norm.ppf(1-self.x)-self.vol*np.sqrt(tau))
        return k
    
    def swapXforY(self, deltax, numeraire):
        '''
        '''
        assert nonnegative(deltax)
        tau = self.T - self.timescale*self.env.now
        new_y_reserves = self.TradingFunction() + self.K * norm.cdf(norm.ppf(1 - (self.x + self.gamma*deltax)) - self.vol * np.sqrt(tau))
        deltay = self.y - new_y_reserves
        assert nonnegative(deltax)
        self.y = new_y_reserves
        self.x += deltax 
        if numeraire == 'y': 
            effective_price = deltay/deltax
        elif numeraire == 'x':
            effective_price = deltax/deltay

        return deltay, effective_price



    def swapYforX(self, deltay, numeraire):
        '''
        '''
        assert nonnegative(deltay)
        tau = self.T - self.timescale*self.env.now
        new_x_reserves = 1 - norm.cdf(norm.ppf(((self.y + self.gamma*deltay) - self.TradingFunction()) / self.K) + self.vol * np.sqrt(tau))
        deltax = self.x - new_x_reserves
        assert nonnegative(deltax)
        self.x = new_x_reserves
        self.y += deltay 
        if numeraire == 'y':
            effective_price = deltay/deltax 
        if numeraire == 'x':
            effective_price = deltax/deltay 
        return deltax, effective_price



    def getMarginalPriceAfterXTrade(self, deltax, numeraire):
        '''
        '''
        tau = self.T - self.timescale*self.env.now
        def g(delta):
            return self.K*np.exp(norm.ppf(1 - self.x - deltax)*self.vol*np.sqrt(tau))*np.exp(-0.5*tau*self.vol**2)
        if numeraire == 'y':
            return self.gamma*g(self.gamma*deltax)
        elif numeraire == 'x':
            return 1/(self.gamma*g(self.gamma*deltax))

    def getMarginalPriceAfterYTrade(self, deltay, numeraire):
        '''
        '''
        tau = self.T - self.timescale*self.env.now
        def g(delta):
            return (1/self.K)*np.exp(-norm.ppf((self.y + delta - self.TradingFunction())/self.K)*self.vol*np.sqrt(tau))*np.exp(0.5*tau*self.vol**2)
        if numeraire == 'x':
            return self.gamma*g(self.gamma*deltay)
        elif numeraire == 'y':
            return 1/(self.gamma*g(self.gamma*deltay))

    def findArbitrageAmountYIn(self, m):
        '''
        '''
        assert m > self.getMarginalPriceAfterYTrade(0, 'y')
        tau = self.T - self.env.now*self.timescale
        def inverseG(ref_price):
            return self.TradingFunction() - self.y + self.K*norm.cdf(np.log(self.K*ref_price)/(self.vol*tau) + 0.5*self.vol*np.sqrt(tau))
        return (1/self.gamma)*inverseG((1/self.gamma)*m)

    
    def findArbitrageAmountXIn(self, m):
        '''
        '''
        assert m < self.getMarginalPriceAfterXTrade(0, 'y')
        tau = self.T - self.env.now*self.timescale
        def inverseG(ref_price):
            return self.x - 1 + norm.cdf(-np.log(ref_price/self.K)/(self.vol*np.sqrt(tau)) - 0.5*self.vol*np.sqrt(tau))
        return (1/self.gamma)*inverseG((1/self.gamma)*m)
