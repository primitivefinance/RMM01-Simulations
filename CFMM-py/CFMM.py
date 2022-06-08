import numpy as np
from scipy.stats import norm
from utils import nonnegative

class CFMM:
    def __init__(self, x, y, xbound, ybound, fee):
        self.x = x
        self.y = y
        self.xbound = xbound
        self.ybound = ybound
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
        self.x += deltax
        self.y -= deltay
        assert nonnegative(self.y)
        effective_price = deltay/deltax
        return deltay, effective_price

    def swapYforX(self, deltay):
        assert nonnegative(deltay)
        deltax = self.x - self.TradingFunction()/(self.y + self.gamma * deltay)
        self.y += deltay
        self.x -= deltax
        assert nonnegative(deltax)
        effective_price = deltay/deltax
        return deltax, effective_price

    def marginalPriceAfterXTrade(self, deltax):
        assert nonnegative(deltax)
        self.y -= self.y - self.TradingFunction()/(self.x + self.gamma * deltax)
        self.x += deltax
        assert nonnegative(self.y)
        Sy = self.TradingFunction()/(self.x**2)
        Sx = self.TradingFunction()/(self.y**2)
        return Sy, Sx

    def marginalPriceAfterYTrade(self, deltay):
        assert nonnegative(deltay)
        self.x -= self.x - self.TradingFunction() / (self.y + self.gamma * deltay)
        self.y += deltay
        assert nonnegative(self.x)
        Sy = self.TradingFunction() / (self.x ** 2)
        Sx = self.TradingFunction() / (self.y ** 2)
        return Sy, Sx

    def getSpot(self):
        Sy = self.TradingFunction() / (self.x ** 2)
        Sx = self.TradingFunction() / (self.y ** 2)
        return Sy, Sx

    def InverseG(self, m):
        '''
        Needs to be checked, can share the derivation with you. Pricing done wrt y.
        Basically took -dy/dx with updated reserves and inversed it for delta
        '''
        if m >> self.getSpot()[0]:
            ## Swap In Y
            deltay = np.sqrt(self.TradingFunction()*m) - self.y
            return deltay
        elif m << self.getSpot()[0]:
            ## Swap In X
            deltax = self.x - np.sqrt(self.TradingFunction()/m)
            return deltax


    class RMM01(CFMM):
        def __init__(self, x, y, fee, strike, vol, duration, env, timescale):
            super().__init__(x, y, 1, np.inf, fee)
            self.K = strike
            self.v = vol
            self.T = duration
            self.env = env
            self.timescale

        def TradingFunction(self):
            tau = self.T - self.timescale*self.env.now
            k = self.y - self.K*norm.cdf(norm.ppf(1-self.x)-self.v*np.sqrt(tau))
            return k
