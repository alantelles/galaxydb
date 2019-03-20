from models.user import User
from galaxydb.logic import Logic
from galaxydb.scheme import Scheme
import time
def print_row(r):
    print(r.id,r.name,r.username,r.password)
def print_list(c):
    for i in c:
        print_row(i)

st=time.time()
u = User()
#y = u.all()
#print_list(y)
x = u.login('alantelles','zikazika')
print_row(x)

#s = Scheme('users')
#s.delete_scheme()

#recorder test
fields = ('name','username','password')
regs = [
    ('Alan Telles','alantelles','zikazika'),
    ('Marina Pereira','marinapereira','minhabebe'),
    ('Regina Helena','regina','929292'),
    ('Marcelino Telles','linao','guitarra'),
    ('João Augusto','joauzaum','jva2001'),
    ('Keli Pereira','kelicris','fofolete'),
    ('Philipe Pinheiro','philipe','phrp')
]
#u.insert_by_tuple(fields,regs)

en=time.time()
print('Benchmark:',en-st)
