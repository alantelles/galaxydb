#functions
import os
from pathlib import Path
from .statics import *

#constants
ROOT = str(Path().absolute())+os.sep+'galaxydb'+os.sep

#data_types
INT, STR, VARI, NULL, DEFAULT, BOOL, FLOAT, DOUBLE ='INT', 'STR', 'VARI', 'NULL', 'DEFAULT', 'BOOL', 'FLOAT', 'DOUBLE'
DATE, DATETIME, TIME = 'DATE', 'DATETIME', 'TIME'

BUF = 64*1024
ASC, DESC = 'ASC', 'DESC'

#column modifiers
PRIMARY_KEY, AUTO_INC, UNIQUE = 'PRIMARY_KEY', 'AUTO_INC', 'UNIQUE'

#default names
STR_ENC='utf-8'
DUMP_EXT='.elph'
TBL_EXT='.eltb'
SCH_EXT='.elsc'
ADDR_EXT='.elad'
TABLES = ROOT+'tables'

MAX_COLS = 2 #max number of cols is 2^(8*MAX_COLS), default 65536 cols
MAX_REGS = 2 #max number of registers in a table is 2^(8*MAX_REGS), default 65536 regs
MAX_PAGES = 2 #max number of pages is 2^(8*MAX_PAGES), default 256 pages 
MAX_PAGE_SIZE = 3 #max size of a page is 2^(8*MAX_PAGE_SIZE), default 16777216 (16MB)
MAX_DEFAULT = {'max_regs':2, 'max_pages':2, 'max_page_size':3, 'max_cols':2}

SCHEMES = ROOT+'schemes' #folder to save the schemes files

# others
RET_AS_NAMESPACE = True

# canonical control bytes
FIELD, VALUE, RECORD, TRASH, FILE_END = 0x9191,0x9292,0x9393, 0x9494, 0x9595
FIELD = to_bytes_e(FIELD)
VALUE = to_bytes_e(VALUE)
RECORD = to_bytes_e(RECORD)
TRASH = to_bytes_e(TRASH)
FILE_END = to_bytes_e(FILE_END)