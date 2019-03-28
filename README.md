# InformatiCup 2018/2019
Solution for the competition [InformatiCup 2018/2019](https://gi.de/informaticup/) 

*Read in other language: [German](https://github.com/MateRyze/InformatiCup-2019/blob/master/README.de.md)*

## Getting Started

### Debian Package (dpkg)

Create a debian package with `dpkg-deb` and install on debian based system:

```sh
$ cd debian
$ create_pkg.sh
$ apt install ./kollektiv5.deb
```
Start the program `kollektiv5` from start menu (or equivalent).
### Manual Installation

Needs Python 3.6, install dependencies with `pip`:

```sh
$ pip install -r requirements.txt
```
Start the program by executing:

```sh
$ python kollektiv5.py
```
### Image Generation

* Enter API key
* Select classes (traffic signs)
* Select generation method and presets or options
* Start generation

## Testing
Run unit tests for the EA generator: 
```sh
$ python -m unittest -v kollektiv5gui/tests/test_ea_generator.py
```

