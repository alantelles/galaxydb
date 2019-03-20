from galaxydb.table import Table
from galaxydb.logic import Logic
class User (Table):
    def __init__(self):
        name = 'users'
        super(User, self).__init__(name)
    def login(self,username,password):
        x = Logic()
        log = x.logic_and(x.eq('username',username),x.eq('password',password))
        return self.filter(log).first()
        
