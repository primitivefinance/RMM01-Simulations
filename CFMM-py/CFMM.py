from bdb import effective
import numpy as np
from scipy.stats import norm
from utils import nonnegative

# For brentq bounds

ZERO = 1e-8
INF = 1e18

class CFMM:
    def __init__(self, x, y, xbounds, ybounds, fee):
        self.x = x
        self.y = y
        self.xbounds = xbounds
        self.ybounds = ybounds
        self.gamma = 1 - fee


class UniV2(CFMM):
    def __init__(self, x, y, fee):
        super().__init__(x, y, [ZERO, INF], [ZERO, INF], fee)

    def TradingFunction(self):
        k = self.x * self.y
        return k

    def swapXforY(self, deltax):
        '''
        Perform swap calculation from asset X to asset Y and updating the reserves accordingly
        
        returns:
        deltay          - Amount of Y asset out
        effective_price - Price the swap was recieved at denominated in Y
        '''
        assert nonnegative(deltax)
        deltay = self.y - self.TradingFunction()/(self.x + self.gamma * deltax)
        assert nonnegative(deltay)
        self.x += deltax
        self.y -= deltay
        effective_price = deltay/deltax
        return deltay, effective_price

    def virtualSwapXforY(self, deltax, numeraire):
        '''
        Perform swap calculation from asset X to asset Y without actually swapping on the AMM (no reserves are updated)
        
        returns:
        deltay          - Amount of Y asset out
        effective_price - Price the swap was recieved at denominated in numeraire of choice
        '''
        assert nonnegative(deltax)
        initial_x, initial_y = self.x, self.y
        # Normalize delta x to 1 unit
        new_y_reserves = self.TradingFunction()/(self.x + self.gamma * deltax)
        deltay = self.y - new_y_reserves
        assert nonnegative(deltay)
        if numeraire == 'y': 
            effective_price = deltay/deltax
        elif numeraire == 'x':
            effective_price = deltax/deltay
        return deltay, effective_price
    
    def swapYforX(self, deltay):
        '''
        Perform swap calculation from asset Y to asset X and updating the reserves accordingly
        
        returns:
        deltax          - Amount of X asset out
        effective_price - Price the swap was recieved at denominated in Y
        '''
        assert nonnegative(deltay)
        deltax = self.x - self.TradingFunction()/(self.y + self.gamma * deltay)
        assert nonnegative(deltax)
        self.y += deltay
        self.x -= deltax
        effective_price = deltay/deltax
        return deltax, effective_price
    
    def virtualSwapYforX(self, deltay, numeraire):
        '''
        Perform swap calculation from asset Y to asset X without actually swapping on the AMM (no reserves are updated)
        
        returns:
        deltax          - Amount of X asset out
        effective_price - Price the swap was recieved at denominated in numeraire of choice
        '''
        assert nonnegative(deltay)
        initial_x, initial_y = self.x, self.y
        new_x_reserves = self.TradingFunction()/(self.y + self.gamma * deltay)
        deltax = self.x - new_x_reserves
        assert nonnegative(deltax)
        if numeraire == 'y':
            effective_price = deltay/deltax 
        if numeraire == 'x':
            effective_price = deltax/deltay 
        return deltax, effective_price

    def getMarginalPriceAfterXTrade(self, deltax, numeraire):
        '''
        Calculate the pool spot price after a trade from asset X to Y of size deltax
        
        returns:
        Spot price after trade denominated in numeraire of choice
        '''
        assert nonnegative(deltax)
        assert numeraire == 'y' or numeraire == 'x'
        if numeraire == 'y':
            return self.gamma*self.TradingFunction()/(self.x + self.gamma*deltax)**2
        elif numeraire == 'x':
            return 1/(self.gamma*self.TradingFunction()/(self.x + self.gamma*deltax)**2)

    def getMarginalPriceAfterYTrade(self, deltay, numeraire):
        '''
        Calculate the pool spot price after a trade from asset Y to X of size deltay
        
        returns:
        Spot price after trade denominated in numeraire of choice
        '''
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
    def __init__(self, x, y, fee, strike, vol, duration, env, timescale, n_shares):
        super().__init__(x, y, [ZERO, 1*n_shares], [ZERO, INF], fee)
        self.K = strike
        self.vol= vol
        self.T = duration
        self.env = env
        self.timescale = timescale
        self.n = n_shares
        # Reserves normalized to one unit of the risky
        # self.xnorm = x/self.n
        # self.ynorm = y/self.n

    def TradingFunction(self):
        tau = self.T - self.timescale*self.env.now
        k = self.y - self.K*norm.cdf(norm.ppf(1-self.x)-self.vol*np.sqrt(tau))
        return k

    def scaleDown(self, amount):
        '''
        Take an amount an normalize it to correspond to a pool 
        that supports only one unit of the risky asset for calculations.
        '''
        return amount/self.n 
    
    def scaleUp(self, amount):
        '''
        Take an amount and scale it up according to the number of shares.
        '''
        return amount*self.n

    
    def swapXforY(self, deltax, numeraire):
        '''
        Perform swap calculation from asset X to asset Y and updating the reserves accordingly
        
        returns:
        deltay          - Amount of Y asset out
        effective_price - Price the swap was recieved at denominated in numeraire of choice
        '''
        assert nonnegative(deltax)
        tau = self.T - self.timescale*self.env.now
        # Normalize delta x to 1 unit
        new_y_reserves = self.TradingFunction() + self.K * norm.cdf(norm.ppf(1 - (self.x + self.gamma*self.scaleDown(deltax))) - self.vol * np.sqrt(tau))
        deltaynorm = self.y - new_y_reserves
        deltay = self.scaleUp(deltaynorm)
        assert nonnegative(deltay)
        self.y = new_y_reserves
        self.x += self.scaleDown(deltax)
        if numeraire == 'y': 
            effective_price = deltay/deltax
        elif numeraire == 'x':
            effective_price = deltax/deltay

        return deltay, effective_price

    def virtualSwapXforY(self, deltax, numeraire):
        '''
        Perform swap calculation from asset X to asset Y without actually swapping on the AMM (no reserves are updated)
        
        returns:
        deltay          - Amount of Y asset out
        effective_price - Price the swap was recieved at denominated in numeraire of choice
        '''
        assert nonnegative(deltax)
        initial_x, initial_y = self.x, self.y
        tau = self.T - self.timescale*self.env.now
        # Normalize delta x to 1 unit
        new_y_reserves = self.TradingFunction() + self.K * norm.cdf(norm.ppf(1 - (self.x + self.gamma*self.scaleDown(deltax))) - self.vol * np.sqrt(tau))
        deltaynorm = self.y - new_y_reserves
        deltay = self.scaleUp(deltaynorm)
        assert nonnegative(deltay)
        if numeraire == 'y': 
            effective_price = deltay/deltax
        elif numeraire == 'x':
            effective_price = deltax/deltay
        return deltay, effective_price


    def swapYforX(self, deltay, numeraire):
        '''
        Perform swap calculation from asset Y to asset X and updating the reserves accordingly
        
        returns:
        deltax          - Amount of X asset out
        effective_price - Price the swap was recieved at denominated in numeraire of choice
        '''
        assert nonnegative(deltay)
        tau = self.T - self.timescale*self.env.now
        new_x_reserves = 1 - norm.cdf(norm.ppf(((self.y + self.gamma*self.scaleDown(deltay)) - self.TradingFunction()) / self.K) + self.vol * np.sqrt(tau))
        deltaxnorm = self.x - new_x_reserves
        deltax = self.scaleUp(deltaxnorm)
        assert nonnegative(deltax)
        self.x = new_x_reserves
        self.y += self.scaleDown(deltay)
        if numeraire == 'y':
            effective_price = deltay/deltax 
        if numeraire == 'x':
            effective_price = deltax/deltay 
        return deltax, effective_price

    def virtualSwapYforX(self, deltay, numeraire):
        '''
        Perform swap calculation from asset Y to asset X without actually swapping on the AMM (no reserves are updated)
        
        returns:
        deltax          - Amount of X asset out
        effective_price - Price the swap was recieved at denominated in numeraire of choice
        '''
        assert nonnegative(deltay)
        initial_x, initial_y = self.x, self.y
        tau = self.T - self.timescale*self.env.now
        new_x_reserves = 1 - norm.cdf(norm.ppf(((self.y + self.gamma*self.scaleDown(deltay)) - self.TradingFunction()) / self.K) + self.vol * np.sqrt(tau))
        deltaxnorm = self.x - new_x_reserves
        deltax = self.scaleUp(deltaxnorm)
        assert nonnegative(deltax)
        if numeraire == 'y':
            effective_price = deltay/deltax 
        if numeraire == 'x':
            effective_price = deltax/deltay 
        return deltax, effective_price



    def getMarginalPriceAfterXTrade(self, deltax, numeraire):
        '''
        Calculate the pool spot price after a trade from asset X to Y of size deltax
        
        returns:
        Spot price after trade denominated in numeraire of choice
        '''
        tau = self.T - self.timescale*self.env.now
        def g(delta):
            return self.K*np.exp(norm.ppf(1 - self.x - delta)*self.vol*np.sqrt(tau))*np.exp(-0.5*tau*self.vol**2)
        if numeraire == 'y':
            return self.gamma*g(self.gamma*self.scaleDown(deltax))
        elif numeraire == 'x':
            return 1/(self.gamma*g(self.gamma*self.scaleDown(deltax)))

    def getMarginalPriceAfterYTrade(self, deltay, numeraire):
        '''
        Calculate the pool spot price after a trade from asset Y to X of size deltay
        
        returns:
        Spot price after trade denominated in numeraire of choice
        '''
        tau = self.T - self.timescale*self.env.now
        def g(delta):
            return (1/self.K)*np.exp(-norm.ppf((self.y + delta - self.TradingFunction())/self.K)*self.vol*np.sqrt(tau))*np.exp(-0.5*tau*self.vol**2)
        if numeraire == 'x':
            return self.gamma*g(self.gamma*self.scaleDown(deltay))
        elif numeraire == 'y':
            return 1/(self.gamma*g(self.gamma*self.scaleDown(deltay)))

    def findArbitrageAmountYIn(self, m):
        '''
        Given a reference price denominated in y, find the amount of y to swap in
        in order to align the price of the pool with the reference market.
        '''
        assert m > self.getMarginalPriceAfterYTrade(0, 'y')
        tau = self.T - self.env.now*self.timescale
        def inverseG(ref_price):
            return self.TradingFunction() - self.y + self.K*norm.cdf(-np.log(self.K*ref_price)/(self.vol*np.sqrt(tau)) - 0.5*self.vol*np.sqrt(tau))
        m = 1/m
        return self.scaleUp((1/self.gamma)*inverseG((1/self.gamma)*m))

    
    def findArbitrageAmountXIn(self, m):
        '''
        Given a reference price denominated in y, find the amount of x to swap in
        in order to align the price of the pool with the reference market.
        '''
        assert m < self.getMarginalPriceAfterXTrade(0, 'y')
        tau = self.T - self.env.now*self.timescale
        def inverseG(ref_price):
            return self.x - 1 + norm.cdf(-np.log(ref_price/self.K)/(self.vol*np.sqrt(tau)) - 0.5*self.vol*np.sqrt(tau))
        return self.scaleUp((1/self.gamma)*inverseG((1/self.gamma)*m))

    def addLiquidity(self, n_shares_to_add):
        '''
        Function to add n risky equivalent units. Returns the amount of 
        each asset that the liquidity provider should subtract from their wallet.
        n_shares_to_add can be fractional.
        '''
        deltax = self.x*n_shares_to_add
        deltay = self.y*n_shares_to_add
        # self.x += deltax 
        # self.y += deltay 
        self.n += n_shares_to_add
        self.xbounds[1] = 1*self.n
        return deltax, deltay
    
    def removeLiquidity(self, n_shares_to_remove):
        '''
        Function to remove liquidity from the pool. 
        Return the amount of each asset credited to the 
        actor initiating the withdrawal.
        '''
        deltax = (n_shares_to_remove/self.n)*self.x
        deltay = (n_shares_to_remove/self.n)*self.y
        self.n -= n_shares_to_remove
        self.xbounds[1] = 1*self.n
        return deltax, deltay
