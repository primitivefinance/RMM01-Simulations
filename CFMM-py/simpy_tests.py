import numpy as np
import simpy
from scipy.optimize import brentq
from CFMM import UniV2, RMM01
from arb import Two_CFMM_Arbitrager, ReferencePriceArbitrager
from utils import gbm, getInitialYGivenInitialXRMM, getInitialXGivenReferencePriceRMM

ONE_SECOND = 3.171e-8
ONE_MINUTE = 1.9026e-6
ONE_HOUR = 0.000114155
ONE_DAY = 0.00273973
ONE_YEAR = 1

if False:

    pool = UniV2(1000, 1000, 0)

    init_price = 0.95
    volatility = 1 
    drift = 1

    price = gbm(init_price, ONE_HOUR, ONE_YEAR, volatility, drift)

    def arbitrage_process(env, price_array, pool):
        arb = ReferencePriceArbitrager(env, pool)
        for p in price_array:
            print("Reference price = ", p)
            arb.arbExactly(p)
            yield env.timeout(1)

    env = simpy.Environment()
    arb_proc = env.process(arbitrage_process(env, price, pool))
    env.run(until=10)

if False: 
    '''
    '''

    class TwoPoolsArbitrageSimulation():

            def __init__(self, env, init_price, dt, time_horizon, volatility, drift, UniPool, RMMPool) -> None:
                '''
                '''
                self.env = env
                self.UniPool = UniPool 
                self.RMMPool = RMMPool
                self.uni_pool_arbitraged = self.env.event()
                self.price_updated = self.env.event()
                self.current_price = init_price
                # print("Uni Pool object = ", UniPool)
                self.RefArbitrager = ReferencePriceArbitrager(UniPool)
                self.TwoPoolArbitrager = Two_CFMM_Arbitrager(self.UniPool, self.RMMPool)
                self.processes = [env.process(self.price_process(init_price, dt, time_horizon, volatility, drift)), env.process(self.uni_pool_arb_process()), env.process(self.rmm_pool_arb_process())]

            
            def price_process(self, init_price, dt, time_horizon, volatility, drift):
                '''
                '''
                price_generator = gbm(init_price, dt, time_horizon, volatility, drift)
                for p in price_generator:
                    print(f"Initial Uniswap pool price = {self.UniPool.getMarginalPriceAfterXTrade(0, 'y')}")
                    print(f"GBM price at {self.env.now} :", p)
                    self.current_price = p
                    self.price_updated.succeed()
                    print(f"price_updated event success at {self.env.now}")
                    self.price_updated = self.env.event()
                    yield self.env.timeout(1)
    
            def uni_pool_arb_process(self):
                '''
                '''
                while True:
                    print(f"In Uniswap pool loop at {self.env.now}")
                    yield self.price_updated
                    print(f"In Uniswap pool arbitrage process after event fired at {self.env.now}")
                    self.RefArbitrager.arbExactly(self.current_price)
                    print(f"Uniswap pool arbitraged at {self.env.now}")
                    print(f"Uniswap pool price after arb = {self.UniPool.getMarginalPriceAfterXTrade(0, 'y')}")
                    self.uni_pool_arbitraged.succeed()
                    print(f"Uniswap pool arbitraged event fired at {self.env.now}")
                    self.uni_pool_arbitraged = self.env.event()

            def rmm_pool_arb_process(self):
                '''
                Only arbitrage the two pools right after the Uniswap pool has been arbitraged.
                '''
                while True: 
                    # Wait for the Uniswap pool to have been arbitraged
                    yield self.uni_pool_arbitraged
                    print(f"In RMM pool arbitrage process at {self.env.now}")
                    self.TwoPoolArbitrager.arbProcess()
                    print(f"RMM pool arbitraged at {self.env.now}")
                    print(f"RMM pool price after arb = {self.RMMPool.getMarginalPriceAfterXTrade(0, 'y')}")
                    print("\n")
                    

    # Create SimPy environment 

    env = simpy.Environment()

    # Desired volatility of the actual price path
    volatility = 1.1
    drift = 1

    # Desired parameters of the RMM pool
    time_horizon = 1
    strike = 1300
    initial_x = 0.35
    fee = 0
    
    # Initialize Uni pool at 1000 USD and RMM pool around that price

    UniPool = UniV2(900, 1000000, 0)
    RMMPool = RMM01(initial_x, getInitialYGivenInitialXRMM(initial_x, strike, volatility, time_horizon), fee, strike, volatility, time_horizon, env, ONE_HOUR, 100) 

    # Desired parameters for the simulation 

    init_price = 1000
    simulation = TwoPoolsArbitrageSimulation(env, init_price, ONE_HOUR, time_horizon, volatility, drift, UniPool, RMMPool)
    env.run(until=10)

