import simpy as sp
from scipy import optimize as op
import scipy

ZERO = 1e-8
INF = 1e15

class Two_CFMM_Arbitrager:

    def __init__(self, unipool, rmmpool):
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
        # print("START ARBAMOUNTM1PRICEGREATER FUNCTION")

        # The maximum amount of y that can be added to the RMM pool.
        deltaymax = self.RMM.ybounds[1] - self.RMM.y

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


        # deltay = amount of y we get out from swapping x in Uni pool
        if deltaxmax < x:
            x = 0.95*deltaxmax

        # Swap small amount of y in Uniswap
        deltay = self.M1.virtualSwapXforY(x, 'y')[0]

        deltax_RMM = self.RMM.virtualSwapYforX(deltay, 'y')[0]

        # If we get more x out of RMM than we put in Uniswap
        if deltax_RMM > x:

            lhs_init_zero = self.M1.getMarginalPriceAfterXTrade(ZERO, 'y')
            deltay = self.M1.virtualSwapXforY(ZERO, 'y')[0]
            rhs_init_zero = self.RMM.getMarginalPriceAfterYTrade(deltay, 'y')
            term_zero = lhs_init_zero - rhs_init_zero
            lhs_init_deltaymax = self.M1.getMarginalPriceAfterXTrade(deltaxmax, 'y')
            deltay = self.M1.virtualSwapXforY(deltaymax, 'y')[0]
            rhs_init_deltaymax = self.RMM.getMarginalPriceAfterYTrade(deltay, 'y')
            term_deltay_max = lhs_init_deltaymax - rhs_init_deltaymax

            if term_zero*term_deltay_max > 0:
                return 0

            def findZero(x):
                lhs = self.M1.getMarginalPriceAfterXTrade(x, 'y')
                deltay = self.M1.virtualSwapXforY(x, 'y')[0]
                rhs = self.RMM.getMarginalPriceAfterYTrade(deltay, 'y')
                return lhs - rhs
            deltax_required = op.brentq(findZero, ZERO, deltaxmax)
            # print("END ARBAMOUNTM1PRICEGREATER FUNCTION")
            return deltax_required
        else:
            # print("END ARBAMOUNTM1PRICEGREATER FUNCTION")
            return 0

    def arbAmount_M1Price_LessThan_RMM(self, y):
        # print("START ARBAMOUNTM1PRICELESS FUNCTION")

        # The maximum amount of x that can be added to the RMM pool.
        deltaxmax = self.RMM.xbounds[1] - self.RMM.x
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

        if deltaymax < y: 
            y = 0.95*deltaymax

        # Deltax = amount of x we get out from swapping y in Uni pool
        deltax = self.M1.virtualSwapYforX(y, 'y')[0]
        # print("deltax virtualswap m1 price less = ", deltax)
        # Deltay_RMM = amount of y we get out from swapping Deltax
        # in RMM pool
        deltay_RMM = self.RMM.virtualSwapXforY(deltax, 'y')[0]
        # If we get more y out of RMM than we put in Uniswap
        if deltay_RMM > y:

            lhs_init_zero = self.M1.getMarginalPriceAfterYTrade(ZERO, 'y')
            deltax = self.M1.virtualSwapYforX(ZERO, 'y')[0]
            rhs_init_zero = self.RMM.getMarginalPriceAfterXTrade(deltax, 'y')
            term_zero = lhs_init_zero - rhs_init_zero
            lhs_init_deltaymax = self.M1.getMarginalPriceAfterYTrade(deltaymax, 'y')
            deltax = self.M1.virtualSwapYforX(deltaymax, 'y')[0]
            rhs_init_deltaymax = self.RMM.getMarginalPriceAfterXTrade(deltax, 'y')
            term_deltay_max = lhs_init_deltaymax - rhs_init_deltaymax

            # If there is no change of sign between a zero swap and the max amount to swap,
            # the pool cannot be reasonably arbitraged.

            if  term_zero*term_deltay_max > 0:
                return 0

            def findZero(y):
                lhs = self.M1.getMarginalPriceAfterYTrade(y, 'y')
                deltax = self.M1.virtualSwapYforX(y, 'y')[0]
                # print("deltax arb amount m1 price less than rmm = ", deltax)
                rhs = self.RMM.getMarginalPriceAfterXTrade(deltax, 'y')
                # print("LHS - RHS = ", lhs - rhs)
                # print("DELTAYMAX = ", deltaymax)
                return lhs - rhs

            deltay_required, r = op.brentq(findZero, ZERO, deltaymax, full_output=True, disp=False)

            if r.converged == False:
                
                deltay_required = r.root


            # print("END ARBAMOUNTM1PRICELESS FUNCTION")
            return deltay_required
        else:
            # print("START ARBAMOUNTM1PRICELESS FUNCTION")
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
        self.M1.swapYforX(y, 'y')
        deltay_RMM = self.RMM.virtualSwapXforY(deltax, 'y')[0]
        self.RMM.swapXforY(deltax, 'y')
        profit = deltay_RMM - y
        return profit
        
    def arbProcess(self):
        price_difference = self.testSpotPriceDifference()[0] - self.testSpotPriceDifference()[1]
        epsilon = 1e-7
        if price_difference > 0:
            arbquantity = self.arbAmount_M1Price_GreaterThan_RMM(epsilon)
            if arbquantity == 0:
                return None
            else:
                self.arbExactly_M1Price_Greater(arbquantity)
                return None
        elif price_difference < 0:
            arbquantity = self.arbAmount_M1Price_LessThan_RMM(epsilon)
            if arbquantity == 0:
                return None
            else:
                self.arbExactly_M1Price_Less(arbquantity)
                return None
        else:
            return None

class ReferencePriceArbitrager:
    def __init__(self, pool) -> None:
        self.pool = pool 
    
    def arbExactly(self, price):
        '''
        Find the optimal arbitrage amount
        given a reference price and execute 
        the arbitrage.

        Returns: denomination of the arb amount, arb amount, and amount out
        '''
        if price > self.pool.getMarginalPriceAfterYTrade(0, 'y'):
            # If the reference price denominated in y 
            # is above the no-arb bounds, we must 
            # swap y in to increase the price of the pool.
            arb_amount = self.pool.findArbitrageAmountYIn(price)
            if arb_amount > 0:
                amount_out, _ = self.pool.swapYforX(arb_amount, 'y')
                # print("Pool reserves: x = ", self.pool.x, " y = ", self.pool.y)
                # print("Pool price = ", self.pool.getMarginalPriceAfterXTrade(0, 'y'), "\n")
                return 'y', arb_amount, amount_out
            return None
        elif price < self.pool.getMarginalPriceAfterXTrade(0, 'y'):
            # If the reference price denominated in y 
            # is below the no-arb bounds, we must 
            # swap x in to increase the price of the pool.
            arb_amount = self.pool.findArbitrageAmountXIn(price)
            if arb_amount > 0:
                amount_out, _ = self.pool.swapXforY(arb_amount, 'y')
                # print("Pool reserves: x = ", self.pool.x, " y = ", self.pool.y)
                # print("Pool price = ", self.pool.getMarginalPriceAfterXTrade(0, 'y'), "\n")
                return 'x', arb_amount, amount_out
            return None