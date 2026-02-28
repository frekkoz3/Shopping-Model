import mesa
from src.agent import *
from src.utils import *
import json
import random
from mesa.time import Schedule
from src import CONFIG_DIR

import json
import os

class Item:
    def __init__(self, cost, recovery_value, name):
        self.cost = cost
        self.recovery_value = recovery_value
        self.name = name

    def __repr__(self):
        return f"Item(name={self.name}, cost={self.cost}, recovery={self.recovery_value})"

class Store:
    def __init__(self, path=os.path.join(CONFIG_DIR, "store_config.json")):
        self.items = {}
        self._load_items(path)

    def _load_items(self, path):
        with open(path, "r") as f:
            data = json.load(f)

        for name, info in data.items():
            item = Item(
                cost=info["cost"],
                recovery_value=info["recovery"],
                name=name
            )
            self.items[name] = item

    def get(self, name):
        return self.items.get(name)

    def get_items(self, budget = None):
        items = list(self.items.values())

        if budget is None:
            return items

        return [item for item in items if item.cost <= budget]

def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B

class ShoppingModel(mesa.Model):

    def __init__(self, n=50, path = os.path.join(CONFIG_DIR, "model_config.json")):
        super().__init__()

        self.num_agents = n

        with open(path, "r") as f:
            data = json.load(f)

        self.average_wealth = data["average_wealth"]
        self.wealth_std = data["wealth_std"]
        self.average_income = data["average_income"]
        self.income_std = data["income_std"]
        self.lowest_shopping_probability = data["lowest_shopping_probability"]
        self.highest_shopping_probability = data["highest_shopping_probability"]
        self.lowest_over_shopping_probability = data["lowest_over_shopping_probability"]
        self.highest_over_shopping_probability = data["highest_over_shopping_probability"]

        self.store = Store(os.path.join(CONFIG_DIR, "store_config.json"))
        self.mall = Store(os.path.join(CONFIG_DIR, "mall_config.json"))

        for _ in range(n):
            a = Individual(self)

            self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "wealth"}
        )
        self.datacollector.collect(self)
        self.schedule_recurring(self.paycheck, Schedule(interval=30),) # 30 days based month

    def paycheck(self):
        for agent in self.agents:
            agent.wealth += agent.income

    def step(self):
        for agent in self.agents:
            agent.hunger_level = min(1, agent.hunger_level + random.uniform(0.4, 0.7)) # each day 
            if random.random() < agent.shopping_probability:
                agent.buy_groceries()
                if random.random() < agent.over_shopping_probability:
                    agent.buy_extras()
            agent.eat()
        dead = self.agents.select(lambda a: a.hunger_level > 1 and a.wealth <= 0)
        for agent in dead:
            agent.remove()
            self.num_agents -= 1
        self.datacollector.collect(self)