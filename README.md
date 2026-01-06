# Inkscape-guitar-plan
## What it is
An Python script that turns fretted string instrument geometry into precise vector drawings for Inkscape.

It automate top-view drawing of:
- Fretboard
- Nut
- Scale
- Symetric axis
- Fret's positions
- Strings

Then you can freely make your own body, headstock, etc.

## Why this project exists
As a guitar builder hobbyist, I need to laser cut template.
The available laser cutting machine around me support svg files, so
I used Inkscape, and then this script is born. 

## Project status
No update scheduled for now
but some idea, like drawing pickup template or drawing side-view

## How to run
**Note that you have to know basic stringed instrument's parameter to use the script efficiently**

1. Install Inkscape *I use Inkscape 1.2.2 (b0a8486541, 2022-12-01) on Ubuntu studio*
2. Install and set up `Simple Inkscape Scripting` [Official repo](https://github.com/spakin/SimpInkScr)
3. Go in `Extensions > Render > Simple Inkscape Scripting`
4. In the pop up, set the script in the `Python file` field
5. Add specific parameters in the `Python code` textfield *more details later*
6. Click on `Apply` and wait for the draw to appear.

Then, I strongly suggest to rename different path & object to keep it clear.

## Example
I'll put some example in the `example` folder.

## License
It is licensed under GNU GPL V3

## Special thanks
- Thanks to [Scott Pakin](https://inkscape.org/fr/~pakin/) for the `Inkscape Simple Scripting` extension
- Thanks to Inkscape teams