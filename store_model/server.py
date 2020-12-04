from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from .model import Store
from .agent import Customer, Shelf, Checkout
import math

"""
possible_content = ["Electronics", "Clothing","Food", "misc"]
"""

def store_portrayal(agent):
    if agent is None:
        return

    # derived from sugarscape and schelling
    portrayal = {}
    if type(agent) is Customer:
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 1
        portrayal["w"] = 1
        portrayal["h"] = 1
        if agent.state == "LOOK": portrayal["Color"] = '#ff0000'
        else: portrayal["Color"] = '#ffff00'

    elif type(agent) is Shelf:
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 1
        portrayal["w"] = 1
        portrayal["h"] = 1
        if agent.contents == "Electronics":
            portrayal["Color"] = '#0000ff'
        elif agent.contents == "Clothing":
            portrayal["Color"] = '#ffff00'
        elif agent.contents == "Food":
            portrayal["Color"] = '#00ff00'
        elif agent.contents == "misc":
            portrayal["Color"] = '#ff00ff'
        elif agent.contents == "Empty":
            portrayal["Color"] = '#C0C0C0'
        else:
            portrayal["Color"] = '#000000'

    if type(agent) is Checkout:
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 1
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Color"] = '#add8e6'

    return portrayal

# dervied from ConwaysGameOfLife
# Make a world that is 50x50, on a 500x500 display.
canvas_element = CanvasGrid(store_portrayal, 108, 108, 1080, 1080)

# derived from schelling
model_params = {
    "height": 108,
    "width": 108,
}

server = ModularServer(
    Store, [canvas_element], "Wack Friday", model_params
)