if True:

    class ThetaVaultSim():

            def __init__(self, env, init_price, dt, time_horizon, volatility, drift, UniPool, RMMPool) -> None:
                '''
                '''
                self.env = env
                self.UniPool = UniPool 
                self.RMMPool = RMMPool
                self.uni_pool_arbitraged = self.env.event()
                self.price_updated = self.env.event()
                self.current_price = init_price
                # print("Uni Pool object = ", UniPool)
                self.RefArbitrager = ReferencePriceArbitrager(UniPool)
                self.TwoPoolArbitrager = Two_CFMM_Arbitrager(self.UniPool, self.RMMPool)
                self.processes = [env.process(self.main_process(init_price, dt, time_horizon, volatility, drift))]

            
            def main_process(self, init_price, dt, time_horizon, volatility, drift):
                '''
                '''
                price_generator = gbm(init_price, dt, time_horizon, volatility, drift)
                for p in price_generator:
                    print("I AM BACK AT THE BEGINNING OF THE LOOP")
                    # print(f"Initial Uniswap pool price = {self.UniPool.getMarginalPriceAfterXTrade(0, 'y')}")
                    # print(f"GBM price at {self.env.now} :", p)
                    self.current_price = p
                    tau = self.RMMPool.T - dt*self.env.now
                    print("\n")
                    print(f"SIMULATION STEP {self.env.now}")
                    print("\n")

                    print("RMM Pool parameters: \n ")

                    print(f"x_rmm = ", self.RMMPool.x)
                    print(f"y_rmm = {self.RMMPool.y}")
                    print(f"n_shares = {self.RMMPool.n}")
                    print(f"tau = {self.RMMPool.T - (self.env.now -self.RMMPool.creation_epoch)*(self.RMMPool.timescale)}")
                    print(f"volatility = {self.RMMPool.vol}")
                    print(f"strike = {self.RMMPool.K} \n")

                    print(f"xbound rmm = {self.RMMPool.xbounds[1]}")
                    print(f"ybound rmm = {self.RMMPool.ybounds[1]} \n")

                    assert self.RMMPool.y > 0 and self.RMMPool.x > 0

                    print("Uniswap pool parameters: \n")
                    print(f"x_uni = {self.UniPool.x}")
                    print(f"y_uni = {self.UniPool.y} \n")

                    print("BEFORE ARBITRAGE")
                    print("current price = ", self.current_price)
                    print("current uni price = ", self.UniPool.getMarginalPriceAfterXTrade(0, 'y'))
                    print("current rmm price = ", self.RMMPool.getMarginalPriceAfterXTrade(0, 'y'),"\n")

                    if tau > dt:
                        print("In normal arbitrage subroutine")
                        yield self.env.process(self.uni_pool_arb_process())
                        
                        print("Uniswap pool parameters after Uni arbitrage: \n")
                        print(f"x_uni = {self.UniPool.x}")
                        print(f"y_uni = {self.UniPool.y} \n")

                        yield self.env.process(self.rmm_pool_arb_process())
                        yield self.env.process(self.uni_pool_arb_process())
                    else: 
                        print("\ In migration subroutine")
                        # Uni pool continues to follow prescribed price path
                        yield self.env.process(self.uni_pool_arb_process())
                        # RMM pool is first rolled to a new one with same 
                        # parameters but different expiry
                        yield self.env.process(self.roll_rmm_at_expiry_process())
                        # # The new RMM pool is arbitraged
                        # yield self.env.process(self.rmm_pool_arb_process())
                    print("AFTER ARBITRAGE")
                    print("current price = ", self.current_price)
                    print("current uni price = ", self.UniPool.getMarginalPriceAfterXTrade(0, 'y'))
                    print("current rmm price = ", self.RMMPool.getMarginalPriceAfterXTrade(0, 'y'))
                    yield self.env.timeout(1)
    
            def uni_pool_arb_process(self):
                '''
                '''
                # print(f"In Uniswap pool loop at {self.env.now}")
                self.RefArbitrager.arbExactly(self.current_price)
                yield self.env.timeout(0)
                # print(f"Uniswap pool arbitraged at {self.env.now}")
                # print(f"Uniswap pool price after arb = {self.UniPool.getMarginalPriceAfterXTrade(0, 'y')}")

            def rmm_pool_arb_process(self):
                # print(f"In RMM pool arbitrage process at {self.env.now}")
                self.TwoPoolArbitrager.arbProcess()
                assert self.RMMPool.y > 0 and self.RMMPool.x > 0
                yield self.env.timeout(0)
                # print(f"RMM pool arbitraged at {self.env.now}")
                # print(f"RMM pool price after arb = {self.RMMPool.getMarginalPriceAfterXTrade(0, 'y')}")
                # print("\n")

            def roll_rmm_at_expiry_process(self):
                '''
                '''
                # Retrieve parameters of current RMM pool
                volatility = self.RMMPool.vol 
                strike = self.RMMPool.K 
                duration = self.RMMPool.T
                x_reserves = self.RMMPool.x 
                y_reserves = self.RMMPool.y 
                fee = 1 - self.RMMPool.gamma
                timescale = self.RMMPool.timescale
                # Check if reserves are almost all x, or almost all y
                # First case if if x reserves are greater than y reserves
                if x_reserves*self.current_price > y_reserves:
                    # Figure out the normalized amount of x that we should 
                    # swap to provide liquidity to a new pool
                    # with same parameters
                    required_x_norm = getInitialXGivenReferencePriceRMM(self.current_price, strike, volatility, duration)
                    required_y_norm = getInitialYGivenInitialXRMM(required_x_norm, strike, volatility, duration)
                    value_norm  = required_x_norm*self.current_price + required_y_norm
                    # There is a unique value of deltay to swap such that the resulting ratio
                    # of obtained x to delta y equals the ratio of the required reserves
                    def ratio(deltax): 
                        y_out = self.UniPool.virtualSwapXforY(deltax, 'y')[0]
                        # We want to migrate the leftover y reserves too
                        return (x_reserves-deltax)/(y_out + y_reserves) - required_x_norm/required_y_norm
                    deltax_required = brentq(ratio, 1e-8, x_reserves-1e-8)
                    # print(f"Delta x required = {deltax_required}")
                    y_out = self.UniPool.swapXforY(deltax_required, 'y')[0]
                    # The Uniswap pool gets arbed back to stay at the current price
                    yield self.env.process(self.uni_pool_arb_process())
                    # Find the amount of shares we need to mint to use up all of our 
                    # portfolio once the rebalance is done 
                    n_shares = ((x_reserves - deltax_required)*self.current_price + (y_out + y_reserves))/value_norm
                    # print(f"n_shares = {n_shares}")
                    # Re-initialize RMM pool logically equivalent to creating a new one
                    self.RMMPool.__init__((x_reserves - deltax_required)/n_shares, (y_out + y_reserves)/n_shares, fee, strike, volatility, duration, self.env, timescale, n_shares, self.env.now)

                #If y reserves greater than x reserves
                else: 
                    required_x_norm = getInitialXGivenReferencePriceRMM(self.current_price, strike, volatility, duration)
                    required_y_norm = getInitialYGivenInitialXRMM(required_x_norm, strike, volatility, duration)
                    value_norm  = required_x_norm*self.current_price + required_y_norm
                    print(f"Value norm = {value_norm}")
                    def ratio(deltay):
                        x_out = self.UniPool.virtualSwapYforX(deltay, 'y')[0]
                        return (y_reserves-deltay)/(x_out + x_reserves) - required_y_norm/required_x_norm
                    deltay_required = brentq(ratio, 1e-8, x_reserves-1e-8)
                    x_out = self.UniPool.swapYforX(deltay_required, 'y')[0]
                    n_shares = ((x_out + x_reserves)*self.current_price+ y_out)/value_norm
                    self.RMMPool.__init__((x_out + x_reserves)/n_shares, (y_reserves  - deltay_required)/n_shares, fee, strike, volatility, duration, self.env, timescale, n_shares, self.env.now)

                print(f"New pool reserves: x = {self.RMMPool.x}, y = {self.RMMPool.y}")
                print(f"New pool tau = {self.RMMPool.T}")
                print(f"New pool object {self.RMMPool}")
                print(f"Check that arbitrager has the same object: {self.TwoPoolArbitrager.RMM}")
                yield self.env.timeout(0)


    # Create SimPy environment 

    env = simpy.Environment()

    # Desired volatility of the actual price path
    volatility = 1.1
    drift = 1

    # Desired parameters of the RMM pool
    time_horizon = 0.1
    strike = 1300
    initial_x = 0.35
    fee = 0
    
    # Initialize Uni pool at 1000 USD and RMM pool around that price

    UniPool = UniV2(90000, 100000000, 0)
    RMMPool = RMM01(initial_x, getInitialYGivenInitialXRMM(initial_x, strike, volatility, time_horizon), fee, strike, volatility, time_horizon, env, ONE_DAY, 100, 0) 

    # Desired parameters for the simulation 

    init_price = 1000
    simulation = ThetaVaultSim(env, init_price, ONE_DAY, time_horizon, volatility, drift, UniPool, RMMPool)
    env.run(until=300)











        




