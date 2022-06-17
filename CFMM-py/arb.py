import simpy as sp
from scipy import optimize as op
import scipy
from CFMM import UniV2
from CFMM import RMM01


class Arbitrage:

    def __init__(self, market1, market2, env):
        self.env = env
        self.Uni = market1
        self.RMM = market2

    def testSpotPriceDifference(self):
        '''
        Tests the difference of spot prices between Uniswap V2 and RMMs.
        :return:
        '''
        epsilon = 1e-8
        sUni = self.Uni.getMarginalPriceAfterXTrade(epsilon, 'y')
        sRMM = RMM01.getMarginalPriceAfterXTrade(epsilon, 'y')
        return sUni, sRMM

    def arbAmountUniPriceGreaterThanRMM01(self, x):
        deltay = self.Uni.swapXforY(x)
        deltax_RMM = self.RMM.swapYforX(deltay, 'y')
        assert deltax_RMM > x
        lhs = self.Uni.getMarginalPriceAfterXTrade(x, 'y')
        rhs = self.RMM.getMarginalPriceAfterYTrade(deltay, 'y')
        deltax_required = op.brentq(lhs-rhs, 0)

        return deltax_required

    def arbAmountUniPriceLessThanRMM01(self, y):
        deltax = self.Uni.swapYforX(y)
        deltay_RMM = self.RMM.swapXforY(deltax, 'y')
        assert deltay_RMM > y
        lhs = self.Uni.getMarginalPriceAfterYTrade(y, 'y')
        rhs = self.RMM.getMarginalPriceAfterXTrade(deltax, 'y')
        deltay_required = op.brentq(lhs-rhs, 0)
        return deltay_required

    def arbExactlyUniPriceGreater(self):


    def arbProcess(self):
        while True:
            price_difference = self.testSpotPriceDifference()[0] - self.testSpotPriceDifference()[1]
            epsilon = 1e-8
            if price_difference > 0:
                arbquantity = self.arbAmountUniPriceGreaterThanRMM01(epsilon)

            elif price_difference < 0:
                arbquantity = self.arbAmountUniPriceLessThanRMM01(epsilon)

            else:

