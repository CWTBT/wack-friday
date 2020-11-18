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
        self.store_pop = 0

        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = SimultaneousActivation(self)

        # Use a simple grid, where edges wrap around.
        self.grid = MultiGrid(height, width, torus=True)

        self.running = True

    def step(self):
        """
        Have the scheduler advance each cell by one step
        """
        if self.store_pop < self.capacity:
            for i in range(4):
                entry_pos = (self.width/2, self.height - 1 + i)
                cust = Customer(self.next_id(), self)
                if self.grid.is_cell_empty(entry_pos):
                    self.grid.place_agent(cust, entry_pos)
                    self.store_pop += 1
                    self.customers -= 1
        self.schedule.step()
