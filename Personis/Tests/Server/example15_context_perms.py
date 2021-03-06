#!/usr/bin/env python

import sys
import Personis
import Personis_base
from Personis_util import showobj, printcomplist

def printAskContext( info ):
	(cobjlist, contexts, theviews, thesubs) = info
	printcomplist(cobjlist, printev = "yes")
	print "Contexts: %s" % str(contexts)
	print "Views: %s" % str(theviews)
	print "Subscriptions: %s" % str(thesubs)
		
print "skipping permission test as these are incorporated into an earlier test - run example 14 instead. Edit script to test"
sys.exit(0)

print "==================================================================="
print "Examples that show how permissions work"
print "==================================================================="

um = Personis.Access(model="Alice", user='alice', password='secret')

print ">>>> Set some permissions for the 'MyHealth' app"
um.setpermission(context=["Personal"], app="MyHealth", permissions={'ask':True, 'tell':False})

print ">>>> Show the permissions"
perms = um.getpermission(context=["Personal"], app="MyHealth")
print "MyHealth:", perms
perms = um.getpermission(context=["Personal"], app="withings")
print "withings:", perms

