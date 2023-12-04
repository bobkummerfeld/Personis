#!/usr/bin/env python

#
# The Personis system is copyright 2000-2016 University of Sydney
#       Bob.Kummerfeld@Sydney.edu.au
# GPL v3
#
# Active User Models: added subscribe method to Access
#

import os, sys, traceback
import jsoncall
import bottle
import Personis_base
import Personis_a
import Personis_exceptions
import cPickle
import types
import simplejson as json
#from Crypto.PublicKey import RSA
import Personis_globals

def MkModel( model=None, modelserver=None, user=None, password=None, description=None, debug=1):
	if modelserver == None:
		raise ValueError("modelserver is None")
	if ':' in modelserver:
		modelserver, modelport = modelserver.split(":")
	else:
		modelport = 2005 # default port for personis server
	modelname = model
	auth = user + ":" + password
	ok = False
	try:
		ok = jsoncall.do_call(modelserver, modelport, "mkmodel", {'modelname':modelname,\
									'descripion':description,\
									'authType':'user',\
									'auth':auth})
	except:
		if debug >0:
			traceback.print_exc()
		raise ValueError("cannot create model '%s', server '%s'" % (modelname, modelserver))
	if not ok:
		raise ValueError("server '%s' cannot create model '%s'" % (modelserver, modelname))

def AppRequestAuth(model=None, modelserver=None, app=None, key=None, description=None, debug=0):
	if modelserver == None:
		raise ValueError("modelserver is None")
	if ':' in modelserver:
		modelserver, modelport = modelserver.split(":")
	else:
		modelport = 2005 # default port for personis server
	modelname = model
	ok = False
	try:
		ok = jsoncall.do_call(modelserver, modelport, "apprequestauth", {'modelname':modelname,\
									'description':description,\
									'app':app,\
									'key':key})
	except:
		if debug >0:
			traceback.print_exc()
		raise ValueError("cannot request authorisation for app '%s', server '%s'" % (app, modelserver))
	if not ok:
		raise ValueError("server '%s' cannot process authorisation request for app '%s'" % (modelserver, app))

