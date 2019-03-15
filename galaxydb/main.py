from table import Table
from datetime import datetime
st=datetime.now()
i = Table('users')
ds=[
    {'name':'Alan Telles','password':'mahailomahailo','username':'alantelles'},
    {'name':'Keli Pereira','password':'929292','username':'kelicris'},
    {'name':'Marina Pereira','password':'yutieor','username':'marinao'},
    {'name':'João Augusto','password':'jva','username':'jv'},
{'name':'Heber Passos','password':'hebinho','username':'hps'},
{'name':'Philipe Pinheiro','password':'daum2','username':'PH'},
{'name':'Nilson Nassion','password':'nilsao','username':'baiano'}
]
#i.insert(*ds)
print(i.all())
en=datetime.now()
print('Benchmark:',en-st)
