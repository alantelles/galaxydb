#main.py
from column import Column
from scheme import Scheme
from table import Table
from constants import *

tds = []
tds.append(Column('name',STR,NULL=False))
tds.append(Column('password',STR,NULL=False,DEFAULT='123456'))
tds.append(Column('username',STR,NULL=False))
#REGS,COLS,PAGES,PAGE_SIZE
max_values = {}
sch = Scheme('users')
sch.create(tds)
sch.save()
