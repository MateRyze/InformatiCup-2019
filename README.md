# Submission for [InformatiCup 2018/2019](https://gi.de/informaticup/)
*Read in other language: [German](https://github.com/MateRyze/InformatiCup-2019/blob/master/README.de.md)*

## Description
The goal of this competition was to fool a traffic sign recognition system with generated images, that do not look like any traffic signs. 

## Example
This tool implements an evolutionary algorithm to generate these images. For example the generated image ![example result](https://github.com/MateRyze/InformatiCup-2019/blob/master/results/polygons_preset_2_example.png "example result") 
has been recognized as
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Zeichen_222_-_Vorgeschriebene_Vorbeifahrt%2C_Rechts_vorbei%2C_StVO_2017.svg/2000px-Zeichen_222_-_Vorgeschriebene_Vorbeifahrt%2C_Rechts_vorbei%2C_StVO_2017.svg.png" width="64" height="64">

## Getting Started

### Debian Package (dpkg)

Create a debian package with `dpkg-deb` and install on debian based system:

```sh
$ cd debian
$ ./create_pkg.sh
$ apt install ./kollektiv5.deb
```
Start the program `kollektiv5` from start menu (or equivalent).
### Manual Installation

Needs Python 3.6, install dependencies with `pip`:

```sh
$ pip3 install -r requirements.txt
```
Start the program by executing:

```sh
$ python3 kollektiv5.py
```
### Image Generation
**Important: This implementation uses the API from the [GI](https://gi.de/informaticup/), that will be shut down in the future**  
* (Optional: Enter API key)
* Select classes (traffic signs) or generate any classes
* Select generation method and presets or select options
* Start generation

![image generation](https://github.com/MateRyze/InformatiCup-2019/blob/master/results/gui_generation.png "Generation")


## Testing
Run unit tests for the EA generator: 
```sh
$ python3 -m unittest -v kollektiv5gui/tests/test_ea_generator.py
```


