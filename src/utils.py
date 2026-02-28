import math 
import random

def hybrid_wealth(mu=10, sigma=1.0, alpha=1.5, tail_fraction=0.05):
    if random.random() < tail_fraction:
        # Pareto tail
        xmin = math.exp(mu + 2*sigma)
        w = xmin * (random.random() ** (-1/alpha))
    else:
        # Lognormal body
        w = random.lognormvariate(mu, sigma)
    return w