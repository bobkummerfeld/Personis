
import types
import _pickle as cPickle
import requests
import simplejson as json

http = None
currentServer = None

def do_call(server, port, fun, args):
	global http, currentServer
	#print "do_call>>%s, args>> %s" % (fun, args)
	args["version"] = "16.0"
	args["function"] = fun
	uri = "http://" + server + ":" + str(port) + "/" + fun + "?"
	logging.info(">>>>do_call: %s", uri)

	logfile = open("json.log", "w")
	logfile.write("requests.post: %s, %s\n"%(uri, args))
	proxies = { 'http': None, 'https': None }
	r = requests.post(uri, data=json.dumps(args), headers={"application":"json"}, proxies=proxies)
	rawresult = r.text

	logfile.write("rawresult>>"); logfile.write(rawresult.encode("ascii", "replace")); logfile.write("\n")
	logfile.close()
	try:
		result = r.json()
	except:
		logging.error("json decode failed!<<%s>>", rawresult)
		raise ValueError("json decode failed")
	# dirty kludge to get around unicode
	for k,v in result.items():
		if type(v) == type(u''):
			result[k] = str(v)
		if type(k) == type(u''):
			del result[k]
			result[str(k)] = v
	## Unpack the error, and if it is an exception throw it.
	if type(result) == types.DictionaryType and result.has_key("result"):
		if result["result"] == "error":
			logging.error(result)
			# We have returned with an error, so throw it as an exception.
			if result.has_key("pythonPickel"):
				raise cPickle.loads(result["pythonPickel"])
			elif len(result["val"]) == 3:
				raise cPickle.loads(str(result["val"][2]))
			else:
				raise Exception(str(result["val"]))
		else:
			# Unwrap the result, and return as normal. 
			result = result["val"]
	return result
