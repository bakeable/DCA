from matplotlib import pyplot as plt
import imageio
from .picking_area import PickingArea
from .empty_maximal_space import EmptyMaximalSpace
from constants import w_i, v_i

class Warehouse:
    def __init__(self, width, height, storage_capacities=[], order_sizes=[], animate=False):
        # Set variables
        self.W = width
        self.H = height

        # Given storage capacities and order sizes
        self.storage_capacities = storage_capacities
        self.order_sizes = order_sizes

        # Maximum number of aisles and cross_aisles
        self.n_max = min(30, round(width/w_i))
        self.k_max = min(10, round(height/v_i))

        # First EMS is complete warehouse
        self.EMS_list = [EmptyMaximalSpace(0, 0, width, height)]

        # Keep a list of PA positions
        self.PA_list = []

        # Metrics
        self.total_travel_distance = 0
        self.number_of_picking_areas = 0
        self.feasible = True

        # Chromosome
        self.chromosome = ""

        # Animation
        self.animate = animate
        self.frame = 0
        self.frame_files = []

    def reset(self):
        # Reset lists
        self.EMS_list = [EmptyMaximalSpace(0, 0, self.W, self.H)]
        self.PA_list = []

        # Reset metrics
        self.total_travel_distance = 0
        self.number_of_picking_areas = 0
        self.feasible = True

    def process(self, chromosome):
        # Reset
        self.reset()

        # Set chromosome
        self.chromosome = "-".join(str(x) for x in chromosome)

        # Determine number of picking areas
        N = round(len(chromosome) / 3)

        # Determine order
        order = chromosome[:N]
        aisles = chromosome[N:2 * N]
        cross_aisles = chromosome[2 * N:3 * N]

        for number in order:
            # Get index
            index = number - 1

            # Get number of aisles
            n = aisles[index]
            k = cross_aisles[index]
            s_i = self.storage_capacities[index]
            m = self.order_sizes[index]

            # Create picking area
            picking_area = PickingArea(s_i, n, k, m)

            # Insert picking area
            self.insert_picking_area(picking_area)

            if self.animate:
                # Draw animation frame
                self.draw(True)

        if self.animate:
            # Create animation
            self.create_animation()

        # Return travel distance and feasibility
        return self.total_travel_distance, self.feasible

    def determine_placement(self, picking_area):
        placement = (2*self.W, 2*self.H)
        for EMS in self.EMS_list:
            # Check if it fits
            width_fits = picking_area.w <= EMS.w
            height_fits = picking_area.h <= EMS.h

            # Check if it fits
            if width_fits and height_fits and placement[1] > EMS.y:
                placement = (EMS.x, EMS.y)

        return placement

    def insert_picking_area(self, picking_area, position=None):
        # Determine position
        if position is None:
            x, y = self.determine_placement(picking_area)
        else:
            x, y = position

        # Set position
        picking_area.set_position(x, y)

        # Check if position is feasible
        if self.feasible:
            self.feasible = picking_area.is_feasible(self.W, self.H)

        # Append to list of picking areas
        self.PA_list.append(picking_area)

        # Update EMS list
        self.update_ems_list(picking_area.x, picking_area.y, picking_area.w, picking_area.h)

        # Update metrics
        self.total_travel_distance = self.total_travel_distance + picking_area.y + picking_area.get_travel_distance()
        self.number_of_picking_areas = self.number_of_picking_areas + 1

    def update_ems_list(self, x, y, w, h):
        # Calculate corners lower-left, lower-right, upper-left, upper-right
        corners = [(x, y, 'lower-left'), (x + w, y, 'lower-right'), (x, y + h, 'upper-left'),
                   (x + w, y + h, 'upper-right')]

        new_EMS_list = []
        for EMS in self.EMS_list:
            # Count number of corner points within EMS
            contained_corners = EMS.get_contained_corners(corners)

            # If there are no corner points within the EMS, keep the old EMS
            if len(contained_corners) == 0:
                # Check if top border splits EMS
                if corners[2][0] == EMS.x and corners[3][0] == EMS.x + EMS.w:
                    # Create new EMS
                    EMS_1 = EmptyMaximalSpace(corners[2][0], corners[2][1], EMS.w, EMS.h - corners[2][1])

                    # Append to list
                    new_EMS_list.append(EMS_1)
                # Check if right border splits EMS
                elif corners[1][1] == EMS.y and corners[3][1] == EMS.y + EMS.h:
                    # Create new EMS
                    EMS_1 = EmptyMaximalSpace(corners[1][0], corners[1][1], EMS.w - (corners[1][x] - EMS.x), EMS.h)

                    # Append to list
                    new_EMS_list.append(EMS_1)
                else:
                    # Append to new list
                    new_EMS_list.append(EMS)

            # If there is one corner point within the EMS, it will be split into  two
            if len(contained_corners) == 1:
                # Split EMS into two new EMS
                EMS_1, EMS_2 = EMS.split_in_two(contained_corners[0])

                # Add to list
                new_EMS_list.append(EMS_1)
                new_EMS_list.append(EMS_2)

            # If there are two corner points within the EMS, it will be split into three
            if len(contained_corners) == 2:
                # Split EMS into three new EMS
                EMS_1, EMS_2, EMS_3 = EMS.split_in_three(contained_corners[0], contained_corners[1])

                # Add to list
                new_EMS_list.append(EMS_1)
                new_EMS_list.append(EMS_2)
                new_EMS_list.append(EMS_3)

        reduced_EMS_list = []
        child_index = 0
        # Reduce list by eliminating fully contained EMSs
        for EMS_child in new_EMS_list:
            # Set variables
            child_fits = False
            parent_index = 0

            # Check if it fits in any other EMS
            for EMS_parent in new_EMS_list:
                # Check if it fits
                left_fits = EMS_parent.left_border <= EMS_child.left_border <= EMS_parent.right_border
                right_fits = EMS_parent.left_border <= EMS_child.right_border <= EMS_parent.right_border
                bottom_fits = EMS_parent.bottom_border <= EMS_child.bottom_border <= EMS_parent.top_border
                top_fits = EMS_parent.bottom_border <= EMS_child.top_border <= EMS_parent.top_border

                # Check if it fits
                if not child_fits and child_index != parent_index:
                    child_fits = left_fits and right_fits and bottom_fits and top_fits

                # Increment index
                parent_index = parent_index + 1

            if not child_fits:
                reduced_EMS_list.append(EMS_child)

            # Increment index
            child_index = child_index + 1

        # Set reduced list
        self.EMS_list = reduced_EMS_list

        # Return list
        return self.EMS_list

    def draw(self, save=False):
        # Create figure
        plt.figure()

        # Set warehouse sizes
        plt.xlim([0, self.W])
        plt.ylim([0, self.H])

        # Get axis
        ax = plt.gca()

        # Plot EMSs
        for EMS in self.EMS_list:
            # Draw rectangle
            ax.add_patch(EMS.get_rectangle())

        # Plot picking areas
        for PA in self.PA_list:
            # Draw rectangle
            ax.add_patch(PA.get_rectangle())

        if save is False:
            # Show plot
            plt.show()
        else:
            # Create file name and append it to a list
            filename = f'animation/frames/{self.frame}.png'
            self.frame_files.append(filename)

            # Save frame
            plt.savefig(filename)
            plt.close()

            # Increment frame
            self.frame = self.frame + 1

    def create_animation(self, fps=2):
        # Build gif
        with imageio.get_writer('animation/finished/' + self.chromosome + '.gif', mode='I', fps=fps) as writer:
            for filename in self.frame_files:
                image = imageio.imread(filename)
                writer.append_data(image)

        # Reset
        self.frame = 0
        self.frame_files = []