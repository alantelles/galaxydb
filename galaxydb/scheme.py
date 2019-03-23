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
        
    def delete_scheme(self):
        done = False
        while not done:
            opt = input("Are you really sure you want to delete the scheme {} and all related files? (Y/n)".format(self.name))
            if opt == ('Y'):
                opt = input("This option can't be undone. Are you really sure? (Y/n)")
                if opt == ('Y'):
                    print("OK! Deleting the scheme, pages and any related files")
                    self.load_scheme()
                    addr = self.sch['locations']['address']+os.sep+self.name+ADDR_EXT
                    print("Deleting address file")
                    if os.path.exists(addr):
                        os.remove(addr)
                    table = self.sch['locations']['table']+os.sep+self.name
                    print('Deleting pages')
                    for f in os.listdir(table):
                        if f.endswith(TBL_EXT):
                            print("Deleting page {}".format(f))
                            if os.path.exists(table+os.sep+f):
                                os.remove(table+os.sep+f)
                    print('Deleting table folder {}'.format(table))
                    os.rmdir(table)
                    print('All scheme files were deleted')
                    done = True
                else:
                    print("The options are 'Y' or 'n'. Care the case, please")
            elif opt == ('n'):
                print ("You choose NO. No files were touched")
                done = True
            else:
                print("The options are 'Y' or 'n'. Care the case, please")
    
    def create (self,type_defs,max_values={},locations={}): # max_values is a dict
        self.sch = dict()
        #id_t = TypeDef('id',INT,size=max_regs,NULL=0,PRIMARY_KEY=True,AUTO_INC=True)
        type_defs.insert(0,Column('id',INT,AUTO_INC=1,PRIMARY_KEY=True))
        #columns = {}
        columns = []
        
        maxes = {}
        for i,j in enumerate(type_defs):
            j.params['name'] = j.name.strip()
            j.params['col_id'] = len(columns)
            columns.append(j.params)
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
            self.sch['locations']['table'] = TABLES
        if not 'address' in locations:
            self.sch['locations']['address'] = TABLES+os.sep+self.name
        if not 'trash' in locations:
            self.sch['locations']['trash'] = TABLES+os.sep+self.name
        
    def __str__(self):
        out='Scheme: {}\n'.format(self.name)
        for i,j in self.sch.items():
            out+='Column: '+i+'\n'
            for k,l in j.items():
                out+='    '+k+': '+str(l)+'\n'
        return out
        
    #alter methods
    
    def alter(self,group,param,new):
        if group == 'location':
            self.alter_location(param,new)
        elif group == 'column':
            self.alter_column(param,new)
        pass
    
    def alter_location(self,param,new):
        self.load_scheme()
        if new.find('file://') == 0:
            new = new[len('file://'),:]
        self.sch['locations'][param] = new
        self.save_scheme(True)
        
    def alter_column(self,column,new):
        if column == 'id':
            raise Exception ("You can't alter 'id' field. It's a core of data storage and can't be changed. Do this will break all your database")
        self.load_scheme()
        if 'name' in new and new['name'] == 'id':
            print("You can't name other field as 'id'. This modification was dropped from list.")
            del new['name']
        if 'col_id' in new:
            print("You can't change 'col_id' parameter. It's a core of data storage and do this will break your database. This modification was dropped from list.")
            del new['col_id']
        for i in self.sch['columns']:
            if column == i['name']:
                for j,k in new.items():
                    i[j] = k
                    self.save_scheme(True)
                break
        else:
            print("Column {} doesn't exist in scheme {}".format(column,self.name))
    
    #end alter methods
    def save(self,log=False):
        self.save_scheme(log)
        
    def save_scheme(self,log=False):
        if log:
            print('Saving scheme "{}"'.format(self.name))
        with open(self.sch_path,'wt') as f:
            json.dump(self.sch,f)
            if log:
                print('Scheme {} saved in {}'.format(self.name,self.sch_path))
        if log:
            print('Details: ')
            with open(self.sch_path,'rt') as f:
                parsed = json.load(f)
                print(json.dumps(parsed,indent=4,sort_keys=True))
        for i,j in self.sch['locations'].items():
            if not os.path.isdir(j):
                os.mkdir(j)
