from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from .model import Store
from .agent import Customer
import math

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
        portrayal["Color"] = '#ff0000'

    return portrayal

# dervied from ConwaysGameOfLife
# Make a world that is 50x50, on a 500x500 display.
canvas_element = CanvasGrid(store_portrayal, 50, 50, 500, 500)

# derived from schelling
model_params = {
    "height": 50,
    "width": 50,
}

server = ModularServer(
    Store, [canvas_element], "Wack Friday", model_params
)
