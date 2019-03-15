import json
import os
from .scheme import Scheme
from .low_level.recorder import Recorder
from .low_level.retriever import Retriever
from .logic import Logic
from .constants import *
class Table():
    def __init__(self,name):
        self.data = []
        self.found_ids = []
        self.name = name
        self.sch_path=SCHEMES+os.sep+self.name+'.json'
        with open(self.sch_path,'rt') as f:
            self.scheme = json.load(f)
            
    def auto_inc(self,column):
        s = Scheme(self.name)
        self.scheme = s.auto_inc(column)
    
    def where(self,logic):
        r = Retriever(self.name,self.scheme)
        c = self.get_code_by_field(logic[0])
        ret = r.find_records_by_field(logic[2],c,logic[1])
        self.data = ret[0]
        self.found_ids = ret[1]
        r.close_retriever()
        return self
    
    def count_all(self):
        r = Retriever(self.name,self.scheme)
        ret = r.count_all()
        r.close_retriever()
        return ret
        
    def all(self):
        self.data = []
        r = Retriever(self.name,self.scheme)
        ret = r.find_all()[0]
        self.data = ret
        self.found_ids = ret[1]
        r.close_retriever()
        return self.data
    
    def filter (self,logic, level=0):
        self.data = []
        self.found_ids = []
        if isinstance(logic,tuple):
            x = logic
            logic = ['or']
            logic.append(x)
        rel = logic[0]
        conds = logic[1:]
        #aqui rola a filtragem
        for i in conds:
            if isinstance(i,list):
                self.filter(i,level+1)
            else:
                continue
        r = Retriever(self.name,self.scheme)
        ret = r.find_records_by_field_sequential(rel,*conds)
        self.data.extend(ret[0])
        self.found_ids.extend(ret[1])
        print(self.found_ids)
        r.close_retriever()
        return self
        
    def find(self,val):
        r = Retriever(self.name,self.scheme)
        k = r.find_record_by_id(val)
        self.data = k[0]
        self.found_ids = k[1]
        r.close_retriever()
        return k
            
    def get_code_by_field (self,field):
        for i in self.scheme['columns']:
            if i['name'] == field:
                return i['col_id']
    
    def column_equals(self,field,val):
        self.data = []
        r = Retriever(self.name,self.scheme)
        ret = r.find_records_by_field(val,self.get_code_by_field(field))
        self.data = ret[0]
        self.found_ids = ret[1]
        r.close_retriever()
        return self
    
    def get(self):
        k = []
        for i in self.data:
            k.append(i)
        self.data = k
        return self.data
        
    def first(self):
        return self.data[0]
    
    def limit(self,first,length=0):
        if length != 0:
            k = self.data[first:first+length]
        else:
            k = self.data[first:]
        self.data = []
        for i in k:
            self.data.append(i)
        return self.data
        
    def logic(self,*cond):
        r = Retriever(self.name,self.scheme)
        ret = r.find_records_by_field_sequential(cond[0],*cond[1:])
        self.data = ret[0]
        self.found_ids = ret[1]
        r.close_retriever()
        return self

    
    def insert_by_tuple(self,fields,values):
        lt = []
        l = len(fields)
        for i in values:
            d = {}
            for j in range(l):
                d[fields[j]] = i[j]
            lt.append(d)
        self.insert(*lt)
        
    def insert(self,*items):
        r = Recorder(self.name,self.scheme)
        for item in items:
            r.new_record()
            for sch_col in self.scheme['columns']:
                if sch_col['name'] in item:                    
                    r.write_val(item[sch_col['name']],sch_col)
                elif DEFAULT in sch_col:
                    r.write_val(sch_col[DEFAULT],sch_col)
                elif AUTO_INC in sch_col:
                    self.auto_inc(sch_col)
                    r.columns = self.scheme['columns']
                    r.write_val(sch_col[AUTO_INC],sch_col)
                elif (NULL in sch_col) and (sch_col[NULL]) == True: #caso null
                    r.write_null(sch_col)
                else:
                    raise Exception ('Mandatory field',sch_col['name'],'is not on passed item')
            r.commit()
        r.close_recorder()
        return len(items)
