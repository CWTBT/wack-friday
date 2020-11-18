from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid

from .agent import Customer

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

        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = SimultaneousActivation(self)

        # Use a simple grid, where edges wrap around.
        self.grid = MultiGrid(height, width, torus=False)

        cust = Customer(self.next_id(), self)
        #self.grid.place_agent(cust, (50,50))

        self.running = True

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
