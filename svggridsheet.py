#!/usr/bin/env python3

# Generate SVG Grid Images
# Written in 2015 by Jordan Vaughan
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

import argparse
import datetime
from decimal import Decimal, getcontext
import math
import os.path
import sys

parser = argparse.ArgumentParser(description="Generate an SVG image of a grid.")
parser.add_argument("-n", "--no-vertical-lines", action="store_true", help="""disable vertical lines (creates an image suitable for ruled pages)""")
parser.add_argument("-p", "--public-domain-dedication", metavar="AUTHOR", default=None, help="""add a Creative Commons CC0 Public Domain Dedication to the generated image using the specified AUTHOR""")
parser.add_argument("-P", "--position", default="c", help="""the position of the grid, which can be "c" for centered, "ul" for the upper left corner, "ur" for the upper right corner, "bl" for the bottom left corner, and "br" for the bottom right corner""")
parser.add_argument("-r", "--precision", type=int, default=8, help="""numerical precision in digits (default: 8)""")
parser.add_argument("-t", "--thickness", type=Decimal, default=Decimal(0.25), help="""thickness of grid lines in mm (default: 0.25)""")
parser.add_argument("gridsize", type=Decimal, help="""the width and height of each grid square in mm""")
parser.add_argument("width", type=Decimal, help="""the width of the image in mm""")
parser.add_argument("height", type=Decimal, help="""the height of the image in mm""")
parser.add_argument("resolution", type=Decimal, help="""SVG pixels per mm""")

errors = False
def error(message):
  global errors
  sys.stderr.write(os.path.basename(sys.argv[0]) + ": error: " + message + "\n")
  errors = True

if __name__ == "__main__":
  try:
    args = parser.parse_args()
  except Exception:
    error("invalid command line arguments (invalid syntax?)")
    sys.exit(1)

  if args.precision <= 0:
    error("precision must be positive")
  if args.width <= 0:
    error("width cannot be zero or negative")
  if args.height <= 0:
    error("height cannot be zero or negative")
  if args.gridsize <= 0:
    error("grid square width and height cannot be zero or negative")
  if args.resolution <= 0:
    error("resolution cannot be zero or negative")
  if args.position not in {"ul", "ur", "c", "bl", "br"}:
    error("position is not valid")
  if args.thickness <= 0:
    error("thickness cannot be zero or negative")
  if errors:
    sys.exit(1)

  getcontext().prec = args.precision
  args.width *= args.resolution
  args.height *= args.resolution
  args.gridsize *= args.resolution
  args.thickness *= args.resolution

  sys.stdout.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" version="1.1" width="{0}" height="{1}">
  <title>Grid of {2}mm x {2}mm Squares</title>
  <desc>This is an image of a grid of {2}mm x {2}mm squares formatted for a {3}mm x {4}mm page (with no margins).""".format(args.width, args.height, args.gridsize / args.resolution, args.width / args.resolution, args.height / args.resolution))
  if args.public_domain_dedication:
    sys.stdout.write("""

Created on {0} by {1}.

To the extent possible under law, {1} has waived all copyright and related or neighboring rights to this image.  You can copy, modify, distribute and perform this image, even for commercial purposes, all without asking permission.  Please see &lt;http://creativecommons.org/publicdomain/zero/1.0/&gt; for more information.""".format(datetime.date.today(), args.public_domain_dedication.strip()))

  sys.stdout.write("""</desc>\n""")
  num_x = math.ceil(args.width / args.gridsize) + 1
  num_y = math.ceil(args.height / args.gridsize) + 1
  start_x = 0
  start_y = 0
  grid_width = args.gridsize * num_x
  grid_height = args.gridsize * num_y
  if args.position == "ur":
    start_x = args.width - grid_width
  elif args.position == "c":
    start_x = (args.width - grid_width) / 2
    start_y = (args.height - grid_height) / 2
  elif args.position == "bl":
    start_y = args.height - grid_height
  elif args.position == "br":
    start_x = args.width - grid_width
    start_y = args.height - grid_height
  sys.stdout.write('  <path d="M{0},{1}'.format(start_x, start_y))
  if not args.no_vertical_lines:
    for x in range(num_x + 1):
      sys.stdout.write("v{0}m{1},-{0}".format(grid_height, args.gridsize))
    sys.stdout.write('M{0},{1}'.format(start_x, start_y))
  for y in range(num_y + 1):
    sys.stdout.write("h{0}m-{0},{1}".format(grid_width, args.gridsize))
  sys.stdout.write('" stroke="#000" stroke-width="{0}" fill="none"/>\n'.format(args.thickness))
  sys.stdout.write("</svg>\n")
