#!/usr/bin/env python3

# Generate Italic Calligraphy Practice Sheet SVG Images
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

parser = argparse.ArgumentParser(description="Generate an SVG image of an Italic calligraphy practice sheet.")
parser.add_argument("-n", "--nib-width", type=Decimal, default=Decimal(2), help="""set the nib width in mm (default is 2)""")
parser.add_argument("-x", "--x-height", type=Decimal, default=Decimal(5), help="""set the x-height (distance between the baseline and the waistline) in nib widths (default is 5)""")
parser.add_argument("-c", "--cap-height", type=Decimal, default=Decimal(7), help="""set the cap height in nib widths (default is 7)""")
parser.add_argument("-a", "--ascender-height", type=Decimal, default=Decimal(5), help="""set the ascender height in nib widths (default is 5)""")
parser.add_argument("-d", "--descender-height", type=Decimal, default=Decimal(5), help="""set the descender height in nib widths (default is 5)""")
parser.add_argument("-s", "--slant-angle", type=Decimal, default=Decimal(90), help="""Generate slant guide lines with the specified angle from vertical in degrees, each separated by the box width (-w) (default is 90, which disables slant guide lines)""")
parser.add_argument("-l", "--pen-ladder", action="store_true", default=False, help="""add a pen ladder to each line""")
parser.add_argument("-w", "--box-width", type=Decimal, default=Decimal(3), help="""set the width of each practice box in nib widths (the distance between slant guide lines; default is 3; has no effect if -s is 90)""")
parser.add_argument("-p", "--public-domain-dedication", metavar="AUTHOR", default=None, help="""add a Creative Commons CC0 Public Domain Dedication to the generated image using the specified AUTHOR""")
parser.add_argument("-r", "--precision", type=int, default=8, help="""numerical precision in digits (default: 8)""")
parser.add_argument("--baseline-thickness", type=Decimal, default=Decimal('0.25'), help="""the thickness of baselines in mm (default is 0.25)""")
parser.add_argument("--waistline-thickness", type=Decimal, default=Decimal('0.1'), help="""the thickness of waistlines in mm (default is 0.1)""")
parser.add_argument("--cap-line-thickness", type=Decimal, default=Decimal('0.25'), help="""the thickness of cap lines in mm (default is 0.25)""")
parser.add_argument("--cap-line-dash-length", type=Decimal, default=Decimal(0.5), help="""the length of the dashes in cap lines in nib widths (default is 0.5)""")
parser.add_argument("--ascender-descender-thickness", type=Decimal, default=Decimal('0.1'), help="""the thickness of ascender and descender lines in mm (default is 0.1)""")
parser.add_argument("--slant-line-thickness", type=Decimal, default=Decimal('0.1'), help="""the thickness of slant lines in mm (default is 0.1)""")
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

	if args.nib_width <= 0:
		error("nib width cannot be zero or negative")
	if args.ascender_height <= 0:
		error("ascender height cannot be zero or negative")
	if args.descender_height <= 0:
		error("descender height cannot be zero or negative")
	if args.x_height <= 0:
		error("x-height cannot be zero or negative")
	if args.cap_height <= 0:
		error("cap height cannot be zero or negative")
	if args.precision <= 0:
		error("precision must be positive")
	if args.slant_angle < 0:
		error("slant angle cannot be negative")
	elif args.slant_angle > 90:
		error("slant angle cannot be greater than 90 degrees")
	elif args.slant_angle != 90 and args.box_width <= 0:
		error("box width cannot be zero or negative")
	if args.width <= 0:
		error("width cannot be zero or negative")
	if args.height <= 0:
		error("height cannot be zero or negative")
	if args.resolution <= 0:
		error("resolution cannot be zero or negative")
	if args.baseline_thickness <= 0:
		error("baseline thickness cannot be zero or negative")
	if args.waistline_thickness <= 0:
		error("x-height thickness cannot be zero or negative")
	if args.ascender_descender_thickness <= 0:
		error("ascender and descender thickness cannot be zero or negative")
	if args.cap_line_thickness <= 0:
		error("cap line thickness cannot be zero or negative")
	if args.slant_line_thickness <= 0:
		error("slant line thickness cannot be zero or negative")
	if args.cap_line_dash_length <= 0:
		error("cap line dash length cannot be zero or negative")
	if errors:
		sys.exit(1)

	getcontext().prec = args.precision
	slope = (-1 if args.slant_angle == 0 else (Decimal(math.tan(math.radians(Decimal(90) - args.slant_angle))) if args.slant_angle != 90 else 0))
	args.width *= args.resolution
	args.height *= args.resolution
	upper_height = args.ascender_height + args.x_height
	if upper_height < args.cap_height:
		upper_height = args.cap_height
	lower_height = args.descender_height
	letter_height = (upper_height + lower_height) * args.nib_width * args.resolution
	if slope > 0 and letter_height / slope > args.width:
		error("slant angle is too large for the specified image width: cannot fit even one letter box into the image")
	if letter_height > args.height:
		error("letter height is greater than the image's height: cannot fit even one letter box into the image")
	if errors:
		sys.exit(1)

	sys.stdout.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" version="1.1" width="{0}" height="{1}">
	<title>Italic Calligraphy Practice Sheet</title>
	<desc>This is an Italic calligraphy practice grid for nib widths of {2}mm.  {3}The x-height is {4} nib widths.  Ascenders are {5} nib widths, descenders are {6} nib widths, and the cap height is {7} nib widths.  This is formatted for a {8}mm x {9}mm page (with no margins).""".format(args.width, args.height, args.nib_width, """There are {:g}-degree slant guide lines every {} nib widths.  """.format(args.slant_angle, args.box_width) if slope != 0 else "", args.x_height, args.ascender_height, args.descender_height, args.cap_height, args.width / args.resolution, args.height / args.resolution))
	if args.public_domain_dedication:
		sys.stdout.write("""

