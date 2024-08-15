revised = false
for x in X.domain:
if no y in Y.domain satisfies constraint for (X,Y):
delete x from X.domain
revised = true
return revised