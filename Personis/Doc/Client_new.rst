===========================
Http Client/Server Protocol
===========================

This document describes the example of Personis functions (e.g. access, ask, tell, and so on)
in http protocol.

**access:**

(Python code)

.. code-block:: python

    def access(modelname=string, authType=string, auth=string, version="11.2")

(Javascript code / JSON)

Server URL/access with POST method and the body is:

*modelname should be pure modelname without server url (e.g. bob@cydex.it.usyd.edu.au -> bob)*


.. code-block:: javascript

    {"authType": "user", "modelname": "bob", "auth": "bob:pass", "version": "11.2"}

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure


**tell:**

(Python code)

.. code-block:: python

    def tell(modelname=string, authType=string, auth=string, version="11.2", 
        context=list-of-strings, componentid=string, evidence=dict)

(Javascript code / JSON)

Server URL/tell with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "evidence": {
            "comment": null, 
            "evidence_type": "explicit", 
            "value": "Bob",
            "objectType": "Evidence", 
            "source": "demoex2", 
            "flags": [],
            "time": null, 
            "exp_time": 0
        },
        "context": ["Personal"],
        "componentid": "firstname"
    }

*Note that the evidence dictionary should be extensible, ie not just the fields shown. 
Keys are strings, values can be strings/None/integer/list-of-strings*

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure

**ask:**

(Python code)

.. code-block:: python

    def ask(modelname=string, authType=string, auth=string, version="11.2",
        context=list-of-strings,
        resolver=dict,
        showcontexts=true-or-false,[b]
        view=list-of-(string-or-list-of-string))

The resolver dictionary is extensible, keys and values are strings, view is a list of strings or (list of strings)

(Javascript code / JSON) - ask **(Need to ask)**

Server URL/ask with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": [
            "Preferences", 
            "Music", 
            "Jazz",
            "Artists"
        ],
        "showcontexts": null,
        "resolver": {"evidence_filter": "all"},
        "view": [
            "Miles_Davis",
            [
            	"Personal",
            	"firstname"
            ]
        ]
    }

The return data is a dictionary containing a result and val entries like the Access function.
The value for "val" is a list of dictionaries, one per component value being returned.

Returns:

.. code-block:: javascript

    {
        "result": "ok",
        "val": [
            {
                "Description":"Miles Davis",
                "component_type":"preference",
                "evidencelist": [
                    {
                        "comment":null,
                        "evidence_type":"explicit",
                        "creation_time":1502675539.824118,
                        "value":4,
                        "source":"alice",
                        "flags":[],
                        "time":null,
                        "owner":"alice",
                        "objectType":"Evidence",
                        "useby":null
                    },
                    {
                        "comment":null,
                        "evidence_type":"explicit",
                        "creation_time":1502675816.885235,
                        "value":4,
                        "source":"alice",
                        "flags":[],
                        "time":null,
                        "owner":"alice",
                        "objectType":"Evidence",
                        "useby":null
                    }
                ],
                "value_list":null,
                "creation_time":1502675518.582243,
                "value":4,
                "value_type":"number",
                "goals":[],
                "resolver":null,
                "Identifier":"Miles_Davis",
                "objectType":"Component"
            },
            {
                "Description":"First name",
                "component_type":"attribute",
                "evidencelist":[],
                "value_list":null,
                "creation_time":1502675516.556165,
                "value":null,
                "value_type":"string",
                "goals":[],
                "resolver":null,
                "Identifier":"firstname",
                "objectType":"Component"
            }
        ]
    }



**mkview:**

(Python code)

.. code-block:: python

    def mkview(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
        viewobj=json-object)

(Javascript code / JSON) - create a view 

Server URL/mkview with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": ["Personal"],
        "viewobj": {
            "Identifier": "fullname",
            "component_list": [
                "firstname",
                "lastname"
            ]
        }
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure

**delview:**

(Python code)

.. code-block:: python

    def delview(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
        viewid=string)

(Javascript code / JSON) - delete a view

