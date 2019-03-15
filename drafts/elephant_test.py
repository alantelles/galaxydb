from elephant.table import Table
from elephant.logic import Logic
from datetime import datetime
import time
st=time.time()
i = Table('users')
l = Logic()
n = l.eq('username','alantelles')
m = l.eq('password','mahailomahailo')
mn = l.l_and(m,n)
o = l.eq('id',1)
a = l.l_and(m,n)
m = l.eq('sex',True)
p = l.eq('name','Regina Helena')
login = l.l_or(a,m)
log = l.l_or(login,p)
x = l.is_not_in('name',['Regina Helena','Keli Pereira'])
#k = i.logic(*x).get()
k = i.filter(l.l_and(x,m)).get()
for d in k:
    print(d['id'],d['name'],d['username'])
en=time.time()
print('Benchmark:',en-st)
