import numpy as np
import simpy
from CFMM import UniV2, RMM01
from arb import Two_CFMM_Arbitrager, ReferencePriceArbitrager
from utils import gbm

ONE_SECOND = 3.171e-8
ONE_MINUTE = 1.9026e-6
ONE_HOUR = 0.000114155
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

if True: 
    '''
    '''

    class TwoPoolsArbitrageSimulation():

            def __init__(self, env, init_price, dt, time_horizon, volatility, drift, UniPool, RMMPool) -> None:
                '''
                '''
                self.UniPool = UniPool 
                self.RMMPool = RMMPool
                self.uni_pool_arbitraged = env.event()
                self.current_price = init_price
                self.RefArbitrager = ReferencePriceArbitrager(env, UniPool)
                self.TwoPoolArbitrager = Two_CFMM_Arbitrager(self.UniPool, self.RMMPool)

            
            def price_process(self, env, init_price, dt, time_horizon, volatility, drift):
                '''
                '''
                price_generator = gbm(init_price, dt, time_horizon, volatility, drift)
                for p in price_generator:
                    self.current_price = p
                    yield env.timeout(1)
    
            def uni_pool_arb_process(self):
                '''
                '''
                while True:
                    self.RefArbitrager.arbExactly(self.current_price)
                    self.uni_pool_arbitraged.succeed()
                    self.uni_pool_arbitraged = self.env.event()

            def rmm_pool_arb_process(self):
                '''
                Only arbitrage the two pools right after the Uniswap pool has been arbitraged.
                '''
                while True: 
                    # Wait for the Uniswap pool to have been arbitraged
                    yield self.uni_pool_arbitraged
                    self.TwoPoolArbitrager.arbProcess()








        




