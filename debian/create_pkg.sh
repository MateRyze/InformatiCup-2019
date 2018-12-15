#!/bin/bash
SRCDIR='..'
PKGROOT='./kollektiv5'
mkdir -p $PKGROOT/usr/bin
mkdir -p $PKGROOT/usr/lib/python3/dist-packages
cp $SRCDIR/kollektiv5.py $PKGROOT/usr/bin/kollektiv5
cp -R $SRCDIR/kollektiv5gui $PKGROOT/usr/lib/python3/dist-packages/
dpkg-deb --build kollektiv5
