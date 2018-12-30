# Kollektiv5

TODO

## Installation

### Per dpkg

TODO

```sh
$ cd debian
$ create_pkg.sh
$ apt install ./kollektiv5.deb
```

### Manuell

Mindestens Python 3.6 muss auf dem System installiert sein. Dann können die nötigen Pakete per `pip` installiert
werden.

```sh
$ pip3 install -r requirements.txt
```

Alternativ sind alle Abhängigkeiten auch über die Ubuntu Paketquellen verfügbar.

```sh
$ apt install python3 python3-requests python3-pyqt5 python3-pil
```

## Ausführen

TODO


## GUI mit Qt Designer bauen
### Konvertierung von .ui zu .py
Beispiel:
```sh
$ python -m PyQt5.uic.pyuic -x ./kollektiv5gui/views/ea_options_widget.ui -o ./kollektiv5gui/views/EaOptionsWidget.py
```
