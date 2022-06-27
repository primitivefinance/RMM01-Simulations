import rlcompleter
from CFMM import UniV2, RMM01
from arb import Two_CFMM_Arbitrage
from scipy.stats import norm
import numpy as np
import simpy

env = simpy.Environment()

def quantilePrime(x):
    '''
    Analytical formula for the derivative of the quantile function (inverse of
    the CDF).
    '''
    EPSILON = 1e-16
    if (x > 1 - EPSILON) or (x < 0 + EPSILON):
        return np.inf
    else:
        return norm.pdf(norm.ppf(x))**-1

# Constant product tests

if False:

    initial_x = 1000
    initial_y = 1000

    # Feeless case
    fee = 0

    test_pool = UniV2(initial_x, initial_y, fee)

    # print("\n ----- Feeless case: -----\n")

    # print("\n----- Invariant ----- \n")
    # print("Expected: ", initial_x*initial_y)
    # print("Actual: ", test_pool.TradingFunction())

    # print("\n----- Swap Amount X In ----- \n")
    # print("Expected: ", 1000000/2000)
    # print("Actual: ", test_pool.y - test_pool.swapXforY(1000)[0])

    # test_pool.x = initial_x
    # test_pool.y = initial_y

    # print("\n----- Swap Amount Y In ----- \n")
    # print("Expected: ", 1000000/2000)
    # print("Actual: ", test_pool.x - test_pool.swapYforX(1000)[0])

    # test_pool.x = initial_x
    # test_pool.y = initial_y

    # print("\n----- X -> Y spot price ----- \n")
    # print("Expected: ", 1)
    # print("Actual: ", test_pool.getMarginalPriceAfterXTrade(0, "y"))

    # print("\n----- Y -> X initial spot price ----- \n")
    # print("Expected: ", 1)
    # print("Actual: ", test_pool.getMarginalPriceAfterYTrade(0, "y"))

    # print("\n----- X -> Y spot price after 100 X in----- \n")
    # print("Expected: ", 1000000/(1100**2))
    # print("Actual: ", test_pool.getMarginalPriceAfterXTrade(100, "y"))

    # print("\n----- Y -> X spot price after 100 Y in----- \n")
    # print("Expected: ", 1/(1000000/(1100**2)))
    # print("Actual: ", test_pool.getMarginalPriceAfterYTrade(100, "y"))

    # Test gamma =/= 0

    # fee = 0.02
    # gamma = 1 - fee
    # test_pool.gamma = gamma

    # print("\n ----- Fee = 0.05 case : -----\n")

    # print("\n----- Swap Amount X In ----- \n")
    # print("Expected: ", 1000000/1980)
    # print("Actual: ", test_pool.y - test_pool.swapXforY(1000)[0])

    # test_pool.x = initial_x
    # test_pool.y = initial_y

    # print("\n----- Swap Amount Y In ----- \n")
    # print("Expected: ", 1000000/1980)
    # print("Actual: ", test_pool.x - test_pool.swapYforX(1000)[0])

    # test_pool.x = initial_x
    # test_pool.y = initial_y

    # print("\n----- X -> Y Spot price  ----- \n")
    # print("Expected: ", gamma*1000000/((test_pool.x)**2))
    # print("Actual: ", test_pool.getMarginalPriceAfterXTrade(0, "y"))

    # print("\n----- Y -> X Spot price  ----- \n")
    # print("Expected: ", 1/(gamma*1000000/((test_pool.y)**2)))
    # print("Actual: ", test_pool.getMarginalPriceAfterYTrade(0, "y"))

    # Test arbitrage

    fee = 0
    gamma = 1 - fee
    test_pool.gamma = gamma

    # Reference market price above price of pool
    m = 1.2
    print("Initial pool price in y: ", test_pool.getMarginalPriceAfterYTrade(0, "y"))
    test_pool.swapYforX(test_pool.findArbitrageAmountYIn(m))
    print("Expected price: ", m)
    print("Actual swap Y in: ", test_pool.getMarginalPriceAfterYTrade(0, "y"))
    print("Actual swap X in: ", test_pool.getMarginalPriceAfterXTrade(0, "y"))

    # Reference market below price of pool
    test_pool.x = initial_x
    test_pool.y = initial_y
    m = 0.8
    print("Initial pool price in y: ", test_pool.getMarginalPriceAfterXTrade(0, "y"))
    test_pool.swapXforY(test_pool.findArbitrageAmountXIn(m))
    print("Expected price: ", m)
    print("Actual swap Y in: ", test_pool.getMarginalPriceAfterYTrade(0, "y"))
    print("Actual swap X in: ", test_pool.getMarginalPriceAfterXTrade(0, "y"))


    print("\n----- X -> Y effective price  ----- \n")
    print("Expected: ", 0.49494949)
    print("Actual: ", test_pool.getEffectivePriceXIn(1000, "y"))

    print("\n----- Y -> X effective price  ----- \n")
    print("Expected: ", 1/0.49494949494949)
    print("Actual: ", test_pool.getEffectivePriceYIn(1000, "y"))

    # Test gamma*g(gamma*delta) == gamma*g(0) after trade

    initial_x = 1000
    iniital_y = 1000
    initial_k = initial_x*initial_y
    gamma = 0.98
    delta_y = 100
    new_y = initial_y + delta_y 
    new_x = initial_k/(initial_y + gamma*delta_y)
    new_k = new_x*new_y
    print("gamma*g(gamma*delta) = ", gamma*initial_k/((initial_y + delta_y)**2))
    print("after trade: gamma*g(0) = ", gamma*new_k/(new_y**2))