class Access(Personis_a.Access):
	""" 
	Client version of access for client/server system

	arguments:
		model		model name
		modelserver	model server and port
		user		user name
		password	password string
		app		app name
		description	app description
	
	Either user and password, or app must be specified for successful authentication.

	returns a user model access object 
	"""
	def __init__(self, model=None, modelserver=None, user=None, password=None, app=None, description="", debug=1):
		if modelserver == None:
			raise ValueError("modelserver is None")
		if ':' in modelserver:
			self.modelserver, self.modelport = modelserver.split(":")
		else:
			self.modelserver = modelserver
			self.modelport = 2005 # default port for personis server
		logging.info(">>>>Access_server %s %s", self.modelserver, self.modelport)
		self.modelname = model
		self.user = user
		self.password = password
		self.app = app
		self.description = description
		self.debug =debug
		self.key = None
		if self.app == None:
			self.auth = user + ":" + password
			self.authType = "user"
		else:
			self.authType = "app"
			try:
				self.key = Personis_base.import_app_key(app)
			except Personis_exceptions.KeyFileNotFoundError:
				self.key = Personis_base.generate_app_key(self.app)
				fingerprint = Personis_base.generate_app_fingerprint(self.key)
				AppRequestAuth(model=self.modelname, modelserver=self.modelserver, app=self.app, 
					key=self.key.publickey().exportKey(), description=self.description)
				message = "Authorisation has been requested for app " + self.app + " to access model " + self.model + " on server " + self.modelserver + ".\n"
				message += "Key fingerprint: %s\n" % (fingerprint)
				raise Personis_exceptions.AuthRequestedError(message)

		ok = False
		try:
			command = "access"
			args = {'modelname':self.modelname}
			if self.app != None:
				self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
				args['authType'] = 'app'
			else:
				args['authType'] = 'user'
			args['auth'] = self.auth
			logging.debug("debug: %s",self.debug)
			if self.debug != 0:
				logging.info("access jsondocall: %s %s %s %s %s", self.modelserver, self.modelport, self.modelname, self.authType, self.auth)

			ok = jsoncall.do_call(self.modelserver, self.modelport, command, args)
			if self.debug != 0:
				logging.info("---------------------- result returned <%s>", ok)
		except:
			if debug >0:
				traceback.print_exc()
			raise ValueError("cannot access model '%s', server '%s'" % (self.modelname, self.modelserver))
		if not ok:
			raise ValueError("server '%s' cannot access model '%s'" % (self.modelserver, self.modelname))

	def ask(self,  
		context=[],
		view=None,
		resolver=None,
		showcontexts=None):
		"""
	arguments: (see Personis_base for details)
		context is a list giving the path of context identifiers
		view is either:
			an identifier of a view in the context specified
			a list of component identifiers or full path lists
			None indicating that the values of all components in
				the context be returned
		resolver specifies a resolver, default is the builtin resolver

	returns a list of component objects
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		reslist = jsoncall.do_call(self.modelserver, self.modelport, "ask", {'modelname':self.modelname,\
												'authType':self.authType,\
												'auth':self.auth,\
												'context':context,\
												'view':view,\
												'resolver':resolver,\
												'showcontexts':showcontexts})
		complist = []
		if showcontexts:
			cobjlist, contexts, theviews, thesubs = reslist
			for c in cobjlist:
				comp = Personis_base.Component(**c)
				if c["evidencelist"]:
					comp.evidencelist = [Personis_base.Evidence(**e) for e in c["evidencelist"]]
				complist.append(comp)
			reslist = [complist, contexts, theviews, thesubs]
		else:
			for c in reslist:
				comp = Personis_base.Component(**c)
				if c["evidencelist"]:
					comp.evidencelist = [Personis_base.Evidence(**e) for e in c["evidencelist"]]
				complist.append(comp)
			reslist = complist
		return reslist
	
	def tell(self, 
		context=[],
		componentid=None,
		evidence=None):   # evidence obj
		"""
	arguments:
		context - a list giving the path to the required context
		componentid - identifier of the component
		evidence - evidence object to add to the component
		"""
		if componentid == None:
			raise ValueError("tell: componentid is None")
		if evidence == None:
			raise ValueError("tell: no evidence provided")
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "tell", {'modelname':self.modelname,\
												'authType':self.authType,\
												'auth':self.auth,\
												'context':context,\
												'componentid':componentid,\
												'evidence':evidence.__dict__})
	def mkcomponent(self,
		context=[],
		componentobj=None):
		"""
        Make a new component in a given context
        arguments:
                context - a list giving the path to the required context
                componentobj - a Component object
        returns:
                None on success
                a string error message on error
		"""
		if componentobj == None:
			raise ValueError("mkcomponent: componentobj is None")
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "mkcomponent", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'componentobj':componentobj.__dict__})
	def delcomponent(self,
		context=[],
		componentid=None):
		"""
        Delete an existing component in a given context
        arguments:
                context - a list giving the path to the required context
                id - the id for a componen
        returns:
                None on success
                a string error message on error
		"""
		if componentid == None:
			raise ValueError("delcomponent: componentid is None")
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "delcomponent", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'componentid':componentid})
	def delcontext(self,
		context=[]):
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "delcontext", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context})
	def getresolvers(self):
		'''Return a list of the available resolver names'''
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "getresolvers", {'modelname':self.modelname,\
											'authType':self.authType, 'auth':self.auth})
	
	def setresolver(self,
		context,
		componentid,
		resolver):
		"""
        set the resolver for a given component in a given context
        arguments:
                context - a list giving the path to the required context
		componentid - the id for a given component
                resolver - the id of the resolver
        returns:
                None on success
                a string error message on error
		"""
		if componentid == None:
			raise ValueError("setresolver: componentid is None")
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "setresolver", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth,\
											'context':context,\
											'componentid':componentid, \
											'resolver':resolver})
		
	def mkview(self,
		context=[],
		viewobj=None):
		"""
        Make a new view in a given context
        arguments:
                context - a list giving the path to the required context
                viewobj - a View object
        returns:
                None on success
                a string error message on error
		"""
		if viewobj == None:
			raise ValueError("mkview: viewobj is None")
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "mkview", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'viewobj':viewobj.__dict__})
	def delview(self,
		context=[],
		viewid=None):
		"""
        Delete an existing view in a given context
        arguments:
                context - a list giving the path to the required context
                viewid - the id for the view
        returns:
                None on success
		"""
		if viewid == None:
			raise ValueError("delview: viewid is None")
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "delview", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'viewid':viewid})

	
	def mkcontext(self, 
		context= [],
		contextobj=None):
		"""
	Make a new context in a given context
	arguments:
		context - a list giving the path to the required context 
		contextobj - a Context object
		"""
		if contextobj == None:
			raise ValueError("mkcontext: contextobj is None")
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "mkcontext", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'contextobj':contextobj.__dict__})


	def getcontext(self,
		context=[],
		getsize=False):
		"""
	Get context information
	arguments:
		context - a list giving the path to the required context
		getsize - True if the size in bytes of the context subtree is required
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "getcontext", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth,\
											'context':context,\
											'getsize':getsize})

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
			subscription is a Subscription object
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return  jsoncall.do_call(self.modelserver, self.modelport, "subscribe", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'view':view,\
											    'subscription':subscription})
	def delete_sub(self,
		context=[],
		componentid=None,
		subname=None):
		"""
	arguments:
		context is a list giving the path of context identifiers
		componentid designates the component subscribed to
		subname is the subscription name
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return  jsoncall.do_call(self.modelserver, self.modelport, "delete_sub", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth,\
											'context':context,\
											'componentid':componentid,\
											'subname':subname})

	def export_model(self,
		context=[],
		level=None,
		resolver=None):
		"""
	arguments:
		context is the context to export
                resolver is a string containing the name of a resolver
                        or
                resolver is a dictionary containing information about resolver(s) to be used and arguments
                        the "resolver" key gives the name of a resolver to use, if not present the default resolver is used
                        the "evidence_filter" key specifies an evidence filter
                        eg 'evidence_filter' =  "all" returns all evidence,
                                                "last10" returns last 10 evidence items,
                                                "last1" returns most recent evidence item,
                                                None returns no evidence
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "export_model", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth,\
											'context':context,\
											'level':level,\
											'resolver':resolver})

	def import_model(self,
		context=[],
		partial_model=None):
		"""
	arguments:
		context is the context to import into
		partial_model is a json encoded string containing the partial model
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "import_model", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'partial_model':partial_model})
	def set_goals(self,
		context=[],
		componentid=None,
		goals=None):
		"""
	arguments:
		context is a list giving the path of context identifiers
		componentid designates the component with subscriptions attached
		goals is a list of paths to components that are:
			goals for this componentid if it is not of type goal
			components that contribute to this componentid if it is of type goal
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return  jsoncall.do_call(self.modelserver, self.modelport, "set_goals", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'componentid':componentid,\
											    'goals':goals})

		
	def list_subs(self,
		context=[],
		componentid=None):
		"""
	arguments:
		context is a list giving the path of context identifiers
		componentid designates the component with subscriptions attached
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return  jsoncall.do_call(self.modelserver, self.modelport, "list_subs", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context':context,\
											    'componentid':componentid})

	def registerapp(self, app=None, desc="", fingerprint=None):
		"""
                        registers an app as being authorised to access this user model
                        app name is a string (needs checking TODO)
                        app passwords are stored at the top level .model db
		"""
		# Only users can register apps
		return jsoncall.do_call(self.modelserver, self.modelport, "registerapp", {'modelname':self.modelname,\
											    'authType':'user',\
											    'auth':self.auth,\
											    'app':app,\
											    'description':desc,\
											    'fingerprint':fingerprint})
	
	def deleteapp(self, app=None):
		"""
                        deletes an app
		"""
		if app == None:
			raise ValueError("deleteapp: app is None")
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "deleteapp", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'app':app})

	def listapps(self):
		"""
			returns array of registered app names
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "listapps", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth})

	def listrequests(self):
		"""
			returns array of apps requesting authorisation
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "listrequests", {'modelname':self.modelname,\
											'authType':self.authType,\
											'auth':self.auth})

	def setpermission(self, context=None, componentid=None, app=None, permissions={}):
		"""
                        sets ask/tell permission for a context (if componentid is None) or
                                a component
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "setpermission", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context': context,\
											    'componentid': componentid,\
											    'app': app,\
											    'permissions': permissions})

	def getpermission(self, context=None, componentid=None, app=None):
		"""
                        gets permissions for a context (if componentid is None) or
                                a component
                        returns a tuple (ask,tell)
		"""
		if self.authType == 'app':
			self.auth = self.app + ":" + Personis_base.generate_app_signature(self.app, self.key)
		return jsoncall.do_call(self.modelserver, self.modelport, "getpermission", {'modelname':self.modelname,\
											    'authType':self.authType,\
											    'auth':self.auth,\
											    'context': context,\
											    'componentid': componentid,\
											    'app': app})



