#functions
import os
from pathlib import Path
def bytes_needed(num):
    i = 1
    while True:
        if num < 2**(8*i):
            return i
        i += 1
        
def zeros_needed_fmt(num):
    num = 2**(8*num)
    zeros = str(num)
    return r"{:0"+str(len(zeros))+r"d}"
    
def to_bytes_e (num,size = 2):
    if size == 0:
        size = bytes_needed(num)
    return num.to_bytes(size,byteorder='big')

def from_bytes_e(num):
    return int.from_bytes(num,byteorder='big')
    
def find_seq (f,seq,start_pos=None):
    # this function return files to the point where it were when the function was called
    seek_back = f.tell()
    if start_pos != None:
        f.seek(start_pos)
    else:
        start_pos = seek_back
    buf = 64*1024
    part = f.read(buf)
    bytes_walked = len(part)
    start_point = start_pos
    while part:
        pos = part.find(seq)
        if pos != -1:
            f.seek(seek_back)
            return (start_point+pos,start_pos+bytes_walked)
        part = f.read(buf)
        bytes_walked += len(part)
        start_point += len(part)
    f.seek(seek_back)
    
    return (-1,start_pos+bytes_walked)
    
def read_until (f,seq,start_pos=None,none_not_found = True):
    where = f.tell()
    pos = find_seq(f,seq,start_pos)
    if pos[0] > -1:
        return f.read(pos[0]-where)
    else:
        if none_not_found:
            return None
        else:
            f.seek(where)
            r = f.read(64*2014)
            while r:
                r += f.read(64*1024)
            return r
    
def seek_until(f,seq,start_pos=None):
    pos = find_seq(f,seq,start_pos)
    if pos[0] > -1:
        f.seek(pos[0])
    # returns the tuple of find_seq for any desired purpose
    return pos
        
def find_all_seq(f,seq,start_pos=None,return_only_pos=True):
    seek_back = f.tell()
    # this function return files to the point where it were when the function was called
    bytes_walked = 0
    x = find_seq(f,seq,start_pos)
    ret = []
    while not x[0] == -1:
        bytes_walked += x[1]
        if return_only_pos:
            ret.append(x[0])
        else:
            ret.append(x)
        x = find_seq(f,seq,x[0]+len(seq))
    f.seek(seek_back)
    return ret

#constants
ROOT = str(Path().absolute())+os.sep+'elephant'+os.sep

#data_types
INT, STR, VARI, NULL, DEFAULT, BOOL, FLOAT, DOUBLE ='INT', 'STR', 'VARI', 'NULL', 'DEFAULT', 'BOOL', 'FLOAT', 'DOUBLE'
DATE, DATETIME, TIME = 'DATE', 'DATETIME', 'TIME'

BUF = 64*1024

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

# canonical control bytes
FIELD, VALUE, RECORD, TRASH, FILE_END = 0x9191,0x9292,0x9393, 0x9494, 0x9595
FIELD = to_bytes_e(FIELD)
VALUE = to_bytes_e(VALUE)
RECORD = to_bytes_e(RECORD)
TRASH = to_bytes_e(TRASH)
FILE_END = to_bytes_e(FILE_END)