if False:

    K = 1500
    sigma = 0.8
    maturity = 1
    fee = 0
    initial_x = 0.5
    initial_y = K*norm.cdf(norm.ppf(1-initial_x) - sigma*np.sqrt(maturity))
    timescale = 1
    # print("Initial x: ", initial_x)
    # print("Initial y: ", initial_y)

    rmm01Pool = RMM01(initial_x, initial_y, fee, K, sigma, maturity, env, timescale, 1)

    print("\n ----- Test RMM01-----\n")

    print("\n ----- Fee = 0 case : -----\n")

    gamma = 1 - fee

    print("\n----- Swap Amount X In ----- \n")
    amount_in = 0.1
    expected_amount_out = initial_y - K*norm.cdf(norm.ppf(1-(initial_x+gamma*amount_in)) - sigma*np.sqrt(maturity))
    print("Expected: ", expected_amount_out)
    print("Actual: ", rmm01Pool.swapXforY(amount_in, "y")[0])

    rmm01Pool.x = initial_x
    rmm01Pool.y = initial_y

    print("\n----- Swap Amount Y In ----- \n")
    amount_in = 100
    expected_amount_out = initial_x - (1 - norm.cdf(norm.ppf((initial_y+gamma*amount_in - 0)/K) + sigma*np.sqrt(maturity)))
    print("Expected: ", expected_amount_out)
    print("Actual: ", rmm01Pool.swapYforX(amount_in, "y")[0])

    rmm01Pool.x = initial_x
    rmm01Pool.y = initial_y

    print("\n----- X -> Y Spot price  ----- \n")

    print("Expected with 0 fees: ", K*norm.pdf(norm.ppf(1 - initial_x) - sigma*np.sqrt(maturity))*quantilePrime(1-initial_x))
    print("Actual: ", rmm01Pool.getMarginalPriceAfterXTrade(0, "y"))

    print("\n----- Y -> X Spot price  ----- \n")
    print("Expected with 0 fees: ", K*norm.pdf(norm.ppf(1 - initial_x) - sigma*np.sqrt(maturity))*quantilePrime(1-initial_x))
    print("Actual: ", rmm01Pool.getMarginalPriceAfterYTrade(0, "y"))


    print("\n----- Arbitrage testing  ----- \n")

    # Reference market price above price of pool
    m = 1300
    print("Reference price: ", m)
    print("Initial pool price in y: ", rmm01Pool.getMarginalPriceAfterYTrade(0, "y"))
    rmm01Pool.swapYforX(rmm01Pool.findArbitrageAmountYIn(m), "y")
    print("No-arbitrage bounds: ", rmm01Pool.getMarginalPriceAfterXTrade(0, "y"), " | ", rmm01Pool.getMarginalPriceAfterYTrade(0, "y"), "\n"  )

    # Reference market below price of pool
    rmm01Pool.x = initial_x
    rmm01Pool.y = initial_y
    m = 900
    print("Reference price: ", m)
    print("Initial pool price in y: ", rmm01Pool.getMarginalPriceAfterXTrade(0, "y"))
    rmm01Pool.swapXforY(rmm01Pool.findArbitrageAmountXIn(m), "y")
    print("No-arbitrage bounds after trade: ", rmm01Pool.getMarginalPriceAfterXTrade(0, "y"), " | ", rmm01Pool.getMarginalPriceAfterYTrade(0, "y")  )

    # print("\n----- X -> Y effective price  ----- \n")
    # amount_in = 0.1
    # print("Expected: ", (initial_y - K*norm.cdf(norm.ppf(1 - (initial_x+ (gamma*amount_in))) - sigma*np.sqrt(maturity)))/0.1)
    # print("Actual: ", rmm01Pool.getEffectivePriceAfterXTrade(amount_in, "y"))

    # print("\n----- Y -> X effective price  ----- \n")
    # amount_in = 100
    # print("Expected: ", amount_in/(initial_x - (1- norm.cdf(norm.ppf((initial_y + (gamma*amount_in))/K) + sigma*np.sqrt(maturity)))))
    # print("Actual: ", rmm01Pool.getEffectivePriceAfterYTrade(amount_in, "y"))

