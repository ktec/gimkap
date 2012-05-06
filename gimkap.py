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

def downloadwithwget(url,filename):
	os.system("""
		wget \
			 --header='Host: khm0.google.com' \
			 --header='User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0 FirePHP/0.7.1' \
			 --header='Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
			 --header='Accept-Language: en-us,en;q=0.5' \
			 --header='Accept-Encoding: gzip, deflate' \
			 --header='Connection: keep-alive' \
			 --header='x-insight: activate' \
			 --header='If-Modified-Since: Fri, 1 Jan 2010 01:00:00 GMT' \
			 --header='Cache-Control: max-age=0' \
		     --no-clobber %s -O %s""" % (url, filename) )

def downloadwithcurl(url,filename):
	print "Downloadng %s" % url
	os.system( '''
		curl -d -S \
		 --header 'Host: khm0.google.com' \
		 --header 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0 FirePHP/0.7.1' \
		 --header 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
		 --header 'Accept-Language: en-us,en;q=0.5' \
		 --header 'Accept-Encoding: gzip, deflate' \
		 --header 'Connection: keep-alive' \
		 --header 'Cache-Control: max-age=0' \
		--cookie cookie.txt \
		"%s" \
		-o "%s"
	''' % ( url, filename ) )


def download2(url,filename):
	from urllib2 import Request, urlopen
	print "Downloadng %s" % url
	headers = {
		"Host": "khm0.google.com",
		"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:12.0) Gecko/20100101 Firefox/12.0 FirePHP/0.7.1",
		"Accept": "image/png,image/*;q=0.8,*/*;q=0.5",
		"Accept-Language": "en-us,en;q=0.5",
		"Accept-Encoding": "gzip, deflate",
		"Connection": "keep-alive",
		"Referer": "http://maps.google.com/",
		"Origin": "http://maps.google.com",
		"x-insight": "activate"
	}
	req = Request(url, None, headers)
	try:
		response = urlopen(req)
	except IOError, e:
		if hasattr(e, 'reason'):
        		print 'We failed to reach a server.'
        		print 'Reason: ', e.reason
    		elif hasattr(e, 'code'):
        		print 'The server couldn\'t fulfill the request.'
        		print 'Error code: ', e.code
	else:
    		# everything is fine
		with open(filename, 'a') as f:
			f.write(response.read())

def download3(host,path,filename):
	from urllib3 import connection_from_url, HTTPError, TimeoutError, MaxRetryError

	http_pool = connection_from_url(host, timeout=1.0)
	try:
	    r = http_pool.get_url(path, retries=2)
	except TimeoutError, e:
	    print "TimeoutError %s" % e.reason
	except MaxRetryError, e:
	    print "MaxRetryError"


if __name__ == "__main__":

	import sys, os
		
	def Usage(s = ""):
		print "Usage: gimkap.py zoomlevel lat lon [latmax lonmax]"
		print
		if s:
			print s
			print
		print "This utility prints for given WGS84 lat/lon coordinates (or bounding box) the list of tiles"
		print "covering specified area. Tiles are in the given 'profile' (default is Google Maps 'mercator')"
		print "and in the given pyramid 'zoomlevel'."
		sys.exit(1)

	profile = 'mercator'
	zoomlevel = None
	lat, lon, latmax, lonmax = None, None, None, None
	boundingbox = False

	argv = sys.argv
	i = 1
	while i < len(argv):
		arg = argv[i]

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
	tminx, tminy = mercator.MetersToTile( mx, my, tz )
	
	if boundingbox:
		mx, my = mercator.LatLonToMeters( latmax, lonmax )
		tmaxx, tmaxy = mercator.MetersToTile( mx, my, tz )
	else:
		tmaxx, tmaxy = tminx, tminy
	
	tiles = []
	#wgs = []
	
	for ty in range(tminy, tmaxy+1):
		for tx in range(tminx, tmaxx+1):
			
			gx, gy = mercator.GoogleTile(tx, ty, tz)
			print "Google tile: %d, %d" % (gx, gy)
			
			dirname = os.path.join(str(tz), str(gx))
			tilefilename = os.path.join(dirname, "%s.jpg" % gy)
			print tilefilename, "( TileMapService: z / x / y )"
		
			if os.path.isfile(tilefilename):
				print "File %s exists." % tilefilename
			else:
				if not os.path.exists(dirname): os.makedirs(dirname)
				#gmapsurl = "http://khm0.google.com/kh/v=109&src=app&host=maps.google.com"
				gmapsurl = "http://khm1.google.co.in/kh/v=109&src=app&s=Galil"
				url = "%s&x=%d&y=%d&z=%d" % (gmapsurl, gx, gy, tz)
				downloadwithcurl(url, tilefilename )

			tiles.append((gx, gy))
			wgsbounds = mercator.TileLatLonBounds( tx, ty, tz)
			#print "Tile %s,%s,%s = [%s,%s,%s,%s]" % (tx, ty, tz, wgsbounds[0],wgsbounds[1],wgsbounds[2],wgsbounds[3])
			#wgs.append(wgsbounds)

			if ty == tminy and tx == tminx:
				#print "First item"
				startx,starty = gx,gy
				lat,lng = wgsbounds[0],wgsbounds[1]
			if ty == tmaxy and tx == tmaxx:
				#print "Last item"
				endx,endy = gx,gy
				latmax,lngmax = wgsbounds[2],wgsbounds[3]


	print
	print "bounds [ %f, %f, %f, %f ]" % (lat,lng,latmax,lngmax)

	#print wgsbounds
	try:
		print "Stitching job 1"

		filename = "%i-%s%s-%s%s" % (tz,startx,starty,endx,endy)
		if not os.path.exists(filename):
			os.makedirs(filename)

		from collections import defaultdict
		res = defaultdict(list)
		for v, k in tiles: res[v].append(k)
		
		for k,v in res.items():
			convert = "convert "
			for l in reversed(v): convert += ("%s/%s/%i.jpg " % (tz, k, l))
			convert += " -append %s/%s.jpg" % (filename, k)
			os.system( convert )

		print "Stitching job 2"
		os.system("convert %s/*.jpg +append %s.jpg" % (filename,filename) )

		print
		print "Map is generated in '%s.jpg'" % filename
		print "Creating kap file..."

		create_kap = "imgkap %s.jpg %f %f %f %f %s.kap" % (filename, latmax,lng,lat,lngmax, filename) 
		print create_kap
		os.system( create_kap )

	except IOError:
		print "IOError"


