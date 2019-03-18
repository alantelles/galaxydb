from galaxydb.table import Table
from galaxydb.logic import Logic
from datetime import datetime
import time
st=time.time()
i = Table('users')
l = Logic()

n = l.eq('username','alantelles')
m = l.eq('password','mahailomahailo')
o = l.eq('id',1)
mn = l.l_and(m,n,o)

is_w = l.eq('sex',False)

m = l.eq('sex',True)
p = l.eq('name','Regina Helena')
id8 = l.eq('id',8)
a = l.l_and(m,p)

test = l.l_or(mn,is_w)
andao = l.l_and(p,test)
k = i.column_equals('name','Regina Helena').get()
for af in k:
    print(af.id,af.name,af.username)
en=time.time()
print('Benchmark:',en-st)
