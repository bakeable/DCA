# from matplotlib.patches import Rectangle


class EmptyMaximalSpace:
    def __init__(self, x, y, w, h, in_warehouse=True):
        # Set parameters
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        # Feasibility
        self.in_warehouse = in_warehouse

        # Set border coordinates
        self.left_border = x
        self.right_border = x + w
        self.bottom_border = y
        self.top_border = y + h

        # Set corner coordinates
        self.corner_lower_left = (x, y)
        self.corner_lower_right = (x + w, y)
        self.corner_upper_left = (x, y + h)
        self.corner_upper_right = (x + w, y + h)

    def get_coordinates(self):
        return self.corner_lower_left, self.corner_lower_right, self.corner_upper_left, self.corner_upper_right

    def get_dimensions(self):
        return self.x, self.y, self.w, self.h

    def contains(self, x, y):
        # Check if EMS contains point
        return self.left_border < x < self.right_border and self.bottom_border < y < self.top_border

    def get_contained_corners(self, corners):
        # Check which points are contained in the EMS
        contained_corners = []
        for (x, y, corner_type) in corners:
            if self.contains(x, y):
                contained_corners.append((x, y, corner_type))

        return contained_corners

    def get_overlapping_borders(self, corners):
        # Overlapping borders
        overlapping_borders = []

        # Get coordinates
        lower_left_x, lower_left_y, lower_left_type = corners[0]  # lower-left
        lower_right_x, lower_right_y, lower_right_type = corners[1]  # lower-right
        upper_left_x, upper_left_y, upper_left_type = corners[2]  # upper-left
        upper_right_x, upper_right_y, upper_right_type = corners[3]  # upper_right

        # Left border
        if upper_left_y >= self.y + self.h and lower_left_y <= self.y and self.x <= upper_left_x <= self.x + self.w:
            overlapping_borders.append((lower_left_x, "left"))

        # Right border
        if upper_right_y >= self.y + self.h and lower_right_y <= self.y and self.x <= upper_right_x <= self.x + self.w:
            overlapping_borders.append((lower_right_x, "right"))

        # Top border
        if upper_left_x <= self.x and upper_right_x >= self.x + self.w  and self.y <= upper_left_y <= self.y + self.h:
            overlapping_borders.append((upper_left_y, "top"))

        # Bottom border
        if lower_left_x <= self.x and lower_right_x >= self.x + self.w  and self.y <= lower_left_y <= self.y + self.h:
            overlapping_borders.append((lower_left_y, "bottom"))

        # Return
        return overlapping_borders

    def is_equal_to(self, x, y, w, h):
        # If we have 4 equal dimensions, it is equal
        return self.x == x and self.y == y and self.w == w and self.h == h

    def split_in_two(self, corner):
        EMSs = []

        # Get corner
        corner_x, corner_y, corner_type = corner

        # Relative to EMS
        rel_corner_x = corner_x - self.x
        rel_corner_y = corner_y - self.y

        # Create new empty maximal spaces
        if corner_type == "upper-right":
            EMSs.append(EmptyMaximalSpace(corner_x, self.y, self.w - rel_corner_x, self.h))
            EMSs.append(EmptyMaximalSpace(self.x, corner_y, self.w, self.h - rel_corner_y))
        elif corner_type == "lower-right":
            EMSs.append(EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_y))
            EMSs.append(EmptyMaximalSpace(corner_x, self.y, self.w - rel_corner_x, self.h))
        elif corner_type == "upper-left":
            EMSs.append(EmptyMaximalSpace(self.x, self.y, rel_corner_x, self.h))
            EMSs.append(EmptyMaximalSpace(self.x, corner_y, self.w, self.h - rel_corner_y))
        else:
            EMSs.append(EmptyMaximalSpace(self.x, self.y, rel_corner_x, self.h))
            EMSs.append(EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_y))

        # Return
        return EMSs

    def split_in_three(self, corner_1, corner_2):
        EMSs = []

        # Get corners
        corner_1_x, corner_1_y, corner_1_type = corner_1
        corner_2_x, corner_2_y, corner_2_type = corner_2

        # Relative to EMS
        rel_corner_1_x = corner_1_x - self.x
        rel_corner_1_y = corner_1_y - self.y
        rel_corner_2_x = corner_2_x - self.x
        rel_corner_2_y = corner_2_y - self.y

        # Create new empty maximal spaces
        if corner_1_type == "upper-left" and corner_2_type == "upper-right":
            EMSs.append(EmptyMaximalSpace(self.x, self.y, rel_corner_1_x, self.h))
            EMSs.append(EmptyMaximalSpace(self.x, corner_1_y, self.w, self.h - rel_corner_1_y))
            EMSs.append(EmptyMaximalSpace(corner_2_x, self.y, self.w - rel_corner_2_x, self.h))
        elif corner_1_type == "lower-left" and corner_2_type == "lower-right":
            EMSs.append(EmptyMaximalSpace(self.x, self.y, self.w - rel_corner_1_x, self.h))
            EMSs.append(EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_1_y))
            EMSs.append(EmptyMaximalSpace(corner_2_x, self.y, self.w - rel_corner_2_x, self.h))
        elif corner_1_type == "lower-left" and corner_2_type == "upper-left":
            EMSs.append(EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_1_y))
            EMSs.append(EmptyMaximalSpace(self.x, self.y, rel_corner_1_x, self.h))
            EMSs.append(EmptyMaximalSpace(self.x, corner_2_y, self.w, self.h - rel_corner_2_y))
        elif corner_1_type == "lower-right" and corner_2_type == "upper-right":
            EMSs.append(EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_1_y))
            EMSs.append(EmptyMaximalSpace(corner_1_x, self.y, self.w - rel_corner_1_x, self.h))
            EMSs.append(EmptyMaximalSpace(self.x, corner_2_y, self.w, self.h - rel_corner_2_y))

        # Return
        return EMSs

    def split_by_borders(self, borders):
        EMSs = []

        # Assess all border splits
        for border in borders:
            coordinate, border_type = border

            # EMS is split by a bottom border
            if border_type == "bottom":
                # Get border y-coordinate
                border_y = coordinate

                # New EMS height changes, equal to distance from bottom of current EMS to the border
                # All other properties are the same
                EMSs.append(EmptyMaximalSpace(self.x, self.y, self.w, border_y - self.y))

            # EMS is split by a top border
            if border_type == "top":
                # Get border y-coordinate
                border_y = coordinate

                # New EMS height changes, equal to distance from border to top of current EMS
                # New EMS y-coordinate changes to y-coordinate of border
                # All other properties are the same
                EMSs.append(EmptyMaximalSpace(self.x, border_y, self.w, self.y + self.h - border_y))

            # EMS is split by a left border
            if border_type == "left":
                # Get border x-coordinate
                border_x = coordinate

                # New EMS width changes, equal to distance from left side of current EMS to border
                # All other properties are the same
                EMSs.append(EmptyMaximalSpace(self.x, self.y, border_x - self.x, self.h))

            # EMS is split by a right border
            if border_type == "right":
                # Get border x-coordinate
                border_x = coordinate

                # New EMS width changes, equal to distance from border to right side of current EMS
                # New EMS x-coordinate changes to x-coordinate of border
                # All other properties are the same
                EMSs.append(EmptyMaximalSpace(border_x, self.y, self.x + self.w - border_x, self.h))

        # Return new EMSs
        return EMSs

    def get_rectangle(self):
        return None # Rectangle((self.x, self.y), self.w, self.h, color="black", fill=True, alpha=.1)
