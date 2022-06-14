from CFMM import UniV2

# Constant product tests

initial_x = 1000
initial_y = 1000

# Feeless case
fee = 0

test_pool = UniV2(initial_x, initial_y, fee)

# print("\n ----- Feeless case: -----\n")

# print("\n----- Invariant ----- \n")
# print("Expected: ", initial_x*initial_y)
# print("Actual: ", test_pool.getInvariant())

# print("\n----- Swap Amount X In ----- \n")
# print("Expected: ", 1000000/2000)
# print("Actual: ", test_pool.y - test_pool.swapAmountXIn(1000))

# test_pool.x = initial_x
# test_pool.y = initial_y

# print("\n----- Swap Amount Y In ----- \n")
# print("Expected: ", 1000000/2000)
# print("Actual: ", test_pool.x - test_pool.swapAmountYIn(1000))

# test_pool.x = initial_x
# test_pool.y = initial_y

# print("\n----- X -> Y spot price ----- \n")
# print("Expected: ", 1)
# print("Actual: ", test_pool.getMarginalPriceXIn(0, "y"))

# print("\n----- Y -> X initial spot price ----- \n")
# print("Expected: ", 1)
# print("Actual: ", test_pool.getMarginalPriceYIn(0, "y"))

# print("\n----- X -> Y spot price after 100 X in----- \n")
# print("Expected: ", 1000000/(1100**2))
# print("Actual: ", test_pool.getMarginalPriceXIn(100, "y"))

# print("\n----- Y -> X spot price after 100 X in----- \n")
# print("Expected: ", 1000000/(1100**2))
# print("Actual: ", test_pool.getMarginalPriceYIn(100, "y"))

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

fee = 0.1
gamma = 1 - fee
test_pool.gamma = gamma

# Reference market price above price of pool
m = 1.2
print("Initial pool price in y: ", test_pool.getMarginalPriceAfterYTrade(0, "y"))
test_pool.swapYforX(test_pool.findArbitrageAmountYIn(m))
print("Expected price: ", m)
print("Actual: ", test_pool.getMarginalPriceAfterYTrade(0, "y"))

# Reference market below price of pool
test_pool.x = initial_x
test_pool.y = initial_y
m = 0.8
print("Initial pool price in y: ", test_pool.getMarginalPriceAfterXTrade(0, "y"))
test_pool.swapXforY(test_pool.findArbitrageAmountXIn(m))
print("Expected price: ", m)
print("Actual: ", test_pool.getMarginalPriceAfterXTrade(0, "y"))


# print("\n----- X -> Y effective price  ----- \n")
# print("Expected: ", 0.49494949)
# print("Actual: ", test_pool.getEffectivePriceXIn(1000, "y"))

# print("\n----- Y -> X effective price  ----- \n")
# print("Expected: ", 1/0.49494949494949)
# print("Actual: ", test_pool.getEffectivePriceYIn(1000, "y"))