# server functions using bottle

# define a decorator for server functions to return the result as a dict
def dictresult(func):
	def mkdict():
		#print "dictresult>> entered"
		try:
			res = func()
			result = dict(result="ok", val=res)
		except:
			result = dict(result="error", val=None)
		#print "dictresult>>> ", repr(result)
		return json.dumps(result)
	return mkdict


@bottle.route('/mkmodel', method='post')
@dictresult
def s_mkmodel():
	# fixme need to implement security
	# and error handling
	
	# Only users can make models, so authType must be 'user'
	pargs = json.loads(bottle.request.body.read())
	(user, password) = pargs['auth'].split(":")
	Personis_base.MkModel(model=pargs['modelname'], modeldir=Personis_globals.modeldir, \
				user=user, password=password, description=pargs['description'])
	return True

@bottle.route('/apprequestauth', method='post')
@dictresult
def s_apprequestauth():
	pargs = json.loads(bottle.request.body.read())
	Personis_base.AppRequestAuth(model=pargs['modelname'], modeldir=Personis_globals.modeldir, \
				app=pargs['app'], key=pargs['key'], description=pargs['description'])
	return True


@bottle.route('/access', method='post')
@dictresult
def s_access():
	#print "s_access>> access request received"
	pargs = json.loads(bottle.request.body.read())
	#print "s_access>> pargs = <%s>" % (pargs)
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	#print "s_access>> returning True"
	return True


