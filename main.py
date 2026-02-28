from src.model import *
from matplotlib import pyplot as plt

if __name__ == '__main__':
    m = ShoppingModel(n = 100)
    m.run_for(180) # 6 months
    data = m.datacollector.get_agent_vars_dataframe()
    # Use seaborn
    plt.hist(x = data["Wealth"])
    plt.show()
    