# NewStroke TTF

A script to convert the NewStroke font used as the default KiCad font to TTF.

Original files: https://vovanium.ru/sledy/newstroke/en

TTF file: (will be here if I finish)

## Usage

How to use the script:

- Download and extract the [original files](https://vovanium.ru/sledy/newstroke/en).

- Create a python virtual environment and activate it.

```bash
python -m venv venv
```

Linux/MacOS:

```bash
. ./venv/bin/activate
```

Windows:

```bash
./venv/Scripts/activate
```

- Install dependencies

```bash
pip install -r requirements.txt
```

- Run the script

```bash
python main.py --charlist /path/to/charlist.txt --font_file /path/to/newstroke_font.h
```

The resulting file will be in `/master_ttf` named `NewStroke_W[width]_T[thickness].ttf`.

### Arguments:

**--charlist** (Required)

    The path to the `charlist.txt` file. This lists all symbols and is used to assign the glyphs to the correct characters.

**--font_file** (Required)

    The path to the `newstroke_font.h` or `newstroke_font.cpp` file. (They have the exact same contents.) This contains the character strokes encoded as characters that are decoded using the mappings in the `coord.txt` file.

**--width**

    Default: 1
    The horizontal scale of the characters relative to the height. 1 uses the original scale.

**--thickness**

    Default: 0.125
    The line thickness relative to the height. 1 is the same line thickness as the height (which is definitely not wanted). The minimum value is 0.01 and the maximum value is 0.25. Values from 0.05 to 0.25 should be mostly readable.