@bottle.route('/tell', method='post')
@dictresult
def s_tell():
	pargs = json.loads(bottle.request.body.read())
	#print "s_tell>> pargs = <%s>" % (pargs); sys.stdout.flush()
	try:
		um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	except:
		return "Access failed"
	try:
		res = um.tell(context=pargs['context'], componentid=pargs['componentid'], evidence=Personis_base.Evidence(**pargs['evidence']))
	except Exception as e:
		return "tell failed: %s\n"%(repr(e))
	return res

@bottle.route('/ask', method='post')
@dictresult
def s_ask():
	#print "Entering ask function...."; sys.stdout.flush()
	b = bottle.request.body.read()
	pargs = json.loads(b)
	#pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	reslist = um.ask(context=pargs['context'], view=pargs['view'], resolver=pargs['resolver'], \
				showcontexts=pargs['showcontexts'])
	if pargs['showcontexts']:
		cobjlist, contexts, theviews, thesubs = reslist
		cobjlist = [c.__dict__ for c in cobjlist]
		for c in cobjlist:
			if c["evidencelist"]:
				c["evidencelist"] = [e for e in c["evidencelist"]]
		newviews = {}
		if theviews != None:
			for vname,v in theviews.items():
				newviews[vname] = v.__dict__
		else:
			newviews = None
		reslist = [cobjlist, contexts, newviews, thesubs]
	else:
		reslist = [c.__dict__ for c in reslist]
		for c in reslist:
			if c["evidencelist"]:
				c["evidencelist"] = [e for e in c["evidencelist"]]
	return reslist

