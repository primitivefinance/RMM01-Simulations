import numpy as np

def nonnegative(x):
    if isinstance(x, np.ndarray):
        return (x >= 0).all()
    return x >= 0
