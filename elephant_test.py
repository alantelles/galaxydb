from models.user import User
from galaxydb.logic import Logic
from galaxydb.scheme import Scheme
from galaxydb.constants import *
import time
def print_row(r):
    print(r.id,r.name,r.username,r.password)
def print_list(c):
    for i in c:
        print_row(i)

st=time.time()
u = User()
l = Logic()
print_list(u.all())
#u.delete(l.eq('id',9))
#recorder test
fields = ('name','username','password')
regs = [
    ('Alan Telles','alantelles','zikazika'),
    ('Marina Pereira','marinapereira','minhabebe'),
    ('Regina Helena','regina','929292'),
    ('Marcelino Telles','linao','guitarra'),
    ('João Augusto','joauzaum','jva2001'),
    ('Keli Pereira','kelicris','fofolete'),
    ('Philipe Pinheiro','philipe','phrp'),
    ('Heber Passos','hebinho','1000lchopp')
]
#u.insert_by_tuple(fields,regs)
#u.insert({'name':'Marina Pereira','username':'marina2'})
en=time.time()
print('Benchmark:',en-st)
