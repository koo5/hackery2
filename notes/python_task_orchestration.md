
Task Orchestration Tools

	meta
		note that "Workflow Orchestration" seems to be a term more strongly associated with "business process automation" stuff, where we talk about capturing and automating business processess, especially the BPM stuff here: https://github.com/meirwah/awesome-workflow-engines
		 
	
		(https://assets-global.website-files.com/5e46eb90c58e17cafba804e9/5f8f885195ca2b64eb6d462c_200027%20ON%20UV%20Workflow%20Orchestration%20White%20Paper.pdf)
	
	https://prefect.io/
		https://www.datarevenue.com/en-blog/what-we-are-loving-about-prefect
        scheduling
        retries
        logging
        caching
        notifications
        observability
        All tasks must be called from within a flow. Tasks may not call other tasks directly.

	
	https://nifi.apache.org/	
        seems like a nice rich dataflow-based plumbing engine, would be exciting to play with
        Data Provenance
        
            NiFi automatically records, indexes, and makes available provenance data as objects flow through the system even across fan-in, fan-out, transformations, and more. This information becomes extremely critical in supporting compliance, troubleshooting, optimization, and other scenarios.
        Recovery / Recording a rolling buffer of fine-grained history
        
            NiFi’s content repository is designed to act as a rolling buffer of history. Data is removed only as it ages off the content repository or as space is needed. This combined with the data provenance capability makes for an incredibly useful basis to enable click-to-content, download of content, and replay, all at a specific point in an object’s lifecycle which can even span generations.

	
	https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/provenance/index.html
	
	airflow
		no attempt at versioning/provenance
	
	https://github.com/d6t/d6t-python
		bring airflow-style DAGs to the data science research and development process.
		https://github.com/d6t/d6t-python/blob/master/blogs/datasci-dags-airflow-meetup.md
        * Instead of having to manually load and save data, this is outsourced to the library
        * intelligently rerun workflow after changing a parameter. Parameters are passed from the target task to the relevant downstream task. 
		
	
	https://nipype.github.io/pydra/
		* Auditing and provenance tracking: Pydra provides a simple JSON-LD-based message passing mechanism to capture the dataflow execution activities as a provenance graph. These messages track inputs and outputs of each task in a dataflow, and the resources consumed by the task.
	

	https://substantic.github.io/rain/docs/quickstart.html
	
	https://github.com/insitro/redun
	
	https://github.com/sailthru/stolos
	
	https://www.nextflow.io/
		dataflow dsl ...

	https://github.com/ovh/celery-director

    cadence
        memory that is not linked to a specific process, and preserves the full application state, including function stacks

	
	https://temporal.io
		* Asynchronous Activity Completion
        * seems more of a dataflow framework, no backtracking  (but backpressure :) )
        * rest api based

    https://dolphinscheduler.apache.org/
        Dingtalk
        task dependency in the form of conditional execution
        nice web ui

    https://www.digdag.io/
        kinda an application server, expects that you submit archives with code

    https://docs.ray.io/en/latest/ray-core/walkthrough.html
        smells like celery

