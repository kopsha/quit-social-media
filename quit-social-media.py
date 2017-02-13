#releaseMe.py
import argparse
import platform
import os
from shutil import copyfile
from subprocess import call

socialDomains = [
		'facebook.com',
		'twitter.com',
		'instagram.com',
		'linkedin.com',
		'pinterest.com',
		'tumblr.com',
		'tieba.baidu.com',
		'foursquare.com',
		'badoo.com'
		# feel free to add more, // ps: drop the 'www.'
	]

freeHeader = """
### stay free, share these lines ___"""
freeFooter = """
### stay free, snippet ends here ^^^
"""

def doTheDarwinMagic( args ):
	'''
	unix like os, modify /etc/hosts and flush dns caches
	macOS Sierra 10.12.0
		sudo killall -HUP mDNSResponder
	OSX 10.11.0
		sudo killall -HUP mDNSResponder
	OSX 10.10.4
		sudo killall -HUP mDNSResponder
	OSX 10.10.0 - 10.10.3
		sudo discoveryutil mdnsflushcache
	OSX 10.9  - 10.8 - 10.7
		sudo killall -HUP mDNSResponder
	OSX 10.5 - 10.6
		sudo dscacheutil -flushcache
	Windows
		ipconfig /flushdns
	Linux (depending on what you're running)
		/etc/init.d/named restart
		/etc/init.d/nscd restart
	'''
	hostsFilename = '/etc/hosts'

	try:
		fileH = open( hostsFilename, 'a+' )
		fileH.seek( 0 )
	except IOError, e:
		if e.errno == 13:
			print( "permission denied, please run with 'sudo'" )
		else:
			print( e )
		return e.errno

	hasPatchAlready = False
	for line in fileH: 
		if line.startswith( '### stay free' ):
			print( "already patched, skipping..." )
			hasPatchAlready = True
			break

	if not hasPatchAlready:
		buff = freeHeader

		for d in socialDomains:
			if d.startswith( 'www.' ):
				d = d.replace( 'www.', '', 1 )

			linesForDomain = """
0.0.0.0			{0}
::			{0}
0.0.0.0			www.{0}
::			www.{0}""".format( d )
			buff += linesForDomain
	
		buff += freeFooter

		if args.readonly:
			print( "[read-only] here are the changes:\n%s" % (buff) )
		else:
			copyfile( hostsFilename, hostsFilename+'.bak' )
			fileH.write( buff )

	fileH.close()

	# flushing dsn caches...
	if args.readonly:
		print( "[read-only] flushing dns caches" )
	else:
		try:
			call( ['killall', '-HUP', 'mDNSResponder'] )
			#call( ['discoveryutil', 'mdnsflushcache'] )
			call( ['dscacheutil', '-flushcache'] )
		except Exception as e:
			print( e )
			return 1

	print( "finished. your're safe" )
	return 0		# 0 means success


parser = argparse.ArgumentParser()
parser.add_argument( "-r", "--readonly", action="store_true", help="no file is actually written" )
parser.add_argument( "-v", "--verbose", action="store_true", help="increase output verbosity" )
args = parser.parse_args()

guestPlatformString = platform.platform( terse=True )

rc = 0
if guestPlatformString.startswith( 'Darwin' ):
	rc = doTheDarwinMagic( args )
elif guestPlatformString.startsWith( "Linux" ):
	rc = doTheDarwinMagic( args )
	rc = 1
elif guestPlatformString.startsWith( "Windows" ):
	print( "comming soon..." )
	rc = 9
else:
	printf( "can't handle %s, yet." % (guestPlatformString) )
	rc = 8

exit(rc)