@bottle.route('/subscribe', method='post')
@dictresult
def s_subscribe():
	pargs = json.loads(bottle.request.body.read())
	logging.info("s_subscribe>> pargs: %s", pargs)
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	res = um.subscribe(context=pargs['context'], view=pargs['view'], subscription=pargs['subscription'])
	return res

@bottle.route('/delete_sub', method='post')
@dictresult
def s_delete_sub():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.delete_sub(context=pargs['context'], componentid=pargs['componentid'], subname=pargs['subname'])

@bottle.route('/list_subs', method='post')
@dictresult
def s_list_subs():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.list_subs(context=pargs['context'], componentid=pargs['componentid'])

@bottle.route('/export_model', method='post')
@dictresult
def s_export_model():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.export_model(context=pargs['context'], resolver=pargs['resolver'])

@bottle.route('/import_model', method='post')
@dictresult
def s_import_model():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.import_model(context=pargs['context'], partial_model=pargs['partial_model'])

@bottle.route('/set_goals', method='post')
@dictresult
def s_set_goals():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.set_goals(context=pargs['context'], componentid=pargs['componentid'], goals=pargs['goals'])

@bottle.route('/registerapp', method='post')
@dictresult
def s_registerapp():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.registerapp(app=pargs['app'], desc=pargs['description'], fingerprint=pargs['fingerprint'])

@bottle.route('/deleteapp', method='post')
@dictresult
def s_deleteapp():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.deleteapp(app=pargs['app'])

@bottle.route('/getpermission', method='post')
@dictresult
def s_getpermission():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.getpermission(context=pargs['context'], componentid=pargs['componentid'], app=pargs['app'])

@bottle.route('/setpermission', method='post')
@dictresult
def s_setpermission():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.setpermission(context=pargs['context'], componentid=pargs['componentid'], app=pargs['app'], permissions=pargs['permissions'])

@bottle.route('/listapps', method='post')
@dictresult
def s_listapps():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.listapps()

@bottle.route('/listrequests', method='post')
@dictresult
def s_listrequests():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.listrequests()

@bottle.route('/mkcomponent', method='post')
@dictresult
def s_mkcomponent():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	comp = Personis_base.Component(**pargs["componentobj"])
	return um.mkcomponent(pargs["context"], comp)

@bottle.route('/delcomponent', method='post')
@dictresult
def s_delcomponent():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.delcomponent(pargs["context"], pargs["componentid"])

@bottle.route('/delcontext', method='post')
@dictresult
def s_delcontext():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.delcontext(pargs["context"])

@bottle.route('/setresolver', method='post')
@dictresult
def s_setresolver():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.setresolver(pargs["context"], pargs["componentid"], pargs["resolver"])

@bottle.route('/getresolvers', method='post')
@dictresult
def s_getresolvers():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.getresolvers()

@bottle.route('/mkview', method='post')
@dictresult
def s_mkview():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	viewobj = Personis_base.View(**pargs["viewobj"])
	return um.mkview(pargs["context"], viewobj)

@bottle.route('/delview', method='post')
@dictresult
def s_delview():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.delview(pargs["context"], pargs["viewid"])

@bottle.route('/mkcontext', method='post')
@dictresult
def s_mkcontext():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	contextobj = Personis_base.Context(**pargs["contextobj"])
	return um.mkcontext(pargs["context"], contextobj)

@bottle.route('/getcontext', method='post')
@dictresult
def s_getcontext():
	pargs = json.loads(bottle.request.body.read())
	um = Personis_a.Access(model=pargs['modelname'], modeldir=Personis_globals.modeldir, authType=pargs['authType'], auth=pargs['auth'])
	return um.getcontext(pargs["context"], pargs["getsize"])

		
if __name__ == '__main__':
	if len(sys.argv) == 2:
		Personis_globals.modeldir = os.path.expanduser(sys.argv[1])
	else:
		Personis_globals.modeldir = 'models'
