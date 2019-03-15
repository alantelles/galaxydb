ALL = ('id','>',0)
class Logic:
    def __init__(self):
        pass
    def eq(self,field,val):
        return (field,'=',val)
    
    def not_eq(self,field,val):
        return (field,'!=',val)
    
    def less(self,field,val):
        return (field,'<',val)
        
    def less_eq(self,field,val):
        return (field,'<=',val)
    
    def big(self,field,val):
        return (field,'>',val)
        
    def big_eq(self,field,val):
        return (field,'>=',val)
        
    def is_in(self,field,vals):
        #l.is_in('username',['alantelles','kelicris'])
        tests = []
        for i in vals:
            tests.append((field,'=',i))
        return self.l_or(*tests)
    
    def is_not_in(self,field,vals):
        tests = []
        if len(vals) > 0:
            for i in vals:
                tests.append((field,'!=',i))
        else:
            tests.append(ALL)
        return self.l_and(*tests)
        
    def l_or(self,*l):
        ret = ['or']
        for i in l:
            ret.append(i)
        return ret
        
    def l_and(self,*l):
        ret = ['and']
        for i in l:
            ret.append(i)
        return ret
    
    def between(self,field,val1,val2):
        return ['and',self.big_eq(field,val1),self.less_eq(field,val2)]
    
    def like(self,field,val,pos=None):
        if pos == 'x...':
            return (field,'LIKE%',val)
        elif pos == '...x':
            return (field,'%LIKE',val)
        else:
            return (field,'LIKE',val)