Server URL/delview with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": ["Personal"],
        "viewid": "fullname"
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure


**mkcontext:**

(Python code)

.. code-block:: python

    def mkcontext(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
        contextobj=json-object)

(Javascript code / JSON) - create a context 

Server URL/mkcontext with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": [""],
        "contextobj": {
            "Identifier": "Test"
        }
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure

**delcontext:**

(Python code)

.. code-block:: python

    def delcontext(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings)

(Javascript code / JSON) - delete a context

Server URL/delcontext with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": ["Test"]
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure

**mkcomponent:**

(Python code)

.. code-block:: python

    def mkcontext(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
        componentobj=json-object)

(Javascript code / JSON) - create a component 

Server URL/mkcomponent with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": ["Test"],
        "componentobj": {
            "Identifier": "age",
            "component_type": "attribute",
            "Description": "age",
            "goals": [
                "Personal",
                "Health",
                "weight"
            ],
            "value_type": "number"
        }
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure

**delcomponent:**

(Python code)

.. code-block:: python

    def delcomponent(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
    	componentid=string)

(Javascript code / JSON) - delete a component

Server URL/delcomponent with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": ["Test"],
        "componentid"
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure


**subscribe:**

(Python code)

.. code-block:: python

    def subscribe(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
    	view=list-of-(string-or-list-of-string)),
    	subscription=json-object)

(Javascript code / JSON) - create a subscription

Server URL/subscribe with POST method and the body is:

.. code-block:: javascript

    code here

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure

**delete_sub:**

(Python code)

.. code-block:: python

    def delete_sub(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
    	componentid=string,
    	subname=string)

(Javascript code / JSON) - delete a subscription

Server URL/delete_sub with POST method and the body is:

.. code-block:: javascript

    code here

Returns:

.. code-block:: javascript

    {"result": "ok", "val": true}    // on success
    {"result": "error", "val": null} // on failure

**list_subs:**

(Python code)

.. code-block:: python

    def list_subs(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
    	componentid=string)

(Javascript code / JSON) - subscription list

Server URL/list_subs with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": ["Personal"],
        "componentid": "lastname"
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": {}}    // on success
    {"result": "error", "val": null} // on failure


**set_goals:**

(Python code)

.. code-block:: python

    def set_goals(modelname=string, authType=string, auth=string, version="11.2", 
    	context=list-of-strings,
    	componentid=string,
    	goals=list-of-strings)

(Javascript code / JSON) - set goals

Server URL/set_goals with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2",
        "context": ["Personal", "Health"],
        "componentid": "weight",
        "goals": [
        	"Personal",
        	"Health",
        	"weight"
        ]
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": null}    // on success
    {"result": "error", "val": null} // on failure

**listapps:**

(Python code)

.. code-block:: python

    def listapps(modelname=string, authType=string, auth=string, version="11.2")

(Javascript code / JSON) - app list

Server URL/listapps with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2"
    }

Returns:

.. code-block:: javascript

    {"result": "ok", "val": {}}    // on success
    {"result": "error", "val": null} // on failure

**listrequests:**

(Python code)

.. code-block:: python

    def listrequests(modelname=string, authType=string, auth=string, version="11.2")

(Javascript code / JSON) - request list

Server URL/listrequests with POST method and the body is:

.. code-block:: javascript

    {
        "authType": "user",
        "modelname": "alice",
        "auth": "alice:secret",
        "version": "11.2"
    }

Returns:

.. code-block:: javascript

    {
        "result": "ok", 
        "val": {
            "MyHealth": {
                "description":"My Health Manager",
                "fingerprint":"ad29ef2fa15a502a8692f0cc2fd1f5ceeea1d923d77e318b4e0c28d1e4596d83"
            },
            "withings": {
                "description":"Unauthorised app",
                "fingerprint":"13276313b21ef98f9f974f80fffb09604a298af8dd91476f9e918c45f867f4bb"
            }
        }
    }    // on success

    {
        "result": "error", 
        "val": null
    } // on failure