# More than one LP share implementation

if False:


    K = 1500
    sigma = 0.8
    maturity = 1
    fee = 0
    initial_x = 0.5
    initial_y = K*norm.cdf(norm.ppf(1-initial_x) - sigma*np.sqrt(maturity))
    timescale = 1
    # print("Initial x: ", initial_x)
    # print("Initial y: ", initial_y)

    n_shares = 10

    rmm01Pool = RMM01(initial_x, initial_y, fee, K, sigma, maturity, env, timescale, n_shares)

    print("x reserves after: ", rmm01Pool.x)
    print("y reserves after: ", rmm01Pool.y)
    x, y = rmm01Pool.addLiquidity(1)
    x, y = rmm01Pool.removeLiquidity(1)
    print("x reserves after: ", rmm01Pool.x)
    print("y reserves after: ", rmm01Pool.y)

    print("\n ----- Test RMM01-----\n")

    print("\n ----- Fee = 0 case : -----\n")

    gamma = 1 - fee

    print("\n----- Swap Amount X In ----- \n")
    amount_in = 0.1*n_shares
    expected_amount_out = initial_y - K*norm.cdf(norm.ppf(1-(initial_x+gamma*rmm01Pool.scaleDown(amount_in))) - sigma*np.sqrt(maturity))
    expected_amount_out = rmm01Pool.scaleUp(expected_amount_out)
    print("Expected: ", expected_amount_out)
    print("Actual: ", rmm01Pool.swapXforY(amount_in, "y")[0])

    rmm01Pool.x = initial_x
    rmm01Pool.y = initial_y

    print("\n----- Swap Amount Y In ----- \n")
    amount_in = 100*n_shares
    expected_amount_out = initial_x - (1 - norm.cdf(norm.ppf((initial_y+gamma*rmm01Pool.scaleDown(amount_in) - 0)/K) + sigma*np.sqrt(maturity)))
    expected_amount_out = rmm01Pool.scaleUp(expected_amount_out)
    print("Expected: ", expected_amount_out)
    print("Actual: ", rmm01Pool.swapYforX(amount_in, "y")[0])

    rmm01Pool.x = initial_x
    rmm01Pool.y = initial_y

    print("\n----- X -> Y Spot price  ----- \n")

    print("Expected with 0 fees: ", K*norm.pdf(norm.ppf(1 - initial_x) - sigma*np.sqrt(maturity))*quantilePrime(1-initial_x))
    print("Actual: ", rmm01Pool.getMarginalPriceAfterXTrade(0, "y"))

    print("\n----- Y -> X Spot price  ----- \n")
    print("Expected with 0 fees: ", K*norm.pdf(norm.ppf(1 - initial_x) - sigma*np.sqrt(maturity))*quantilePrime(1-initial_x))
    print("Actual: ", rmm01Pool.getMarginalPriceAfterYTrade(0, "y"))


    print("\n----- Arbitrage testing  ----- \n")

    # Reference market price above price of pool
    m = 1300
    print("Reference price: ", m)
    print("Initial pool price in y: ", rmm01Pool.getMarginalPriceAfterYTrade(0, "y"))
    arbitrage_amount = rmm01Pool.findArbitrageAmountYIn(m)
    rmm01Pool.swapYforX(arbitrage_amount, "y")
    print("scaled down arbitrage amount: ", rmm01Pool.scaleDown(arbitrage_amount))
    print("No-arbitrage bounds: ", rmm01Pool.getMarginalPriceAfterXTrade(0, "y"), " | ", rmm01Pool.getMarginalPriceAfterYTrade(0, "y"), "\n"  )

    # Reference market below price of pool
    rmm01Pool.x = initial_x
    rmm01Pool.y = initial_y
    m = 900
    print("Reference price: ", m)
    print("Initial pool price in y: ", rmm01Pool.getMarginalPriceAfterXTrade(0, "y"))
    arbitrage_amount = rmm01Pool.findArbitrageAmountXIn(m)
    rmm01Pool.swapXforY(arbitrage_amount, "y")
    print("scaled down arbitrage amount: ", rmm01Pool.scaleDown(arbitrage_amount))
    print("No-arbitrage bounds after trade: ", rmm01Pool.getMarginalPriceAfterXTrade(0, "y"), " | ", rmm01Pool.getMarginalPriceAfterYTrade(0, "y")  )


