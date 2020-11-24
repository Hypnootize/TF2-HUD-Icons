#!/usr/bin/python
# vim:ts=8:sw=4:expandtab:encoding=utf-8
'''Center glyphs.
Copyright <hashao2@gmail.com>  2008, Gumble <abcdoyle888@gmail.com> 2013-2014

#	   This program is free software; you can redistribute it and/or modify
#	   it under the terms of the GNU General Public License as published by
#	   the Free Software Foundation; either version 3 of the License, or
#	   (at your option) any later version.
#	   
#	   This program is distributed in the hope that it will be useful,
#	   but WITHOUT ANY WARRANTY; without even the implied warranty of
#	   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	   GNU General Public License for more details.
#	   
#	   You should have received a copy of the GNU General Public License
#	   along with this program; if not, write to the Free Software
#	   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	   MA 02110-1301, USA.

Put the file in $(PREFIX)/share/fontforge/python or ~/.FontForge/python, invoke
from "Tools->Metrics->Center in Glyph" after selected some glyphs.

'''
__version__ = '1.1'

import sys
import fontforge
import psMat

def center_glyph(glyph, vcenter=0, lbearing=15, rbearing=None):
	'''Center a glyph.'''
	# Shift width
	if not rbearing:
		rbearing = lbearing
	bounding = glyph.boundingBox() # xmin,ymin,xmax,ymax
	width = (bounding[2] - bounding[0])
	width_new = width+(lbearing+rbearing)
	glyph.width = width_new
	glyph.left_side_bearing = lbearing
	glyph.right_side_bearing = rbearing

	# Shift Height
	center_glyph_height(glyph, vcenter, bounding)

def center_glyph_height(glyph, vcenter, abound=None):
	bounding = abound or glyph.boundingBox() # xmin,ymin,xmax,ymax
	glyphcenter = (bounding[3] - bounding[1])/2+bounding[1]
	deltay = vcenter - glyphcenter

	matrix = psMat.translate(0, deltay)
	glyph.transform(matrix)
	
def CenterGlyph(junk, afont):
	'''Main function.'''
	center = (afont.ascent - afont.descent/2)/2

	# total 5% margin
	em = afont.ascent + afont.descent
	lbearing = int(em*0.05)

	for glyph in afont.selection.byGlyphs:
		center_glyph(glyph, center, lbearing)

def CenterHeight(junk, afont):
	'''Main function.'''
	center = (afont.ascent - afont.descent)/2

	for glyph in afont.selection.byGlyphs:
		bounding = glyph.boundingBox()
		if not [x for x in (bounding[1],bounding[3]) if abs(x-center)<center/2]:
			center_glyph_height(glyph, center)

def fit_glyph_plus(glyph, em, percent, wavg, havg):
	'''Scale a glyph horizontally to fit the width.'''
	bounding = glyph.boundingBox() # xmin, ymin, xmax, ymax
	gwidth = (bounding[2] - bounding[0])
	gheight = (bounding[3] - bounding[1])
	if not gwidth or not gheight:
		return
	rate = (em-min(wavg-gwidth, havg-gheight)*0.01)*percent/max(gwidth, gheight)
	if gwidth < 0.95*wavg and gheight < 0.95*havg:
		rate = (em-min(wavg-gwidth, havg-gheight)*0.6)*percent/max(gwidth, gheight)
	#print gwidth, rate, em
	if rate*max(gwidth, gheight) > em:
		rate = em*percent/max(gwidth, gheight)
	matrix = psMat.scale(rate)
	glyph.transform(matrix)

def box_fit_square(glyph, em, percent, wavg, havg):
	'''Scale a width horizontally to fit the average width.'''
	bounding = glyph.boundingBox() # xmin, ymin, xmax, ymax
	gwidth = (bounding[2] - bounding[0]) + 2*int(em*0.05)
	if not gwidth:
		return
	newwid = (wavg + 2*int(em*0.05) - gwidth)*percent + gwidth
	if 0.68*wavg > gwidth:
		newwid = 0.68*wavg
	if newwid < bounding[2] - bounding[0] + 10:
		newwid = bounding[2] - bounding[0] + 10 
	width = (bounding[2] - bounding[0])
	glyph.width = newwid
	glyph.left_side_bearing = (newwid - width)/2
	glyph.right_side_bearing = (newwid - width)/2

def fit_glyph_box(glyph, percent):
	'''Scale a font to nearly fit a square.'''
	bounding = glyph.boundingBox() # xmin, ymin, xmax, ymax
	gwidth = (bounding[2] - bounding[0])
	gheight = (bounding[3] - bounding[1])
	if not gwidth or not gheight:
		return
	if 0.64*max(gwidth, gheight) < min(gwidth, gheight):
		if gwidth > gheight:
			rate = ((gwidth - gheight)*percent + gwidth)/gwidth
			matrix = psMat.scale(1,rate)
		else:
			rate = ((gheight - gwidth)*percent + gheight)/gheight
			matrix = psMat.scale(rate,1)
		glyph.transform(matrix)

def ScaleToEm(percent, afont):
	'''Scale a font to fit 5% less than the em.'''
	#em = afont.ascent + afont.descent
	em = afont.ascent + afont.descent/2
	center = (afont.ascent - afont.descent/2)/2
	lbearing = int(em*0.05)
	if not percent:
		ret = fontforge.askString('Scale Percent?',
				'Percent of Line Height (em)?', '95' )
		if not ret:
			return
		try:
			percent = float(ret)/100
			if percent <= 0 or percent > 1.5:
				raise ValueError
		except ValueError:
			fontforge.postError('Wrong Percent!', "Need a value <= 150.")
			return
	wavg, havg = get_avg_size(afont)
	for glyph in afont.selection.byGlyphs:
		#fit_glyph(glyph, em, percent)
		fit_glyph_plus(glyph, em, percent, wavg, havg)
		#center_glyph(glyph, center, lbearing) # Maybe not move glyph?
		center_glyph_height(glyph, center) 

