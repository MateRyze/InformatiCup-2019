# Kollektiv5

Dieses Tool implementiert einen evolutionären Algorithmus, mit dem Bilder generiert werden. Diese Bilder werden an ein Neuronales Netz gereicht, welches auf das Erkennen von Verkehrsschildern spezialisiert ist. Die generierten Bilder sehen allerdings keinem Verkehrsschild ähnlich und werden dennoch mit einer hohen Konfidenz erkannt.

Es ist möglich eine Menge von Klassen auszuwählen in die das generierte Bild fällt.

Die Software basiert auf Python 3.6 und nutzt PyQt5 als GUI Toolkit.

## Installation

### Per dpkg

Die Software kann per Skript in ein .deb Paket gepackt werden. Einizge
Vorraussetzung ist das Vorhandensein des `dpkg-deb` Tools. Da dieses ein Teil von `dpkg` ist, sollte es bereits auf jedem Debian basierten System vorhanden sein.

```sh
$ cd debian
$ create_pkg.sh
$ apt install ./kollektiv5.deb
```

Die nötigen Abhängigkeiten werden dann automatisch installiert. Unter Umständen werden
diese nicht bereitgestellt, falls ältere Repositories verwendet werden. Ubuntu 18.04
bietet alle Abhängigkeiten direkt an.

### Manuell

Mindestens Python 3.6 muss auf dem System installiert sein. Dann können die nötigen Pakete per `pip3` installiert werden.

```sh
$ pip3 install -r requirements.txt
```

## Ausführen

Bei der Installation via `dpkg` ist das Programm unter dem Bezeichner `kollektiv5` systemweit verfügbar und über das Startmenu der Desktopoberfläche zu finden. Hier ist es möglicherweise in die Kategorie `Accessories` einsortiert.

Bei manueller Installation muss lediglich die Datei `kollektiv5.py` ausgeführt werden.

## Generation von Bildern

TODO

## Einstellungen

TODO

## GUI mit Qt Designer bauen
### Konvertierung von .ui zu .py
Beispiel:
```sh
$ python -m PyQt5.uic.pyuic -x ./kollektiv5gui/views/ea_options_widget.ui -o ./kollektiv5gui/views/EaOptionsWidget.py
```
