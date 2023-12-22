#!/usr/bin/env python

#
# The Personis system is copyright 2000-2011 University of Sydney
#	Bob.Kummerfeld@Sydney.edu.au
# GPL v3
#
# Active User Models: added subscribe method to Access

import Personis_base
import Subscription
from types import *
import re, time
import cronserver


class Access(Personis_base.Access):

	def __init__(self, model=None, modeldir=None, authType=None, auth=None):
		Personis_base.Access.__init__(self, model=model, modeldir=modeldir, authType=authType, auth=auth)
	
	def subscribe(self,
		context=[],
		view=None,
		subscription=None):
		"""
	arguments:
		context is a list giving the path of context identifiers
		view is either:
			an identifier of a view in the context specified
			a list of component identifiers or full path lists
			None indicating that the values of all components in
				the context be returned
		subscription is a dictionary containing owner, password and subscription statement string
		"""
		subscription['modelname'] = self.modelname
		print("subscription>>> %s %s %s" % (repr(context), repr(view), repr(subscription)))
		cronsub = subscription["statement"].strip().startswith("[")
		token = "%s:%f" % (self.user, time.time())
		for elt in ("user", "password", "statement"):
			if elt not in subscription:
					raise ValueError('"%s" key missing from subscription dict' % (elt))
		if len(list(subscription.items())) != 4:
				raise ValueError('unknown attribute in subscription %s'%(subscription))
		print("subscribe>> token:", token)
		self.curcontext = self._getcontextdir(context)
		contextinfo = self.getcontext(context)
		try:
			comps,comps_shelf_fd = Personis_base.shelf_open(self.curcontext+"/.components", "r")
		except:
			print("can't open ",self.curcontext+"/.components")
			comps = None
		try:
			views,views_shelf_fd = Personis_base.shelf_open(self.curcontext+"/.views", "r")
		except:
			views = None
		try:
			subs,subs_shelf_fd = Personis_base.shelf_open(self.curcontext+"/.subscriptions", "w")
		except:
			print("opening subs for <%s> failed"%(self.curcontext+"/.subscriptions"))
			subs = None
		cidlist = []
		cobjlist = []
		if isinstance(view, str):
			if views != None:
				if view not in views:
					raise ValueError('"%s" view not found'%(view))
				cidlist = views[view].component_list
			else:
				raise ValueError('"%s" view not found'%(view))
		elif isinstance(view, list):
			cidlist = view
		elif view == None: 
			if comps != None:
				cidlist = list(comps.keys())
		else:
			raise TypeError('view "%s" has unknown type'%(repr(view)))
		for cid in cidlist:
			if isinstance(cid, bytes):
				cid = str(cid)
			if isinstance(cid, str):
				if comps != None:
					if cid in comps:
						# add sub dict to subs for cid ######
						if cid in subs:
							newsub = subs[cid]
						else:
							newsub = {}
						newsub[token] = subscription
						subs[cid] = newsub
						if cronsub:
							cronserver.cronq.put(dict(op="put",context=context, comp=cid, subscription=subscription))
					else:
						raise ValueError('component "%s" not in view "%s" (%s)'%(cid,view,cidlist))
				else:
					raise ValueError('component "%s" not found'%(cid))
			elif isinstance(cid, list):
				vcontext = self._getcontextdir(cid[:-1])
				try:
					vcomps,vcomps_shelf_fd = Personis_base.shelf_open(vcontext+"/.components", "r")
				except:
					raise ValueError('context "%s" not in view "%s"'%(cid[-1],repr(view)))
				if cid[-1] in vcomps:
					# add sub dict to subs for cid[-1] #########
					if cid[-1] not in subs:
						newsub = {}
					else:
						newsub = subs[cid[-1]]
					newsub[token] = subscription
					subs[cid[-1]] = newsub
					if cronsub:
						cronserver.cronq.put(dict(op="put",context=context, comp=cid, subscription=subscription))
				else:
					raise ValueError('component "%s" not in view "%s"'%(cid[-1],repr(view)))
				Personis_base.shelf_close(vcomps, vcomps_shelf_fd)
					
		if comps != None:
			Personis_base.shelf_close(comps, comps_shelf_fd)
		if views != None:
			Personis_base.shelf_close(views, views_shelf_fd)
		if subs != None:
			Personis_base.shelf_close(subs, subs_shelf_fd)
		return token

	def delete_sub(self, context=None, componentid=None, subname=None):
		self.curcontext = self._getcontextdir(context)
		if type(componentid) == type(''):
			componentid = str(componentid)
		try:
			subs,subs_shelf_fd = Personis_base.shelf_open(self.curcontext+"/.subscriptions", "w")
		except:
			raise ValueError('no subs db when deleting sub %s for component "%s" in context "%s" not found'%(subname, componentid,self.curcontext))
		if componentid not in subs:
			raise ValueError('sub %s for component "%s" in context "%s" not found'%(subname, componentid,self.curcontext))
		subdict = subs[componentid]
		try:
			del subdict[subname]
		except:
			raise ValueError('cannot delete subname "%s" for component "%s" in context "%s" '%(subname,componentid,self.curcontext))
		subs[componentid] = subdict
		if subs != None:
			Personis_base.shelf_close(subs, subs_shelf_fd)
		return None

	def list_subs(self, context=None, componentid=None):
		self.curcontext = self._getcontextdir(context)
		try:
			subs,subs_shelf_fd = Personis_base.shelf_open(self.curcontext+"/.subscriptions", "r")
		except:
			raise ValueError('no subs db when listing subs for component "%s" in context "%s" '%(componentid,self.curcontext))
		if componentid not in subs:
			raise ValueError('no subs for component "%s" in context "%s" not found'%(componentid,self.curcontext))
		subdict = subs[componentid]
		if subs != None:
			Personis_base.shelf_close(subs, subs_shelf_fd)
		return subdict


	def checksubs(self, context, componentid):
		subs,subs_shelf_fd = Personis_base.shelf_open(self.curcontext+"/.subscriptions", "r")
		#print ">>>subs in context '%s': %s" % (self.curcontext, subs.keys())
		#print "checking subs for '%s'"%(componentid)
		if componentid in subs:
			subdict = subs[componentid]
			for subname,sub in list(subdict.items()):
				if sub == {}:
					continue
				#print "do the sub:", sub
				Subscription.dosub(sub, self)

