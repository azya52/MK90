#!/usr/bin/python

#
#	Grayscale image converter for mk90
#

from PIL import Image
import sys

im = Image.open(sys.argv[1])
colorCount = im.getextrema()[1]

if im.width!=120 or im.height!=64 or im.getbands()[0]!="P" or colorCount not in range(1,10):
	print("Image must be 120x64 grayscale with 2-10 clors")
	sys.exit(-1)	

pix = im.load()

outfile = ["\n\ncolor"+str(x)+":" for x in range(colorCount-1)]
outfile.append("\n\nlastColor:")

for y in range(0, round(im.height/2)):
	outfile = [x+"\n    .word " for x in outfile]
	x = 0
	while x < im.width:
		currentWord = [0]*(colorCount)
		for i in range(8):
			currentWord = [(x << 1 & 0xFFFF) for x in currentWord]
			currentPixel = pix[x+i, y+im.height/2]
			for k in range(currentPixel,colorCount):
				currentWord[k] |= 0x0100
			currentPixel = pix[x+i, y]
			for k in range(currentPixel,colorCount):
				currentWord[k] |= 0x0001
		for k in range(colorCount):
			outfile[k] += str(currentWord[k])+", "
		x += 8

with open(sys.argv[1].split(".")[0]+'.mac', 'w', encoding='utf-8') as f:
	for color in outfile:
		f.write(color)
	f.close()