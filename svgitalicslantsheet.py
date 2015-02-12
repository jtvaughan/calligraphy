#!/usr/bin/env python3

# Generate Slant Guide Lines for Italic Calligraphy Guide Sheets
# Written in 2014 by Jordan Vaughan
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

parser = argparse.ArgumentParser(description="""Generate an SVG image of long lines slanting at the specified angle.  Printed copies of the image can be used as guide sheets while writing with an italic hand on ruled or grid paper.""")
parser.add_argument("-p", "--public-domain-dedication", metavar="AUTHOR", default=None, help="""add a Creative Commons CC0 Public Domain Dedication to the generated image using the specified AUTHOR""")
parser.add_argument("-r", "--precision", type=int, default=8, help="""numerical precision in digits (default: 8)""")
parser.add_argument("-t", "--thickness", type=Decimal, default=Decimal('0.2'), help="""the slanted lines' thickness in mm (default is 0.2)""")
parser.add_argument("angle", type=Decimal, help="""the angle of each guide line clockwise from vertical in degrees (must be in [0,90))""")
parser.add_argument("space", type=Decimal, help="""the horizontal distance between slanted lines in mm""")
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
	if args.angle < 0:
		error("angle cannot be negative")
	elif args.angle > 90:
		error("angle must be less than 90 degrees")
	if args.space <= 0:
		error("space must be positive")
	if args.width <= 0:
		error("width cannot be zero or negative")
	if args.height <= 0:
		error("height cannot be zero or negative")
	if args.resolution <= 0:
		error("resolution cannot be zero or negative")
	if args.thickness <= 0:
		error("line thickness must be positive")
	if errors:
		sys.exit(1)

	getcontext().prec = args.precision

	sys.stdout.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" version="1.1" width="{0}" height="{1}">
	<title>Italic Calligraphy Slant Line Guide Sheet</title>
	<desc>This is an Italic calligraphy guide sheet with slant lines at {2} degrees every {3}mm.  This is formatted for a {4}mm x {5}mm page (with no margins).""".format(args.width * args.resolution, args.height * args.resolution, args.angle, args.space, args.width, args.height))
	if args.public_domain_dedication:
		sys.stdout.write("""

Created on {0} by {1}.

To the extent possible under law, {1} has waived all copyright and related or neighboring rights to this image.  You can copy, modify, distribute and perform this image, even for commercial purposes, all without asking permission.  Please see &lt;http://creativecommons.org/publicdomain/zero/1.0/&gt; for more information.""".format(datetime.date.today(), args.public_domain_dedication.strip()))

	slope = (-1 if args.angle == 0 else Decimal(math.tan(math.radians(Decimal(90) - args.angle))))
	args.width *= args.resolution
	args.height *= args.resolution
	args.space *= args.resolution
	args.thickness *= args.resolution

	sys.stdout.write("""</desc>\n""")
	if slope == -1:
		# Vertical guide lines
		sl_str = """v{0}m{1},-{0}""".format(args.height, args.space)
		x = 0
		end = args.width
		sys.stdout.write("""	<path d="m0,0v{}""".format(letter_height))
	else:
		# Slanted guide lines
		slant_width = args.height / slope
		sl_str = """l-{0},{1}m{2},-{1}""".format(slant_width, args.height, args.space + slant_width)
		x = args.space
		end = args.width + slant_width
	sys.stdout.write("""	<path d="m{0},0""".format(x))
	while x <= end:
		sys.stdout.write(sl_str)
		x += args.space
	sys.stdout.write("""\" stroke="#000" fill="none" stroke-width="{}"/>
</svg>\n""".format(args.thickness))

