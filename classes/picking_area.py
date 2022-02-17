from functions import lookup_travel_distance
from constants import w_i, v_i
from matplotlib.patches import Rectangle



class PickingArea:
    def __init__(self, s_i, n, k, m, alpha):
        # Set storage capacity
        self.s_i = s_i

        # Set parameters
        self.n = n
        self.k = k
        self.m = m
        self.alpha = alpha

        # Set position
        self.x = 0
        self.y = 0

        # Calculate width and height
        self.w = w_i * self.n
        self.h = self.s_i / self.n + v_i * self.k

        # Instantiate metrics
        self.travel_distance = (1 + self.alpha) * lookup_travel_distance(self.n, self.k, self.m)

    def set_parameters(self, n=None, k=None, m=None, alpha=None):
        # Set parameters
        self.n = self.n if n is None else n
        self.k = self.k if k is None else k
        self.m = self.m if m is None else m
        self.alpha = self.alpha if alpha is None else alpha

        # Calculate width and height
        self.w = w_i * self.n
        self.h = self.s_i / self.n + v_i * self.k

        # Get travel distance from lookup
        self.travel_distance = (1 + self.alpha) * lookup_travel_distance(self.n, self.k, self.m)

    def set_position(self, x, y):
        # Set position
        self.x = x
        self.y = y

    def is_feasible(self, width, height):
        if self.x + self.w > width or self.y + self.h > height or self.x < 0 or self.y < 0:
            return False
        else:
            return True

    def get_travel_distance(self, n=None, k=None, m=None):
        # Set parameters
        self.set_parameters(n, k, m)

        # Return distance
        return self.travel_distance

    def get_rectangle(self):
        return Rectangle((self.x, self.y), self.w, self.h, color="red", fill=True, alpha=.5)