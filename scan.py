#!/usr/bin/env python
import pyinsane.abstract as pyinsane
import subprocess
import tempfile
from PIL import Image
import os
import sys

if len(sys.argv) == 1:
  sessionName = raw_input("What filename will you give this session? [foo.png] ")
else:
  sessionName = sys.argv[1]

if sessionName == '':
  sessionName = 'foo.png'

pageNum = 0

devices = pyinsane.get_devices()

device = pyinsane.Scanner(name=devices[1].name)

dpi = 300
imgWidth = int(dpi * 8.5)
imgHeight = int(dpi * 11)
device.options['resolution'].value = dpi
device.options['mode'].value = 'Gray'

while True:
  session = device.scan(multiple=False)

  try:
    while True:
      session.scan.read()
  except EOFError:
    pass

  fh, tmpfile = tempfile.mkstemp()
  os.close(fh)
  output = "%s-%d.png"%(sessionName, pageNum)
  image = session.images[0]
  image.crop((0, 0, imgWidth, imgHeight)).save(tmpfile, "PNG")
  print "Wrote", tmpfile
  subprocess.call(['pngnq', tmpfile])
  subprocess.call(['pngcrush', tmpfile+'-nq8.png', output])
  print "Saved to", output
  doNext = raw_input("Next page? [Y/n] ").upper()
  pageNum += 1
  if doNext == "" or doNext == "Y":
    continue
  else:
    break

fnames = map(lambda x:"%s-%d.png"%(sessionName, x), xrange(0, pageNum))

subprocess.call(['convert', ] + fnames + [sessionName+'.pdf'])
for f in fnames:
  os.unlink(f)
print "Wrote %s.pdf"%(sessionName)
