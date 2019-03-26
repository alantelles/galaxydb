from ..constants import *
from ..statics import *
from struct import unpack,pack
from datetime import datetime
import time
import os
import re
class Retriever:
    def __init__(self,name,scheme):
        self.name = name
        self.scheme = scheme
        #addr_path = TABLES+os.sep+self.name+os.sep+self.name+ADDR_EXT
        addr_path = self.scheme['locations']['address']+os.sep+self.name+ADDR_EXT
        self.tb_prefix = self.scheme['locations']['table']+os.sep+self.name+os.sep+self.name+'-'
        self.addr_path = addr_path
        try:
            f = open(addr_path,'rb')
        except:
            raise Exception ("Address file doesn't found")
        self.addr = f
        self.files = {}
    
    def get_code_by_field (self,field):
        for i in self.scheme['columns']:
            if i['name'] == field:
                return i['col_id']
    
    def find_data_by_addr(self,page,addr,length):
        page_needed = self.tb_prefix+zeros_needed_fmt(self.scheme['max_values']['max_pages']).format(page)+TBL_EXT
        if not page_needed in self.files:
            self.files[page_needed] = open(page_needed,'rb')
        self.files[page_needed].seek(addr)
        return self.files[page_needed].read(length)
    
    def find_records_by_field_sequential (self,columns,logic,*field_relation_val_tuples):
        # working for new address model
        self.addr.seek(0)
        ids = []
        found = []
        tests = []
        data = []
        found_ids = []
        for i in field_relation_val_tuples:
            tests.append({'field':i[0],'oper':i[1],'val':i[2]})
        max_regs = self.scheme['max_values']['max_regs']
        max_pages = self.scheme['max_values']['max_pages']
        max_page_size = self.scheme['max_values']['max_page_size']
        max_cols = self.scheme['max_values']['max_cols']
        self.addr.seek(0)
        r = self.addr.read(BUF)
        offset = 0
        id_ptn = b''
        for i in range(max_regs):
            id_ptn += b'[\x00-\xFF]'
        while r:
            ids.extend(re.findall(FIELD+to_bytes_e(0,max_cols)+id_ptn,r))
            r = self.addr.read(BUF)
        ids = [from_bytes_e(x[len(FIELD)+max_cols:]) for x in ids]
        for i in ids:
            cand = self.find_record_by_id(i)
            if logic == 'and':
                can_add = True
            elif logic == 'or':
                can_add = False
            for t in tests:
                match = logic_oper(t['oper'],cand[t['field']],t['val'])
                if logic == 'and' and not match:
                    can_add = False
                    break
                if logic == 'or' and match:
                    can_add = True
                    break
            if can_add:
                if len(columns) > 0:
                    a_reg = {}
                    for key,value in cand.items():
                        if key in columns:
                            a_reg[key] = value
                    data.append(a_reg)
                else:
                    data.append(cand)
                    found_ids.append(i)
        return (data,found_ids)

    def find_record_by_id(self,id,columns = []):
        # working for new address model
        data = {}
        self.addr.seek(0)
        max_regs = self.scheme['max_values']['max_regs']
        max_pages = self.scheme['max_values']['max_pages']
        max_page_size = self.scheme['max_values']['max_page_size']
        max_cols = self.scheme['max_values']['max_cols']
        id_b = to_bytes_e(id,max_regs)
        r = self.addr.read(BUF)
        offset = 0
        ret_cols = []
        if len(columns) > 0:
            for i in self.scheme['columns']:
                if i['name'] in columns:
                    ret_cols.append((to_bytes_e(i['col_id'],max_cols),i['name']))
        else:
            for i in self.scheme['columns']:
                ret_cols.append((to_bytes_e(i['col_id'],max_cols),i['name']))
        while r:
            if r.find(FIELD+b'\x00'+id_b) < 0:
                return None
            if len(r) == BUF:
                r += read_until(self.addr.read,FIELD)
            for i in ret_cols:
                pos = r.find(FIELD+i[0]+id_b)
                pos += len(FIELD+i[0]+id_b)
                temp = b''
                for j in range(pos,pos+max_pages):
                    temp += to_bytes_e(r[j],1)
                    pos += 1
                page = from_bytes_e(temp)
                temp = b''
                for j in range(pos,pos+max_page_size):
                    temp += to_bytes_e(r[j],1)
                    pos += 1
                addr = from_bytes_e(temp)
                temp = b''
                for j in range(pos,pos+len(r)):
                    temp += to_bytes_e(r[j],1)
                    next_f = b''
                    pos += 1
                    for k in range(pos,pos+len(FIELD)):
                        next_f += to_bytes_e(r[k],1)
                    if next_f == FIELD or next_f == FILE_END:
                        length = from_bytes_e(temp)
                        break
                data[i[1]] = self.conform_val(self.find_data_by_addr(page,addr,length),from_bytes_e(i[0]))
            r = self.addr.read(BUF)
            offset = len(r)
        return data
                
    def find_all(self,columns=[]):
        # working for new address model
        data = []
        found_ids = []
        ids = []
        self.addr.seek(0)
        max_regs = self.scheme['max_values']['max_regs']
        max_pages = self.scheme['max_values']['max_pages']
        max_page_size = self.scheme['max_values']['max_page_size']
        max_cols = self.scheme['max_values']['max_cols']
        r = self.addr.read(BUF)
        offset = 0
        id_ptn = b''
        for i in range(max_regs):
            id_ptn += b'[\x00-\xFF]'
        while r:
            ids.extend(re.findall(FIELD+to_bytes_e(0,max_cols)+id_ptn,r))
            r = self.addr.read(BUF)
        for i in ids:
            id = from_bytes_e(i[len(FIELD)+max_cols:])
            data.append(self.find_record_by_id(id,columns))
            found_ids.append(id)
        return (data,found_ids)
            
    def count_all(self):
        # working for new address model
        data = []
        found_ids = []
        self.addr.seek(0)
        max_regs = self.scheme['max_values']['max_regs']
        max_pages = self.scheme['max_values']['max_pages']
        max_page_size = self.scheme['max_values']['max_page_size']
        max_cols = self.scheme['max_values']['max_cols']
        r = self.addr.read(BUF)
        offset = 0
        id_ptn = b''
        for i in range(max_regs):
            id_ptn += b'[\x00-\xFF]'
        while r:
            ids = re.findall(FIELD+to_bytes_e(0,max_cols)+id_ptn,r)
            r = self.addr.read(BUF)
        return len(ids)
                        
    def byte_val(self,val,field):
        t = self.scheme['columns'][field]['type']
        if t == STR:
            return val.encode(STR_ENC)
        elif t == INT:
            return to_bytes_e(val,0)
        elif t == FLOAT:
            return pack('>f',val)
        elif t == DOUBLE:
            return pack('>d',val)
        elif t == BOOL:
            return to_bytes_e(1 if val else 0,1)
        elif t == DATETIME:
            e = val.split(" ")
            e = [int(x) for x in e[0].split('-')+e[1].split(':')]
            e = datetime.datetime(*e)
            stamp = round(time.mktime(e.timetuple()))
            return to_bytes_e(stamp,0)
        elif t == DATE:
            e = [int(x) for x in val.split('-')]
            e = datetime.datetime(*e)
            stamp = round(time.mktime(e.timetuple()))
            return to_bytes_e(stamp,0)
        elif t == TIME:
            k = [int(j) for j in val.split(':')]
            mid = datetime.datetime(1970,1,1,0,0,0)
            now = datetime.datetime(1970,1,1,*k)
            ret = round((now - mid).total_seconds())
            return to_bytes_e(ret,0)
            
    def conform_val(self,val,code):
        c_type = self.scheme['columns'][code]['type']
        if  c_type == STR:
            return val.decode(STR_ENC)
        elif c_type == INT:
            return int.from_bytes(val,byteorder='big')
        elif c_type == BOOL:
            return True if int.from_bytes(val,byteorder='big') == 1 else False
        elif c_type == FLOAT:
            return unpack('>f',val)[0]
        elif c_type == DOUBLE:
            return unpack('>d',val)[0]
        elif c_type == DATE:
            return datetime.utcfromtimestamp(from_bytes_e(val))
        elif c_type == DATETIME:
            return datetime.utcfromtimestamp(from_bytes_e(val))
        elif c_type == TIME:
            time1970 = datetime(1970,1,1,0,0,0)
            return datetime.utcfromtimestamp(round(time.mktime(time1970.timetuple())) + from_bytes_e(val))
            # TODO
            
    def close_retriever(self):
        for i,j in self.files.items():
            j.close()
        self.addr.close()
