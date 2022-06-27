from classes import Warehouse
from .data_handling import read_instance
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import imageio
import os
from tqdm import tqdm
from pathlib import Path
import numpy as np


# Definitions
def create_image(im1, im2, im3=None, generation=0, child_no=1, mutation="", data={}):
    # All images are same sizes
    width = im1.width * 2
    height = im1.height * 2
    dst = Image.new('RGB', (width, height))

    # Draw on image
    draw = ImageDraw.Draw(dst)

    # Get font
    font = ImageFont.truetype("data/arial.ttf", 30)

    # Generation number
    draw.text((width/2 + 5, int(im2.height)*2 - 50), "Generation " + str(generation), (255, 255, 255), font=font)
    draw.text((width/2, int(im2.height)), mutation, (255, 255, 255), font=font)

    # Draw
    if im3 is not None:
        # Mother
        dst.paste(im1, (0, 0))
        draw.text((0, 0), "Mother, value: " + str(data["mother"][0]), (0, 0, 0), font=font)

        # Father
        dst.paste(im2, (0, im1.height))
        draw.text((0, im1.height), "Father, value: " + str(data["father"][0]), (0, 0, 0), font=font)

        # Child
        dst.paste(im3, (max(im1.width, im2.width), 0))
        draw.text((max(im1.width, im2.width), 0),
                  "Child " + str(int(child_no)) + ", value: " + str(data["child"][0]) + ", feasible: " + str(
                      data["child"][1]), (0, 0, 0), font=font)

    else:
        # Mother
        dst.paste(im1, (0, int(height / 2 - im1.height / 2)))
        draw.text((0, int(height / 2 - im1.height / 2)), "Mother, value: " + str(data["mother"][0]), (0, 0, 0),
                  font=font)

        # Child
        dst.paste(im2, (im1.width, 0))
        draw.text((im1.width, 0),
                  "Child " + str(int(child_no)) + ", value: " + str(data["child"][0]) + ", feasible: " + str(
                      data["child"][1]), (0, 0, 0), font=font)

    return dst


