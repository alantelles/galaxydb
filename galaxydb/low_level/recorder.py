from ..constants import *
from ..statics import *
import os
from struct import pack
import datetime
import time

class Creator:
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
        self.tb_prefix = self.tables_path+os.sep+self.name+'-'
        self.files = {}
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
            self.f = open(page,'wb+')
            self.addr = open(self.address_path,'wb+')
        addr_trash_path = self.locations['addr_trash']+os.sep+self.name+ADDR_TRASH_EXT
        if os.path.isfile(addr_trash_path):
            self.addr_trash = open(addr_trash_path,'rb+')
        else:
            self.addr_trash = open(addr_trash_path,'wb+')
        data_trash_path = self.locations['data_trash']+os.sep+self.name+DATA_TRASH_EXT
        if os.path.isfile(data_trash_path):
            self.data_trash = open(data_trash_path,'rb+')
        else:
            self.data_trash = open(data_trash_path,'wb+')
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
    
    
    def find_empty_addr(self,length):
        max_regs = self.maxes['max_regs']
        max_pages = self.maxes['max_pages']
        max_page_size = self.maxes['max_page_size']
        max_cols = self.maxes['max_cols']
        self.addr_trash.seek(0)
        r = self.addr_trash.read(BUF)
        if len(r) == BUF:
            r += read_until(self.addr_trash,TRASH)
        trash_addr = 0
        while r:
            offset = self.addr_trash.tell()
            trashes = r.split(TRASH)[1:-1]
            for t in trashes:
                if t.find(PERMA_TRASH) > -1:
                    trash_addr += len(TRASH)+len(t)
                    continue
                addr,leng = t.split(VALUE)
                leng = leng[:len(leng)-len(FIELD_END)]
                addr_int = from_bytes_e(addr)
                leng_int = from_bytes_e(leng)
                if leng_int == length:
                    #can save here
                    return {'addr':addr_int,'trash_addr':trash_addr,'trash_len':len(TRASH)+len(t)}
                trash_addr += len(TRASH)+len(t)
            r = self.addr_trash.read(BUF)
            if len(r) == BUF:
                r += read_until(self.addr_trash,TRASH)
        return None
    
    def clean_trash (self,f,pos,length):
        f.seek(pos+length-len(PERMA_TRASH))
        f.write(PERMA_TRASH)
        
    def clean_data_trash (self,f,pos,length,length_rec):
        max_regs = self.maxes['max_regs']
        max_pages = self.maxes['max_pages']
        max_page_size = self.maxes['max_page_size']
        max_cols = self.maxes['max_cols']
        where = f.tell()
        f.seek(pos)
        r = f.read(length)
        length_trash = from_bytes_e(r[len(TRASH)+max_pages+max_page_size:-len(FIELD_END)])
        rest_space = length_trash - length_rec
        f.seek(pos)
        f.write(r[:len(FIELD)+max_pages+max_page_size]+to_bytes_e(rest_space,0)+PERMA_TRASH)
        
    def find_empty_space(self,length):
        max_regs = self.maxes['max_regs']
        max_pages = self.maxes['max_pages']
        max_page_size = self.maxes['max_page_size']
        max_cols = self.maxes['max_cols']
        self.data_trash.seek(0)
        r = self.data_trash.read(BUF)
        if len(r) == BUF:
            r += read_until(self.data_trash,TRASH)
        trash_addr = 0
        while r:
            trashes = r.split(TRASH)[1:]
            for t in trashes:
                if t.find(PERMA_TRASH) > -1:
                    trash_addr += len(TRASH)+len(t)
                    continue
                page = t[:max_pages]
                addr = t[max_pages:max_pages+max_page_size]
                len_avail = t[max_pages+max_page_size:t.find(FIELD_END)]
                if from_bytes_e(len_avail) >= length:
                    #can save here
                    return {
                        'addr':from_bytes_e(addr),
                        'page':from_bytes_e(page),
                        'length':from_bytes_e(len_avail),
                        'trash_addr':trash_addr,
                        'trash_len':len(TRASH)+len(t)
                    }
                trash_addr += len(TRASH)+len(t)
            r = self.data_trash.read(BUF)
            if len(r) == BUF:
                r += read_until(self.data_trash,TRASH)
        return None
        
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
        adf = b''
        for i,j in enumerate(self.rec_buffer):
            adf += FIELD
            adf += to_bytes_e(self.c_ids[i],self.maxes['max_cols']) #self.maxes['max_cols'] column_id
            adf += to_bytes_e(self.last_pri,self.maxes['max_regs']) #2
            data_pos_rec = self.find_empty_space(from_bytes_e(self.lengths[i])) # gets an empty space to record data
            if data_pos_rec == None:
                pos_rec = self.f.tell()
                page_rec = from_bytes_e(self.page)
                self.f.seek(0,2)
            else:
                pos_rec = data_pos_rec['addr']
                page_rec = data_pos_rec['page']
                page_needed = self.tb_prefix+zeros_needed_fmt(self.maxes['max_pages']).format(page_rec)+TBL_EXT
                if not page_needed in self.files:
                    self.files[page_needed] = open(page_needed,'rb+')
                self.f = self.files[page_needed]
            adf += to_bytes_e(page_rec,self.maxes['max_pages'])
            adf += to_bytes_e(pos_rec,self.maxes['max_page_size'])
            adf += self.lengths[i]
            adf += FIELD_END
            rec_addr = self.find_empty_addr(len(adf))
            if not rec_addr == None:
                self.addr.seek(rec_addr['addr'])
                self.clean_trash(self.addr_trash,rec_addr['trash_addr'],rec_addr['trash_len'])
            else:
                self.addr.seek(0,2)
            self.addr.write(adf)
            adf = b''
            ##### TODO
            ##### open the the indicated page
            ##### goto to indicated address
            len_write = from_bytes_e(self.lengths[i])
            if len_write < (max_int_bytes(self.maxes['max_page_size'])-pos_rec):
                self.f.write(j)
            else:
                partial = j[:max_int_bytes(self.maxes['max_page_size'])-pos_rec]
                self.f.write(partial)
                rest = j[len(partial):]
                while len(rest) > max_int_bytes(self.maxes['max_page_size']):
                    page_rec += 1
                    page_needed = self.tb_prefix+zeros_needed_fmt(self.maxes['max_pages']).format(page_rec)+TBL_EXT
                    if not page_needed in self.files:
                        if os.path.isfile(page_needed):
                            self.files[page_needed] = open(page_needed,'rb+')
                        else:
                            self.page = to_bytes_e(page_rec,self.maxes['max_pages'])
                            self.files[page_needed] = open(page_needed,'wb+')
                    #rest = j[len(partial):]
                    self.files[page_needed].write(rest[:max_int_bytes(self.maxes['max_page_size'])])
                    rest = rest[max_int_bytes(self.maxes['max_page_size']):]
                page_rec += 1
                self.page = to_bytes_e(page_rec,self.maxes['max_pages'])
                page_needed = self.tb_prefix+zeros_needed_fmt(self.maxes['max_pages']).format(page_rec)+TBL_EXT
                if not page_needed in self.files:
                    if os.path.isfile(page_needed):
                        self.files[page_needed] = open(page_needed,'rb+')
                    else:
                        self.files[page_needed] = open(page_needed,'wb+')
                self.f = self.files[page_needed]
                self.f.write(rest)
            if not data_pos_rec == None:
                self.clean_data_trash(self.data_trash,data_pos_rec['trash_addr'],data_pos_rec['trash_len'],len(j))
        self.rec_buffer = []
        self.addr_buffer = []
        self.lengths = []
        
    def close_recorder(self):
        self.f.close()
        for i,j in self.files.items():
            j.close()
        self.addr.seek(0,2)
        self.addr.write(FIELD)
        self.addr.close()
