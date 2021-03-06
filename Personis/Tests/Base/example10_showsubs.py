#!/bin/env python2.4

import Personis_base
from Personis_util import showobj, printcomplist

def showall(reslist):
	cobjlist, contexts, theviews, thesubs = reslist
	printcomplist(cobjlist, printev = "yes")
	print "contexts:", contexts
	print "views:", theviews
	print "subscriptions:"
	for k,v in thesubs.items():
		print "\t%s:" % (k)
		for name,val in v.items():
			print "\t\t%s: %s" % (name, val)


um = Personis_base.Access(model='Alice', modeldir='Tests/Models', authType='user', auth='alice:secret')

print "==================================================================="
print "ask for alice's fullname, also get contexts/views/subs in current context"
reslist = um.ask(context=["Personal"], view='fullname', showcontexts=True)
print reslist
print "ask for alice's email"
showall(reslist)
reslist = um.ask(context=["Personal"], view=['email'], showcontexts=True)
