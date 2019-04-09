from models.user import User
from galaxydb import *
import time
def print_row(r):
    print(r.id,r.name,r.username,r.password)
def print_list(c):
    for i in c:
        print_row(i)

st=time.time()
u = User()
l = Logic()
fields = ('name','username','password')
regs = [
    ('Alan Telles','alantelles','zikazika'),
    ('Marina Pereira','marinapereira','minhabebe'),
    ('Regina Helena','regina','929292'),
    ('Marcelino Telles','linao','guitarra'),
    ('João Augusto','joauzaum','jva2001'),
    ('Keli Pereira','kelicris','fofolete'),
    ('Philipe Pinheiro','philipe',"""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc elit leo, interdum at dictum id, maximus efficitur neque. Aenean semper metus in sollicitudin scelerisque. Proin vitae velit purus. Donec cursus sodales commodo. Praesent hendrerit tellus ligula, vitae auctor turpis hendrerit a. Nullam vitae ex quam. Vivamus commodo est vitae efficitur ultricies. Suspendisse viverra semper ultrices. Donec est enim, tempor fermentum placerat eu, bibendum ac est. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Fusce at nibh felis. Maecenas commodo dui tincidunt ullamcorper lobortis.

In tempor aliquet nulla sit amet mattis. Nunc eget nulla tincidunt, vulputate dolor sit amet, congue quam. Cras quis sodales velit. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nullam vel placerat augue. Praesent lacinia eu magna id gravida. Praesent sagittis suscipit erat, a elementum mi rutrum in.

Donec maximus consequat nulla et tincidunt. Donec nisl elit, commodo id scelerisque id, egestas vel erat. Nullam nec convallis augue. Ut ullamcorper et risus ac iaculis. Aliquam venenatis sapien vel egestas finibus. Quisque vehicula pulvinar tortor ut tristique. Morbi ultrices rhoncus nisi, fringilla faucibus ipsum lacinia vitae. Donec ac pretium mi. Vivamus ac lacinia tortor. Integer ex lacus, molestie id mollis et, vestibulum ut justo. Fusce ac pulvinar nisl.

"""),
    ('Felipe Marques','fpm','mp'),
    ('Marcos Pablo','marcos pablo','eusouo pablo * logador de multidões'),
    ('Zikão Legeu','zikao','marhailp')
]
for i in range(1):
    #u.insert_by_tuple(fields,regs)
    pass
ins = time.time()
ins_b = ins-st
print('Insert benchmark:',ins-st)
en=time.time()
fi_b = en-ins
print('Find benchmark:',fi_b)
print('Benchmark:',en-st)
