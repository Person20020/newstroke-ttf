import argparse
import os
import time
import turtle
from hashlib import sha256

# File hashes
newstroke_font_file_hash = (
    "e40d317d8b212d41e7a076a5823cec3656e373d06cf5646fb6c24795aed1675d"
)

CHAR_HEIGHT = 400


def float_range(min_val, max_val):
    def checker(value):
        try:
            f = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"must be a number between {min_val} and {max_val}."
            )
        if f < min_val or f > max_val:
            raise argparse.ArgumentTypeError(
                f"must be between {min_val} and {max_val}."
            )
        return f

    return checker


# Handle arguments
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False
)
parser.epilog = "Example usage: python main.py --charlist ./charlist.txt --font_file ./newstroke_font.h"
# Input files (Required)
input_files_group = parser.add_argument_group("input files")
input_files_group.title = "Input Files (Required)"
input_files_group.add_argument(
    "--charlist", required=True, help="Input file containing character list."
)
input_files_group.add_argument(
    "--font_file",
    required=True,
    help="Input file containing character path strings.",
)

# Options
options_group = parser.add_argument_group("options")
options_group.title = "Options"
options_group.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="Skip hash checks for charlist and font file.",
)
options_group.add_argument(
    "-h",
    "--help",
    action="help",
    help="Show this help message and exit.",
)
options_group.add_argument(
    "-w",
    "--width",
    type=float_range(0.5, 2.0),
    default=1.0,
    help="Horizontal scale of characters.",
)
options_group.add_argument(
    "-t",
    "--thickness",
    default=0.125,
    type=float_range(0.01, 0.25),
    help="Stroke thickness relative to character height.",
)

args = parser.parse_args()

font_file = args.font_file
thickness = args.thickness * CHAR_HEIGHT / 2

if not os.path.isfile(font_file):
    print(f"Font file '{font_file}' not found.")
    exit(1)
font_file = os.path.expanduser(font_file)

# Verify source file hashe
if not args.force:
    with open(font_file, "rb") as f:
        if sha256(f.read()).hexdigest() != newstroke_font_file_hash:
            print(
                "Font file hash does not match expected value. If the file has been modified the script may not work properly, however, the --force flag can be used to skip this check."
            )
            exit(1)

# Load font data
with open(font_file, "r") as f:
    lines = f.readlines()

font_path_strings = []

for line in lines:
    line = line.strip()
    if line.startswith('"'):
        if line.endswith('",'):
            font_path_strings.append(line[1:-2].replace("\\\\", "\\"))
        if line.endswith("*/"):
            while len(line) > 0:
                line = line[:-1]
                if line.endswith('",'):
                    font_path_strings.append(line[1:-2].replace("\\\\", "\\"))
                    continue


# Convert character to coordinate
def get_char_coord(char):
    center_char = "R"
    step_size = CHAR_HEIGHT / 2 * 0.05
    return float(ord(char) - ord(center_char)) * step_size


# Get strokes for character
def get_char_strokes(string):
    # Returns a tuple containing a list of strokes and a list containing the left and right bounds.
    # Validate string length
    if len(string) < 2:
        # Character path string is less than 2 characters long
        return (None, "too_short")
    if len(string) % 2 != 0:
        # Character string length is uneven and therefore has unpaired coordinates
        print(f"String: '{string}'")
        print(f"Length: {len(string)}")
        return (None, "uneven_length")
    # Get char bounds
    left_bound = get_char_coord(string[0]) * args.width
    right_bound = get_char_coord(string[1]) * args.width

    strokes = []
    last_coord = None

    i = 2
    while i < len(string):
        if string[i : i + 2] == " R":
            last_coord = None
        else:
            current_coord = [
                get_char_coord(string[i]) * args.width,
                -get_char_coord(string[i + 1]),
            ]
            if last_coord is not None:
                strokes.append((last_coord, current_coord))
            last_coord = current_coord
        i += 2

    return (strokes, [left_bound, right_bound])


# Visualize characters using turtle graphics
def visualize_strokes(font_path_strings):
    wn = turtle.Screen()
    wn.bgcolor("gray")
    wn.title("Stroke Visualization")
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()

    for index, string in enumerate(font_path_strings):
        # if index + 32 < 169:
        #     continue

        strokes, bounds = get_char_strokes(string)
        if strokes is None or isinstance(bounds, str):
            print(f"Invalid character string: {bounds}")
            print(f"Character index: {index}")
            print(f"Character: {chr(index + 32)}")
            continue

        # Draw character bounds
        t.pencolor("red")
        t.pensize(int(0.005 * CHAR_HEIGHT))
        t.penup()
        t.goto((bounds[0], CHAR_HEIGHT / 2))  # Top left
        t.pendown()
        t.goto((bounds[1], CHAR_HEIGHT / 2))  # Top right
        t.goto((bounds[1], -CHAR_HEIGHT / 2))  # Bottom right
        t.goto((bounds[0], -CHAR_HEIGHT / 2))  # Bottom left
        t.goto((bounds[0], CHAR_HEIGHT / 2))  # Top left
        t.penup()

        # Draw strokes
        t.pencolor("black")
        t.pensize(int(thickness))
        for stroke in strokes:
            t.penup()
            t.goto(stroke[0][0], stroke[0][1])
            t.pendown()
            t.goto(stroke[1][0], stroke[1][1])

        time.sleep(1)
        t.clear()

    wn.bye()


try:
    visualize_strokes(font_path_strings)
except KeyboardInterrupt, turtle.Terminator:
    print("Visualization interrupted by user.")
    turtle.bye()
