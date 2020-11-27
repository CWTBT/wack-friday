from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
import random

from .agent import Customer, Shelf

# derived from ConwaysGameOfLife
class Store(Model):

    def __init__(self, height=108, width=108, capacity=525, customers=2000):
        """
        Create a new playing area of (height, width) cells.
        """
        super().__init__()
        self.height = height
        self.width = width
        self.capacity = capacity
        self.customers = customers
        self.store_pop = 0
        self.possible_content = ["Electronics", "Clothing", "Food", "misc"]

        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = SimultaneousActivation(self)

        # Use a simple grid, where edges wrap around.
        self.grid = MultiGrid(height, width, torus=False)

        self.create_layout(40)

        self.running = True

    def create_layout(self, amount = 20):
        for i in range(amount):
            content = random.choice(self.possible_content)
            self.add_shelf(content)

    def add_shelf(self, content):
        done = False
        direction = "h"
        if random.random() > .5: direction = "v"
        while not done:
            x = random.randint(4, self.width - 4)
            y = random.randint(4, self.height - 10)
            pos = (x,y)

            if direction == "h" and (not self.check_for_shelf(pos, 'h')):
                for j in range(4):
                    shelf1 = Shelf(self.next_id(), self, content)
                    shelf2 = Shelf(self.next_id(), self, content)
                    self.grid.place_agent(shelf1, (x + j, y))
                    self.grid.place_agent(shelf2, (x + j, y - 1))
                    self.schedule.add(shelf1)
                    self.schedule.add(shelf2)
                done = True

            elif not self.check_for_shelf(pos, 'v'):
                for j in range(4):
                    shelf1 = Shelf(self.next_id(), self, content)
                    shelf2 = Shelf(self.next_id(), self, content)
                    self.grid.place_agent(shelf1, (x, y + j))
                    self.grid.place_agent(shelf2, (x  - 1, y + j))
                    self.schedule.add(shelf1)
                    self.schedule.add(shelf2)
                done = True

    def check_for_shelf(self, pos, direction):
        x, y = pos
        for j in range(4):
            if direction == 'h':
                if (not self.grid.is_cell_empty((x+j,y))) or not self.grid.is_cell_empty((x + j, y - 1)):
                    return True
            elif direction == 'v':
                if (not self.grid.is_cell_empty((x, y + j))) or not self.grid.is_cell_empty((x - 1, y +j)):
                    return True
        return False

    def step(self):
        """
        Have the scheduler advance each cell by one step
        """
        if self.store_pop < self.capacity:
            for i in range(4):
                entry_pos = (int(self.width/2  - 1 + i), int(self.height) -1)
                cust = Customer(self.next_id(), self)
                if self.grid.is_cell_empty(entry_pos):
                    self.grid.place_agent(cust, entry_pos)
                    self.schedule.add(cust)
                    self.store_pop += 1
                    self.customers -= 1
        self.schedule.step()
