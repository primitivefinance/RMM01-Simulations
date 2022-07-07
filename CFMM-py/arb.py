import simpy as sp
from scipy import optimize as op
import scipy

ZERO = 1e-8
INF = 1e18

class Two_CFMM_Arbitrager:

    def __init__(self, unipool, rmmpool, env):
        self.env = env
        self.M1 = unipool
        self.RMM = rmmpool

    def testSpotPriceDifference(self):
        '''
        Tests the difference of spot prices between Uniswap V2 and RMMs.
        :return:
        '''
        epsilon = 1e-8
        sM1 = self.M1.getMarginalPriceAfterXTrade(epsilon, 'y')
        sRMM = self.RMM.getMarginalPriceAfterXTrade(epsilon, 'y')
        return sM1, sRMM

    def arbAmount_M1Price_GreaterThan_RMM(self, x):
         # deltay = amount of y we get out from swapping x in Uni pool
        deltay = self.M1.virtualSwapXforY(x, 'y')[0]
         # deltax_RMM = amount of x we get out from swapping deltax
        # in RMM pool
        deltax_RMM = self.RMM.virtualSwapYforX(deltay, 'y')[0]
        # If we get more x out of RMM than we put in Uniswap
        if deltax_RMM > x:
            # The maximum amount of y that can be added to the RMM pool.
            deltaymax = self.RMM.ybounds[1] - self.RMM.y*self.RMM.n
            # This amount of y may be inverted to obtain the maximum amount of 
            # y that may be swapped in the Uniswap pool
            if self.M1.y - deltaymax < 0:
                # If the maximum amount of y that may be added to the RMM 
                # pool is greater than the amount of y in the Uniswap pool
                # we can swap an arbitrary amount of x in the Uniswap pool
                deltaxmax = INF 
            else: 
                # Otherwise, we simply invert the amount out formula 
                deltaxmax = self.M1.TradingFunction()/(self.M1.y - deltaymax) - self.M1.x
            def findZero(x):
                lhs = self.M1.getMarginalPriceAfterXTrade(x, 'y')
                deltay = self.M1.virtualSwapXforY(x, 'y')[0]
                rhs = self.RMM.getMarginalPriceAfterYTrade(deltay, 'y')
                return lhs - rhs
            deltax_required = op.brentq(findZero, ZERO, deltaxmax)
            return deltax_required
        else:
            return 0

    def arbAmount_M1Price_LessThan_RMM(self, y):
        # Deltax = amount of x we get out from swapping y in Uni pool
        deltax = self.M1.virtualSwapYforX(y, 'y')[0]
        # Deltay_RMM = amount of y we get out from swapping Deltax
        # in RMM pool
        deltay_RMM = self.RMM.virtualSwapXforY(deltax, 'y')[0]
        # If we get more y out of RMM than we put in Uniswap
        if deltay_RMM > y:
            # The maximum amount of x that can be added to the RMM pool.
            deltaxmax = self.RMM.xbounds[1] - self.RMM.x*self.RMM.n
            # This amount of x may be inverted to obtain the maximum amount of 
            # y that may be swapped in the Uniswap pool
            if self.M1.x - deltaxmax < 0:
                # If the maximum amount of x that may be added to the RMM 
                # pool is greater than the amount of x in the Uniswap pool
                # we can swap an arbitrary amount of y in the Uniswap pool
                deltaymax = INF
            else:
                # Otherwise, we simply invert the amount out formula 
                deltaymax = self.M1.TradingFunction()/(self.M1.x - deltaxmax) - self.M1.y - 1
            def findZero(y):
                lhs = self.M1.getMarginalPriceAfterYTrade(y, 'y')
                deltax = self.M1.virtualSwapYforX(y, 'y')[0]
                rhs = self.RMM.getMarginalPriceAfterXTrade(deltax, 'y')
                return lhs - rhs
            deltay_required = op.brentq(findZero, ZERO, deltaymax)
            return deltay_required
        else:
            return 0

    def arbExactly_M1Price_Greater(self, x):
        deltay = self.M1.virtualSwapXforY(x, 'y')[0]
        self.M1.swapXforY(x)
        deltax_RMM = self.RMM.virtualSwapYforX(deltay, 'y')[0]
        self.RMM.swapYforX(deltay, 'y')
        profit = deltax_RMM - x
        return profit
    
    def arbExactly_M1Price_Less(self, y):
        deltax = self.M1.virtualSwapYforX(y, 'y')[0]
        self.M1.swapYforX(y)
        deltay_RMM = self.RMM.virtualSwapXforY(deltax, 'y')[0]
        self.RMM.swapXforY(deltax, 'y')
        profit = deltay_RMM - y
        return profit
        
    def arbProcess(self):
        while True:
            price_difference = self.testSpotPriceDifference()[0] - self.testSpotPriceDifference()[1]
            epsilon = 1e-8
            if price_difference > 0:
                arbquantity = self.arbAmount_M1Price_GreaterThan_RMM(epsilon)
                if arbquantity == 0:
                    continue
                else:
                    self.arbExactly_M1Price_Greater(arbquantity)
            elif price_difference < 0:
                arbquantity = self.arbAmount_M1Price_LessThan_RMM(epsilon)
                if arbquantity == 0:
                    continue
                else:
                    self.arbExactly_M1Price_Less(arbquantity)
            else:
                continue

class ReferencePriceArbitrager:
    def __init__(self, env, pool) -> None:
        self.env = env 
        self.pool = pool 
    
    def arbExactly(self, price):
        '''
        Find the optimal arbitrage amount
        given a reference price and execute 
        the arbitrage.
        '''
        if price > self.pool.getMarginalPriceAfterYTrade(0, 'y'):
            # If the reference price denominated in y 
            # is above the no-arb bounds, we must 
            # swap y in to increase the price of the pool.
            arb_amount = self.pool.findArbitrageAmountYIn(price)
            self.pool.swapYforX(arb_amount, 'y')
        elif price < self.pool.getMarginalPriceAfterXTrade(0, 'y'):
            # If the reference price denominated in y 
            # is below the no-arb bounds, we must 
            # swap x in to increase the price of the pool.
            arb_amount = self.pool.findArbitrageAmountXIn(price)
            self.pool.swapXforY(arb_amount, 'y')