from matplotlib.patches import Rectangle


class EmptyMaximalSpace:
    def __init__(self, x, y, w, h):
        # Set parameters
        self.x = x
        self.y = y
        self.w = w
        self.h = h

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
        # Top border
        lower_left_x, lower_left_y, lower_left_type = corners[0] # lower-left
        lower_right_x, lower_right_y, lower_right_type = corners[0] # lower-right
        upper_left_x, upper_left_y, upper_right_type = corners[0] # lower-left
        lower_left_x, lower_left_y, corner_type = corners[0] # lower-left

    def split_in_two(self, corner):
        # Get corner
        corner_x, corner_y, corner_type = corner

        # Relative to EMS
        rel_corner_x = corner_x - self.x
        rel_corner_y = corner_y - self.y

        # Create new empty maximal spaces
        EMS_1, EMS_2 = None, None
        if corner_type == "upper-right":
            EMS_1 = EmptyMaximalSpace(corner_x, self.y, self.w - rel_corner_x, self.h)
            EMS_2 = EmptyMaximalSpace(self.x, corner_y, self.w, self.h - rel_corner_y)
        elif corner_type == "lower-right":
            EMS_1 = EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_y)
            EMS_2 = EmptyMaximalSpace(corner_x, self.y, self.w - rel_corner_x, self.h)
        elif corner_type == "upper-left":
            EMS_1 = EmptyMaximalSpace(self.x, self.y, self.w - rel_corner_x, self.h)
            EMS_2 = EmptyMaximalSpace(self.x, corner_y, self.w, self.h - rel_corner_y)
        else:
            EMS_1 = EmptyMaximalSpace(self.x, self.y, rel_corner_x, self.h)
            EMS_2 = EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_y)
        
        # Return
        EMSs = (EMS_1, EMS_2)
        return EMSs

    def split_in_three(self, corner_1, corner_2):
        corner_1_x, corner_1_y, corner_1_type = corner_1
        corner_2_x, corner_2_y, corner_2_type = corner_2

        # Relative to EMS
        rel_corner_1_x = corner_1_x - self.x
        rel_corner_1_y = corner_1_y - self.y
        rel_corner_2_x = corner_2_x - self.x
        rel_corner_2_y = corner_2_y - self.y

        # Create new empty maximal spaces
        EMS_1, EMS_2, EMS_3 = None, None, None
        if corner_1_type == "upper-left" and corner_2_type == "upper-right":
            EMS_1 = EmptyMaximalSpace(self.x, self.y, rel_corner_1_x, self.h)
            EMS_2 = EmptyMaximalSpace(self.x, corner_1_y, self.w, self.h - rel_corner_1_y)
            EMS_3 = EmptyMaximalSpace(corner_2_x, self.y, self.w - rel_corner_2_x, self.h)
        elif corner_1_type == "lower-left" and corner_2_type == "lower-right":
            EMS_1 = EmptyMaximalSpace(self.x, self.y, self.w - rel_corner_1_x, self.h)
            EMS_2 = EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_1_y)
            EMS_3 = EmptyMaximalSpace(corner_2_x, self.y, self.w - rel_corner_2_x, self.h)
        elif corner_1_type == "lower-left" and corner_2_type == "upper-left":
            EMS_1 = EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_1_y)
            EMS_2 = EmptyMaximalSpace(self.x, self.y, rel_corner_1_x, self.h)
            EMS_3 = EmptyMaximalSpace(self.x, corner_2_y, self.w, self.h - rel_corner_2_y)
        elif corner_1_type == "lower-right" and corner_2_type == "upper-right":
            EMS_1 = EmptyMaximalSpace(self.x, self.y, self.w, rel_corner_1_y)
            EMS_2 = EmptyMaximalSpace(corner_1_x, self.y, self.w - rel_corner_1_x, self.h)
            EMS_3 = EmptyMaximalSpace(self.x, corner_2_y, self.w, self.h - rel_corner_2_y)

        # Return
        EMSs = (EMS_1, EMS_2, EMS_3)
        return EMSs

    def get_rectangle(self):
        return Rectangle((self.x, self.y), self.w, self.h, color="black", fill=True, alpha=.1)
        
