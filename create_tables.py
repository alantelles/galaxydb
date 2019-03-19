#main.py
from galaxydb.column import Column
from galaxydb.scheme import Scheme
from galaxydb.constants import *
from galaxydb.statics import *

tds = []
tds.append(Column('name',STR,NULL=False))
tds.append(Column('password',STR,NULL=False,DEFAULT='123456'))
tds.append(Column('username',STR,NULL=False))
#REGS,COLS,PAGES,PAGE_SIZE
max_values = {}
sch = Scheme('users')
sch.create(tds,max_values)
sch.save()