def draw_evolution(instances=None, remove_files=True):
    if instances is None:
        # Get all instances
        instances = []
        pathlist = Path("data/generations").glob("*.csv")
        for path in pathlist:
            # Convert to string
            path_in_str = str(path)

            # Get instance
            instances.append(int(path_in_str.split("inst").pop().split(".csv").pop(0)))

        # Sort instances
        instances = sorted(instances)
        print("Found", str(len(instances)), "instances")

    # Run all instances
    for instance in instances:
        print("\r\nProcessing instance", str(instance), "of", str(len(instances)))
        # Get generation data
        df = pd.read_csv("data/generations/inst" + str(instance) + ".csv")

        # Read variables from instance
        W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(instance)

        # Instantiate warehouse
        warehouse = Warehouse(W, H, S, u, alpha, animate=False, w_i=w_i, v_i=v_i)

        # Failsafe
        if len(df.index) == 0:
            print("\r\nInstance has no generations\r\n")
        else:
            # Iterate each rows
            print("\r\nProcessing all generations\r\n")
            for index in tqdm(range(len(df.index))):
                # Get row
                row = df.iloc[index]

                # Only draw father if there are two parents
                if row["mother"] == row["father"]:
                    types_to_draw = ["mother", "child"]
                else:
                    types_to_draw = ["mother", "father", "child"]

                # Dissect mutation
                description = "Mutations:"
                child = [float(x) if "." in str(x) else int(x) for x in row["child"].split("|")]
                mutation = [float(x) if "." in str(x) else int(x) for x in row["mutation"].split("|")]
                N = round(len(mutation)/3)

                # Order
                child_order = np.argsort(child[:N])
                original_child_order = np.argsort(np.array(child[:N]) + np.array(mutation[:N]))
                if "".join(str(x) for x in child_order) != "".join(str(x) for x in original_child_order):
                    description = description + "\r\nOrder changed from " + ">".join(str(x) for x in original_child_order) + " to " + ">".join(str(x) for x in child_order)

                # Aisles and cross-aisles
                aisles = np.array(mutation[N:2*N]).round(0)
                cross_aisles = np.array(mutation[2*N:3*N]).round(0)
                for i in range(N):
                    if int(cross_aisles[i]) > 0 or int(cross_aisles[i]) < 0 or int(aisles[i]) > 0 or int(aisles[i]) < 0:
                        description = description + "\r\nPA " + str(i)
                        if int(aisles[i]) < 0:
                            description = description + ", removed " + str(-1*int(aisles[i])) + " aisle(s)"
                        elif int(aisles[i]) > 0:
                            description = description + ", added " + str(int(aisles[i])) + " aisle(s)"

                        if int(cross_aisles[i]) < 0:
                            description = description + ", removed " + str(-1 * int(cross_aisles[i])) + " cross-aisle(s)"
                        elif int(cross_aisles[i]) > 0:
                            description = description + ", added " + str(int(cross_aisles[i])) + " cross-aisle(s)"

                # Draw
                processed = {"mother": (0, True), "father": (0, True), "child": (0, True)}
                for type_to_draw in types_to_draw:
                    # Get chromosome
                    chromosome = [float(x) if "." in str(x) else int(x) for x in row[type_to_draw].split("|")]

                    # Create image
                    processed[type_to_draw] = warehouse.process(chromosome)
                    warehouse.draw(save=True,
                                   filename=f'animation/frames/{type_to_draw}-{row["child_no"]}-{row["generation"]}.png')

                # Frame filename
                filename = 'animation/frames/concatenated/' + str(index) + ".png"

                # Concatenate images
                if row["mother"] == row["father"]:
                    mother_image = Image.open(f'animation/frames/mother-{row["child_no"]}-{row["generation"]}.png')
                    child_image = Image.open(f'animation/frames/child-{row["child_no"]}-{row["generation"]}.png')

                    # Create combined image
                    create_image(mother_image, child_image, generation=row["generation"], child_no=row["child_no"],
                                 mutation=description, data=processed).save(
                        filename)

                    # Remove
                    if remove_files:
                        os.remove(f'animation/frames/mother-{row["child_no"]}-{row["generation"]}.png')
                        os.remove(f'animation/frames/child-{row["child_no"]}-{row["generation"]}.png')
                else:
                    mother_image = Image.open(f'animation/frames/mother-{row["child_no"]}-{row["generation"]}.png')
                    father_image = Image.open(f'animation/frames/father-{row["child_no"]}-{row["generation"]}.png')
                    child_image = Image.open(f'animation/frames/child-{row["child_no"]}-{row["generation"]}.png')

                    # Create combined image
                    create_image(mother_image, father_image, child_image, generation=row["generation"],
                                 child_no=row["child_no"], mutation=description, data=processed).save(filename)

                    # Remove
                    if remove_files:
                        os.remove(f'animation/frames/mother-{row["child_no"]}-{row["generation"]}.png')
                        os.remove(f'animation/frames/father-{row["child_no"]}-{row["generation"]}.png')
                        os.remove(f'animation/frames/child-{row["child_no"]}-{row["generation"]}.png')

            print("\r\nAll generations have been processed\r\n")

            # Get all files
            filenames = []
            pathlist = Path("animation/frames/concatenated").glob("*.png")
            for path in pathlist:
                # Convert to string
                path_in_str = str(path.resolve())

                # Get instance
                filenames.append(path_in_str)

            # Sort filenames
            filenames = sorted(filenames, key=lambda x: int(x.split("/").pop().split(".").pop(0)))

            # Build gif
            with imageio.get_writer("animation/finished/inst" + str(instance) + ".gif", mode='I', fps=10) as writer:
                print("\r\nCreating GIF\r\n")
                for index in tqdm(range(len(filenames))):
                    # Get filename
                    filename = filenames[index]

                    # Get image
                    image = imageio.imread(filename)

                    # Write image
                    writer.append_data(image)

                    # Remove
                    if remove_files:
                        os.remove(filename)

                # Report
                print("\r\nCreated GIF")
