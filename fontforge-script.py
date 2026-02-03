# This program should be run as a fontforge script.
# fontforge -lang=py -script fontforge-script.py /path/to/newstroke_font.h [-t --thickness=[0.01-0.25]] [-f --force]

import os
import re
import sys
from hashlib import sha256

import fontforge


class Colors:
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    RED = "\033[0;31m"
    YELLOW = "\033[1;33m"
    RESET = "\033[0m"


argv = sys.argv


CHAR_HEIGHT = 2048
font_source_file_hash = (
    "e40d317d8b212d41e7a076a5823cec3656e373d06cf5646fb6c24795aed1675d"
)


if len(argv) not in [2, 3, 4]:
    print(
        Colors.BLUE
        + "Usage:\n   fontforge -lang=py -script fontforge-script.py /path/to/newstroke_font.h [-t= --thickness=[0.01-0.25]] [-f --force]"
        + Colors.RESET
    )
    exit(1)

font_file = argv[1]

if not os.path.exists(font_file):
    print(
        Colors.RED
        + "Could not find newstroke_font file."
        + Colors.RESET
        + "\nUsage:\n"
        + Colors.BLUE
        + "   fontforge -lang=py -script fontforge-script.py /path/to/newstroke_font.h [-t= --thickness=[0.01-0.25]] [-f --force]"
        + Colors.RESET
    )
    exit(2)


thickness = 0.125
force = False
for i, arg in enumerate(argv):
    if i in [0, 1]:
        continue
    if arg.startswith("--thickness") or arg.startswith("-t"):
        try:
            thickness = float(arg.split("=", 1)[1])
        except Exception:
            print(
                Colors.RED
                + "Could not get thickness. Should be in format '-t=...' or '--thickness=...`"
                + Colors.RED
            )
            exit(1)
        if thickness > 0.25 or thickness < 0.01:
            print(
                Colors.RED + "Thickness should be between 0.01 and 0.25" + Colors.RESET
            )
            exit(2)
    elif arg == "--force" or arg == "-f":
        force = True
        print(Colors.YELLOW + "Skipping file hash check." + Colors.RESET)
    else:
        print(Colors.YELLOW + f"Unrecognized argument '{arg}'. Ignoring" + Colors.RESET)

# Verify file hash as an easy way to check
if not force:
    with open(font_file, "rb") as f:
        content = f.read()
        if not sha256(content).hexdigest() == font_source_file_hash:
            print(
                "Font file hash does not match expected value. If the file has been modified the script may not work properly, however, the --force flag can be used to skip this check."
            )
            exit(3)


# Load strings from font file
font_path_strings = []
with open(font_file, "r") as f:
    content = f.read()
    # Regex to find strings enclosed in double quotes. Then replace escaped backslashes. If string contains any characters not used as Hershey coordinates, it is discarded.
    for match in re.finditer(r'"((?:[^"\\]|\\.)*)"', content):
        s = match.group(1).replace("\\\\", "\\")
        if s == "newstroke_font.h":
            # Skip the import statement
            continue
        font_path_strings.append(s)


# Convert characters to coordinates
def get_char_coord(char):
    center_char = "R"
    scale = 1.05
    step_size = CHAR_HEIGHT / 2 * 0.05 * scale
    return float(ord(char) - ord(center_char)) * step_size


# Convert path strings to coordinates
def get_char_info(strings):
    start_char_code = 32
    char_info = []

    for index, string in enumerate(strings):
        left_bound = int(get_char_coord(string[0]))
        right_bound = int(get_char_coord(string[1]))

        strokes = []
        last_coord = None
        i = 2
        while i < len(string):
            chars = string[i] + string[i + 1]
            if chars == " R":
                last_coord = None
            else:
                coord = (get_char_coord(chars[0]), get_char_coord(chars[1]))
                if last_coord is not None:
                    strokes.append([coord, last_coord])
                last_coord = coord

            i += 2

        char_info.append(
            {
                "char_code": index + start_char_code,
                "left_bound": left_bound,
                "right_bound": right_bound,
                "strokes": strokes,
            }
        )
        # print(
        #     f"Char {index + start_char_code} ({chr(index + start_char_code)}): left {left_bound}, right {right_bound}, strokes {len(strokes)}, strokes data: {strokes}"
        # )
    return char_info


char_info = get_char_info(font_path_strings)


def create_font():
    font = fontforge.font()
    font.familyname = "NewStroke"
    font.fontname = f"NewStrokeT{thickness:.3f}".replace(".", "_")
    font.fullname = f"NewStroke T{thickness:.3f}"
    font.encoding = "UnicodeFull"
    font.em = CHAR_HEIGHT

    font.version = "0.2"
    font.copyright = "Based on NewStroke (CC0) https://vovanium.ru/sledy/newstroke/en. Modifications © 2026 Koji Ino. Licensed under CC BY-SA 4.0"
    font.appendSFNTName(
        "English (US)",
        "License",
        "This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 "
        "International License. To view a copy of this license, visit "
        "http://creativecommons.org/licenses/by-sa/4.0/",
    )

    font.appendSFNTName(
        "English (US)", "License URL", "https://creativecommons.org/licenses/by-sa/4.0/"
    )

    font.appendSFNTName("English (US)", "Designer", "Koji Ino")

    for char in char_info:
        glyph = font.createChar(char["char_code"])
        glyph.width = char["right_bound"] - char["left_bound"]
        pen = glyph.glyphPen()
        for stroke in char["strokes"]:
            pen.moveTo(
                stroke[0][0] - char["left_bound"], -stroke[0][1] + CHAR_HEIGHT * 0.28
            )
            pen.lineTo(
                stroke[1][0] - char["left_bound"], -stroke[1][1] + CHAR_HEIGHT * 0.28
            )
            pen.endPath()

        pen = None

        glyph.round()
        glyph.stroke("circular", thickness * CHAR_HEIGHT / 2, cap="round", join="round")
        try:
            glyph.simplify(1)
            glyph.removeOverlap()
        except Exception as e:
            print(
                Colors.RED
                + f"Error removing overlap for char {chr(char['char_code'])}: {e}"
                + Colors.RESET
            )

        xmin, ymin, xmax, ymax = glyph.boundingBox()
        bbox_width = xmax - xmin

        glyph.left_side_bearing = int(xmin)
        glyph.width = char["right_bound"] - char["left_bound"]

    output_path = f"./NewStroke-T{thickness:.3f}.ttf"
    font.generate(output_path)
    font.close()
    print(Colors.GREEN + f"Generated font at '{output_path}'" + Colors.RESET)


create_font()
