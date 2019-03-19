from ..constants import *
from ..statics import *
from struct import unpack,pack
from datetime import datetime
import time
import os
class Retriever:
    def __init__(self,name,scheme):
        self.name = name
        self.scheme = scheme
        addr_path = TABLES+os.sep+self.name+os.sep+self.name+ADDR_EXT
        #self.tb_prefix = TABLES+os.sep+self.name+os.sep+self.name+'-'
        self.addr_path = addr_path
        f = open(addr_path,'rb')
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
    
    def find_records_by_field_sequential (self,logic,*field_relation_val_tuples):
        self.addr.seek(0)
        ids = []
        fields = []
        opers = []
        vals = []
        found = []
        for i in field_relation_val_tuples:
            fields.append(self.get_code_by_field(i[0]))
            opers.append(i[1])
            vals.append(i[2])
        r = self.addr.read(BUF)
        r = r + read_until(self.addr,RECORD,None,False)
        max_cols = self.scheme['max_values']['max_cols']
        max_pages = self.scheme['max_values']['max_pages']
        max_page_size = self.scheme['max_values']['max_page_size']
        while r:
            recs = r.split(RECORD)[1:]
            for i in recs:
                id = from_bytes_e(i[:max_cols])
                cols = i.split(FIELD)[1:]
                for j in cols:
                    code = j[0:max_cols]
                    if from_bytes_e(code) in fields:
                        page = from_bytes_e(j[max_cols:max_cols+max_pages])
                        addr = from_bytes_e(j[max_cols+max_pages:max_cols+max_pages+max_page_size])
                        length = from_bytes_e(j[max_cols+max_pages+max_page_size:])
                        data = self.find_data_by_addr(page,addr,length)
                        found.append({'code':code,'data':data,'id':id})
            r = self.addr.read(BUF)
            r = r + read_until(self.addr,RECORD,None,False)
        cons = {}
        for i in found:
            if not i['id'] in cons:
                cons[i['id']] = []
            cons[i['id']].append({from_bytes_e(i['code']):i['data']})
        found = []
        for i,j in cons.items():
            len_f = len(fields)
            match = False
            for k in range(len_f):
                for l in j:
                    if fields[k] in l:
                        # tests
                        data = l[fields[k]]
                        val_b = self.byte_val(vals[k],fields[k])
                        comp = opers[k]
                        test = logic_oper(comp,data,val_b)
                        if test:
                            match = True
                            if logic == 'or':
                                break
                        else:
                            match = False
                            if logic == 'and':
                                break
                            
                if logic == 'and' and not match:
                    break
                if logic == 'or' and match:
                    break
            if match:
                ids.append(i)
                found.append(self.find_record_by_id(i))
        return (found,ids)
        
    def filter_results(self):
        pass
        
    def find_records_by_field(self,val,field,comp):
        self.addr.seek(0)
        maxes = self.scheme['max_values']
        val_b = self.byte_val(val,field)
        f_b = to_bytes_e(field,maxes['max_cols'])
        a = self.addr.read(BUF)
        pos = last = -1
        stp = 0
        ret = []
        ids = []
        while a:
            pos = a.find(FIELD+f_b,stp+last+1)
            while pos > -1:
                st = pos+len(FIELD)+len(f_b)
                page = a[st:st+maxes['max_pages']]
                page = from_bytes_e(page)
                st = st+maxes['max_pages']
                addr = a[st:st+maxes['max_page_size']]
                addr = from_bytes_e(addr)
                next_f = a.find(FIELD,pos+1)
                if next_f == -1: # last col
                    next_f = a.find(RECORD,pos+1)
                    if next_f == -1:
                        next_f = a.find(FILE_END,pos+1)
                length = a[st+maxes['max_page_size']:next_f]
                length = from_bytes_e(length)
                data = self.find_data_by_addr(page,addr,length)
                # tests
                test = logic_oper(comp,data,val_b)
                # end tests
                if test:
                    for i in range(pos,last,-1):
                        test = b''
                        for temp in range(len(RECORD)):
                            test += to_bytes_e(a[temp+i],0)
                        #test = to_bytes_e(a[i],0)+to_bytes_e(a[i+1],0)
                        if test == RECORD:
                            id = []
                            for temp in range(maxes['max_regs']):
                                id.append(a[temp+len(RECORD)+i])
                            id = from_bytes_e(bytes(id))
                            ids.append(id)
                            ret.append(self.find_record_by_id(id))
                            break
                last = pos
                pos = a.find(FIELD+f_b,stp+last+1)
            a = self.addr.read(BUF)
            stp = self.addr.tell()
        return (ret,ids)
    
    def find_record_by_id(self,id):
        self.addr.seek(0)
        maxes = self.scheme['max_values']
        id_byte = to_bytes_e(id,maxes['max_regs'])
        target = RECORD + id_byte
        pos = seek_until(self.addr,target)[0]
        if pos == -1:
            return None
        data = {}
        self.addr.seek(len(target),1)
        num_cols = len(self.scheme['columns'])
        for i in range(num_cols):
            self.addr.seek(len(FIELD),1)
            code = from_bytes_e(self.addr.read(maxes['max_cols']))
            page = from_bytes_e(self.addr.read(maxes['max_pages']))
            addr = from_bytes_e(self.addr.read(maxes['max_page_size']))
            if i < num_cols-1:
                length = from_bytes_e(read_until(self.addr,FIELD))
            else:
                r = read_until(self.addr,RECORD)
                if not r == None:
                    length = from_bytes_e(r)
                else:
                    length = from_bytes_e(read_until(self.addr,FILE_END))
            data[self.scheme['columns'][i]['name']] = self.conform_val(self.find_data_by_addr(page,addr,length),code)
        return data
    
    def find_all(self):
        ret = []
        ids = []
        for i in find_all_seq(self.addr,RECORD):
            self.addr.seek(i+2)
            an_id = from_bytes_e(self.addr.read(self.scheme['max_values']['max_regs']))
            ret.append(self.find_record_by_id(an_id))
            ids.append(an_id)
        return (ret,ids)
        
    def count_all(self):
        self.addr.seek(0)
        f = self.addr.read(64*1024)
        f147 = 0
        founds = 0
        while f:
            for i in f:
                if i == 147:
                    f147 += 1
                if f147 == 2:
                    f147 = 0
                    founds += 1
            f = self.addr.read(64*1024)
        return founds
                        
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
