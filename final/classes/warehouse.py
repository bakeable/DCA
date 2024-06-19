import math
import numpy as np
# d
import imageio
from random import random
from .picking_area import PickingArea
from .empty_maximal_space import EmptyMaximalSpace
# from matplotlib.patches import Rectangle


class Warehouse:
    def __init__(self, width, height, storage_capacities=[], order_sizes=[], replenishments=[], w_i=1, v_i=1, penalty=10,
                 animate=False, save_history=True):
        # Set variables
        self.W = width
        self.H = height
        self.surface = self.W * self.H
        self.penalty = penalty

        # Given storage capacities and order sizes
        self.storage_capacities = storage_capacities
        self.order_sizes = order_sizes
        self.replenishments = replenishments

        # Maximum number of aisles and cross_aisles
        self.n_max = min(30, round(width / w_i))
        self.k_max = min(10, round(height / v_i))
        self.k_min = 2
        self.n_min = np.ceil(np.array(storage_capacities) / (self.H - v_i * 2))

        # Aisle sizes
        self.w_i = w_i
        self.v_i = v_i

        # First EMS is complete warehouse
        self.EMS_list = [EmptyMaximalSpace(0, 0, width, height)]

        # Keep a list of PA positions
        self.PA_list = []
        self.PA_colors = [(random() / 2, random(), random()) for x in storage_capacities]

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

        # History
        self.save_history = save_history
        self.EMS_history = []

    def reset(self):
        # Reset lists
        self.EMS_list = [EmptyMaximalSpace(0, 0, self.W, self.H)]
        self.EMS_history = []
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
        aisles = chromosome[N:(2 * N)]
        cross_aisles = chromosome[(2 * N):(3 * N)]

        # np.argsort converts the goncalves order to an array of indexes
        for index in np.argsort(order):
            # Get number from index
            number = index + 1

            # Get number of aisles, cross-aisles, storage capacity, order distribution and replenishment constant
            n = aisles[index]
            k = cross_aisles[index]
            s_i = self.storage_capacities[index]
            m = self.order_sizes[index]
            alpha = self.replenishments[index]
            color = self.PA_colors[index]

            # Create picking area
            picking_area = PickingArea(s_i, n, k, m, s_i, alpha, self.w_i, self.v_i, number, color)

            # Insert picking area
            self.insert_picking_area(picking_area)

            # If we choose to animate the placement, we set animate to True
            if self.animate:
                # Draw animation frame
                self.draw(True)

        # If we choose to animate the placement, we set animate to True
        if self.animate:
            # Create animation
            self.create_animation(fps=.5)

        # Return travel distance and feasibility
        return round(self.total_travel_distance, 2), self.feasible

    def determine_ems(self, picking_area):
        best_EMS = EmptyMaximalSpace(0, 0, math.inf, math.inf, in_warehouse=False)
        for EMS in self.EMS_list:
            # Check if it fits
            width_fits = picking_area.w <= EMS.w
            height_fits = picking_area.h <= EMS.h

            # Check if it fits
            if width_fits and height_fits and (EMS.y < best_EMS.y or not best_EMS.in_warehouse):
                best_EMS = EMS

        return best_EMS

    def insert_picking_area(self, picking_area):
        # Get best EMS
        EMS = self.determine_ems(picking_area)

        # Get position
        x, y = EMS.x, EMS.y

        # Set position
        picking_area.set_position(x, y)

        # Set EMS in which picking area will be fitted
        picking_area.EMS = EMS

        # Picking area is feasible if EMS is contained in the warehouse
        picking_area.feasible = EMS.in_warehouse
        if self.feasible:
            self.feasible = picking_area.feasible

        # Append to list of picking areas
        self.PA_list.append(picking_area)

        # Ignore PA if it is infeasible
        if picking_area.feasible:
            # Update EMS list
            self.update_ems_list(picking_area.x, picking_area.y, picking_area.w, picking_area.h)
        else:
            # Save EMS options to determine possible new strategies
            picking_area.EMS_options = self.EMS_list

            # Set initial penalty
            picking_area.penalty = self.penalty
            if picking_area.EMS.w < picking_area.w:
                picking_area.penalty = picking_area.penalty * (1 + picking_area.w - picking_area.EMS.w)

            if picking_area.EMS.h < picking_area.h:
                picking_area.penalty = picking_area.penalty * (1 + picking_area.h - picking_area.EMS.h)


        # Update metrics
        self.total_travel_distance = self.total_travel_distance + picking_area.get_travel_distance()
        self.number_of_picking_areas = self.number_of_picking_areas + 1

    def remove_last_picking_area(self):
        # Remove
        self.PA_list = self.PA_list[:-1]

        # Reset EMS
        if len(self.EMS_history) > 1:
            self.EMS_list = []
            # Create EMS list
            for tup in self.EMS_history[len(self.PA_list) - 1]:
                self.EMS_list.append(EmptyMaximalSpace(tup[0], tup[1], tup[2], tup[3]))

        else:
            self.EMS_list = [EmptyMaximalSpace(0, 0, self.W, self.H)]

        # Reset history
        self.EMS_history = self.EMS_history[len(self.PA_list) - 1:]

    def remove_infeasible_picking_areas(self):
        # Remove infeasible
        reduced_PA_list = []
        for PA in self.PA_list:
            if PA.feasible:
                reduced_PA_list.append(PA)

        # Set reduced PA list
        self.PA_list = reduced_PA_list

    def update_ems_list(self, x, y, w, h):
        # Calculate corners lower-left, lower-right, upper-left, upper-right
        corners = [(x, y, 'lower-left'), (x + w, y, 'lower-right'), (x, y + h, 'upper-left'),
                   (x + w, y + h, 'upper-right')]

        new_EMS_list = []
        for EMS in self.EMS_list:
            new_EMSs = []
            # Count number of corner points within EMS
            contained_corners = EMS.get_contained_corners(corners)

            # If there are no corner points within the EMS, keep the old EMS
            if len(contained_corners) == 0:
                # Get overlapping borders
                overlapping_borders = EMS.get_overlapping_borders(corners)
                if len(overlapping_borders) > 0:
                    # Split EMS
                    new_EMSs = EMS.split_by_borders(overlapping_borders)

                    # Add to list
                    for new_EMS in new_EMSs:
                        new_EMS_list.append(new_EMS)

                # Check if EMS is not equal to PA
                elif not EMS.is_equal_to(x, y, w, h):

                    # Append to new list
                    new_EMS_list.append(EMS)

            # If there is one corner point within the EMS, it will be split into  two
            if len(contained_corners) == 1:
                # Split EMS into two new EMS
                new_EMSs = EMS.split_in_two(contained_corners[0])

                # Add to list
                for new_EMS in new_EMSs:
                    new_EMS_list.append(new_EMS)

            # If there are two corner points within the EMS, it will be split into three
            if len(contained_corners) == 2:
                # Split EMS into three new EMS
                new_EMSs = EMS.split_in_three(contained_corners[0], contained_corners[1])

                # Add to list
                for new_EMS in new_EMSs:
                    new_EMS_list.append(new_EMS)

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

        # Save history
        if self.save_history:
            self.EMS_history.append([(EMS.x, EMS.y, EMS.w, EMS.h) for EMS in self.EMS_list])

        # Return list
        return self.EMS_list

    def get_total_ems(self):
        # Calculate total surface space left
        surface_space = 0

        # Iterate through EMSs
        for EMS in self.EMS_list:
            # Add to surface space
            surface_space = surface_space + EMS.w * EMS.h

        # Return
        return surface_space

    def get_PA_dimensions(self, ordered = False):
        # Instantiate dimensions
        dimensions = []

        # Order list
        pa_list = sorted(self.PA_list, key=lambda x: x.number) if ordered else self.PA_list

        # Get dimensions
        for PA in pa_list:
            dimensions.append((round(PA.x), round(PA.y, 2), int(PA.n), int(PA.k)))

        # Return
        return dimensions

    def draw(self, save=False, filename=None):
        return None
        # # Create figure
        # plt.figure()
        #
        # # Set warehouse sizes
        # plt.xlim([0, self.W])
        # plt.ylim([-.1 * self.H, self.H])
        #
        # # Get axis
        # ax = plt.gca()
        #
        # # Remove ticks
        # plt.tick_params(axis='both', which='both', bottom=False, top=False, labelbottom=False, right=False, left=False,
        #                 labelleft=False)
        #
        # # Plot EMSs
        # for EMS in self.EMS_list:
        #     # Draw rectangle
        #     ax.add_patch(EMS.get_rectangle())
        #
        # # Plot picking areas
        # for PA in self.PA_list:
        #     # Get rectangle
        #     rectangle = PA.get_rectangle()
        #
        #     # Annotate
        #     ax.add_artist(rectangle)
        #     rx, ry = rectangle.get_xy()
        #     cx = rx + rectangle.get_width() / 2
        #     cy = ry + rectangle.get_height() / 2
        #
        #     # Content
        #     content = PA.name + "\nn_" + str(PA.number) + "=" + str(round(PA.n)) + "\nk_" + str(PA.number) + "=" + str(
        #         round(PA.k))
        #
        #     # Place annotation
        #     ax.annotate(content, (cx, cy), color="black", weight="bold", fontsize=10, ha='center', va='center')
        #
        # # Plot docking doors
        # docking_doors = Rectangle((0, -.1 * self.H), self.W, .1 * self.H, color="black", fill=True, alpha=1)
        #
        # # Annotate
        # ax.add_artist(docking_doors)
        # rx, ry = docking_doors.get_xy()
        # cx = rx + docking_doors.get_width() / 2
        # cy = ry + docking_doors.get_height() / 2
        #
        # # Place annotation
        # ax.annotate("Docking doors", (cx, cy), color="white", weight="bold", fontsize=10, ha='center', va='center')
        #
        # # Save plot
        # if save is False:
        #     # Show plot
        #     plt.show()
        # else:
        #     # Create file name and append it to a list
        #     if filename is None:
        #         # Create frame
        #         filename = f'animation/frames/{self.frame}.png'
        #         self.frame_files.append(filename)
        #
        #         # Increment frame
        #         self.frame = self.frame + 1
        #
        #     # Save frame
        #     plt.savefig(filename)
        #     plt.close()

    def create_animation(self, fps=2):
        # Build gif
        return None
        # with imageio.get_writer('animation/finished/' + self.chromosome + '.gif', mode='I', fps=fps) as writer:
        #     for filename in self.frame_files:
        #         image = imageio.imread(filename)
        #         writer.append_data(image)
        #
        # # Reset
        # self.frame = 0
        # self.frame_files = []
