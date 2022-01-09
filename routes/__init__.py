import os, glob

files = [item[item.rindex("/")+1:item.rindex(".")] for item in glob.glob(os.getcwd()+"/routes/*.py")]
files.remove("__init__")

for f in files: 
	exec(f"from routes import {f}")