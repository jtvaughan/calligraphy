#!/usr/bin/env python3

# Generate Italic calligraphy SVG images and OpenDocument documents according
# to the specified parameters.
#
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
import csv
from decimal import Decimal, InvalidOperation, getcontext
import os.path
import subprocess
import sys

default_description_format = ""
default_svg_filename_format = "italic-sheet-{nibwidth}mm-5degrees-5-5-5-7.{papersize}.svg"
default_fodt_filename_format = "italic-sheets-5degrees-5-5-5-7.{papersize}.fodt"
default_title_format = "Italic Calligraphy Practice Sheets ({papersize})"

errors = False
def error(message):
	global errors
	sys.stderr.write(os.path.basename(sys.argv[0]) + ": error: " + message + "\n")
	errors = True

def field_to_decimal(lineno, fieldno, field):
	try:
		return Decimal(field)
	except InvalidOperation as e:
		error("{0}: field {1} is not a number".format(lineno, fieldno))
		return Decimal(0)

class Paper(object):
	def __init__(self, lineno, width, height, margin, name):
		self.width = field_to_decimal(lineno, 1, width)
		self.height = field_to_decimal(lineno, 2, height)
		self.margin = field_to_decimal(lineno, 3, margin)
		self.name = name
		if self.width <= 0:
			error("{0}: width must be positive".format(lineno))
		if self.height <= 0:
			error("{0}: height must be positive".format(lineno))
		if self.margin < 0:
			error("{0}: margin must be positive or zero".format(lineno))
		if self.margin > self.width * Decimal(0.5):
			error("{0}: margin exceeds horizontal page dimensions (i.e., it's too large!)".format(lineno))
		if self.margin > self.height * Decimal(0.5):
			error("{0}: margin exceeds vertical page dimensions (i.e., it's too large!)".format(lineno))

parser = argparse.ArgumentParser(description="Generate SVG images of Italic calligraphy practice sheets and combine them into flat OpenDocument text files.  The dimensions and margins of each document's pages are read in tab-separated value (TSV) format from standard input, one page size per line.  Each line has four fields: page width in mm, page height in mm, margin in mm, and a nickname for the page type (e.g., letter or a4).  This program will generate a set of SVG images and an OpenDocument text file for each page size.")
parser.add_argument("-x", "--x-height", type=Decimal, default=Decimal(5), help="""set the x-height (distance between the baseline and the waistline) in nib widths (default is 5)""")
parser.add_argument("-c", "--cap-height", type=Decimal, default=Decimal(7), help="""set the cap height in nib widths (default is 7)""")
parser.add_argument("-a", "--ascender-height", type=Decimal, default=Decimal(5), help="""set the ascender height in nib widths (default is 5)""")
parser.add_argument("-d", "--descender-height", type=Decimal, default=Decimal(5), help="""set the descender height in nib widths (default is 5)""")
parser.add_argument("-l", "--pen-ladder", action="store_true", default=False, help="""add a pen ladder to each line""")
parser.add_argument("-s", "--slant-angle", type=Decimal, default=Decimal(90), help="""Generate slant guide lines with the specified angle from vertical in degrees, each separated by the box width (-w) (default is 90, which disables slant guide lines)""")
parser.add_argument("-w", "--box-width", type=Decimal, default=Decimal(3), help="""set the width of each practice box in nib widths (the distance between slant guide lines; default is 3; has no effect if -s is 90)""")
parser.add_argument("-p", "--public-domain-dedication", metavar="AUTHOR", default=None, help="""add a Creative Commons CC0 Public Domain Dedication to the generated image using the specified AUTHOR""")
parser.add_argument("-r", "--precision", type=int, default=8, help="""numerical precision in digits (default: 8)""")
parser.add_argument("-R", "--resolution", type=int, default=30, help="""SVG pixels per mm (default: 30)""")
parser.add_argument("-v", "--verbose", action="store_true", default=False, help="""print processing information on standard error""")
parser.add_argument("--baseline-thickness", type=Decimal, default=Decimal('0.25'), help="""the thickness of baselines in mm (default is 0.25)""")
parser.add_argument("--waistline-thickness", type=Decimal, default=Decimal('0.1'), help="""the thickness of waistlines in mm (default is 0.1)""")
parser.add_argument("--cap-line-thickness", type=Decimal, default=Decimal('0.25'), help="""the thickness of cap lines in mm (default is 0.25)""")
parser.add_argument("--cap-line-dash-length", type=Decimal, default=Decimal(0.5), help="""the length of the dashes in cap lines in nib widths (default is 0.5)""")
parser.add_argument("--ascender-descender-thickness", type=Decimal, default=Decimal('0.1'), help="""the thickness of ascender and descender lines in mm (default is 0.1)""")
parser.add_argument("--slant-line-thickness", type=Decimal, default=Decimal('0.1'), help="""the thickness of slant lines in mm (default is 0.1)""")
parser.add_argument("--description-format", default=default_description_format, help="""the format for the description of each OpenDocument text file (the public domain dedication, if any [see -p], is appended to this) (default is blank); use "{{papersize}}" where you'd like the document's paper size to appear""".format(default_description_format))
parser.add_argument("--fodt-filename-format", default=default_fodt_filename_format, help="""set the file name pattern for generated OpenDocument text files (default: {0}); use "{{papersize}}" where you'd like each document's paper size to appear; don't use spaces!""".format(default_fodt_filename_format))
parser.add_argument("--svg-filename-format", default=default_svg_filename_format, help="""set the file name pattern for generated SVG images (default: {0}); use "{{nibwidth}}" and "{{papersize}}" where you'd like each images's pen nib width and paper size to appear; don't use spaces!""".format(default_svg_filename_format))
parser.add_argument("--title-format", default=default_title_format, help="""the format for the title of each OpenDocument text file (default: {}); use "{{papersize}}" where you'd like the document's paper size to appear""".format(default_title_format))
parser.add_argument("nibwidth", type=Decimal, nargs="+", help="""pen nib width in mm""")

