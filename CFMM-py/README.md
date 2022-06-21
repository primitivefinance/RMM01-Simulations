# CFMM-py
Package for simulating RMM-01 performance with respect to various market conditions and arbitrage rules using the simpy discrete event simulator package. Based off the RMM-py package in https://github.com/primitivefinance/rmm-research

Consists of four main ``module`` files:

- ``CFMM.py`` contains logic for CFMM pools. Currently includes RMM-01 and Uniswap V2 logic
- ``arb.py`` contains optimal arbitrage logic given minimum arb profit for execution. Arbitrage occurs between RMM-01 and a reference AMM market with finite liquidity, currently Uniswap V2 
- ``main.py`` contains simpy environment/simulation path logic
- ``test.py`` contains testing logic for each module and resulting set of functions

### Dependencies:
``pip install numpy, pip install scipy, pip install simpy, pip install matplotlib.pyplot``
