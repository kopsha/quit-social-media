#stay-free.py

from argparse import ArgumentParser
from platform import platform

from os import path
from subprocess import call

def main():
	# let's interact with our user
	parser = ArgumentParser()
	parser.add_argument( "-r", "--readonly", action="store_true", help="no file is actually written" )
	parser.add_argument( "-u", "--undo", action="store_true", help="remove the block" )
	args = parser.parse_args()

	# what os are we running on?
	guestPlatformString = platform( terse=True )
	print( guestPlatformString )
	configFilePath = ''

	if guestPlatformString.startswith( 'Darwin' ):
		configFilePath = path.join( '/etc', 'hosts')
		print( "- using osx strategy (%s)" % (configFilePath) )
	elif guestPlatformString.startswith( 'Linux' ):
		configFilePath = path.join( '/etc', 'hosts')
		print( "- using linux strategy (%s)" % (configFilePath) )
	elif guestPlatformString.startswith( 'Windows' ):
		configFilePath = path.join( 'c:/Windows/System32/Drivers/etc', 'hosts')
		print( "- using windows strategy, %s" % (configFilePath) )
	else:
		printf( "error: can't handle %s, yet." % (guestPlatformString) )
		exit(1)

	if args.undo:
		if args.readonly:
			print( "> removing blocked domains [read-only]" )
		else:
			removeConfigPatch( configFilePath )
	else:
		if args.readonly:
			print( "> patching config [read-only]" )
		else:
			applyConfigPatch( configFilePath )

	if args.readonly:
		print( "> flushing dns caches [read-only]" )
	else:
		flushDnsCache( guestPlatformString )

	print( "- job finished. stay free" )
	return

### glob #
freeHeader = '### stay free, share these lines ___'
freeFooter = '### stay free, snippet ends here ^^^'
domainsToBlock = [
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

### func #
def isConfigPatched( configPath ):
	configStr = ''
	with open(configPath, 'r') as config_file:
		configStr = config_file.read()
	config_file.close()

	hasHeader = False
	isPatched = False

	i = 0
	for line in configStr.split( '\n' ):
		if line == freeHeader:
			hasHeader = True
		elif hasHeader and (line == freeFooter):
			isPatched = True
		i += 1

	return isPatched

def applyConfigPatch( configPath ):
	configStr = ''

	with open(configPath, 'r') as config_file:
	    configStr = config_file.read()
	config_file.close()

	cleanConfigStr = ''
	insideHeader = False

	for line in configStr.split( '\n' ):
		# header tracking
		if line == freeHeader:
			insideHeader = True
		elif not insideHeader:
			cleanConfigStr += line + '\n'
		elif line == freeFooter:
			insideHeader = False

	patchedConfigStr = cleanConfigStr + makeConfigString()

	try:
		with open(configPath, 'w') as config_file:
			config_file.write( patchedConfigStr )
		config_file.close()
	except IOError as e:
		if e.errno == 13:
			print( e )
			print( "You need root permissions to run this script." )
			exit(13)
		else:
			raise e

def removeConfigPatch( configPath ):
	configStr = ''

	with open(configPath, 'r') as config_file:
	    configStr = config_file.read()
	config_file.close()

	cleanConfigStr = ''
	insideHeader = False

	for line in configStr.split( '\n' ):
		# header tracking
		if line == freeHeader:
			insideHeader = True
		elif not insideHeader:
			cleanConfigStr += line + '\n'
		elif line == freeFooter:
			insideHeader = False

	try:
		with open(configPath, 'w') as config_file:
			config_file.write( cleanConfigStr )
		config_file.close()
	except IOError as e:
		if e.errno == 13:
			print( e )
			print( "You need root permissions to run this script." )
			exit(13)
		else:
			raise e

def makeConfigString():
	buff = freeHeader

	for d in domainsToBlock:
		if d.startswith( 'www.' ):
			d = d.replace( 'www.', '', 1 )

		linesForDomain = """0.0.0.0			{0}
::			{0}
0.0.0.0			www.{0}
::			www.{0}""".format( d )
		buff += '\n' + linesForDomain
	buff += '\n' + freeFooter + '\n'

	return buff

def flushDnsCache( guestPlatformString ):
	osPlatform, osVersion = guestPlatformString.split( '-', 1 )
	osMajorVersion, osMinorVersion = osVersion.split( '.', 1 )

	print( 'Flushing dns caches...' )

	### os x #
	if osPlatform == 'Darwin':
		try:
			osMajorVersion = int(osMajorVersion)
			osMinorVersion = float(osMinorVersion)
		except ValueError as e:
			print( '* error: could not parse os major version string.' )
			osMajorVersion = 16			# assume latest version

		if osMajorVersion <= 10:
			if osMinorVersion < 7.0:
				call( ['dscacheutil', '-flushcache'] )
			elif osMinorVersion >= 7.0 and osMinorVersion < 10.0:
				call( ['killall', '-HUP', 'mDNSResponder'] )
			elif osMinorVersion >= 10.0 and osMinorVersion < 10.4:
				call( ['discoveryutil', 'mdnsflushcache'] )
			else:
				call( ['killall', '-HUP', 'mDNSResponder'] )
		else:
			call( ['killall', '-HUP', 'mDNSResponder'] )
	### linux #			
	elif guestPlatformString.startswith( 'Linux' ):
		call( ['nscd', '-i', 'hosts'] )
	### windows #
	elif guestPlatformString.startswith( 'Windows' ):
		call( ['ipconfig', '/flushdns'] ) 
	### others # ???
	else:
		printf( "error: can't handle %s, yet." % (guestPlatformString) )
	return

### main #
if __name__ == "__main__":
    main()
    exit(0)
### _fin #