if __name__ == "__main__":
	try:
		args = parser.parse_args()
	except Exception:
		error("invalid command line arguments (invalid syntax?)")
		sys.exit(1)

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
	def test_format(format, format_name, *args, **kwargs):
		try:
			format.format(**kwargs)
		except KeyError as e:
			error("{} format string is invalid: it specifies an illegal key {{".format(format_name) + str(e) + """} (try doubling '{' and '}' characters to "{{" and "}}")""")
	test_format(args.description_format, "OpenDocument description", papersize="a4")
	test_format(args.svg_filename_format, "SVG file name", nibwidth=2, papersize="a4")
	test_format(args.fodt_filename_format, "OpenDocument text file name", papersize="a4")
	test_format(args.title_format, "OpenDocument title", papersize="a4")
	if any(nw <= 0 for nw in args.nibwidth):
		error("nib widths must be positive")
	if errors:
		sys.exit(1)
	if not args.nibwidth:
		sys.exit(0)

	getcontext().prec = args.precision

	def verbose(level, msg):
		if args.verbose:
			sys.stderr.write("=" + "=" * (level * 2) + " " + msg + "\n")
	verbose(0, "Reading paper dimensions, margins, and names from standard input")
	papers = []
	try:
		for lineno, line in enumerate(csv.reader(sys.stdin, delimiter="\t"), start=1):
			line = list(filter(None, line))
			if len(line) is 0:
				continue
			elif len(line) < 4:
				error("{0}: expected at least 4 fields, got {1}".format(lineno, len(line)))
			else:
				paper = Paper(lineno, line[0], line[1], line[2], line[3])
				papers.append(paper)
				verbose(1, paper.name + ": {0}mmx{1}mm with {2}mm margins".format(paper.width, paper.height, paper.margin))
	except csv.Error as e:
		error("stdin isn't a tab-delimited file")
	if errors:
		sys.exit(2)
	if not papers:
		sys.exit(0)

	verbose(0, "Generating files")
	for paper in papers:
		verbose(1, paper.name)
		imgwidth = paper.width - 2 * paper.margin
		imgheight = paper.height - 2 * paper.margin
		svgimages = []
		svgerrors = False
		verbose(2, "SVG images ({}mmx{}mm)".format(imgwidth, imgheight))
		for nibwidth in args.nibwidth:
			svgimage = args.svg_filename_format.format(nibwidth=nibwidth, papersize=paper.name)
			verbose(3, str(nibwidth) + "mm -- " + svgimage)
			if subprocess.call("svgitalicsheet.py -n {0} -x {args.x_height} -c {args.cap_height} -a {args.ascender_height} -d {args.descender_height} -s {args.slant_angle} {1}-w {args.box_width} {2}-r {args.precision} --baseline-thickness {args.baseline_thickness} --waistline-thickness {args.waistline_thickness} --cap-line-thickness {args.cap_line_thickness} --cap-line-dash-length {args.cap_line_dash_length} --ascender-descender-thickness {args.ascender_descender_thickness} --slant-line-thickness {args.slant_line_thickness} {3} {4} {5} >{6}".format(nibwidth, "-l " if args.pen_ladder else "", '-p "{}" '.format(args.public_domain_dedication) if args.public_domain_dedication else "", imgwidth, imgheight, args.resolution, svgimage, args=args), shell=True) != 0:
				error("svgitalicsheet.py failed for paper size {0} and nib width {1}".format(paper.name, nibwidth))
				svgerrors = True
			else:
				svgimages.append(svgimage)
		if svgerrors:
			error("skipping OpenDocument generation for paper size {} due to prior errors".format(paper.name))
		else:
			fodtfile = args.fodt_filename_format.format(papersize=paper.name)
			verbose(2, "OpenDocument file " + fodtfile)
			if subprocess.call("""fodtitalicsheets.py {}{} -t "{}" {} {} {} {} >{}""".format('-p "{}" '.format(args.public_domain_dedication) if args.public_domain_dedication else "", '-d "{}" '.format(args.description_format.format(papersize=paper.name)) if args.description_format else "", args.title_format.format(papersize=paper.name), paper.width, paper.height, paper.margin, " ".join(svgimages), fodtfile), shell=True) != 0:
				error("fodtitalicsheets.py failed for paper size {}".format(paper.name))
	if errors:
		verbose(0, "ERRORS!  Exiting...")
		sys.exit(2)
	verbose(0, "Done")

