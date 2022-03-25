import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# Config
Px0 = 6     # Initial Asset Price
Pc0 = 1     # Initial Cash Price
Pct = 1     # Future Cash Price

v = 1.25    # Implied Volatility (Annualized)
t = 0.0833    # Time to Expiration

pdomainA = np.linspace(0.1,Px0,200)
pdomainB = np.linspace(Px0,30,200)

# Options Quantity Equations
def d1(x,K):
    return np.log(x/K)/(v*np.sqrt(t))+0.5*v*np.sqrt(t)
def d2(x,K):
    return d1(x,K)-v*np.sqrt(t)

def alpha(x,K):
    return (Px0/x-1)*x/(Pct*(norm.cdf(-d2(x,K))*K-norm.cdf(-d1(x,K))*x/Pct))

def beta(x,K):
    return x*(1-Px0/x)/(Pct*(norm.cdf(d1(x,K))*x/Pct-norm.cdf(d2(x,K))*K))

# At-The-Money Options
plt.plot(pdomainA,alpha(pdomainA,Px0/Pc0))
plt.xlabel("Price P(t)")
plt.ylabel("# of Puts")
plt.title(r'$\frac{\alpha(P)}{x}$')
plt.show()
plt.close()

plt.plot(pdomainB,beta(pdomainB,Px0/Pc0),'r')
plt.xlabel("Price P(t)")
plt.ylabel("# of Calls")
plt.title(r'$\frac{\beta(P)}{y}$')
plt.show()
plt.close()

# Near-The-Money Options Surface Plots
'''
Simply have to change the strike price of the options in alpha(x,f) and beta(x,f), using the f variable
'''
fdomain = np.linspace(Px0/Pc0*0.6,Px0/Pc0*1.6, 300)

A,F = np.meshgrid(pdomainA,fdomain)
alpha = alpha(A,F)
B,F = np.meshgrid(pdomainB,fdomain)
beta = beta(B,F)

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(A, F, alpha, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.set_xlabel('Price')
ax.set_ylabel('Strike')
ax.set_zlabel('Quantity of Puts')
plt.title(r'Near Money Adjusted $\frac{\alpha(P)}{x}$')
plt.show()
plt.close()

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(B, F, beta, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.set_xlabel('Price')
ax.set_ylabel('Strike')
ax.set_zlabel('Quantity of Calls')
plt.title(r'Near Money Adjusted $\frac{\beta(P)}{y}$')
plt.show()
plt.close()

# Non-Zero Replication Error
'''
Here since we are long the options, we are effectively in a put on the invariant with strike k=0
(As per the definition of the long options described in "RMM-01 Derivatives & Structured Products").
We'll need to modify the quantity functions to account for a translation in the option's value
'''
def alphamod1(x,k):
    return (Px0/x-1)*x/(Pct*(norm.cdf(-d2(x,Px0/Pc0))*(Px0/Pc0)-norm.cdf(-d1(x,Px0/Pc0))*x/Pct-k))
def alphamod2(x):
    return (Px0/x-1)*x/(Pct*(norm.cdf(-d2(x,Px0/Pc0))*(Px0/Pc0)-norm.cdf(-d1(x,Px0/Pc0))*x/Pct))

def betamod1(x,k):
    return x*(1-Px0/x)/(Pct*(norm.cdf(d1(x,Px0/Pc0))*x/Pct-norm.cdf(d2(x,Px0/Pc0))*(Px0/Pc0)-k))
def betamod2(x):
    return x*(1-Px0/x)/(Pct*(norm.cdf(d1(x,Px0/Pc0))*x/Pct-norm.cdf(d2(x,Px0/Pc0))*(Px0/Pc0)))

kdomain1 = np.linspace(-5,0,250)
kdomain2 = np.linspace(0,5,250)

C1,K1 = np.meshgrid(pdomainA,kdomain1)
alphamod1 = alphamod1(C1,K1)
C2,K2 = np.meshgrid(pdomainA,kdomain2)
alphamod2 = alphamod2(C2)

D1,K1 = np.meshgrid(pdomainB,kdomain1)
betamod1 = betamod1(D1,K1)
D2,K2 = np.meshgrid(pdomainB,kdomain2)
betamod2 = betamod2(D2)

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(D1, K1, betamod1, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.plot_surface(D2, K2, betamod2, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.set_xlabel('Price')
ax.set_ylabel('Invariant')
ax.set_zlabel('Quantity of Calls')
plt.title(r'Non-Zero Invariant Adjusted $\frac{\beta(P)}{y}$')
plt.show()
plt.close()

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot_surface(C1, K1, alphamod1, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.plot_surface(C2, K2, alphamod2, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax.set_xlabel('Price')
ax.set_ylabel('Invariant')
ax.set_zlabel('Quantity of Puts')
plt.title(r'Non-Zero Invariant Adjusted $\frac{\alpha(P)}{x}$')
plt.show()
plt.close()