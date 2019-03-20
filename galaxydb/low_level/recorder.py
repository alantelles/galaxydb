from ..constants import *
from ..statics import *
import os
from struct import pack
import datetime
import time

class Recorder:
    def __init__(self,name,scheme):
        self.name = name
        #self.tables_path = TABLES+os.sep+self.name
        #address_path = self.tables_path+os.sep+self.name+ADDR_EXT
        self.pages = []
        self.rec_buffer = []
        self.addr_buffer = []
        self.c_ids = []
        self.lengths = []
        self.columns = scheme['columns']
        self.maxes = scheme['max_values']
        self.locations = scheme['locations']
        self.tables_path = self.locations['table']+os.sep+self.name
        if not os.path.exists(self.tables_path):
            os.mkdir(self.tables_path)
        self.address_path = self.locations['address']+os.sep+self.name+ADDR_EXT
        for f in os.listdir(self.tables_path):
            if f.endswith(TBL_EXT):
                self.pages.append(self.tables_path+os.sep+f)
        if len(self.pages) > 0:
             # a page already exists
            self.pages.sort()
            size_last = os.path.getsize(self.pages[-1])
            page_num = self.pages[-1][self.pages[-1].rfind('-')+1:self.pages[-1].rfind('.')]
            page = self.pages[-1]
            self.f = open(page,'ab')
            self.addr = open(self.address_path,'rb+')
        else:
            #it's the first page
            #page_num = zeros_needed_fmt(self.maxes['max_pages']).format(0)
            page_num = zeros_needed_fmt(self.maxes['max_pages']).format(0)
            page = self.tables_path+os.sep+self.name+'-'+page_num+TBL_EXT
            self.f = open(page,'wb')
            self.addr = open(self.address_path,'wb')
            self.addr.write(FILE_END)
        self.get_auto_inc()
        self.page = int(page_num)
        self.page = to_bytes_e(self.page,self.maxes['max_pages'])
         
    def write_val (self, val, field):
        if field['type'] == INT:
            self.write_int(val,field['col_id'])
        elif field['type'] == STR:
            self.write_str(val,field['col_id'])
        elif field['type'] == BOOL:
            self.write_bool(val,field['col_id'])
        elif field['type'] == FLOAT:
            self.write_float(val,field['col_id'])
        elif field['type'] == DOUBLE:
            self.write_double(val,field['col_id'])
        elif field['type'] == DATETIME:
            self.write_datetime(val,field['col_id'])
        elif field['type'] == TIME:
            self.write_time(val,field['col_id'])
        elif field['type'] == DATE:
            self.write_date(val,field['col_id'])
    
    def write_time (self,val,c_id):
        k = [int(j) for j in val.split(':')]
        mid = datetime.datetime(1970,1,1,0,0,0)
        now = datetime.datetime(1970,1,1,*k)
        self.write_int(round((now - mid).total_seconds()),c_id)
    
    def write_datetime (self,val,c_id):
        e = val.split(" ")
        e = [int(x) for x in e[0].split('-')+e[1].split(':')]
        e = datetime.datetime(*e)
        stamp = round(time.mktime(e.timetuple()))
        self.write_int(stamp,c_id)
    
    def write_date (self,val,c_id):
        e = [int(x) for x in val.split('-')]
        e = datetime.datetime(*e)
        stamp = round(time.mktime(e.timetuple()))
        self.write_int(stamp,c_id)
    
    def write_int (self,val,c_id):
        size = bytes_needed(val)
        seq = to_bytes_e(val,size)
        self.rec_buffer.append(seq)
        self.c_ids.append(c_id)
        self.lengths.append(to_bytes_e(size,0))
    
    def write_float (self,val,c_id):
        seq = pack('>f',val)
        self.rec_buffer.append(seq)
        self.c_ids.append(c_id)
        self.lengths.append(to_bytes_e(4,0))
    
    def write_double (self,val,c_id):
        seq = pack('>d',val)
        self.rec_buffer.append(seq)
        self.c_ids.append(c_id)
        self.lengths.append(to_bytes_e(8,0))
    
    def write_str (self,val,c_id):
        v_enc = val.encode(STR_ENC)
        seq = v_enc
        self.rec_buffer.append(seq)
        self.lengths.append(to_bytes_e(len(v_enc),0))
        self.c_ids.append(c_id)
    
    def write_bool(self,val,c_id):
        val = 1 if val == True else 0
        self.write_int(val,c_id)
    def new_record(self):
        pass
        
    def is_new(self,id):
        adv = self.addr.tell()
        self.addr.seek(2)
        p = self.addr.read(2)
        while p != id:
            self.addr.seek(2,1)
            p = self.addr.read(2)
    
    def get_auto_inc(self):
        for i in self.columns:
            if PRIMARY_KEY in i:
                self.last_pri = i[AUTO_INC] - 1
                break
            
    def commit(self):
        self.get_auto_inc()
        self.addr.seek(-2,2)
        adf = RECORD #2
        adf += to_bytes_e(self.last_pri,self.maxes['max_regs']) #2
        self.f.seek(0,2) # points to end of file
        pos_rec=to_bytes_e(self.f.tell(),self.maxes['max_page_size'])
        for i,j in enumerate(self.rec_buffer):
            adf += FIELD
            adf += to_bytes_e(self.c_ids[i],self.maxes['max_cols']) #self.maxes['max_cols'] column_id
            adf += self.page #self.maxes['max_pages'] page
            adf += pos_rec #self.maxes['max_page_size'] address in a page
            adf += self.lengths[i]
            self.addr.write(adf)
            adf = b''
            self.f.write(j)
            pos_rec=to_bytes_e(self.f.tell(),self.maxes['max_page_size'])
        self.addr.write(FILE_END)
        self.rec_buffer = []
        self.addr_buffer = []
        self.lengths = []
        
    def close_recorder(self):
        self.f.close()
        self.addr.close()
