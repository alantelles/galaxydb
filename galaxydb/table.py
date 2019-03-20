import json
import os
from .scheme import Scheme
from .low_level.recorder import Recorder
from .low_level.retriever import Retriever
from .logic import Logic
from .constants import *
from .statics import *
from argparse import Namespace
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
    
    def count_all(self):
        r = Retriever(self.name,self.scheme)
        ret = r.count_all()
        r.close_retriever()
        return ret
        
    def all(self,as_namespace = RET_AS_NAMESPACE):
        self.data = []
        r = Retriever(self.name,self.scheme)
        ret = r.find_all()[0]
        self.data = ret
        self.found_ids = ret[1]
        r.close_retriever()
        if (as_namespace):
            ret = []
            for i in self.data:
                ret.append(Namespace(**i))
            self.data = ret
        return self.data

# free conditional return methods    
    def where(self,logic):
        r = Retriever(self.name,self.scheme)
        c = self.get_code_by_field(logic[0])
        ret = r.find_records_by_field(logic[2],c,logic[1])
        self.data = ret[0]
        self.found_ids = ret[1]
        r.close_retriever()
        return self
        
    def filter (self,logic):
        if isinstance(logic,tuple):
            x = logic
            logic = ['or']
            logic.append(x)
        rel = logic[0]
        conds = logic[1:]
        tests = {}
        for i in conds:
            if isinstance(i,list):
                self.filter(i)
            else:
                tests[i[0]] = {'oper':i[1],'val':i[2]}
        r = Retriever(self.name,self.scheme)
        ret = r.find_records_by_field_sequential(rel,*conds)
        if rel == 'and' and len(self.found_ids) > 0:
            for i in range(len(ret[1])):
                if ret[1][i] in self.found_ids:
                    res.append(ret[1][i])
                    res_reg.append(ret[0][i])
            self.data = res
            self.found_ids = res_reg
        else:
            self.data.extend(ret[0])
            self.found_ids.extend(ret[1])
        r.close_retriever()
        return self
        
    def logic(self,*cond):
        r = Retriever(self.name,self.scheme)
        ret = r.find_records_by_field_sequential(cond[0],*cond[1:])
        self.data = ret[0]
        self.found_ids = ret[1]
        r.close_retriever()
        return self
        
# strictly built logic conditional methods            
    def find(self,val,as_namespace=RET_AS_NAMESPACE):
        r = Retriever(self.name,self.scheme)
        k = r.find_record_by_id(val)
        r.close_retriever()
        if not k == None:
            self.data = k
            self.found_ids = k['id']
            if (as_namespace):
                return Namespace(**self.data)
            else:
                return self.data
        else:
            return None
        
    def column_equals(self,field,val):
        self.data = []
        r = Retriever(self.name,self.scheme)
        ret = r.find_records_by_field(val,self.get_code_by_field(field),'=')
        self.data = ret[0]
        self.found_ids = ret[1]
        r.close_retriever()
        return self

# auxiliary methods            
    def get_code_by_field (self,field):
        for i in self.scheme['columns']:
            if i['name'] == field:
                return i['col_id']

# data return methods    
    def get(self,as_namespace = RET_AS_NAMESPACE):
        k = []
        for i in self.data:
            if (as_namespace):
                k.append(Namespace(**i))
            else:
                k.append(i)
        self.data = k
        return self.data
        
    def first(self,as_namespace = RET_AS_NAMESPACE):
        if (as_namespace):
            return Namespace(**self.data[0])
        else:
            return self.data[0]
    
    def limit(self,first,length=0,as_namespace = RET_AS_NAMESPACE):
        if length != 0:
            k = self.data[first:first+length]
        else:
            k = self.data[first:]
        self.data = []
        for i in k:
            if (as_namespace):
                self.data.append(Namespace(**i))
            else:
                self.data.append(i)
        return self.data

#insert methods    
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

#order methods
    def order(self,*rules):
        r = []
        for i in rules:
            if isinstance(i,tuple):
                r.append({'col':i[0],'dir':i[1]})
            elif isinstance(i,str):
                r.append({'col':i[0],'dir':ASC})
            else:
                raise Excepetion ('Unknown direction order modifier')
        ## some order algorithm
