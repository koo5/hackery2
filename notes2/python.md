# CLI
	fire and click both have their uses, fire is more quick and dirty.
### fire	
https://github.com/google/python-fire
### click
https://click.palletsprojects.com/



# UI
https://github.com/willmcgugan/textual

	reactivity on the desktop! Never tried but looks fun.
	
	
	
# web gui frameworks
never tried.	
### https://github.com/dddomodossola/remi
	
### https://www.nagare.org/
	"back and fork", cute
	
### https://holoviz.org/
	
	

# configuration management

https://www.dynaconf.com/

https://hydra.cc/docs/intro/
	




# debugging
```
# def tr():
# 	try:
# 		import sys
# 		sys.path.append('/app/sources/internal_workers/pydevd-pycharm.egg')
# 		import pydevd_pycharm
# 		pydevd_pycharm.settrace('172.17.0.1', port=12345, stdoutToServer=True, stderrToServer=True)
# 	except Exception as e:
# 		logging.getLogger().info(e)


```
https://github.com/jlubcke/pytest-pycharm

	Plugin for py.test to enter PyCharm debugger on uncaught exceptions




# profiling

	time python3 -m cProfile -o ooo <file>; pyprof2calltree -o oooo -i ooo; kcachegrind oooo


### https://github.com/benfred/py-spy

### https://functiontrace.com/

### https://profiler.firefox.com/

### https://github.com/jlfwong/speedscope


	

# misc
### TriOptima/tri.struct
tri.struct supplies classes that can be used like dictionaries and as objects with attribute access at the same time

https://github.com/TriOptima/tri.struct

see also (my) dotdict.



[:keyphrase "for each line of input:";
:code [
:lang :python;
:contents """
import sys
for line in sys.stdin.readlines():
"""]]


[:keyphrase "standard_python_header"
:code """#!/usr/bin/env python3"""
:note """"coding" no longer necessary, with python 3"]

[:contents """
how to activate a virtualenv in a child shell:
bash --init-file "venv/bin/activate"
fish -C ". venv/bin/activate.fish"
"""].
```

https://news.ycombinator.com/item?id=28880782


## if you want to see current env:
#import sys
#print(sys.path)
#p = subprocess.Popen(['bash', '-c', 'export'], universal_newlines=True)
#p.communicate()




# typing

	https://www.reddit.com/r/Python/comments/qlotne/github_beartypebeartype_unbearably_fast_o1/
	







# rdf and rdf orm stuff
```
	dead:
		owl and stuff:
			https://pythonhosted.org/ordf/index.html
		https://github.com/oldm/OldMan
		http://www.openvest.com/trac/wiki/RDFAlchemy
	maintained:
		SuRF


	pydatalog


	https://pypi.org/project/properties/
```


