# RMM01-Simulations
This repository serves as the central repository for all simulations of products/mechanism built using RMM-01. Its contents, as currently stands, includes simulation packages intended to analyze the replication accuracy of RMM-01 under various market conditions and market assumptions, as well as the generation of an optimal swap fee.

## Directory

### rmms-py
**Package finalized**

This project is intended to investigate the replication of payoffs using custom Constant Function Market Makers (CFMMs) in the spirit of the 2021 paper from [Angeris, Evans and Chitra.](https://stanford.edu/~guillean/papers/rmms.pdf) For now it only focuses on the Covered Call replication. The project is organized as follows:

``modules`` contains all the simulation toolkit. In particular:

- ``modules/arb.py`` implements the optimal arbitrage logic.
- ``modules/cfmm.py`` implements the actual CFMM pool logic.
- ``modules/utils.py`` contains a number of utility functions (math, geometric brownian motion generation).
- ``modules/simulate.py`` is simply the function used to run an individual simulation.
- ``modules/optimize_fee.py`` contains the logic required to find the optimal fee given some market and pool parameters.

``simulation.py`` is a script used to run individual simulations whose parameters are specified in the ``config.ini`` file.

``optimal_fees_parallel.py`` is a script to run an actual fee optimization routine for a prescribed parameter space (to be specified within the script itself).

``optimal_fees_visualization.py`` is a script that generates a visual representation of the output of a fee optimization routine.

``error_distribution.py`` is a script to plot the distribution of errors given some market and pool parameters for different fee regimes.

All the different functions and design choices are documented in a separate document.

### CFMM-py
🚧 **Package still under construction** 🚧

Package for simulating RMM-01 performance with respect to various market conditions and arbitrage rules using the simpy discrete event simulator package. Based off the rmms-py package, with now arbitrary share count and arbitrage occuring with respect to a finite liquidity market, currently Uniswap V2. Price generation now no longer just geometric brownian motion with intentions to make actor-based price generation on the reference market.

Consists of four main ``module`` files:

- ``CFMM.py`` contains logic for CFMM pools. Currently includes RMM-01 and Uniswap V2 logic
- ``arb.py`` contains optimal arbitrage logic given minimum arb profit for execution. Arbitrage occurs between RMM-01 and a reference AMM market with finite liquidity, currently Uniswap V2 
- ``main.py`` contains simpy environment/simulation path logic
- ``test.py`` contains testing logic for each module and resulting set of functions