# Test arbitrager class


if True:

    ###################################################
    # PRICE UNI LOWER THAN RMM TEST 
    ###################################################

    print("------- PRICE UNI LOWER THAN RMM ------- \n")

    K = 1500
    sigma = 0.8
    maturity = 1
    fee = 0
    initial_x_rmm = 0.5
    initial_y_rmm = K*norm.cdf(norm.ppf(1-initial_x_rmm) - sigma*np.sqrt(maturity))
    timescale = 1
    # print("Initial x: ", initial_x)
    # print("Initial y: ", initial_y)

    n_shares = 10

    initial_x_uni = 10
    initial_y_uni = 9000

    rmm01Pool = RMM01(initial_x_rmm, initial_y_rmm, fee, K, sigma, maturity, env, timescale, n_shares)

    univ2pool = UniV2(initial_x_uni, initial_y_uni, 0)

    arbitrager = Two_CFMM_Arbitrage(univ2pool, rmm01Pool, env)

    # No fee

    print("NO FEE CASE \n")

    print("Initial price: ", "\n")
    print("RMM pool: ", rmm01Pool.getMarginalPriceAfterXTrade(0, 'y'))
    print("Uni Pool: ", univ2pool.getMarginalPriceAfterXTrade(0, 'y'), "\n")

    arbitrager.arbProcess() 
    
    print("Price after arbprocess: ", "\n")
    print("RMM pool: ", rmm01Pool.getMarginalPriceAfterXTrade(0, 'y'))
    print("Uni pool: ", univ2pool.getMarginalPriceAfterXTrade(0, 'y'), "\n")

    # Non zero and equal fee

    rmm01Pool.x = initial_x_rmm
    rmm01Pool.y = initial_y_rmm
    univ2pool.x = initial_x_uni
    univ2pool.y = initial_y_uni

    fee = 0.02
    rmm01Pool.gamma = 1-fee 
    univ2pool.gamma = 1-fee

    print("FEE CASE \n")

    print("RMM pool no-arb band before arbitrage:")
    print(rmm01Pool.getMarginalPriceAfterXTrade( 0, 'y'), ", ",rmm01Pool.getMarginalPriceAfterYTrade(0, 'y'), "\n")

    print("Uni pool no-arb band before arbitrage:")
    print(univ2pool.getMarginalPriceAfterXTrade(0, 'y'), ", ",univ2pool.getMarginalPriceAfterYTrade(0, 'y'), "\n")

    arbitrager.arbProcess()

    print("RMM pool no-arb band after arbitrage:")
    print(rmm01Pool.getMarginalPriceAfterXTrade(0, 'y'), ", ",rmm01Pool.getMarginalPriceAfterYTrade(0, 'y'), "\n")

    print("Uni pool no-arb band after arbitrage: ")
    print(univ2pool.getMarginalPriceAfterXTrade(0, 'y'), ", ", univ2pool.getMarginalPriceAfterYTrade(0, 'y'), "\n")

    print("------- PRICE UNI GREATER THAN RMM ------- \n")

    K = 1500
    sigma = 0.8
    maturity = 1
    fee = 0
    initial_x_rmm = 0.5
    initial_y_rmm = K*norm.cdf(norm.ppf(1-initial_x_rmm) - sigma*np.sqrt(maturity))
    timescale = 1
    # print("Initial x: ", initial_x)
    # print("Initial y: ", initial_y)

    n_shares = 10

    initial_x_uni = 10
    initial_y_uni = 12000

    rmm01Pool = RMM01(initial_x_rmm, initial_y_rmm, fee, K, sigma, maturity, env, timescale, n_shares)

    univ2pool = UniV2(initial_x_uni, initial_y_uni, 0)

    arbitrager = Two_CFMM_Arbitrage(univ2pool, rmm01Pool, env)

    # No fee

    print("NO FEE CASE \n")

    print("Initial price: ", "\n")
    print("RMM pool: ", rmm01Pool.getMarginalPriceAfterXTrade(0, 'y'))
    print("Uni Pool: ", univ2pool.getMarginalPriceAfterXTrade(0, 'y'), "\n")

    arbitrager.arbProcess() 
    
    print("Price after arbprocess: ", "\n")
    print("RMM pool: ", rmm01Pool.getMarginalPriceAfterXTrade(0, 'y'))
    print("Uni pool: ", univ2pool.getMarginalPriceAfterXTrade(0, 'y'), "\n")

    # Non zero and equal fee

    rmm01Pool.x = initial_x_rmm
    rmm01Pool.y = initial_y_rmm
    univ2pool.x = initial_x_uni
    univ2pool.y = initial_y_uni

    fee = 0.02
    rmm01Pool.gamma = 1-fee 
    univ2pool.gamma = 1-fee

    print("FEE CASE \n")

    print("RMM pool no-arb band before arbitrage:")
    print(rmm01Pool.getMarginalPriceAfterXTrade( 0, 'y'), ", ",rmm01Pool.getMarginalPriceAfterYTrade(0, 'y'), "\n")

    print("Uni pool no-arb band before arbitrage:")
    print(univ2pool.getMarginalPriceAfterXTrade(0, 'y'), ", ",univ2pool.getMarginalPriceAfterYTrade(0, 'y'), "\n")

    arbitrager.arbProcess()

    print("RMM pool no-arb band after arbitrage:")
    print(rmm01Pool.getMarginalPriceAfterXTrade(0, 'y'), ", ",rmm01Pool.getMarginalPriceAfterYTrade(0, 'y'), "\n")

    print("Uni pool no-arb band after arbitrage: ")
    print(univ2pool.getMarginalPriceAfterXTrade(0, 'y'), ", ", univ2pool.getMarginalPriceAfterYTrade(0, 'y'), "\n")