from ..constants import *
from ..statics import *
import os, re
class Deleter:
    pass
    def __init__(self,name,scheme):
        self.name = name
        self.scheme = scheme
        addr_path = self.scheme['locations']['address']+os.sep+self.name+ADDR_EXT
        self.addr = open(addr_path,'rb+')
        addr_trash_path = self.scheme['locations']['addr_trash']+os.sep+self.name+ADDR_TRASH_EXT
        data_trash_path = self.scheme['locations']['data_trash']+os.sep+self.name+DATA_TRASH_EXT
        if os.path.isfile(data_trash_path):
            self.data_trash = open(data_trash_path,'rb+')
        else:
            self.data_trash = open(data_trash_path,'wb')
        if os.path.isfile(addr_trash_path):
            self.addr_trash = open(addr_trash_path,'rb+')
        else:
            self.addr_trash = open(addr_trash_path,'wb')
        
    def delete_by_id(self,id):
        max_cols = self.scheme['max_values']['max_cols']
        max_regs = self.scheme['max_values']['max_regs']
        max_pages = self.scheme['max_values']['max_pages']
        max_page_size = self.scheme['max_values']['max_page_size']
        self.addr.seek(0)
        self.addr_trash.seek(0,2)
        self.data_trash.seek(0,2)
        k = self.addr.read(BUF)
        if len(k) == BUF:
            k = read_until(self.addr.read,FIELD)
        where = self.addr.tell()
        offset = 0
        while k:
            pos_field = k.find(FIELD,offset)
            while pos_field > -1: 
                #pos_field address all fields
                id_b = k[pos_field+len(FIELD)+max_cols:pos_field+len(FIELD)+max_cols+max_regs]
                #9191 0 0 0 000 00 9494 9191
                if from_bytes_e(id_b) == id:
                    end_field = k.find(FIELD_END,pos_field+len(FIELD))
                    sub_bytes = k[pos_field:end_field+len(FIELD_END)]
                    data_trash = {
                        'page':sub_bytes[len(FIELD)+max_cols+max_regs:len(FIELD)+max_cols+max_regs+max_pages],
                        'addr':sub_bytes[len(FIELD)+max_cols+max_regs+max_pages:len(FIELD)+max_cols+max_regs+max_pages+max_page_size],
                        'length':sub_bytes[len(FIELD)+max_cols+max_regs+max_pages+max_page_size:-len(FIELD_END)]
                    }
                    data_trash_dump = TRASH+data_trash['page']+data_trash['addr']+data_trash['length']+FIELD_END
                    trash_mark = TRASH+to_bytes_e(pos_field,0)+VALUE+to_bytes_e(len(sub_bytes),0)+FIELD_END
                    trash = FIELD
                    trash += to_bytes_e(2**(8*max_cols)-1,max_cols) ## 0xFF in a column
                    self.addr.seek(pos_field)
                    self.addr_trash.write(trash_mark)
                    self.data_trash.write(data_trash_dump)
                    # records the address and length of a deleted register in address file
                    #self.addr.seek(len(trash),1) #teste
                    self.addr.write(trash)
                    
                offset = pos_field+len(FIELD)
                pos_field = k.find(FIELD,offset)
            self.addr.seek(where)
            k = self.addr.read(BUF)
            where = self.addr.tell()
        pass
    
    def close_deleter(self):
        self.addr_trash.seek(0,2)
        self.addr_trash.write(TRASH)
        self.addr_trash.close()
        self.data_trash.seek(0,2)
        self.data_trash.write(TRASH)
        self.data_trash.close()
