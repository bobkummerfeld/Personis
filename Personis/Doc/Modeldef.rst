
Model Definition Format
=======================

When creating a new model it is possible to build the tree of contexts and components from a template file 
in "Model Definition Format" or "modeldef". This is useful when installing applications that need their
own subtree of contexts and components. The subtree could be built by the application using the *mkcontext*
and *mkcomponent* methods but there is also a "bulk" creation script (Src/Utils/mkmodel.py)
that reads files in the "modeldef" format and creates the specified contexts, components, views, subscriptions 
and initial evidence.

Modeldef files consist of a series of *lines of text*. Create a modeldef with any plain text editor.

Lines that start with # are comments and ignored. 

Lines that start with @@ specify a context to be made. The context name is in the form of a pathname starting
at the root of the model. For example::

	@@Personal: description="Personal information"

This specifies a context called "Personal" in the root context of the model. For example::

	@@Personal/Health: description="Health information"

This specifies a context called "Health" in the "Personal" context of the model.

A short string description of the context must be included.

After a context (@@) line, that context becomes the *current* context and any additional non-context elements 
are created in that context until the current context is changed by another @@ line.

Components are specified using lines that begin with two minus signs (--). For example::

	--firstname: type="attribute", value_type="string", description="First name", 
			[evidence_type="explicit", value="Alice"]

this line specifies that a new component called "firstname" is created in the current context. 
Attributes of the component are specified using name=value elements.  In this example the component is of type "attribute" and
the type of the value is "string".
The description of the component is "First name".
Initial evidence for the component is included as a sequence of bracketed sections, so in this example there is one piece of
evidence with type "explicit" and value "Alice".

Subscription rules can also be included with a new component using the "rule" attribute. Eg::

	--email: type="attribute", value_type="string", description="email address",
	# create a subscription that will notify when email address changes
		rule="<default!./Personal/email> ~ '*' : NOTIFY 'http://www.somewhere.com/' 
								'email=' <./Personal/email>"

lines can be continued by breaking them after a comma.

Views are specified by lines starting with "==" and include a list of component pathnames. For example::

	==fullname: firstname, lastname

Here is a more complete example::


	
	## Notes: 
	##  This is an example modeldef file that describes the structure of a model.
	##  To create a context and make it current:
	##  @@word/word/.../word: description="description string"
	##  To create a component in the current context:
	##  --componentname: type="type of component", value_type="type of value", 
		description="description", value="blah"[, value=".."]  
		subscription="sub statement"
	##  To create a view in the current context:
	##  ==viewname: path, path,....
	
	##  defs continue on new line starting with whitespace
	##  ComponentTypes = ["attribute", "activity", "knowledge", 
				"belief", "preference", "goal"]
	##  ValueTypes = ["string", "number", "boolean", "enum", "JSON"]
	
	
	# start with the root context:
	
	@@Location: description="Information about the users' location."
	--seenby: type="attribute", value_type="string", 
			description="sensor that has seen this person"
	--location: type="attribute", value_type="string", description="Location"
	
	@@Work: description="Information about the users work."
	--role: description="the users main role in the organisation", type="attribute", 
			value_type="enum", value="Academic", value="Postgraduate", value="etc"
	
	@@Devices: description="Devices related to the user"
	--syssensors: type="attribute", value_type="string", 
			description="list of system activity which detect the user"
	--carrying: type="attribute", value_type="string", 
			description="Device(s) being carried"
	
	@@modelinfo: description="Model Information"
	--modeled: type="attribute", value_type="string", 
			description="type of entity being modeled"
	--personisversion: type="attribute", value_type="string", 
			description="version of the Personis version in use"
	
	@@Personal: description="Personal data"
	--firstname: type="attribute", value_type="string", description="First name", 
			[evidence_type="explicit", value="Bob"]
	--lastname: type="attribute", value_type="string", description="Last name"
	--gender: type="attribute", value_type="enum", description="Gender", 
			value="male", value="female"
	--email: type="attribute", value_type="string", description="email address",
	# create a subscription that will notify when email address changes
		rule="<default!./Personal/email> ~ '*' : NOTIFY 'http://www.somewhere.com/' 
				'email=' <./Personal/email>"
	
	# ==viewname: list of components from current context
	#	create a view in the current context
	==fullname: firstname, lastname
	
	@@Personal/Health: description="Health information"
	--weight: type="attribute", value_type="number", description="My Weight", 
				[evidence_type="explicit", value="75", flags=["goal"]]
	--sleep: type="attribute", value_type="string", description="Sleep info"
	
	@@People: description="Information about people who may be relevant to the user"
	--bob: type="attribute", value_type="string", 
			description="relevance of showing Bob's status"
	--fullname: type="attribute", value_type="JSON", 
			description="first+last name JSON encoded"
	
	
	@@Preferences: description="preferences"
	@@Preferences/Music: description="Music preferences, playlists etc"
	--playlist: type="attribute", value_type="string", description="Tracks on my playlist"
	--played: type="attribute", value_type="string", description="Tracks played"
	@@Preferences/Music/Jazz: description="preferences for Jazz"
	@@Preferences/Music/Jazz/Artists: description="preferences for Jazz artists"
	--Miles_Davis: type="preference", value_type="number", description="Miles Davis"
	
	@@Preferences/Food: description="Food preferences"
	@@Preferences/Food/Thai: description="Thai food preferences"
	--orders: type="attribute", value_type="string", description="orders"
	--preferences: type="attribute", value_type="string", 
			description="preferred thai dishes"
	
	@@Temp: description="temporary components"


