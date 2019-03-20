from models.user import User
from galaxydb.logic import Logic
import time
def print_rec(r):
    print(r.id,r.name,r.username,r.password)
def print_col(c):
    for i in c:
        print_rec(i)

st=time.time()
u = User()
x = u.login('alantelles','zikazika')
print_rec(x)
"""
fields = ('name','username','password')
regs = [
    ('Regina Helena','regina','929292'),
    ('Marcelino Telles','linao','guitarra'),
    ('João Augusto','joauzaum','jva2001'),
    ('Keli Pereira','kelicris','fofolete'),
    ('Philipe Pinheiro','philipe','phrp')
]
u.insert_by_tuple(fields,regs)
"""
en=time.time()
print('Benchmark:',en-st)