Created on {0} by {1}.

To the extent possible under law, {1} has waived all copyright and related or neighboring rights to this image.  You can copy, modify, distribute and perform this image, even for commercial purposes, all without asking permission.  Please see &lt;http://creativecommons.org/publicdomain/zero/1.0/&gt; for more information.""".format(datetime.date.today(), args.public_domain_dedication.strip()))

	args.nib_width = args.nib_width * args.resolution
	args.box_width = args.box_width * args.nib_width
	args.x_height = args.x_height * args.nib_width
	args.ascender_height = args.ascender_height * args.nib_width
	args.descender_height = args.descender_height * args.nib_width
	args.cap_height = args.cap_height * args.nib_width
	args.baseline_thickness *= args.resolution
	args.waistline_thickness *= args.resolution
	args.ascender_descender_thickness *= args.resolution
	args.cap_line_thickness *= args.resolution
	args.slant_line_thickness *= args.resolution
	args.cap_line_dash_length *= args.nib_width
	cap_diff = args.ascender_height + args.x_height - args.cap_height

	sys.stdout.write("""</desc>\n	<defs>\n""")
	if args.pen_ladder:
		sys.stdout.write("""		<rect id="pl" width="{0}" height="{0}" fill="#000" stroke="none"/>\n""".format(args.nib_width))
	sys.stdout.write("""		<g id="l" stroke="#000">\n""")
	if slope == -1:
		# Vertical guide lines
		sl_str = """m{0},-{1}v{1}""".format(args.box_width, letter_height)
		sys.stdout.write("""			<path d="m0,0v{}""".format(letter_height))
		x = args.box_width
		while x <= args.width:
			sys.stdout.write(sl_str)
			x = x + args.box_width
		sys.stdout.write("""\" fill="none" stroke-width="{}"/>\n""".format(args.slant_line_thickness))
	elif slope > 0:
		# Slanted guide lines
		slopedlinewidth = letter_height / slope
		x_start = (slopedlinewidth / args.box_width - Decimal(int(slopedlinewidth / args.box_width))) * args.box_width
		sl_str = """m{0},-{1}l-{2},{1}""".format(args.box_width + slopedlinewidth, letter_height, slopedlinewidth)
		sys.stdout.write("			<path d=\"m{0},0l-{1},{2}".format(x_start, slopedlinewidth, letter_height))
		x = x_start + args.box_width
		end = args.width + slopedlinewidth
		while x < end:
			sys.stdout.write(sl_str)
			x = x + args.box_width
		sys.stdout.write("""\" fill="none" stroke-width="{}"/>\n""".format(args.slant_line_thickness))
	if cap_diff >= 0:
		sys.stdout.write("""			<line id="adl" x2="{0}" stroke-width="{5}"/>
			<line y1="{1}" x2="{0}" y2="{1}" stroke-width="{6}" stroke-dasharray="{7} {7}"/>
			<line y1="{2}" x2="{0}" y2="{2}" stroke-width="{8}"/>
			<line y1="{3}" x2="{0}" y2="{3}" stroke-width="{9}"/>
			<use xlink:href="#adl" y="{4}"/>\n""".format(args.width, cap_diff, args.ascender_height, args.ascender_height + args.x_height, letter_height, args.ascender_descender_thickness, args.cap_line_thickness, args.cap_line_dash_length, args.waistline_thickness, args.baseline_thickness))
	else:
		# Cap line is above the ascender line
		sys.stdout.write("""			<line id="cl" x2="{0}" stroke-width="{5}" stroke-dasharray="{6} {6}"/>
			<line y1="{1}" x2="{0}" y2="{1}" stroke-width="{7}"/>
			<line y1="{2}" x2="{0}" y2="{2}" stroke-width="{8}"/>
			<line y1="{3}" x2="{0}" y2="{3}" stroke-width="{9}"/>
			<use xlink:href="#cl" y="{4}"/>\n""".format(args.width, -cap_diff, args.ascender_height - cap_diff, args.cap_height, letter_height, args.cap_line_thickness, args.cap_line_dash_length, args.ascender_descender_thickness, args.waistline_thickness, args.baseline_thickness))
	if args.pen_ladder:
		pen_ladder_height = Decimal(int(upper_height) + int(lower_height)) * args.nib_width
		ladder_y_offset = (upper_height - Decimal(int(upper_height))) * args.nib_width
		ladder_y = Decimal(0)
		x = Decimal(0)
		while ladder_y < pen_ladder_height:
			sys.stdout.write("""			<use xlink:href="#pl" x="{}" y="{}"/>\n""".format((x % 2 - Decimal('0.5')) * args.nib_width, ladder_y_offset + ladder_y))
			x = x + Decimal(1)
			ladder_y = ladder_y + args.nib_width
	sys.stdout.write("""		</g>\n	</defs>\n""")

	y = Decimal(0)
	while y < args.height:
		sys.stdout.write("""	<use xlink:href="#l" y="{}"/>\n""".format(y))
		y = y + letter_height
	sys.stdout.write("</svg>\n")

