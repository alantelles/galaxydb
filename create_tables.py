#main.py
from galaxydb import *

tds = []
tds.append(Column('name',STR,NULL=False))
tds.append(Column('password',STR,NULL=False,DEFAULT='123456'))
tds.append(Column('username',STR,NULL=False))
#REGS,COLS,PAGES,PAGE_SIZE
max_values = {'max_regs':2,'max_page_size':1,'max_cols':1,'max_pages':1}
rt = '/home/alantelles/develop/python/galaxydb/'
locations = {
    'address':rt+'non-default-address',
    'table':rt+'non-default-tables'
}
sch = Scheme('users')
#sch.alter('column','contrasenha',{'name':'password'})
sch.create(tds,max_values)
#sch.delete_scheme()
sch.save(True)
