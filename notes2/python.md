# CLI
	## fire	
		https://github.com/google/python-fire
	## click
		https://click.palletsprojects.com/



# UI
	https://github.com/willmcgugan/textual
		reactivity on the desktop!
	
	
	
# web gui frameworks
	
	https://github.com/dddomodossola/remi
	
	https://www.nagare.org/
		"back and fork", cute
	
	https://holoviz.org/
	
	

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



[a :note; :contents """
https://github.com/jlubcke/pytest-pycharm
Plugin for py.test to enter PyCharm debugger on uncaught exceptions
"""].

```



# profiling

	time python3 -m cProfile -o ooo <file>; pyprof2calltree -o oooo -i ooo; kcachegrind oooo

	===

	https://github.com/benfred/py-spy

	==


	https://functiontrace.com/ https://profiler.firefox.com/


	===

	https://github.com/jlfwong/speedscope


	===

	stay away from:
	?


	

# misc
```
[a :note; :contents """
TriOptima/tri.struct
tri.struct supplies classes that can be used like dictionaries and as objects with attribute access at the same time
https://github.com/TriOptima/tri.struct
see also my dotdict
"""].


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
	


# task queues


## airflow?
## fireworq?


## huey
	monitoring -- https://pypi.org/project/django-huey-monitor/
	Immediate mode - not useful when i have a separate webserver trigerring the tasks

## RQ
	monitoring -- https://github.com/Parallels/rq-dashboard

	| For testing purposes, you can enqueue jobs without delegating the actual execution to a worker (available since version 0.3.1). To do this, pass the is_async=False argument into the Queue constructor

	"register its own death." => register a failed task for retrying?

	| kill -9, which will not give the workers a chance to finish the job gracefully or to put the job on the failed queue. Therefore, killing a worker forcefully could potentially lead to damage.
		eew

	By default, jobs should execute within 180 seconds.




## MRQ
	RQ fork
	looks great but python2 only?
	monitoring - https://mrq.readthedocs.io/en/latest/dashboard/
	https://pythonrepo.com/repo/pricingassistant-mrq-python-working-with-event-and-task-queues


## dramatiq
	no monitoring

## remoulade
	dramatiq fork
	monitoring -- https://github.com/wiremind/super-bowl
		vue


## TaskTiger
	no monitoring


## celery

	RDB!
		https://www.youtube.com/watch?v=0LOytHKMSz0
		this explains a lot. I had huge trouble trying to debug my celery tasks.
		still it's a question if i'll be able to make pycharm connect to that and do "normal" graphical debugging / break on exceptions...

	```
	from celery import current_app
	current_app.conf.CELERY_ALWAYS_EAGER = True
	current_app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
	Doing so makes celery execute in the same thread as the currently executing thread.
	```
		- https://stackoverflow.com/questions/29312809/how-do-i-enable-remote-celery-debugging-in-pycharm



	worker_max_tasks_per_child = 1

	https://youtu.be/ceJ-vy7fvus?t=811
		-Ofair
		app.task_acks_late = True
		app.worker_prefetch_multiplier = 1 # CELERY_PREFETCH_MULTIPLIER

	ALWAYS_EAGER
		| The above code runs without an active worker and executes fib(8) synchronously within the same process. You may know this behaviour from Celery as ALWAYS_EAGER

	joining all tasks is called "chord"

	| If you call the group, the tasks will be applied one after another in the current process
		what?

	https://youtu.be/Bo6UtRhedjE?t=557
		interesting idea, only import your code when task is starting - avoid need for reloads of whole worker

	https://youtu.be/Bo6UtRhedjE?t=912
		paralleling task states in an sql table, this would be useful....

	https://www.youtube.com/watch?v=V6XRf457Es8
		declarative dataflows





## note also
	https://www.rabbitmq.com/networking.html




## non-python
	Bull

		focusing on atomicity

		several frontends

		| Nest provides the @nestjs/bull package as an abstraction/wrapper on top of Bull, a popular, well supported, high performance Node.js based Queue system implementation. The package makes it easy to integrate Bull Queues in a Nest-friendly way to your application.

		probably uses JSON for serialization, right?:-)


# workflow orchestration
	https://news.ycombinator.com/item?id=14555740




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



# dependency management
## Python Package Management is a Nightmare!
https://medium.com/@damngoodtech/the-great-python-package-management-war-49f25df33d26
## setup.py, setup.cfg, requirements.txt, Pipfile, pyproject.toml – oh my!
https://venthur.de/2021-06-26-python-packaging.html
## Managing Python Dependencies – Everything You Need To Know 
https://www.activestate.com/resources/quick-reads/python-dependencies-everything-you-need-to-know/

## my plan (?)
### 1) use apt or `pip install --user` to install exclusively python package management tools
#### pipreqs
```pip install pipreqs```
| Create a requirements.in file and list just the direct dependencies of your app. 
```pipreqs --savepath requirements.in```


#### https://pypa.github.io/pipx/
| pipx — Install and Run Python Applications in Isolated Environments
```
python3 -m pip install --user pipx
pipx ensurepath
register-python-argcomplete --shell fish pipx >~/.config/fish/completions/pipx.fish

```

### venv as usual
```
virtualenv -p /usr/bin/python3.10 venv
. venv/bin/activate.fish
```
where python3.10 obviously magically corresponds to the python version inside your dockers or whatever..




#### pip-tools must go inside the venv
```
pip install pip-tools
```

| pip-compile command lets you compile a requirements.txt file from your dependencies, specified in either pyproject.toml, setup.cfg, setup.py, or requirements.in.
pip-tools seems to require a virtualenv and to be installed in that virtualenv .. will see.. but i guess it's reasonable to always maintain a virtualenv even for pycharm etc..
```
pip-compile --resolver=backtracking
```

