from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import Grid
import random
import numpy as np
import math

from .agent import Customer, Shelf, Checkout

# derived from ConwaysGameOfLife
class Store(Model):

    # default capacity = 525
    # default customers = 2000
    def __init__(self, height=108, width=108, capacity=525, customers=2000, layout=0):
        """
        Create a new playing area of (height, width) cells.
        """
        super().__init__()
        self.height = height
        self.width = width
        self.capacity = capacity
        self.customers = customers
        self.store_pop = 0
        self.to_kill = []
        self.possible_content = ["Electronics", "Clothing", "Food", "misc"]
        self.layout = layout
        self.shelf_list = []
        self.checkout_list = []

        self.total_satisfaction = 0
        self.total_profit = 0

        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = SimultaneousActivation(self)

        # Use a simple grid, where edges wrap around.
        self.grid = Grid(height, width, torus=False)

        # if no layout is fed in, generates it's own layout. Else it feeds the layout to the grid
        if self.layout == 0:
            self.create_layout(40)
        else:
            self.set_up()

        # place check-out squares
        for x in np.arange(2, self.width-2, 3):
            if (x < self.width / 2 - 15) or (x > self.width / 2 ):
                checkout = Checkout(self.next_id(), self)
                self.grid.place_agent(checkout, (x, self.height - 5))
                self.schedule.add(checkout)
                self.checkout_list.append(checkout)

        self.running = True

    # sigmoid function for calculating success
    def __sigmoid__(self, x):
        return 1 / (1 + math.exp(-x))

    def score(self):
        """

        :return: Score for evo algorithm
        """
        return self.__sigmoid__(self.total_satisfaction) + self.__sigmoid__(self.total_profit)

    def clone(self):
        """
        :return: a clone with the same layout
        """
        return Store(self.height, self.width, self.capacity, self.customers, self.layout)

    def get_layout(self):
        """
        :return: the layout of the store
        """
        return self.layout

    def set_up(self):
        """Loads a set up to the grid based on a provided layout"""
        for shelf in self.layout:
            pos, direction, content = shelf
            if direction == 'v':
                self.__place_v_shelf__(pos, content)
            else:
                self.__place_h_shelf__(pos, content)

    # places a vertical shelf on the grid
    def __place_v_shelf__(self, pos, content):
        x, y = pos
        for j in range(4):
            shelf1 = Shelf(self.next_id(), self, content)
            shelf2 = Shelf(self.next_id(), self, content)
            self.grid.place_agent(shelf1, (x, y + j))
            self.grid.place_agent(shelf2, (x - 1, y + j))
            self.schedule.add(shelf1)
            self.schedule.add(shelf2)
            self.shelf_list.append(shelf1)
            self.shelf_list.append(shelf2)

    # places a horizontal shelf on the grid
    def __place_h_shelf__(self, pos, content):
        x,y = pos
        for j in range(4):
            shelf1 = Shelf(self.next_id(), self, content)
            shelf2 = Shelf(self.next_id(), self, content)
            self.grid.place_agent(shelf1, (x + j, y))
            self.grid.place_agent(shelf2, (x + j, y - 1))
            self.schedule.add(shelf1)
            self.schedule.add(shelf2)
            self.shelf_list.append(shelf1)
            self.shelf_list.append(shelf2)

    def create_layout(self, amount=20):
        """
        Creates a random store layout. Places 2x4 shelves that can be horizontal or vertical.
        """
        self.layout = []
        for i in range(amount):
            content = random.choice(self.possible_content)
            self.add_shelf(content)

    def shelf_count(self):
        """returns the number of shelves"""
        return len(self.layout)

    def add_shelf(self, content):
        """adds shelf to the layout and to the grid"""
        done = False
        pos = (0,0)
        direction = ""
        while not done:
            direction = "h"
            if random.random() > .5: direction = "v"
            x = random.randint(1, self.width - 4)
            y = random.randint(1, self.height - 10)
            pos = (x, y)

            if direction == "h" and (not self.check_for_shelf(pos, 'h')):
                self.__place_h_shelf__(pos, content)
                done = True

            elif direction == 'v' and (not self.check_for_shelf(pos, 'v')):
                self.__place_v_shelf__(pos, content)
                done = True

        self.layout.append([pos, direction, content])

    def check_for_shelf(self, pos, direction):
        """
        Checks if a shelf can be placed in a area without overlapping.
        Returns true if there is a shelf in the way
        """
        x, y = pos
        for j in range(4):
            if direction == 'h':
                if (not self.grid.is_cell_empty((x + j, y))) or (not self.grid.is_cell_empty((x + j, y - 1))):
                    return True
            elif direction == 'v':
                if (not self.grid.is_cell_empty((x, y + j))) or (not self.grid.is_cell_empty((x - 1, y + j))):
                    return True
        return False

    def mutate(self):
        """adds or removes a random shelf"""
        if random.random() > 0.5:
            self.add_shelf(random.choice(self.possible_content))
        else:
            self.remove_random_shelf()

    def remove_random_shelf(self):
        """Removes a random shelf from the layout and the grid"""
        if self.shelf_count() == 0:
            return
        else:
            shelf_info = random.choice(self.layout)
            self.layout.remove(shelf_info)
            pos, direction, content = shelf_info
            self.remove_shelf(pos, direction)

    def remove_shelf(self, pos, direction):
        x,y = pos
        if direction == 'h':
            for j in range(4):
                self.__remove_shelf_square__(x + j, y)
                self.__remove_shelf_square__(x + j, y - 1)
        else:
            for j in range(4):
                self.__remove_shelf_square__(x, y + j)
                self.__remove_shelf_square__(x - 1, y + j)

    def __remove_shelf_square__(self, x, y):
        contents = self.grid.iter_cell_list_contents((x, y))
        to_remove = 0
        for c in contents:
            if type(c) == Shelf:
                to_remove = c
        if to_remove == 0:
            return
        self.grid.remove_agent(to_remove)

    def step(self):
        """
        Have the scheduler advance each cell by one step
        """
        self.schedule.step()
        for cust in self.to_kill:
            self.grid.remove_agent(cust)
            self.schedule.remove(cust)
            self.to_kill.remove(cust)
            self.store_pop -= 1
        for i in range(4):
            entry_pos = (int(self.width / 2 - 9 + i), int(self.height) - 1)
            if self.grid.is_cell_empty(entry_pos) and self.store_pop < self.capacity:
                if self.customers > 0:
                    self.store_pop += 1
                    self.customers -= 1
                    cust = Customer(self.next_id(), self)
                    self.grid.place_agent(cust, entry_pos)
                    self.schedule.add(cust)
                    cust.target = cust.find_shelf(cust.wants[0])
        print(f"SATISFACTION: {self.total_satisfaction}")
        print(f"PROFIT: {self.total_profit}")

    def exit(self, cust):
        self.to_kill.append(cust)
