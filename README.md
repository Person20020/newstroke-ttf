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
python main.py --font_file /path/to/newstroke_font.h
```

The resulting file will be in `/master_ttf` named `NewStroke_W[width]_T[thickness].ttf`.

### Arguments:

**--font_file** (Required)

    The path to the `newstroke_font.h` or `newstroke_font.cpp` file. (They have the exact same contents.) This contains the character strokes encoded as characters that are decoded using the mappings in the `coord.txt` file.

**--force**

    Skip hash check for font file. (Normally used as an easy way to verify the contents will be correct.) The script may fail in unexpected ways if the file is changed significantly.

**--width**

    Default: 1
    The horizontal scale of the characters. 1 uses the original scale. [0.5-2.0]

**--thickness**

    Default: 0.125
    The line thickness relative to the height. [0.01-0.25]

**--visualization**

    Enable stroke visualization using turtle graphics and disable font output.