interesting libs related to luigi, rougly ordered from most interesting to least:
	

    https://github.com/riga/law
        - now those are some nice additions
        * Environment sandboxing, configurable on task level 
        * Remote targets with automatic retries and local caching
        - this means we can fetch result files automatically...


	https://github.com/boschglobal/luisy
		- active, ci, tests 
        - opinionated about where data goes

		* luisy has a smart way of passing parameters between tasks
		* luisy can just download results of pipelines that were already executed by others
		* Decorating your tasks is enough to define your read/write of your tasks
		* Hash functionality automatically detects changes in your code and deletes files that are created by deprecated project versions
		* Testing module allows easy and quick testing of your implemented pipelines and tasks


	https://github.com/pharmbio/sciluigi
		- active, vm, ...
		* Separation of dependency definitions from the tasks themselves, for improved modularity and composability.
		* Inputs and outputs implemented as separate fields, a.k.a. "ports", to allow specifying dependencies between specific input and output-targets rather than just between tasks. This is again to let such details of the network definition reside outside the tasks.
	
	
	https://github.com/riga/law
		* Remote targets with automatic retries and local caching
		* Automatic submission to batch systems from within tasks
		* Environment sandboxing, configurable on task level
	
	
	https://github.com/kyocum/disdat-luigi/tree/master
		* Simplified pipelines -- Users implement two functions per task: requires and run.
		* Enhanced re-execution logic -- Disdat re-runs processing steps when code or data changes.
		* Data versioning/lineage -- Disdat records code and data versions for each output data set.
		* Share data sets -- Users may push and pull data to remote contexts hosted in AWS S3.
		* Auto-docking -- Disdat dockerizes pipelines so that they can run locally or execute on the cloud.

	https://pypi.org/project/funsies/
		* The design of funsies is inspired by git and ccache. All files and variable values are abstracted into a provenance-tracking DAG structure.

		
	https://github.com/gityoav/pyg-cell	
		* saves and persists the data in nicely indexed tables with primary keys decided by user, no more any nasty key = "COUNTRY_US_INDUSTRY_TECH_STOCK_AAPL_OPTION_CALL_EXPIRY_2023M_STRIKE_100_TOO_LONG_TICKER"
		*  allows you to save the actual data either as npy/parquet/pickle files or within mongo/sql dbs as doc-stores.		
	
	https://pypi.org/project/luigi-tools/
		* --rerun parameter that forces a given task to run again
		* remove the output of failed tasks which is likely to be corrupted or incomplete
		...
	
	
	
	
	https://github.com/datails/ruig   
	
	
	
	
	
	https://github.com/pollination/queenbee
	
	
	https://github.com/m3dev/gokart
	
	
	https://github.com/madconsulting/datanectar
		* dynamically available API for HTTP based task execution
		* target locations based on project-level code locations     
		* ..
	
	
	https://pypi.org/project/curifactory/
		* Adds a CLI layer on top of your codebase, a single entrypoint for running experiments
		* Automatic caching of intermediate data and lazy loading of stored objects
		* Jupyter notebook output for further exploration of an experiment run
		* Docker container output with copy of codebase, conda environment, full experiment run cache, and jupyter run notebook
		* HTML report output from each run with graphviz-rendered diagram of experiment
		* Easily report plots and values to HTML report
		* Configuration files are python scripts, allowing programmatic definition, parameter composition, and parameter inheritance
		* Output logs from every run
		* Run experiments directly from CLI or other python code, notebooks, etc.
		
	
	https://github.com/WithPrecedent/chrisjen
	
	
	https://github.com/pwoolvett/waluigi/blob/master/waluigi/tasks.py
	
	
		
	https://github.com/maurosilber/donkeykong/blob/master/donkeykong/scripts/invalidate.py
	
	
	
	https://github.com/miku/gluish
		minor wrapping and subclasses for conventions / automanaging input/output filenames
		utilities for
			dealing with datetimes
			running shell commands inside tasks
			tsv format data
			
			
		
	https://github.com/bopen/mariobros


	notes:
		A lot of these wrappers / extensions seems to involve conventions and automation of input/output file pathing/naming, and making task parameters a part of those names, in order to make artifacts uniquely related to an exact configuration used to run the pipeline. 
		
		I'm not sure i can actually frame our requirements in terms of a "data pipeline", even if there is some resemblance.



# purely function composition i guess:
	https://github.com/aitechnologies-it/datafun
	https://www.root.cz/clanky/knihovna-polars-vykonnejsi-alternativa-ke-knihovne-pandas-line-vyhodnocovani-operaci/#k15
	https://pypi.org/project/graphtik/
	https://github.com/hazbottles/flonb
	https://pypi.org/project/pydags/
		
		
## function graph search / typing libs / inputs / outputs 
### non-python
* https://www.commonwl.org/user_guide/
* https://sourceforge.net/projects/conversio/
* https://web.archive.org/web/20040930065210/http://libs.sourceforge.net/user/welcome.php
* https://fno.io/
* https://github.com/aindilis/cfo
* https://frdcsa.org/~andrewdo/software/domains.lisp
* https://github.com/w3c/N3/blob/51f370ffb880effb089190076b956d16035f4ea3/files/builtin%20definitions/builtins.n3




# task queues

## meta
	https://news.ycombinator.com/item?id=14555740
	https://www.reddit.com/r/Python/comments/ugkja3/what_is_your_favourite_task_queuing_framework/


## airflow? -> see task orchestration
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

    https://github.com/ovh/celery-director
        declarative dataflows
	    https://www.youtube.com/watch?v=V6XRf457Es8
		


## note also
	https://www.rabbitmq.com/networking.html
	https://github.com/antirez/disque



## non-python
	Bull

		focusing on atomicity

		several frontends

		| Nest provides the @nestjs/bull package as an abstraction/wrapper on top of Bull, a popular, well supported, high performance Node.js based Queue system implementation. The package makes it easy to integrate Bull Queues in a Nest-friendly way to your application.

		probably uses JSON for serialization, right?:-)






# RPC / remote object access between python processess
pizco.  
Qt-like (and Qt compatible!) signal and slot mechanism.
https://github.com/hgrecco/pizco/tree/_multiobject
The multiobject branch seems unfinished, repeating functionality and was made against an old version. The file isnt long,
keeping intact some of the pizco functionality like 'instantiate' could require more investigation
and not sure if worth it. (at least for a start i could drop "instantiate"). The things touching the io loop
are a bit arcane, maybe the gevent fork can help. 
Other option is to not rpc so seamlessly, give up on seamless object/attribute access and make the interface from method calls.
At any case, the priority of splitting lemon into rpcing components has decreased, as ive optimized it to run quite nicely as a single process (with marpa in a thread). Disorganized notes follow.

zerorpc 
doesnt have any remote attributes. Other libraries seem to be even worse, requiring
various declarations and stuff. One thing zerorpc has is streaming generators.


misc
http://morepypy.blogspot.cz/2014/11/tornado-without-gil-on-pypy-stm.html
http://nanomsg.org/

