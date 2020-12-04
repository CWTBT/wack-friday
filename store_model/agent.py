from mesa import Agent
import math
import random

wanted_items = ["Electronics", "Clothing", "Food", "misc"]
price_map = {"Electronics": 200, "Clothing": 50, "Food": 20, "misc":10}


# from sugarscape_cg
def get_distance(pos_1, pos_2):
    """ Get the distance between two point

    Args:
        pos_1, pos_2: Coordinate tuples for both points.

    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)



class Shelf(Agent):
    """
    The shelves
    """
    def __init__(self, unique_id, model, contents, moore=True):
        super().__init__(unique_id, model)
        self.moore = moore
        self.contents = contents
        self.amount = 10


class Customer(Agent):
    """
    The customer
    """
    def __init__(self, unique_id, model, moore=True):
        super().__init__(unique_id, model)
        self.state = "LOOK"
        self.moore = moore
        self.patience = 500
        self.item_patience = 100
        self.satisfaction = 100
        self.wants = []
        self.haves = []
        self.want_index = 0
        self.target = None
        self.next_pos = None
        for i in range(5):
            self.wants.append(random.choice(wanted_items))
        self.exit_positions = [(int(self.model.grid.width/2  + 7 + i), int(self.model.grid.height) -1) for i in range(4)]

    def step(self):
        if self.state == "LOOK":
            self.next_pos = self.homing_move(self.target.pos)
            self.shop()
            self.patience -= 1
            self.item_patience -= 1
            if self.patience == 0: 
                self.state = "CHECKOUT"
                self.target = self.find_checkout()
            elif self.item_patience == 0:
                self.satisfaction -= 10
                self.next_item()
                self.item_patience = 100
        if self.state == "CHECKOUT":
            if self.target in [n for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Checkout]:
                 self.state = "CHECKING OUT"
            else: 
                self.next_pos = self.homing_move(self.target.pos)
        if self.state == "CHECKING OUT":
            # TODO: Change this into cashing out items
            if len(self.haves) == 0: 
                self.satisfaction -= 20 * len(self.wants)
                self.state = "FINDING EXIT"
            else: 
                self.model.total_profit += price_map[self.haves[-1]]
                del self.haves[-1]
        if self.state == "FINDING EXIT":
            if self.pos in self.exit_positions: 
                self.state = "EXITING"
                self.model.total_satisfaction += self.satisfaction
                self.model.exit(self)
            else: self.next_pos = self.homing_move(self.exit_positions[3])
    
    def advance(self):
        self.model.grid.move_agent(self, self.next_pos)

    #TODO: The following two functions could be combined somehow, they're almost identical
    def find_shelf(self, wanted_item):
        best_shelf = None
        min_dist = 9999
        for shelf in self.model.shelf_list:
            if shelf.contents == wanted_item:
                dist = get_distance(shelf.pos, self.pos)
                if dist < min_dist:
                    min_dist = dist
                    best_shelf = shelf
        return best_shelf

    def find_checkout(self):
        best_checkout = None
        min_dist = 9999
        for checkout in self.model.checkout_list:
            dist = get_distance(checkout.pos, self.pos)
            if dist < min_dist:
                min_dist = dist
                best_checkout = checkout
        return best_checkout

    def shop(self):
        n_shelves = [n for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Shelf]
        for shelf in n_shelves:
            if shelf.amount == 0: continue
            elif self.wants[self.want_index] == shelf.contents:
                shelf.amount -= 1
                self.patience += 100
                self.item_patience = 100
                self.haves.append(self.wants[self.want_index])
                del self.wants[self.want_index]
                if len(self.wants) == 0: 
                    self.state = "CHECKOUT"
                    self.target = self.find_checkout()
                    break
                else: 
                    self.next_item()

    def next_item(self):
        self.want_index += 1
        if self.want_index >= len(self.wants): self.want_index = 0
        self.target = self.find_shelf(self.wants[self.want_index])

    def homing_move(self, target_square):
        # Get neighborhood within vision
        valid_moves = [n for n in self.model.grid.get_neighborhood(self.pos, self.moore, True) if self.model.grid.is_cell_empty(n)]
        if len(valid_moves) == 0: return self.pos
        min_dist = min([get_distance(target_square, pos) for pos in valid_moves])
        
        final_candidates = [
            pos for pos in valid_moves if get_distance(target_square, pos) == min_dist
        ]
        self.random.shuffle(final_candidates)
        return final_candidates[0]


class Checkout(Agent):

    def __init__(self, unique_id, model, moore=True):
        super().__init__(unique_id, model)
        self.moore = moore