#!/usr/local/bin/python

import Personis
import Personis_base
import Personis_a


um = Personis_a.Access(model='Alice', modeldir='Tests/Models', authType='user', auth='alice:secret')

print "-----> subscribe to changes in lastname"
sub = """
<default!./Personal/lastname> ~ '.*' :
         NOTIFY 'http://www.it.usyd.edu.au/~bob/Personis/tst.cgi?' 'lastname=' <./Personal/lastname> 
"""

result = um.subscribe(context=["Personal"], view=['lastname'], subscription={'user':'alice', 'password':'secret', 'statement':sub})
print "Result:", result, "---\n"

ev = Personis_base.Evidence(evidence_type="explicit", value="Smith")
um.tell(context=["Personal"], componentid='lastname', evidence=ev)


print "-----> publish to localhost:1883 when lastname changed"
sub = """
<default!./Personal/lastname> ~ '.*' :
         PUBLISH '127.0.0.1:1883' 'Test' <./Personal/lastname> 
"""

result = um.subscribe(context=["Personal"], view=['lastname'], subscription={'user':'alice', 'password':'secret', 'statement':sub})
print "Result:", result, "---\n"

ev = Personis_base.Evidence(evidence_type="explicit", value="Smith")
um.tell(context=["Personal"], componentid='lastname', evidence=ev)
print "===== done"

print "-----> add a subscription that is examined according to a cron rule"
sub = """
 ["*/15 * * * *"] <default!./Location/location> ~ '.*' :
         NOTIFY 'http://www.it.usyd.edu.au/~bob/Personis/tst.cgi?' 'location=' <./Location/location>  '&name=' <./Personal/firstname>
"""

result = um.subscribe(context=["Personal"], view=['lastname'], subscription={'user':'alice', 'password':'secret', 'statement':sub})
print "Result:", result, "---\n"

ev = Personis_base.Evidence(evidence_type="explicit", value="Smith")
um.tell(context=["Personal"], componentid='lastname', evidence=ev)
