# RMM-research

This repository has all the workings of the Primitive research for Replicating Market Makers. This work is primarily managed by Primitives Head of Research [0xEstelle](https://github.com/0xEstelle), and [0xJepsen](https://github.com/0xJepsen). Because we believe in public open source work, we intend to upload all work to this repository. Please use this repository for the most up to date versions of our work.

## Papers

Here are the abstracts of the papers we finished

### [Whitepaper RMM-01](/papers/Whitepaper.pdf)

Constant function market makers (CFMMs) have evolved from a small group of decentralized exchanges (DEXs) to a broad and largely undiscovered class of automated market makers (AMMs). CFMMs are decentralized exchanges fully backed by a community of liquidity providers seeking to earn a yield on their deposited assets. The portfolio of a liquidity provider follows a payoff structure specific to the CFMM they are providing liquidity too. It was recently shown that the space of concave, non-negative, non-decreasing, 1-homogeneous payoff functions and the space of convex CFMMs are equivalent, along with a method to convert between a given payoff of the above type with an associated CFMM. These CFMMs, which replicate specific, desired payoff functions, are called replicating market makers (RMMs). In this paper, we present an implementation of an RMM that approximates a Black--Scholes covered call, which we call RMM-01.

### [Replicating Portfolios: Constructing Permissionless Derivatives](/papers/ConstructingPermissionlessDerivatives.pdf)

The current design space of derivatives in Decentralized Finance (DeFi) relies heav- ily on oracle systems. Replicating market makers (RMMs) provide a mechanism for converting specific payoff functions to an associated Constant Function Market Makers (CFMMs). We leverage RMMs to replicate the approximate payoff of a Black-Scholes covered call option. RMM-01 is the first implementation of an on-chain expiring option mechanism that relies on arbitrage rather than an external oracle for price. We pro- vide frameworks for derivative instruments and structured products achievable on-chain without relying on oracles. We construct long and binary options and briefly discuss perpetual covered call strategies commonly referred to as "theta vaults". Moreover, we introduce a procedure to eliminate liquidation risk in lending markets. The results suggest that CFMMs are essential for structured product design with minimized trust dependencies.

## Simulations

Most of this work will be python simulations for product performance and analysis. Each project will have its own directory with its affiliated simulations. We will also publish finished work for these projects in their directories.
