# Combine multiple images into one.
#
# To install the Pillow module on Mac OS X:
#
# $ xcode-select --install
# $ brew install libtiff libjpeg webp little-cms2
# $ pip install Pillow
#

from __future__ import print_function
import os

from PIL import Image

files = [
  '~/Downloads/1.png',
  '~/Downloads/2.png',
  '~/Downloads/3.png',
  '~/Downloads/4.png']

result = Image.new("RGB", (128, 128))

for index, file in enumerate(files):
  path = os.path.expanduser(file)
  img = Image.open(path)
  img.thumbnail((64, 64), Image.ANTIALIAS)
  x = index // 2 * 64
  y = index % 2 * 64
  w, h = img.size
  print('pos {0},{1} size {2},{3}'.format(x, y, w, h))
  result.paste(img, (x, y, x + w, y + h))
  #result.thumbnail((64,64), Image.ANTIALIAS)
  size=[64,64,]
  result = result.resize(size)

result.save(os.path.expanduser('~/image.jpg'))