def ScaleToSquare(percent, afont):
	'''Scale a font to nearly fit a square.'''
	if not percent:
		ret = fontforge.askString('Scale Percent?',
				'Percent of Scale?', '20' )
		if not ret:
			return
		try:
			percent = float(ret)/100
			if percent <= 0 or percent > 1:
				raise ValueError
		except ValueError:
			fontforge.postError('Wrong Percent!', "Need a value <= 100.")
			return
	for glyph in afont.selection.byGlyphs:
		fit_glyph_box(glyph, percent)

def BoundToSquare(percent, afont):
	'''Scale a font to nearly fit the average width.'''
	em = afont.ascent + afont.descent
	if not percent:
		ret = fontforge.askString('Scale Percent?',
				'Percent of Scale?', '36' )
		if not ret:
			return
		try:
			percent = float(ret)/100
			if percent <= 0 or percent > 1:
				raise ValueError
		except ValueError:
			fontforge.postError('Wrong Percent!', "Need a value <= 100.")
			return
	wavg, havg = get_avg_size(afont)
	for glyph in afont.selection.byGlyphs:
		box_fit_square(glyph, em, percent, wavg, havg)

def YOffset(percent, afont):
	'''Adjust the Y position.'''
	em = afont.ascent + afont.descent/2
	if not percent:
		ret = fontforge.askString('Offset Percent?',
				'Percent of Offset?', '64' )
		if not ret:
			return
		try:
			percent = float(ret)/100
			if percent < -1.5 or percent > 1.5:
				raise ValueError
		except ValueError:
			fontforge.postError('Wrong Percent!', "Need a value abs(x) <= 150.")
			return
	if percent == 0: # Do Nothing.
		return
	tavg, bavg = get_avg_topbtm(afont)
	if percent > 0:
		deltay = (afont.ascent - tavg)*percent
	else:
		deltay = (afont.descent - bavg)*percent
	matrix = psMat.translate(0, deltay)
	for glyph in afont.selection.byGlyphs:
		glyph.transform(matrix)

def AutoAdjust(afont):
	ScaleToEm(None, afont)
	ScaleToSquare(None, afont)
	YOffset(None, afont)
	BoundToSquare(None, afont)

def get_max_size(afont):
	'''Get the max size of the selected glyphs.'''
	wmax = 0
	hmax = 0
	for glyph in afont.selection.byGlyphs:
		bbox = glyph.boundingBox()
		wmax = max(wmax, bbox[2] - bbox[0])
		hmax = max(hmax, bbox[3] - bbox[1])
	em = afont.ascent + afont.descent
	wpct = wmax and em/wmax*100
	hpct = hmax and em/hmax*100
	return wmax, hmax, wpct, hpct

def get_avg_size(afont):
	'''Get the max size of the selected glyphs.'''
	wsum = 0
	hsum = 0
	gcount = 0
	for glyph in afont.selection.byGlyphs:
		gcount = gcount + 1
		bbox = glyph.boundingBox()
		wsum = wsum + bbox[2] - bbox[0]
		hsum = hsum + bbox[3] - bbox[1]
	wavg = wsum / gcount
	havg = hsum / gcount
	return wavg, havg

def get_avg_topbtm(afont):
	'''Get the max size of the selected glyphs.'''
	tsum = 0
	bsum = 0
	gcount = 0
	for glyph in afont.selection.byGlyphs:
		gcount = gcount + 1
		bbox = glyph.boundingBox()
		tsum = tsum + bbox[3]
		bsum = bsum + bbox[1]
	tavg = tsum / gcount
	bavg = bsum / gcount
	return tavg, bavg

def GetSelectedBound(junk, afont):
	'''Show max height and width of the selected glyphs.'''
	wmax, hmax, wpct, hpct = get_max_size(afont)
	wavg, havg = get_avg_size(afont)
	em = afont.ascent + afont.descent
	msg = ('The max width and height of the selected glyphs are:\n'
			'Points:\t%d\t%d\nScale Factor to 100%%:\t%.3f\t  %.3f%%')
	msg = msg % (wmax, hmax, wpct, hpct)
	msg += "\nEm:\t%d" % em
	msg += '\nThe average width and height of the selected glyphs are:\n'
	msg += 'Points:'
	msg += str(wavg)
	msg += '\t'
	msg += str(havg)
	fontforge.postError('Max Demension', msg)

if fontforge.hasUserInterface():
	fontforge.registerMenuItem(GetSelectedBound, None, None, "Font", None,
			"Metrics", "Max Selected Size");
	fontforge.registerMenuItem(CenterHeight, None, None, "Font", None, "Metrics", 
			"Center in Height");
	fontforge.registerMenuItem(CenterGlyph, None, None, "Font", None, "Metrics", 
			"Center in Glyph");
	fontforge.registerMenuItem(YOffset, None, None, "Font", None, "Metrics", 
			"Y Offset");
	fontforge.registerMenuItem(BoundToSquare, None, None, "Font", None, "Metrics", 
			"Bounding to Square");
	fontforge.registerMenuItem(ScaleToEm, None, None, "Font", None, "Transform", 
			"Scale to Em");
	fontforge.registerMenuItem(ScaleToSquare, None, None, "Font", None, "Transform", 
			"Scale to Sqare");
	fontforge.registerMenuItem(ScaleToSquare, None, None, "Font", None, "Transform", 
			"Auto Adjust");
