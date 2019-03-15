from elephant.constants import *
from elephant.scheme import Scheme
from elephant.column import Column
tds = []
tds.append( Column('name',STR,NULL=False))
tds.append( Column('password',STR,NULL=False,DEFAULT='123456'))
tds.append( Column('username',STR,NULL=False))
tds.append( Column('sex',BOOL,DEFAULT=True))
tds.append(Column('average',FLOAT,DEFAULT=2.5))
tds.append(Column('x_average',DOUBLE,DEFAULT=3.8))
tds.append(Column('a_data',DATE,DEFAULT='2015-12-20'))
tds.append(Column('a_time',TIME,DEFAULT='18:30:21'))
tds.append(Column('a_datetime',DATETIME,DEFAULT='2017-03-28 15:13:52'))

texts = []
texts.append(Column('title',STR,DEFAULT='Sem título')
texts.append(Column('content',STR,NULL=True))

#REGS,COLS,PAGES,PAGE_SIZE
#sch = Scheme('users')
#sch.create(tds)
#sch.save()
