#!/usr/bin/env python3

# Combine SVG Images of Italic Practice Sheets into an OpenDocument Document
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
import base64
import datetime
from decimal import Decimal
import math
import os.path
import sys

parser = argparse.ArgumentParser(description="Combine images of Italic calligraphy practice sheets into a single OpenDocument file.  Note that this program does not verify that the specified images will fit and retain their aspect ratios within the specified page dimensions: You must verify that yourself.  The generated flat OpenDocument file is printed on standard output.")
parser.add_argument("-d", "--description", default="", help="""description of the file (added before the public domain dedication [see -p], if any; default is blank)""")
parser.add_argument("-p", "--public-domain-dedication", metavar="AUTHOR", default=None, help="""add a Creative Commons CC0 Public Domain Dedication to the generated image using the specified AUTHOR""")
parser.add_argument("-t", "--title", default="Italic Calligraphy Practice Sheets", help="""the document's title in its metadata (default: "Italic Calligraphy Practice Sheets")""")
parser.add_argument("-u", "--units", default="mm", help="""units used for page and margin dimensions (can be any unit suffix recognized by the OpenDocument standard; default: mm)""")
parser.add_argument("width", type=Decimal, help="""the width of the page""")
parser.add_argument("height", type=Decimal, help="""the height of the page""")
parser.add_argument("margin", type=Decimal, help="""the width of page margins""")
parser.add_argument("sheetimage", nargs="+", help="""a list of SVG images of Italic calligraphy practice sheets""")

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

	if args.width <= 0:
		error("width must be positive")
	if args.height <= 0:
		error("height must be positive")
	if args.margin < 0:
		error("margin must be positive or zero")
	if args.margin > args.width * Decimal(0.5):
		error("margin exceeds horizontal page dimensions (i.e., it's too large!)")
	if args.margin > args.height * Decimal(0.5):
		error("margin exceeds vertical page dimensions (i.e., it's too large!)")
	if args.units not in {"mm", "cm", "m", "km", "pt", "pc", "inch", "ft", "mi"}:
		error("unrecognized units: must be one of mm, cm, m, km, pt, pc, inch, ft, or mi")
	if errors:
		sys.exit(1)
	if not args.sheetimage:
		sys.exit(0)

	imgwidth = args.width - 2 * args.margin
	imgheight = args.height - 2 * args.margin
	now = datetime.datetime.today()
	sys.stdout.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" office:version="1.2" office:mimetype="application/vnd.oasis.opendocument.text">
	<office:meta>
		<meta:creation-date>{0}</meta:creation-date>
		<dc:description>{1}Pages are {2}{5}x{3}{5} with {4}{5} margins.""".format(now.strftime("%FT%TZ"), "{0}\n\n".format(args.description) if args.description else "", args.width, args.height, args.margin, args.units))
	if args.public_domain_dedication:
		sys.stdout.write("""

Created on {0} by {1}.

To the extent possible under law, {1} has waived all copyright and related or neighboring rights to this image.  You can copy, modify, distribute and perform this image, even for commercial purposes, all without asking permission.  Please see &lt;http://creativecommons.org/publicdomain/zero/1.0/&gt; for more information.""".format(now.strftime("%F"), args.public_domain_dedication.strip()))
	sys.stdout.write("""</dc:description>
		<dc:title>{0}</dc:title>
		<dc:date>{1}</dc:date>
	</office:meta>
	<office:styles>
		<style:style style:name="Standard" style:family="paragraph" style:class="text"/>
		<style:style style:name="Graphics" style:family="graphic">
			<style:graphic-properties text:anchor-type="paragraph" svg:x="0mm" svg:y="0mm" style:wrap="dynamic" style:number-wrapped-paragraphs="no-limit" style:wrap-contour="false" style:vertical-pos="top" style:vertical-rel="paragraph" style:horizontal-pos="center" style:horizontal-rel="paragraph"/>
		</style:style>
	</office:styles>
	<office:automatic-styles>
		<style:style style:name="P1" style:family="paragraph" style:parent-style-name="Standard">
			<style:paragraph-properties fo:break-before="page"/>
		</style:style>
		<style:style style:name="fr1" style:family="graphic" style:parent-style-name="Graphics">
			<style:graphic-properties style:mirror="none"/>
		</style:style>
		<style:page-layout style:name="pm1">
			<style:page-layout-properties fo:page-width="{2}{5}" fo:page-height="{3}{5}" fo:margin-top="{4}{5}" fo:margin-bottom="{4}{5}" fo:margin-left="{4}{5}" fo:margin-right="{4}{5}"/>
		</style:page-layout>
	</office:automatic-styles>
	<office:master-styles>
		<style:master-page style:name="Standard" style:page-layout-name="pm1"/>
	</office:master-styles>
	<office:body>
		<office:text>\n""".format(args.title, now.strftime("%FT%TZ"), args.width, args.height, args.margin, args.units))

	def add_image(path, imgno, paragraph_style):
		sys.stdout.write("""			<text:p text:style-name="{0}"><draw:frame draw:style-name="fr1" draw:name="n{1}" text:anchor-type="paragraph" svg:width="{2}{4}" svg:height="{3}{4}" draw:z-index="0"><draw:image><office:binary-data>""".format(paragraph_style, imgno, imgwidth, imgheight, args.units))
		data = None
		try:
			with open(path, "rb") as imgfile:
				data = imgfile.read()
		except OSError as e:
			error("unable to read " + path + ": " + e.strerror)
		if data:
			sys.stdout.write(str(base64.b64encode(data), encoding="UTF-8"))
		sys.stdout.write("""</office:binary-data></draw:image></draw:frame></text:p>\n""")
	for index, path in enumerate(args.sheetimage):
		add_image(path, index, "Standard" if index is 0 else "P1")

	sys.stdout.write("""		</office:text>
	</office:body>
</office:document>\n""")

	if errors:
		sys.exit(2)

