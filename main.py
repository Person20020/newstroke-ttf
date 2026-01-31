import argparse
import os
import time
import turtle
from hashlib import sha256

import defcon
import shapely
from colorama import Fore, Style
from fontmake.font_project import FontProject

# File hashes
newstroke_font_file_hash = (
    "e40d317d8b212d41e7a076a5823cec3656e373d06cf5646fb6c24795aed1675d"
)

CHAR_HEIGHT = 2048


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
parser.epilog = "Example usage: python main.py --font_file ./newstroke_font.h"
# Input files (Required)
input_files_group = parser.add_argument_group("input files")
input_files_group.title = "Input Files (Required)"
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
    help="Skip hash check for font file.",
)
options_group.add_argument(
    "-h",
    "--help",
    action="help",
    help="Show this help message and exit.",
)
options_group.add_argument(
    "-t",
    "--thickness",
    default=0.125,
    type=float_range(0.01, 0.25),
    help="Stroke thickness relative to character height.",
)
options_group.add_argument(
    "-w",
    "--width",
    type=float_range(0.5, 2.0),
    default=1.0,
    help="Horizontal scale of characters.",
)
options_group.add_argument(
    "--visualization",
    action="store_true",
    help="Enable stroke visualization using turtle graphics and disable font output.",
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
print(Fore.BLUE + "Loading font data..." + Style.RESET_ALL)
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
print(
    Fore.GREEN
    + f"Loaded {len(font_path_strings)} character path strings."
    + Style.RESET_ALL
)


# Convert character to coordinate
def get_char_coord(char):
    center_char = "R"
    step_size = CHAR_HEIGHT / 2 * 0.0525
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


# Convert strokes to outlines
def strokes_to_outline(strokes, char_width, thickness):
    shapes = []

    for stroke in strokes:
        # Transform the strokes to center the character for font
        stroke = (
            [
                (stroke[0][0] + char_width / 2),
                (stroke[0][1] + CHAR_HEIGHT * 3 / 10),
            ],
            [
                (stroke[1][0] + char_width / 2),
                (stroke[1][1] + CHAR_HEIGHT * 3 / 10),
            ],
        )
        line = shapely.geometry.LineString(stroke)
        outline = line.buffer(
            thickness / 2,
            cap_style="round",
            join_style="round",
        )
        shapes.append(outline)

    return shapely.unary_union(shapes)


# Draw glyphs
def draw_glyph(glyph, outline):
    pen = glyph.getPen()
    if outline.geom_type == "Polygon":
        polygons = [outline]
    else:
        polygons = outline.geoms

    for poly in polygons:
        exterior = list(poly.exterior.coords)
        pen.moveTo(exterior[0])
        for coord in exterior[1:]:
            pen.lineTo(coord)
        pen.closePath()

        for interior in poly.interiors:
            interior_coords = list(interior.coords)
            pen.moveTo(interior_coords[0])
            for coord in interior_coords[1:]:
                pen.lineTo(coord)
            pen.closePath()


# Generate UFO font
def generate_ufo(chars_strokes_list):
    font = defcon.Font()
    font.info.unitsPerEm = CHAR_HEIGHT * 0.9
    font.info.ascender = int(CHAR_HEIGHT * 0.7)
    font.info.descender = CHAR_HEIGHT * -0.2

    font.info.familyName = "NewStroke"
    font.info.styleName = f"W{args.width}_T{args.thickness}"
    font.info.fullName = f"NewStroke W{args.width} T{args.thickness}"
    font.info.postscriptFontName = f"NewStroke-W{args.width}-T{args.thickness}"

    notdef = font.newGlyph(".notdef")
    notdef.width = CHAR_HEIGHT // 2

    for index, char_strokes_bounds in enumerate(chars_strokes_list):
        char_code = index + 32
        glyph_name = f"uni{char_code:04X}"

        char_strokes, char_bounds = char_strokes_bounds
        char_width = abs(char_bounds[1] - char_bounds[0])

        glyph = font.newGlyph(glyph_name)
        glyph.unicode = char_code
        glyph.width = char_width

        if char_strokes is None:
            continue

        outline = strokes_to_outline(char_strokes, char_width, thickness)

        draw_glyph(glyph, outline)

    return font


# Visualization mode
if args.visualization:
    try:
        visualize_strokes(font_path_strings)
    except KeyboardInterrupt, turtle.Terminator:
        print("Visualization interrupted by user.")
        turtle.bye()
    exit(0)

# Run normally and generate font
char_strokes_list = []
for string in font_path_strings:
    char_strokes_list.append(get_char_strokes(string))

print(Fore.BLUE + "Generating UFO font..." + Style.RESET_ALL)
font = generate_ufo(char_strokes_list)
print(Fore.GREEN + "UFO font generation complete." + Style.RESET_ALL)

project = FontProject()
print(Fore.BLUE + "Building TTF font..." + Style.RESET_ALL)
project.build_ttfs(ufos=[font])
print(Fore.GREEN + "TTF font build complete." + Style.RESET_ALL)
