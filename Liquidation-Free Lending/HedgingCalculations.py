import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# Config
# Defining The CFMM and Options
class RMM01:
    def __init__(self,strike,vol,tte,invariant):
        self.K = strike
        self.v = vol
        self.t = tte
        self.k = invariant

    def d1(self,x):
        return np.log(x/self.K)/(self.v*np.sqrt(self.t))+0.5*self.v*np.sqrt(self.t)

    def d2(self,x):
        return self.d1(x)-self.v*np.sqrt(self.t)

    def PutValueWithPositiveInvariant(self,x):
        return norm.cdf(-self.d2(x))*self.K-norm.cdf(-self.d1(x))*x
    def PutValueWithNegativeInvariant(self,x):
        return self.PutValueWithPositiveInvariant(x)+self.k

    def CallValueWithPositiveInvariant(self,x):
        return norm.cdf(self.d1(x))*x-norm.cdf(self.d2(x))*self.K
    def CallValueWithNegativeInvariant(self,x):
        return self.CallValueWithPositiveInvariant(x)+self.k