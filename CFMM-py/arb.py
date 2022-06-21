import simpy as sp
from scipy import optimize as op
import scipy


class Two_CFMM_Arbitrage:

    def __init__(self, market1, market2, env):
        self.env = env
        self.M1 = market1
        self.RMM = market2

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
        deltay = self.M1.virtualSwapXforY(x, 'y')[0]
        deltax_RMM = self.RMM.virtualSwapYforX(deltay, 'y')
        if deltax_RMM > x:
            def findZero(x):
                lhs = self.M1.getMarginalPriceAfterXTrade(x, 'y')
                deltay = self.M1.virtualSwapXforY(x, 'y')[0]
                rhs = self.RMM.getMarginalPriceAfterYTrade(deltay, 'y')
                return lhs - rhs
            deltax_required = op.brentq(FindZero(x), 0)
            return deltax_required
        else:
            return 0

    def arbAmount_M1Price_LessThan_RMM(self, y):
        deltax = self.M1.virtualSwapYforX(y, 'y')[0]
        deltay_RMM = self.RMM.virtualSwapXforY(deltax, 'y')[0]
        if deltay_RMM > y:
            def findZero(y):
                lhs = self.Uni.getMarginalPriceAfterYTrade(y, 'y')
                deltax = self.M1.virtualSwapYforX(y)[0]
                rhs = self.RMM.getMarginalPriceAfterXTrade(deltax, 'y')
                return lhs - rhs
            deltay_required = op.brentq(lhs-rhs, 0)
            return deltay_required
        else:
            return 0

    def arbExactly_M1Price_Greater(self, x):
        deltay = self.M1.virtualSwapXforY(x, 'y')[0]
        self.M1.swapXforY(x, 'y')
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
                arbquantity = self.arbAmountUniPriceGreaterThanRMM01(epsilon)
                if arbquantity == 0:
                    continue
                else:
                    arbExactly_M1Price_Greater(arbquantity)
            elif price_difference < 0:
                arbquantity = self.arbAmountUniPriceLessThanRMM01(epsilon)
                if arbquantity == 0:
                    continue
                else:
                    arbExactly_M1Price_Less(arbquantity)
            else:
                continue
