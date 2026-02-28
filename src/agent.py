import mesa
import random
from src.utils import *

class Individual(mesa.Agent):
    """
        This represents a simple Individual within the population.
        It has:
            - wealth : its economical capacity in terms of moneys. its initial value is distributed following a log normal body plus a pareto tail.
            - income : its monthly income . it follows a lognormal centered in "average income" with variance of "income variance".
            - hunger level : its level of hunger (0, 1). when this level reaches 1, it must buy food or the individual will die.
            - shopping probability : this is the probability of doing shopping at a given time step.
            - over shopping probability : this is the probability of buying extra item while doing shopping. this probability is higher during holidays.
    """

    def __init__(self, model):
        super().__init__(model)
        self.wealth = random.lognormvariate(mu = model.average_wealth, sigma = model.wealth_std)
        self.income = random.lognormvariate(mu = model.average_income, sigma = model.income_std) 
        self.hunger_level = 0
        self.shopping_probability = random.uniform(model.lowest_shopping_probability, model.highest_shopping_probability)
        self.over_shopping_probability = random.uniform(model.lowest_over_shopping_probability, model.highest_over_shopping_probability)
        self.groceries = []
        self.extras = []

    def buy_groceries(self):
        """
            In this version, the shopping strategy is very simple:
            the agent repeatedly selects random items until its hunger is relieved.
            Each chosen item reduces hunger by its relief value and decreases wealth by its cost.
        """
        if self.wealth > 0:
            available_items = self.model.store.get_items(budget = self.wealth) # this will be a list containing items (based on the budget), which are objects with a cost and a recovery value
            goal = self.hunger_level
            while goal > 0:
                if available_items:
                    item = random.choice(available_items)
                    self.wealth -= item.cost
                    self.groceries.append(item)
                    available_items = self.model.store.get_items(budget = self.wealth)
                else:
                    return False
            return True
        else:
            return False
        
    def buy_extras(self):
        """
            Just buying one random item from the mall.
        """
        if self.wealth > 0:
            available_items = self.model.mall.get_items(budget = self.wealth)
            if available_items:
                item = random.choice(available_items) 
                self.extras.append(item)
                self.wealth -= item.cost

    def eat(self):
        if self.groceries:
            item = self.groceries.pop()
            self.hunger_level = max(0, self.hunger_level - item.recovery_value)
        else:
            if self.buy_groceries():
                self.eat()
            else:
                self.die() # this is just for logical structure, it does nothing

    def die(self):
        pass

