
Task Orchestration Tools

	meta
		note that "Workflow Orchestration" seems to be a term more strongly associated with "business process automation" stuff, where we talk about capturing and automating business processess, especially the BPM stuff here: https://github.com/meirwah/awesome-workflow-engines
		 
	
		https://assets-global.website-files.com/5e46eb90c58e17cafba804e9/5f8f885195ca2b64eb6d462c_200027%20ON%20UV%20Workflow%20Orchestration%20White%20Paper.pdf
	
	https://docs.prefect.io/
		https://www.datarevenue.com/en-blog/what-we-are-loving-about-prefect
	
	https://temporal.io
		* Asynchronous Activity Completion
	
	https://nifi.apache.org/	
	
	https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/provenance/index.html
	
	airflow
		no attempt at versioning/provenance
	
	https://github.com/d6t/d6t-python
		bring airflow-style DAGs to the data science research and development process.
		https://github.com/d6t/d6t-python/blob/master/blogs/datasci-dags-airflow-meetup.md
		
	
	https://nipype.github.io/pydra/
		* Auditing and provenance tracking: Pydra provides a simple JSON-LD-based message passing mechanism to capture the dataflow execution activities as a provenance graph. These messages track inputs and outputs of each task in a dataflow, and the resources consumed by the task.
	
	https://www.digdag.io/
	
	https://substantic.github.io/rain/docs/quickstart.html
	
	https://github.com/insitro/redun
	
	https://github.com/sailthru/stolos
	
	https://www.nextflow.io/
		dataflow dsl ...

	https://github.com/ovh/celery-director



interesting libs related to luigi, rougly ordered from most interesting to least:
	
	https://github.com/boschglobal/luisy
		- active, ci, tests 
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

















