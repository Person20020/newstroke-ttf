# NewStroke TTF

A script to convert the NewStroke font used as the default KiCad font to TTF.

Original files: https://vovanium.ru/sledy/newstroke/en

TTF file: [download](https://github.com/Person20020/newstroke-ttf/releases/download/v0.1/NewStroke-W1.0_T0.125.ttf)

## Usage

### Fontforge script:

This script is run using [Fontforge](https://fontforge.org/en-US/). It uses actual curves for rounded parts which results in much cleaner edges and lower file sizes.

The script does output many errors but it does not appear to affect the quality of the glyphs.

Run the scrip with this command:
```bash
fontforge -lang=py -script fontforge-script.py /path/to/newstroke_font.h [-t --thickness=[0.01-0.25]] [-f --force]
```

The resulting file is saved as `./NewStroke-T[thickness].ttf`.

### Standalone script:

This script uses shapely to approximate the outline and results in somewhat jagged curves. The Fontforge script uses curves and does not loose quality in this way.

- Clone this repository:

```bash
git clone https://github.com/Person20020/newstroke-ttf.git
cd newstroke-ttf
```

- Download and extract the original files. ([link](https://vovanium.ru/sledy/newstroke/en))

- Create a python virtual environment and activate it.

Linux/MacOS:

```bash
python -m venv venv
. ./venv/bin/activate
```

Windows:

```bash
python -m venv venv
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

The resulting file will be in `/master_ttf` named `NewStroke-W[width]_T[thickness].ttf`.

### Arguments:

- `--font_file` (Required)

    The path to the `newstroke_font.h` or `newstroke_font.cpp` file. (They have the exact same contents.) This contains the character strokes encoded as characters.

- `--force`

    Skip hash check for font file. (Normally used as an easy way to verify the contents will be correct.) The script may fail in unexpected ways if the file is changed significantly.

- `--width`

    Default: 1
    The horizontal scale of the characters. 1 uses the original scale. [0.5-2.0]

- `--thickness`

    Default: 0.125
    The line thickness relative to the height. [0.01-0.25]

- `--visualization`

    Enable stroke visualization using turtle graphics and disable font output.
