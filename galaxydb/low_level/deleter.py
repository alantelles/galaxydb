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
        trash_path = self.scheme['locations']['trash']+os.sep+self.name+TRASH_EXT
        if os.path.isfile(trash_path):
            self.trash = open(trash_path,'rb+')
        else:
            self.trash = open(trash_path,'wb')
        
    def delete_by_id(self,id):
        max_cols = self.scheme['max_values']['max_cols']
        max_regs = self.scheme['max_values']['max_regs']
        max_pages = self.scheme['max_values']['max_pages']
        max_page_size = self.scheme['max_values']['max_page_size']
        self.addr.seek(0)
        self.trash.seek(0,2)
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
                if from_bytes_e(id_b) == id:
                    end_field = k.find(FIELD,pos_field+len(FIELD))
                    if end_field == -1:
                        end_field = k.find(FILE_END,pos_field+len(FIELD))
                    sub_bytes = k[pos_field:end_field]
                    len_length = len(sub_bytes[len(FIELD)+max_cols+max_regs+max_pages+max_page_size:])
                    trash = FIELD
                    trash += to_bytes_e(2**(8*max_cols)-1,max_cols)
                    self.addr.seek(pos_field)
                    trash_mark = TRASH+to_bytes_e(pos_field,0)+VALUE+to_bytes_e(len(sub_bytes),0)
                    self.trash.write(trash_mark)
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
        self.trash.close()
