import json
import os
from .scheme import Scheme
from .low_level.recorder import Creator
from .low_level.retriever import Retriever
from .low_level.deleter import Deleter
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
        
    def all(self,columns=[],order_rule=(),as_namespace = RET_AS_NAMESPACE):
        self.data = []
        r = Retriever(self.name,self.scheme)
        ret = r.find_all(columns)
        self.data = ret[0]
        if len(order_rule) > 0:
            self.order(*order_rule)
        self.found_ids = ret[1]
        r.close_retriever()
        if (as_namespace):
            ret = []
            for i in self.data:
                ret.append(Namespace(**i))
            self.data = None
            self.found_ids = []
        return ret

# free conditional return methods    

#    def where(self,logic):
#    r = Retriever(self.name,self.scheme)
#        c = self.get_code_by_field(logic[0])
#        ret = r.find_records_by_field(logic[2],c,logic[1])
#        self.data = ret[0]
#        self.found_ids = ret[1]
#        r.close_retriever()
#        return self
        
    def filter (self,logic,columns=[]):
        self.data = []
        self.found_ids = []
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
        ret = r.find_records_by_field_sequential(columns,rel,*conds)
        if rel == 'and' and len(self.found_ids) > 0:
            res = []
            res_reg = []
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
        
#    def logic(self,*cond):
#        r = Retriever(self.name,self.scheme)
#        ret = r.find_records_by_field_sequential(cond[0],*cond[1:])
#        self.data = ret[0]
#        self.found_ids = ret[1]
#        r.close_retriever()
#        return self
        
# strictly built logic conditional methods            
    def find(self,val,columns=[],as_namespace=RET_AS_NAMESPACE):
        #val is any
        #columns is a list
        #as_namespace is a bool
        r = Retriever(self.name,self.scheme)
        k = r.find_record_by_id(val,columns)
        r.close_retriever()
        if not k == None:
            self.data = None
            self.found_ids = []
            if (as_namespace):
                return Namespace(**k)
            else:
                return k
        else:
            return None
        
#    def column_equals(self,field,val):
#        self.data = []
#        r = Retriever(self.name,self.scheme)
#        ret = r.find_records_by_field(val,self.get_code_by_field(field),'=')
#        self.data = ret[0]
#        self.found_ids = ret[1]
#        r.close_retriever()
#        return self

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
        self.data = None
        return k
        
    def first(self,as_namespace = RET_AS_NAMESPACE):
        k = self.data
        self.data = None
        if (as_namespace):
            return Namespace(**k[0])
        else:
            return k[0]
    
    def limit(self,first,length=0,as_namespace = RET_AS_NAMESPACE):
        if length != 0:
            self.data = self.data[first:first+length]
        else:
            self.data = self.data[first:]
        k = []
        for i in self.data:
            if (as_namespace):
                k.append(Namespace(**i))
            else:
                k.append(i)
        self.data = None
        return k

#delete methods
    def delete(self,logic):
        self.filter(logic)
        d = Deleter(self.name,self.scheme)
        for i in self.found_ids:
            d.delete_by_id(i)
        d.close_deleter()

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
        r = Creator(self.name,self.scheme)
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
    def order(self,direction,*rules):
        rules = list(rules)
        if not type(direction) == bool:
            rules.insert(0,direction)
            direction = ASC
        newlist = sorted(self.data, key=lambda k: ([k[x] for x in rules]), reverse=direction)
        self.data = newlist
        return self
        ## some order algorithm
    
    def zika(self):
        d = Deleter(self.name,self.scheme)
        d.close_deleter()
