from mesa import Agent
import math
import random

wanted_items = ["Electronics", "Clothing", "Food", "misc"]


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
        self.patience = random.randint(100, 200)
        self.wants = []
        self.want_index = 0
        self.target = None
        self.next_pos = None
        for i in range(3):
            self.wants.append(random.choice(wanted_items))
        self.exit_positions = [(int(self.model.grid.width/2  + 7 + i), int(self.model.grid.height) -1) for i in range(4)]

    def step(self):
        if self.state == "LOOK":
            self.next_pos = self.look_move()
            self.shop()
            self.patience -= 1
            if self.patience == 0: self.state = "CHECKOUT"
        if self.state == "CHECKOUT":
            if self.pos in self.exit_positions: 
                self.state = "EXITING"
                self.model.exit(self)
            else: self.next_pos = self.exit_move()
    
    def advance(self):
        self.model.grid.move_agent(self, self.next_pos)

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

    # TODO: combine look_move() and exit_move() into homing_move(target)
    def look_move(self):
        # Get neighborhood within vision
        valid_moves = [n for n in self.model.grid.get_neighborhood(self.pos, self.moore, True) if self.model.grid.is_cell_empty(n)]
        if len(valid_moves) == 0: return self.pos
        min_dist = min([get_distance(self.target.pos, pos) for pos in valid_moves])
        final_candidates = [
            pos for pos in valid_moves if get_distance(self.target.pos, pos) == min_dist
        ]
        self.random.shuffle(final_candidates)
        return final_candidates[0]
        #self.model.grid.move_agent(self, final_candidates[0])

    def shop(self):
        n_shelves = [n for n in self.model.grid.get_neighbors(self.pos, self.moore) if type(n) is Shelf]
        for shelf in n_shelves:
            if shelf.amount == 0: continue
            elif self.wants[self.want_index] == shelf.contents:
                shelf.amount -= 1
                self.patience += 100
                del self.wants[self.want_index]
                if len(self.wants) == 0: 
                    self.state = "CHECKOUT"
                    break
                else: 
                    self.want_index = 0
                    self.target = self.find_shelf(self.wants[self.want_index])

            
    def exit_move(self):
        # Get neighborhood within vision
        valid_moves = [n for n in self.model.grid.get_neighborhood(self.pos, self.moore, True) if self.model.grid.is_cell_empty(n)]
        if len(valid_moves) == 0: return self.pos
        # For now, just pathfinds to the far right door
        min_dist = min([get_distance(self.exit_positions[0], pos) for pos in valid_moves])
        
        final_candidates = [
            pos for pos in valid_moves if get_distance(self.exit_positions[0], pos) == min_dist
        ]
        self.random.shuffle(final_candidates)
        return final_candidates[0]
        #self.model.grid.move_agent(self, final_candidates[0])

