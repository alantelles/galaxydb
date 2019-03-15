# columns names can't have characters forbidden in variables names
class Column:
    def __init__(self,name,val_type,**params):
        self.name=name
        self.params={}
        self.params['type'] = val_type
        for i,j in params.items():
            self.params[i] = j
    def __str__ (self):
        out=self.name+'\n'
        for i,j in self.params.items():
            out+=i+' -- '+str(j)+'\n'
        return out
