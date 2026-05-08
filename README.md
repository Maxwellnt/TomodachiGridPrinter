
# TomodachiGridPrinter (W.I.P)

Readme work in progress

Python module to automatically print a dissing from [Living the grid](https://living-the-grid.com/) using the JSON export feature.
This project support multiple controller emulation projects:

* Linux PC: [hannahbee91/nuxbt](https://github.com/hannahbee91/nuxbt) (Recommended)
* ESP32: [nullstalgia/UARTSwitchCon](https://github.com/nullstalgia/UARTSwitchCon) (Not Recommended)
  * I have a lot of miss inputs using it in my ESP32!
* And more coming in the future

This only have been tested in a linux machine

**Thanks to the Living the grid dev to implement the JSON feature.**

## Milestones to achieve

* Improve input optimization
* Improve print times until it matches Living the grid estimate time.
* Fix weird artifact found in large paintings
* Create a PyQt application for the user

## How to use it

Clone this repository, then create a python virtual environment (python 3.13 is recommended).
Activate the environment
Install pip packages:

```venv
pip install -r requirements.txt
```

For nuxbt:
```python3 -m gridprinter --controller="nuxbt" <json_path>```

For UARTSwitchCon (ESP32):
```python3 -m gridprinter --controller="urat" <json_path>```

For a dry run without controllers:
```python3 -m gridprinter --controller="dry-run" <json_path>```

* First, the program will ask if you are in the current canvas you want to use; use your normal controller to navigate the Palette House menu.
* Secondly, it will ask to turn off your controller once inside the canvas screen.
* Then it will ask if the controller has been selected
* Finally, the program will ask if you want to restore the canvas. This is used if the program fails so you can restore the canvas to the original state.

## How the printing process is actually done

First the script selects the first 9 colors the JSON has in the in-game color palette, then it starts printing.
The printing is done with a zig-zag pattern (right to left), skipping rows if there are no pixels or no pixels with the current selected palette.