http://zeromq.github.io/pyzmq/eventloop.html
http://www.tornadoweb.org/en/stable/ioloop.html
https://github.com/zeromq/pyzmq/blob/master/zmq/eventloop/minitornado/ioloop.py
https://github.com/hgrecco/pizco/pull/22
http://twistedmatrix.com/documents/13.0.0/core/howto/threading.html

debugging the rpc server code under tornado io loop: give up trying to make it propagate exceptions,
get a scriptable debugger (unlike pycharms..)

http://nbviewer.ipython.org/gist/ChrisBeaumont/5758381/descriptor_writeup.ipynb
http://stackoverflow.com/a/26096355
http://www.tornadoweb.org/en/stable/guide/coroutines.html

"""can a client be a server at the same time? question of event loops integration i think
a not so neat but okay alternative for the distributed event handling:
make the nonlocal client frames in keybindings.py stubs that raise an error
catch and proceed to emit a signal with that event on the server (implemented in pizco in one of the forks/branches?)
then all clients try it again? or more organized, at the moment its just root and menu,
 so 'all' would work, if there will be multiple editor clients, we can have 'last active editor'
...?.?.?"""



"""
general ways that rpcing complicates things;

have to do more effort at proper mvc-y eventing, This would in some form be
necessary for best performance anyway (keeping track of dirtiness at various levels.
But the split between the server and client part of frames isnt nice..

proxying elements: wont be a performance hit, if it will, it can be easily stubbed
proxy_this() and deproxy() have to be in places tho

"""




       # lets try setting a reasonable rpc timeout on the proxy
       #and wrapping everything in a try except catching the timeout?
       #also, i will be adressing the server objects explicitly
       #instead of instantiating the client frames with references to the server counterparts
       #this way it will be easier to have it survive a reconnect/server restart..



required features of the pizco fork:
no separate remoteattribute: Proxy has a path - a list of attribute names,
and handles all accesssess. 
boxing: 



or..actually..zerorpc?
no attribute access -> what must be wrapped in functions?
signals?
"boxing":quick dumb values for when the client only needs to pass them back later
 in the serializer



""" this will be the responsibility of pizco/serialization
proxied = WeakValueDictionary()
key_counter = 0
# distributed computing is fun.
# lets work with the theoretical possibiliy that the counter
# will overflow (makes me feel a bit easier than a runaway bignum)
# the point is that we want to be sure what object the client is talking about.
# ids can repeat. This doesnt save the clients from sending events while their data is
# outdated, but at least it cant seem they reference a different object than they mean.
#
def proxy_this(v):
       global key_counter
       while key_counter in proxied:
               key_counter += 1
       proxied[key_counter] = v
       return key_counter
"""



#total split or threading? 
https://wiki.python.org/moin/GlobalInterpreterLock
http://pypy.readthedocs.org/en/latest/stm.html

add --server to main_sdl and main_curses

accepts tcp connection, creates some 
client object
  .proxy is a weakref dict from some int

for tag in tags:
  if type(tag) == ElementTag:
    proxy[len(proxy)] = weakref(node)

incrementing render(transmission) id







protocols:

http://www.jsonrpc.org/specification
https://github.com/grpc/grpc
https://thrift.apache.org/tutorial/



serialization:
http://www.oilshell.org/blog/2017/01/09.html
http://cbor2.readthedocs.io/en/latest/usage.html
https://github.com/slisznia/pcos
https://en.wikipedia.org/wiki/Apache_Avro
https://github.com/google/flatbuffers
https://developers.google.com/protocol-buffers/docs/techniques

unsuitable:swagger


misc:
https://code.visualstudio.com/blogs/2016/06/27/common-language-protocol
https://cloud.google.com/speech/reference/rpc/




jena,redis,rethink




https://pypi.python.org/pypi/ladon



kafka
	https://hackernoon.com/a-super-quick-comparison-between-kafka-and-message-queues-e69742d855a8?gi=e965191e72d0



https://pydoit.org/

https://github.com/Lancetnik/Propan





---
I disqualified dramatiq on the basis of missing a monitoring solution. See its sucessor, remoulade + superbowl, i'm happy with them so far, and it seems to be the only option here that offers monitoring.
I disqualified RQ on the basis of being unreliable by design, ARQ is apparently a sucessor of RQ that "fixes" that problem.

Now the issue of calling the "worker code" by name VS having to import the worker codebase into the "calling" code is something to think about, with pros and cons. Calling by name seems cleaner wrt code organization, but importing potentially offers the benefits of type-checking, IDE navigation, etc. Just saying.

As on interoperability with different languages, remoulade docs already say:
```All you have to do is push a JSON-encoded dictionary containing the following fields to your queue:
{
  "queue_name": "default",     // The name of the queue the message is being pushed on
....
```

But repid definitely looks nice, being "inspired by dramatiq and arq", and with some modern and possibly cleaner practices.

Some of these options are more "down to the metal", some with "middlewares" that offer AOP-style extensions/abstraction. You need to make you own choice in that regard. And maybe one day we can have a cross-task-queue monitoring solution.....
---


https://tkte.ch/chancy/#similar-projects


