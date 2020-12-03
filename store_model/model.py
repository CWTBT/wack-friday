from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
import random
import numpy as np

from .agent import Customer, Shelf

# derived from ConwaysGameOfLife
class Store(Model):

    # default capacity = 525
    # default customers = 2000
    def __init__(self, height=108, width=108, capacity=525, customers=2000, layout = []):
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

        # Set up the grid and schedule.

        # Use SimultaneousActivation which simulates all the cells
        # computing their next state simultaneously.  This needs to
        # be done because each cell's next state depends on the current
        # state of all its neighbors -- before they've changed.
        self.schedule = SimultaneousActivation(self)

        # Use a simple grid, where edges wrap around.
        self.grid = MultiGrid(height, width, torus=False)

        if self.layout == []:
            self.create_layout(40)
        else:
            self.set_up()

        self.running = True

    def get_layout(self):
        return self.layout

    def set_up(self):
        for x in range(len(self.layout)):
            for y in range(len(self.layout[x])):
                content = self.layout[x][y]
                if content == 'h':
                    self.__add_h_shelf__((x,y))
                elif content == 'v':
                    self.__add_v_shelf__((x, y))


    def __add_v_shelf__(self, pos):
        for j in range(4):
            shelf1 = Shelf(self.next_id(), self, content)
            shelf2 = Shelf(self.next_id(), self, content)
            self.grid.place_agent(shelf1, (x, y + j))
            self.grid.place_agent(shelf2, (x - 1, y + j))
            self.schedule.add(shelf1)
            self.schedule.add(shelf2)
            self.shelf_list.append(shelf1)
            self.shelf_list.append(shelf2)

    def __add_h_shelf__(self, pos):
        for j in range(4):
            shelf1 = Shelf(self.next_id(), self, content)
            shelf2 = Shelf(self.next_id(), self, content)
            self.grid.place_agent(shelf1, (x + j, y))
            self.grid.place_agent(shelf2, (x + j, y - 1))
            self.schedule.add(shelf1)
            self.schedule.add(shelf2)
            self.shelf_list.append(shelf1)
            self.shelf_list.append(shelf2)

    def create_layout(self, amount = 20):
        self.layout = np.zeros((self.width, self.height), dtype=str).tolist()
        for i in range(amount):
            content = random.choice(self.possible_content)
            self.add_shelf(content)

    def shelf_count(self):
        toReturn = 0
        for x in self.layout:
            for y in x:
                if y == 'h' or y == 'v':
                    toReturn+=1
        return toReturn

    def add_shelf(self, content):
        done = False
        while not done:
            direction = "h"
            if random.random() > .5: direction = "v"
            x = random.randint(4, self.width - 4)
            y = random.randint(1, self.height - 10)
            pos = (x,y)
            self.layout[x][y] = direction

            if direction == "h" and (not self.check_for_shelf(pos, 'h')):
                for j in range(4):
                    shelf1 = Shelf(self.next_id(), self, content)
                    shelf2 = Shelf(self.next_id(), self, content)
                    self.grid.place_agent(shelf1, (x + j, y))
                    self.grid.place_agent(shelf2, (x + j, y - 1))
                    self.schedule.add(shelf1)
                    self.schedule.add(shelf2)
                    self.shelf_list.append(shelf1)
                    self.shelf_list.append(shelf2)
                done = True

            elif not self.check_for_shelf(pos, 'v'):
                for j in range(4):
                    shelf1 = Shelf(self.next_id(), self, content)
                    shelf2 = Shelf(self.next_id(), self, content)
                    self.grid.place_agent(shelf1, (x, y + j))
                    self.grid.place_agent(shelf2, (x  - 1, y + j))
                    self.schedule.add(shelf1)
                    self.schedule.add(shelf2)
                    self.shelf_list.append(shelf1)
                    self.shelf_list.append(shelf2)
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

    def mutate(self):
        if random.random() > 1:
            self.add_shelf(random.choice(self.possible_content))
        else:
            self.remove_random_shelf()

    def remove_random_shelf(self):
        if self.shelf_count() == 0:
            return
        else:
            done = False
            while not done:
                x = random.randint(4, self.width - 4)
                y = random.randint(4, self.height - 10)
                direction = self.layout[x][y]
                if direction == 'h' or direction == 'v':
                    self.remove_shelf((x,y),direction)
                    done = True

    def remove_shelf(self, pos, dir):
        x,y = pos
        self.layout[x][y] = ''
        if dir == 'h':
            for j in range(4):
                self.__remove_shelf_square__(x + j, y)
                self.__remove_shelf_square__(x + j, y - 1)
        else:
            for j in range(4):
                self.__remove_shelf_square__(x, y + j)
                self.__remove_shelf_square__(x - 1, y + j)

    def __remove_shelf_square__(self, x, y):
        contents = self.grid.iter_cell_list_contents((x, y))
        toRemove = 0
        for c in contents:
            toRemove = c
        if toRemove == 0: return
        self.grid.remove_agent(toRemove)

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
            entry_pos = (int(self.width/2  - 1 + i), int(self.height) -1)
            if self.grid.is_cell_empty(entry_pos) and self.store_pop < self.capacity:
                if self.customers > 0:
                    self.store_pop += 1
                    self.customers -= 1
                    cust = Customer(self.next_id(), self)
                    self.grid.place_agent(cust, entry_pos)
                    self.schedule.add(cust)
                    cust.target = cust.find_shelf()

    def exit(self, cust):
        self.to_kill.append(cust)
