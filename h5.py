import h5py
import numpy as np
f=h5py.File("model.txt",'r')
print("Keys: %s"%f.keys())
def dfs(layer,x):
    if type(x)==type(0.5) or type(x)==type(1):
        return
    else:
        print(layer,x)
        try:
            for each in x:
                if type(each)==type("a"):
                    dfs(layer+1,x[each])
        except:
            pass
dfs(0,f['model_weights'])
dfs(0,f['optimizer_weights'])

a=f["model_weights"]["secret_layer"]

