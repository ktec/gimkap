#!/usr/bin/env python
# -*- coding: latin-1 -*-

from globalmaptiles import *

def unique(seq, idfun=None): 
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

if __name__ == "__main__":

	import sys, os
		
	def Usage(s = ""):
		print "Usage: globalmaptiles.py [-profile 'mercator'|'geodetic'] zoomlevel lat lon [latmax lonmax]"
		print
		if s:
			print s
			print
		print "This utility prints for given WGS84 lat/lon coordinates (or bounding box) the list of tiles"
		print "covering specified area. Tiles are in the given 'profile' (default is Google Maps 'mercator')"
		print "and in the given pyramid 'zoomlevel'."
		print "For each tile several information is printed including bonding box in EPSG:900913 and WGS84."
		sys.exit(1)

	profile = 'mercator'
	zoomlevel = None
	lat, lon, latmax, lonmax = None, None, None, None
	boundingbox = False

	argv = sys.argv
	i = 1
	while i < len(argv):
		arg = argv[i]

		if arg == '-profile':
			i = i + 1
			profile = argv[i]
		
		if zoomlevel is None:
			zoomlevel = int(argv[i])
		elif lat is None:
			lat = float(argv[i])
		elif lon is None:
			lon = float(argv[i])
		elif latmax is None:
			latmax = float(argv[i])
		elif lonmax is None:
			lonmax = float(argv[i])
		else:
			Usage("ERROR: Too many parameters")

		i = i + 1
	
	if profile != 'mercator':
		Usage("ERROR: Sorry, given profile is not implemented yet.")
	
	if zoomlevel == None or lat == None or lon == None:
		Usage("ERROR: Specify at least 'zoomlevel', 'lat' and 'lon'.")
	if latmax is not None and lonmax is None:
		Usage("ERROR: Both 'latmax' and 'lonmax' must be given.")
	
	if latmax != None and lonmax != None:
		if latmax < lat:
			Usage("ERROR: 'latmax' must be bigger then 'lat'")
		if lonmax < lon:
			Usage("ERROR: 'lonmax' must be bigger then 'lon'")
		boundingbox = (lon, lat, lonmax, latmax)
	
	tz = zoomlevel
	mercator = GlobalMercator()

	mx, my = mercator.LatLonToMeters( lat, lon )
	#print "Spherical Mercator (ESPG:900913) coordinates for lat/lon: "
	#print (mx, my)
	tminx, tminy = mercator.MetersToTile( mx, my, tz )
	
	if boundingbox:
		mx, my = mercator.LatLonToMeters( latmax, lonmax )
		#print "Spherical Mercator (ESPG:900913) cooridnate for maxlat/maxlon: "
		#print (mx, my)
		tmaxx, tmaxy = mercator.MetersToTile( mx, my, tz )
	else:
		tmaxx, tmaxy = tminx, tminy
	
	tiles = []
	wgs = []

	for ty in range(tminy, tmaxy+1):
		for tx in range(tminx, tmaxx+1):
			tilefilename = "%s/%s/%s" % (tz, tx, ty)
			#print tilefilename, "( TileMapService: z / x / y )"
		
			gx, gy = mercator.GoogleTile(tx, ty, tz)
			tiles.append((gx, gy))
			#print "\tGoogle:", gx, gy
			#quadkey = mercator.QuadTree(tx, ty, tz)
			#print "\tQuadkey:", quadkey, '(',int(quadkey, 4),')'
			#bounds = mercator.TileBounds( tx, ty, tz)
			#print
			#print "\tEPSG:900913 Extent: ", bounds
			wgsbounds = mercator.TileLatLonBounds( tx, ty, tz)
			wgs.append(wgsbounds)
			#print "\tWGS84 Extent:", wgsbounds
			#print "\tgdalwarp -ts 256 256 -te %s %s %s %s %s %s_%s_%s.tif" % (
			#	bounds[0], bounds[1], bounds[2], bounds[3], "<your-raster-file-in-epsg900913.ext>", tz, tx, ty)
			#print

	startx = tiles[0][0]
	starty = tiles[0][1]
	endx = tiles[len(tiles)-1][0]
	endy = tiles[len(tiles)-1][1]

	print
	print "bounds [ %f, %f, %f, %f ]" % (wgs[0][0], wgs[0][1], wgs[len(wgs)-1][2], wgs[len(wgs)-1][3])

	# apparent curl will automagically create directories as required
	for x in range(startx, endx+1):
		os.system("mkdir %d" % x)

	os.system( '''
curl -d -S --user-agent "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13" --header "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" --header "Accept-Language: en-US,id-ID;q=0.8,id;q=0.6,en;q=0.4" --header "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3" --header "Keep-Alive: 300" --header "Connection: keep-alive" --cookie cookie.txt "http://khm1.google.co.in/kh/v=109&src=app&x=[%s-%s]&y=[%s-%s]&z=%s&s=Galil" -o "#1/#2.jpg"
''' % ( startx,endx,endy,starty,zoomlevel) )

	print "Stitching job 1"

	os.system("for dir in $(ls); do convert $dir/*.jpg -append $dir.jpg;done;")

	print "Stitching job 2"

	os.system("convert *.jpg +append map.jpg")

	print "Map is generated in 'map.jpg', you may remove other files"

	print "Creating kap file..."

	print "imgkap map.jpg %f %f %f %f map.kap" % (wgs[0][0], wgs[0][1], wgs[len(wgs)-1][2], wgs[len(wgs)-1][3])
	os.system("imgkap map.jpg %f %f %f %f map.kap" % (wgs[0][0], wgs[0][1], wgs[len(wgs)-1][2], wgs[len(wgs)-1][3]))
