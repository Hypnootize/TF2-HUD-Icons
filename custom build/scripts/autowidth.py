#!/usr/bin/python
# vim:ts=8:sw=4:expandtab:encoding=utf-8
'''Auto adjust stroke width.
Copyright Gumble <abcdoyle888@gmail.com> 2013-2014

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
'''
__version__ = '1.1'

import sys,os,shutil
from subprocess import Popen

import math
import io
import sys
import json

import bdflib
import k3m

N = ((32,64,128), (16,0,1), (8,4,2))
A0 = [3,6,7,12,14,15,24,28,30,31,48,56,60,62,63,96,112,120,124,\
	  126,127,129,131,135,143,159,191,192,193,195,199,207,223,224,\
	  225,227,231,239,240,241,243,247,248,249,251,252,253,254]
A1 = [7, 14, 28, 56, 112, 131, 193, 224]
A2 = [7, 14, 15, 28, 30, 56, 60, 112, 120, 131, 135, 193, 195, 224, 225, 240]
A3 = [7, 14, 15, 28, 30, 31, 56, 60, 62, 112, 120, 124, 131, 135, 143, 193, 195, 199, 224, 225, 227, 240, 241, 248]
A4 = [7, 14, 15, 28, 30, 31, 56, 60, 62, 63, 112, 120, 124, 126, 131, 135, 143, 159, 193, 195, 199, 207, 224, 225, 227, 231, 240, 241, 243, 248, 249, 252]
A5 = [7, 14, 15, 28, 30, 31, 56, 60, 62, 63, 112, 120, 124, 126, 131, 135, 143, 159, 191, 193, 195, 199, 207, 224, 225, 227, 231, 239, 240, 241, 243, 248, 249, 251, 252, 254]
A1pix = [3, 6, 7, 12, 14, 15, 24, 28, 30, 31, 48, 56, 60, 62, 63, 96, 112, 120, 124, 126, \
		 127, 129, 131, 135, 143, 159, 191, 192, 193, 195, 199, 207, 223, 224, 225, 227, \
		 231, 239, 240, 241, 243, 247, 248, 249, 251, 252, 253, 254]
A1pfix = [21,69,81,84]

def simpscale(x,B,D):
	'''Scale x in [0,B] to [0,D]'''
	return int(D*(float(x)/B))


def AutoStrokeWidth(size, afont):
	pass
	
def CountPix(img):
	black=0
	for aline in img:
		black+=aline.count(1)
	return black

pointsize=48

with open('gwid_dict.json', 'r') as f:
	gwid = json.load(f)
avgwid = gwid['##avg']
fontlen = gwid['##len']

thres=1
scalen=1024.0/pointsize-1	#32
#66.365850877
k=0
toolbar_width = 60
#sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
#sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['
lastprg=0

for i in xrange(0,fontlen,64):
	Popen(u"python -u awff.py %s 2>&1" % str(i), shell=True, cwd=os.getcwdu()).wait()

sys.stdout.write("\n")
print "OK."
