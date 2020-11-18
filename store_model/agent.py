from mesa import Agent
import math


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


class Customer(Agent):
    """
    The customer
    """
    def __init__(self, unique_id, model, moore=True):
        super().__init__(unique_id, model)
        self.state = "LOOK"
        self.moore = moore

    def step(self):
        """
        For now, customers simply move randomly and cannot take up an occupied square
        """
        if self.state == "LOOK":
            self.random_move()

    # based on wolf_sheep RandomWalker
    def random_move(self):
        """
        Step one cell in any allowable direction.
        """
        # Pick the next cell from the adjacent empty cells.
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, True)
        for move in next_moves:
            if not self.model.grid.is_cell_empty(move):
                next_moves.remove(move)
        next_move = self.random.choice(next_moves)
        # Now move:
        self.model.grid.move_agent(self, next_move)

