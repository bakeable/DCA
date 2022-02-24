from functions import lookup_travel_distance
from matplotlib.patches import Rectangle
import math
from random import random

class PickingArea:
    def __init__(self, s_i, n, k, m, alpha, w_i, v_i, number, color):
        # Set storage capacity
        self.s_i = s_i

        # Set parameters
        self.n = n
        self.k = k
        self.m = m
        self.alpha = alpha
        self.w_i = w_i
        self.v_i = v_i

        # Set position
        self.x = 0
        self.y = 0

        # Set name and number
        self.name = "PA " + str(number)
        self.number = number
        self.color = color

        # Assume feasible
        self.feasible = True

        # Calculate width and height
        self.w = self.w_i * self.n
        self.h = self.s_i / self.n + self.v_i * self.k

        # Instantiate metrics
        self.travel_distance = 2 * self.y * (1 + self.alpha) + (1 + self.alpha) * lookup_travel_distance(self.n, self.k, self.m)
        self.EMS = None
        self.EMS_options = []
        self.penalty = 0

    def set_parameters(self, n=None, k=None, m=None, alpha=None):
        # Set parameters
        self.n = self.n if n is None else n
        self.k = self.k if k is None else k
        self.m = self.m if m is None else m
        self.alpha = self.alpha if alpha is None else alpha

        # Calculate width and height
        self.w = self.w_i * self.n
        self.h = self.s_i / self.n + self.v_i * self.k

        # Get travel distance from lookup
        self.travel_distance = 2 * self.y * (1 + self.alpha) + (1 + self.alpha) * lookup_travel_distance(self.n, self.k, self.m)

    def set_position(self, x, y):
        # Set position
        self.x = x
        self.y = y

    def get_dimensions(self):
        return self.x, self.y, self.w, self.h

    def is_feasible(self, width, height):
        if self.x + self.w > width or self.y + self.h > height or self.x < 0 or self.y < 0:
            self.feasible = False
        else:
            self.feasible = True

        # Return
        return self.feasible

    def get_travel_distance(self, n=None, k=None, m=None):
        if self.feasible:
            # Set parameters
            self.set_parameters(n, k, m)

            # Return distance
            return self.travel_distance
        else:
            # Calculate penalty


            # Return penalty plus actual travel distance
            return self.penalty + self.travel_distance

    def get_rectangle(self):
        # Determine color
        color = self.color if self.feasible else "red"

        # Create rectangle
        return Rectangle((self.x, self.y), self.w, self.h, color=color, fill=True, alpha=.5)
