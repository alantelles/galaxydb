from .column import Column
import os
import json
from .constants import *
from .statics import *
class Scheme:
    def __init__(self,name): # max_values is a dict
        self.name = name
        self.sch_path = SCHEMES+os.sep+self.name+'.json'
        pass
        
    def auto_inc(self,column):
        self.load_scheme()
        for i,j in enumerate(self.sch['columns']):
            if column['col_id'] == i:
                if AUTO_INC in column:
                    self.sch['columns'][i][AUTO_INC] += 1
                    self.save()
        self.load_scheme()
        return self.sch
        
    def load_scheme(self):
        name = SCHEMES+os.sep+self.name+'.json'
        with open(self.sch_path,'rt') as f:
            self.sch = json.load(f)
        return self.sch
    
    def create (self,type_defs,max_values={},locations={}): # max_values is a dict
        self.sch = dict()
        #id_t = TypeDef('id',INT,size=max_regs,NULL=0,PRIMARY_KEY=True,AUTO_INC=True)
        type_defs.insert(0,Column('id',INT,AUTO_INC=1,PRIMARY_KEY=True))
        #columns = {}
        columns = []
        
        maxes = {}
        for i,j in enumerate(type_defs):
            j.params['name'] = j.name
            j.params['col_id'] = len(columns)
            columns.append(j.params)
            #j.params['column'] = i+1
            #columns[j.name] = j.params
        #max_names = ['max_regs','max_cols', 'max_pages', 'max_page_size']
        for i,j in MAX_DEFAULT.items():
            if i in max_values:
                if max_values[i] != 0:
                    maxes[i] = max_values[i]
                else:
                    maxes[i] = j
            else:
                maxes[i] = j
        self.sch['columns'] = columns
        self.sch['max_values'] = maxes
        self.sch['locations'] = locations
        if not 'table' in locations:
            self.sch['locations']['table'] = TABLES+os.sep+self.name
        if not 'address' in locations:
            self.sch['locations']['address'] = TABLES+os.sep+self.name+os.sep+self.name+ADDR_EXT
        else:
            self.sch['locations']['address'] = locations['address']+os.sep+self.name+ADDR_EXT
        
    def __str__(self):
        out='Scheme: {}\n'.format(self.name)
        for i,j in self.sch.items():
            out+='Column: '+i+'\n'
            for k,l in j.items():
                out+='    '+k+': '+str(l)+'\n'
        return out
        
    def save(self):
        print('Saving scheme "{}"'.format(self.name))
        with open(self.sch_path,'wt') as f:
            json.dump(self.sch,f)
            print('Scheme {} saved in {}'.format(self.name,self.sch_path))
        print('Details: ')
        with open(self.sch_path,'rt') as f:
            parsed = json.load(f)
            print(json.dumps(parsed,indent=4,sort_keys=True))
        for i,j in self.sch['locations'].items():
            if not os.path.exists(j):
                os.mkdir(j)
