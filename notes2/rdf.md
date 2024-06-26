So, the main distinction to see is between the resources listed in these two files:

rdf_explore_manage.txt is about software that:
	* sees rdf as a method to encode graphs. There are graph visualizers.
	* allows you to explore rdf data in a tabular form. Subject predicate object columns, one row for each triple.
	* is like ontowiki, basically a readymade user application with a fixed-ish UI, and that just happens to use RDF underneath.
	* is specialized for editing RDFS/OWL ontologies

whereas rdf_forms.txt is about libraries that allow you to generate user interfaces for/from rdf data / generate user interfaces by writing rdf declarations

see also:
	https://github.com/koo5/understand_humans/tree/master/mrkev is about:
		augmented_text.txt



rdf_forms.txt:
		
	https://rdforms.org
		alive
		no shacl
		part of a larger suite:
			https://entrystore.org
			https://entryscape.com
		LGPL
		recommended?


	https://github.com/jmvanel/semantic_forms
		model driven form-based editing, useful as a framework for making rdf-stored data editable to users
		needs polishing, but recommended


	TBCME/TBCSE/TBCFE
		recommended, but expensive
		TBCFE and TBCSE are discontinued editions
		TBCFE dosen't support SWP or anything
		template engine with sparql:
			https://www.topquadrant.com/resources/technology/docs/swp-skos-broader.html
			https://www.topquadrant.com/technology/sparql-web-pages-swp/
		https://www.topquadrant.com/technology/graphql/
			seems buggy, can't even load a file
			many cool features: "We are planning to support syntax highlighted entry of SHACL Shapes in the next release (in addition to forms, etc.)."
			seems to be heavily aimed at editing ontologies in exactly-shaped forms rather than at working with arbitrary rdf data (can't even paste our data in)
		authors of http://datashapes.org/forms.html
			recommended
			SHACL
			only implemented in TBC?
			https://www.topquadrant.com/constraints-on-rdflists-using-shacl/
		https://uispin.org/
			not sure how is related to shacl, since spin is like a predecessor to shacl


	https://medium.com/@sdmonroe/vios-network-99488f5bf29d
		https://alpha.vios.network/?
		" A record is just an RDF resource URI and its DESCRIBE. Records are rendered by record handers (Angular templates) registered in the V.I. cloud. Record handlers can attach actions (e.g. buttons, an entire suite of actions, etc) "
		https://medium.com/@sdmonroe/vios-reference-implementation-3153a3d589cf
		""" The Data Relationships and YASGUI Lister (DARYL) is a reference implementation of the linked data browser concept used by VIOS Network. The DARYL features innovations introduced in several linked data browsers, including:
			Piggy Bank
			Simile
			Tabulator (see also)
			OpenLink Faceted Search
			Microsoft Pivot
			Parallax
			Razorbase
			Qanvas
			TFacets
			Sparqlis
		"""


	https://github.com/hypermedia-app/shaperone
		shacl
		
		
	https://metaphacts.com/product
		"""
		declarative Web components for end-user interaction and visualization, and publish dynamic REST services for external data consumption"""
		"Form-based authoring using customizable, flexible forms"

		https://aws.amazon.com/blogs/apn/exploring-knowledge-graphs-on-amazon-neptune-using-metaphactory/

		demo of browsing/search functionality:
			https://wikidata.metaphacts.com/resource/app:Examples
			https://wikidata.metaphacts.com/resource/wd:Q7187
			https://wikidata.metaphacts.com/resource/app:Start
			https://wikidata.metaphacts.com/resource/wd:Q766195
			https://wikidata.metaphacts.com/resource/app:LifeSciences
			https://wikidata.metaphacts.com/resource/?uri=http%3A%2F%2Fwww.metaphacts.com%2Fresource%2Fassets%2FOntodiaDiagrams
			https://wikidata.metaphacts.com/resource/app:FederationExamples


	https://www.cubicweb.org/
		interesting, recommended
		https://cubicweb.readthedocs.io/en/default/book/devweb/edition/form/#webform
		web app framework, higher-level than django
		data format compatible with rdf (EAV)
		export into rdf
			https://www.cubicweb.org/link/1347429?vid=rdf
		nice community
		seems kinda overcomplicated?
		```
		(16:19:43) matrix: <nchauvat> instead of overcomplicated, I would say underdocumented :)
		(16:19:59) matrix: <nchauvat> documentation is the target of version 3.29
		(16:20:29) matrix: <nchauvat> and client-side views are in the works to replace cubicweb.web
		(16:20:37) matrix: <nchauvat> it should make things simpler
		(16:20:45) matrix: <nchauvat> hopefully
		```
		extension seems bitrotten a bit:
			https://forge.extranet.logilab.fr/open-source/LDBrowser/cubicweb-browser-extension
			but see demo
				https://archive.fosdem.org/2019/schedule/event/collab_cwldbe/attachments/video/3348/export/events/attachments/collab_cwldbe/video/3348/nchauvat_cubicweb_ld_browser_demo.webm
				comparable to link-redux principle


		https://forge.extranet.logilab.fr/open-source/LDBrowser/sparqlexplorer
			https://forge.extranet.logilab.fr/culture/culture-views/-/blob/branch/default/src/bienCulturelClass/bienCulturelClass.tsx
			how does it compare to link-redux exactly?
		https://open-source.pages.logilab.fr/LDBrowser/logilab-views/			


	LDBrowser
		https://forge.extranet.logilab.fr/open-source/LDBrowser/libview/-/blob/branch/default/src/rdf-entities.ts
		not sure what's that about


	https://wiki.duraspace.org/display/ld4lLABS/The+VitroLib+Metadata+Editor
		"Vitro is a general-purpose web-based ontology and instance editor with customizable public browsing. "


	https://sinopia.io
		editor, requires registration
		has a system of editable form templates
		probably only browsing strictly by these templates


	ontowiki
		recommended
		dead, needs maintenance, but seems well-developed, and works, and installation is fairly easy
		on ubuntu 18.04:
			https://vitux.com/how-to-install-php5-and-php7-on-ubuntu-18-04-lts/
			http://docs.ontowiki.net/Ubuntu-Quick-Install-Guide.html
			sudo apt-get install php5.6-xml php5.6-mbstring
			sudo apt install virtuoso-opensource
			sudo systemctl restart apache2
			http://docs.ontowiki.net/Getting-Started-Users.html
		https://github.com/AKSW/cubeviz.ontowiki
		
	ecceneca
		https://documentation.eccenca.com/blog/2021/11/corporate-memory-21-11-released

	https://github.com/AtomGraph/Web-Client
		"Web-Client renders (X)HTML user interface by transforming "plain" RDF/XML (without nested resource descriptions) using XSLT 2.0 stylesheets."


	excel
		- http://labs.sparna.fr/skos-play/convert
			```
			XLWrap (I used it quite a bit, it is good but uses complex configuration files)
			Sheet2RDF, from the team that makes VocBench
			Open Anzo (never tested it)
			You can check for other tools on the W3C RDF converter wiki page.
			```
		- our currently closed-source solution
		- topbraid also does import from excel files, both
			- semantically (one object per row, for example)
			- and simple spreadsheet-described-in-rdf for further processing

	https://ruben.verborgh.org/blog/2018/12/28/designing-a-linked-data-developer-experience/
		Solid

	?
		http://ld-r.org/docs/configFacets.html
		https://semwidg.org/page/semwidgql
		http://viejs.org/widgets/forms/
		https://pythonhosted.org/Shabti/shabti_templates/shabti_formalchemy.html

	http://opoirel.free.fr/strixDB/VGR.html
		forms defined by sparql queries

	misc related
		https://github.com/mdauner/sveltejs-forms

	meta
		"The only thing more painful than filling out a form is creating one"
		- https://hackersandslackers.com/flask-wtforms-forms

	https://github.com/FormAlchemy/pyramid_formalchemy
		?

	http://vos.openlinksw.com/owiki/wiki/VOS/VirtuosoFacetsWebService
		The selection of facets and values is represented as an XML tree. Such a representation is easier to process in an application than the SPARQL source text


	https://github.com/AKSW/vue-rdform/blob/master/src/rdform.vue


	https://www.researchgate.net/publication/228854943_Tracking_rdf_graph_provenance_using_rdf_molecules

	https://solidproject.org/

	https://medium.com/@sdmonroe/vios-reference-implementation-3153a3d589cf

	http://vos.openlinksw.com/owiki/wiki/VOS/VirtuosoFacetsWebService


	https://www.w3.org/TR/xforms/
		http://emacspeak.sourceforge.net/raman/xf-book-accessibility/online-access.html

	https://github.com/MaillPierre/formulis


	https://github.com/AKSW/OntoPad


	https://aksw.org/Projects/JekyllRDF.html
		The approach is based on devising a declarative DSL to create templates to render instance data.
	

	https://vemonet.github.io/json-ld-editor-react/
	

rdf_explore_manage.txt

	note:
		there is kind of a continuum starting from dealing with bare triples:
			strictly: management of graph and rdf-based data in a generic way
				Just nodes and edges:
					sw that deals with graphs in the mathematical sense, mostly represented by tools for "property graph" databases, ie, neo4j. Rdf is more expressive and can map to this only partially.
				sw aware of contexts(graphs):
					for example gruff.
				sw that includes special functionality for managing rdf lists (still in a non-domain-specific way).
					none found yet, but not so hard to add implement
				less common/new idioms:
					dealing with properties of graphs / properties of triples i ntelligently, understanding nested graphs/contexts
			less strictly:
				sw for managing domain-specific data, where rdf is largely just a storage mechanism, "templating systems".
			even less strictly, could be said: starting from freeform text, progressively adding stronger semantics, and not losing the implicit information hidden in the form...


	software, roughly ordered by immediate relevance:

		https://github.com/sebferre/sparklis
			CNL

		https://www.tomsawyer.com/graph-database-browser/
			recommended?
			viewing/explorations

		yED
			recommended, but probably chokes on 10k+ nodes
			https://www.yworks.com/products/yed/download#download
			automatic layouting
			how to export into it:
				we need to do it in a streaming fashion:

				pyyed:
					chokes on 1000+ triples
				best to save our stuff as graphml, that's a xml format comparable to graphviz's.
				https://www.swi-prolog.org/pack/file_details/graphml/prolog/graphml_ugraph.pl is no use because it only uses "ugraphs", undirected graphs
				maybe use networkx in python?
					https://stackoverflow.com/questions/51048833/networkx-exporting-graphml-with-edge-labels-height-and-width-attributes-cust

		allegro graph + gruff + agraph webview:
			recommended
			form-based editing, graph navigation, would be more useful if it understood rdf lists, but definitely has some merit
			Graphical SPARQL builder

		https://zeppelin.apache.org/
			recommended for exploration/visualizations?
			http://zeppelin.apache.org/docs/0.9.0-SNAPSHOT/usage/dynamic_form/intro.html
			https://hub.docker.com/r/cambridgesemantics/contrib-zeppelin/

		jupyter notebook
			"you can run SPARQL queries against AnzoGraph."


		mindmapping/mind-mapping sw potentially usable with rdf:
			meta:
				http://www.opensourcecreative.org/ep040/

			ordered from most promising to least:
				iMapping
					recommended
					https://www.youtube.com/watch?v=KKh6XY2DHS8
						"formality considered harmful"
					setevi-html
					http://xam.de/go/pkm/

				freeplane
					recommended
					seems to have a more freeform attitude, yet still keyboard friendly.
					i can definitely imagine this used for exploring rdf-based data (or a high-level, possibly domain-specific export of them)
					scriptable
					MapInsight
						https://freeplane.sourceforge.io/wiki/index.php/Add-ons_(install)
						https://github.com/adxsoft/MapInsight-Addon
					https://freeplane.sourceforge.io/wiki/index.php/Current_Freeplane_File_Format
					http://freemind.sourceforge.net/wiki/index.php/Import_and_export

				inforapid
					http://www.buildyourmap.com/
					many import formats
					rdf import, somewhat usable, but skips some nodes
					"build sitemap"
					"watch clipboard"

				https://www.thebrain.com/
					maybe useful for some creative mindmapping, but the navigation doesn't seem suited for factual work?

				"XMind: ZEN 2020"
					keyboard based navigation between nodes, so far the closest to what i'd want in a rdf viewer
					implicit "is-part-of" relation, other relations possible but not keyboard navigable

					"open source"(?..)

				"XMind 8 Pro"
					"open-source"(?..)

				https://mind42.com/
					basic, browser based, not sure if it supports "custom" links

				vym
					no "custom" links, even in latest version
					Qt (probably snappier than java)

				note
					an issue with all of them so for is a lack of automatic layouting for "non-primary" connections, ie, nodes are layouted by their "part-of" relationship, and you can choose different presentations of that, or move a child node into different slots of the parent node, but once you add a "custom" relation, you have to position it yourself. But we could tackle that.


		dmx
			https://demo.dmx.systems/systems.dmx.webclient/#/topicmap/2767
			https://dmx.readthedocs.io/en/latest/tutorial.html
			can this manage arbitrary rdf?
			
			"""
			Create a topic type “Tree name”. It can keep the default data type “text”. Create an association between the “Tree name” and the “Tree”. By dragging from the child type (“Tree name”) to the parent type (“Tree”) you assign the right order on the fly.

			Create a topic type “Blooming period”. Edit it and change its data type to “value”. Create an association between the topic type “Blooming period” and the topic type “Tree”."""
			
			blah blah blah.
			
			https://dmx.readthedocs.io/en/latest/plugins.html#the-tableview-plugin
			
		

		CNL-based:

			https://www.cognitum.eu/semantics/examples/FIBO.aspx

			ACE.. (verbalizes OWL, generates OWL and a bit of SWRL)

			https://aspen-lang.org/
				graph data (cypher) input, syntax sugar


		rdf in js, pointers on how to start building something, but no ready solutions

			nice but paid
				https://gojs.net
					interactive diagrams and graphs
					nice demos but no keyboard-friendly navigation (by default)

			free but commercially used, looking robust
				https://github.com/bpmn-io/diagram-js
				https://github.com/jgraph/mxgraph

			hmh

				https://github.com/bricaud/graphexp
					Interactive visualization of the Gremlin graph database with D3.js

				https://madsholten.github.io/sparql-visualizer/
				
				
				https://www.rubensworks.net/blog/2019/10/06/using-rdf-in-javascript/
				https://www.google.com/search?q=js+scene+graph
				https://rdf.js.org/
				https://github.com/linkeddata/rdflib.js
				https://raptorlicious.blogspot.com/2017/08/1st-stages-of-exploring-sigmajs-for-use.html
				https://www.w3.org/wiki/SparqlImplementations


				diagramming
					https://github.com/mdaines/viz.js/wiki
					https://github.com/magjac/d3-graphviz

				new and cool
					https://github.com/dagrejs/dagre-d3/wiki#demos
					https://github.com/vasturiano/react-force-graph#react-force-graph
					https://github.com/vasturiano/force-graph
					http://vis.arc.vt.edu/projects/zbb/
					https://www.web3d.org/x3dv4-implementations
					http://stars.chromeexperiments.com/
					http://haylyn.io/
					
					https://github.com/dletta/visualGraph
				

				d3.js
					
					https://github.com/timrdf/vsr/wiki/d3
					https://medium.com/dailyjs/the-trouble-with-d3-4a84f7de011f
						https://docs.google.com/spreadsheets/d/1k-GVrhLw2_KdSvfCOt3RzF6otWfZQ5rbsBpVnTP425w/edit#gid=0
					simple demo
						https://github.com/jimmccusker/rdfviewer
					cool demo
						http://givingsense.eu/demo/bloomdisplay/d3TreeBloom.htm
						https://onsem.wp.imt.fr/2014/03/18/web-visualization-of-a-simple-ontology/


				cytoscape.js
					https://dmx-systems.github.io/cytoscape-edge-connections/
					didnt find anything rdf related, but i guess it would be a reasonable engine for building something
					-> https://github.com/koo5/QuadLad/blob/master/src/Cytoscape.svelte

				https://github.com/marklogic-community/grove-vue-visjs-graph



		neo4j for rdf visualization, neo4j built-in editor:
			https://neo4j.com/developer/tools-graph-visualization/
			https://www.google.com/search?q=neo4j+visual+editor
			https://pehei.de/en/posts/neo4j-graph-view-editor
				https://github.com/adadgio/neo4j-js-ng2
			..not too impressed, maybe:

			https://graphileon.com
				https://graphileon.com/getting-started-videos/
				https://graphileon.com/licenses/
				not full rdf support, but worth exploring
				they are working on integration with triplestores, but dunno how that'll work

			https://neo4j.com/blog/introducing-neo4j-bloom-graph-data-visualization-for-everyone/
			will be inherently limited by not being able to follow properties of graphs. But then, what existing rdf tool wont?
			it should be useful enough for letting users produce data
			https://neo4j.com/docs/labs/nsmntx/current/import/#ImportQuadRDF
			https://github.com/Rothamsted/rdf2neo
			https://adamcowley.co.uk/neo4j/real-time-ui-vuejs-neo4j-kafka/


		cytoscape
			- desktop, java

			cytoscape version 2,
				RDFScsape
					unclear if it still can be downloaded from anywhere
			cytoscape version 3
				https://apps.cytoscape.org/apps/semscape
					try with http://chianti.ucsd.edu/cytoscape-3.1.0/ or older
			i didnt get any cytoscape version to run on ubuntu 18.04 ..


		small projects, ponderings

			https://github.com/timrdf/vsr
				https://github.com/timrdf/vsr/wiki

			http://www.visualdataweb.org/tfacet.php
				hierarchical faceted exploration of RDF

			https://www.researchgate.net/publication/221607731_Jambalaya_an_interactive_environment_for_exploring_ontologies
				interactive environment for exploring ontologies


		http://rdfvizler.dyreriket.xyz/
			looks good
			visualization ontology + implementation

		https://github.com/koo5/ontology-visualization
			general purpose rdf visualization
			nice simple picture generator, somewhat useful. Could add logic for:
				special presentation of lists, with graphviz nested nodes
				non-default graphs, graph properties, with graphviz nested graphs
			but in the end, without interactivity, it's always gonna have limited usefulness
			```
			python3 ontology_viz.py ~/LodgeITSmart/LodgeiTSmart/LodgeiTSmart/Resources/RdfTemplates.n3
			dot -Tpng -o test.png ontology.dot
			```

		http://vowl.visualdataweb.org/webvowl.html
			OWL ontology visualizer
			recommended

		https://github.com/JanWielemaker/triple20.git
			works, could have some use, somewhat confusing

		OSDE - The OpenLink Structured Data Editor
			http://osde.openlinksw.com/
			simple table-of-triples-based rdf editor, virtuoso-integrated

		https://medium.com/@sdmonroe/vios-reference-implementation-3153a3d589cf
			interesting wrt web based UI

		ClioPatria
			http://cliopatria.swi-prolog.org/swish/pldoc/doc/home/swipl/src/ClioPatria/ClioPatria/web/tutorial/LoadPirates.txt
			http://cliopatria.swi-prolog.org/browse/list_graph?graph=https%3A//cliopatria.swi-prolog.org/packs/vumix
			http://irnok.net:3030/help/source/doc/home/prolog/ontology-server/ClioPatria/lib/semweb/rdf_optimise.pl
			http://irnok.net:3030/help/source/doc/home/prolog/ontology-server/ClioPatria/lib/semweb/rdf_label.pl
			http://irnok.net:3030/help/source/doc/home/prolog/ontology-server/ClioPatria/lib/semweb/rdf_json.pl
			http://irnok.net:3030/help/source/doc/home/prolog/ontology-server/ClioPatria/lib/semweb/rdf_graphviz.pl

		https://www.semantic-mediawiki.org
			interesting, long-lived project
			embedding triples into wiki markdown, and an ecosystem around that

		https://www.rdfexplorer.org/
			browser-based,
			some kind of browsing-by-querying-something

		http://en.lodlive.it/
			browser-based,
			cannot load own data yet

		simple visualizers
			https://github.com/mhausenblas/turtled
			http://www.easyrdf.org/converter
			http://rhizomik.net/html/redefer/rdf2svg-form/
			https://github.com/idafensp/ar2dtool

		wtf:
			https://linkedpipes.com/
			https://www.researchgate.net/publication/283345803_OSMoSys_A_Web_Interface_for_Graph-Based_RDF_Data_Visualization_and_Ontology_Browsing

		nope:
			https://geistmap.com/
				undirected, unlabeled nodes, why would you use that?

			https://sourceforge.net/projects/veudas/
				dead

			https://sourceforge.net/projects/brownsauce/
				dead

			https://www.w3.org/RDF/Validator/
				basic

			http://trac.biostr.washington.edu/trac/wiki/VIQUEN
				interesting query builder

			http://www.visualdataweb.org/relfinder.php
				flash

			https://www.w3.org/2001/11/IsaViz/
				edit run.sh, still doesnt start

			http://www.linkeddatatools.com
				dead/nonexistent?:

			RDF Gravity
				http://tapor.ca/tools/363
				dead

		dead
			https://www.semanticweb.org/wiki/OpenLink_Data_Spaces.html
				mostly broken demos, seems dead

			https://www.semanticweb.org/wiki/BOWiki.html
			https://www.semanticweb.org/wiki/Braindump.html
			https://www.semanticweb.org/wiki/COW.html
			https://www.semanticweb.org/wiki/Freebase.html
				merged into..?
			https://www.semanticweb.org/wiki/Hypertext_Knowledge_Workbench.html
				CDS Tools is a single application that bundles three CDS tools: Hypertext Knowledge Workbench, IMapping, and QuiKey.
			https://www.semanticweb.org/wiki/Semantic_MediaWiki-2.html
				https://www.researchgate.net/profile/Dave_Braines/publication/39996382_A_Controlled_Natural_Language_Interface_for_Semantic_Media_Wiki_Using_the_Rabbit_Language/links/5646021708ae54697fb9cab2/A-Controlled-Natural-Language-Interface-for-Semantic-Media-Wiki-Using-the-Rabbit-Language.pdf
				https://www.semanticscholar.org/paper/Development-of-a-Controlled-Natural-Language-for-Smart-Bao/ec0631faf6202fa6d906eab6d2202b9c596ab1e4


			https://sourceforge.net/projects/wikiont/
				ontology editor
				not maintained

			https://www.researchgate.net/publication/316898476_WikiOnt_An_Ontology_for_Describing_and_Exchanging_Wiki_Articles
				WikiOnt: An Ontology for Describing and Exchanging Wiki Articles

			WikiOnt-CNL
				https://www.academia.edu/34644576/Development_of_a_controlled_natural_language_interface_for_semantic_MediaWiki?auto=download

			http://openrecord.org/bookmarks.html
				loosely-structured database content.


		statistical visualization
			http://aksw.org/Projects/CubeViz.html
			gephi


		large scale graph visualization framework
			https://github.com/Tulip-Dev/tulip



	resources
		recommended
			https://doriantaylor.com/the-symbol-management-problem
			http://graphdatamodeling.com/Graph%20Data%20Modeling/HallOfFame/DMHallOfFame.html

		nothing new here
			https://www.semanticweb.org/wiki/Category_Semantic_wiki.html

		https://www.w3.org/wiki/TaskForces/CommunityProjects/LinkingOpenData/SemWebClients

		interesting wrt UI development
			https://github.com/timrdf/vsr/wiki
				https://github.com/timrdf/vsr/wiki/General-Strategies-for-Visualizing-RDF-Graphs


		http://svn.code.sf.net/p/eulergui/code/trunk/eulergui/html/semantic_based_apps_review.html
			todo, outdated but useful

		i think i've mostly reviewed these and noted anything notable here already, but a double-check and actually creating a note about each sw found wouldn't hurt:
			https://stackoverflow.com/questions/66720/are-there-any-tools-to-visualize-a-rdf-graph-please-include-a-screenshot
			http://tapor.ca/tools?attribute_values=66&order=rating&sort=desc
			https://www.w3.org/2018/09/rdf-data-viz/
			https://github.com/w3c/EasierRDF/issues/35
			https://github.com/w3c/EasierRDF/issues/53
			http://sensormeasurement.appspot.com/?p=visualization_sota
			https://www.w3.org/wiki/Ontology_editors
			https://pdfs.semanticscholar.org/fe40/f2de08684299b3a6e7466d9420e977c9f420.pdf?_ga=2.39233379.1908259706.1580280149-1924257816.1580280149
			http://activearchives.org/wiki/Visualizing_RDF
			https://wiki.lyrasis.org/pages/viewpage.action?pageId=69014248
			https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=8&ved=2ahUKEwj1-_HI4urmAhXONcAKHaq7BRMQFjAHegQICRAC&url=http%3A%2F%2Fwww.dsi.uclm.es%2Fdescargas%2Ftechnicalreports%2FDIAB-13-09-1%2FTR_linked_data_tools.pdf&usg=AOvVaw3tKcNVfWq-A72UIUXyR_Ls
			http://raghavam.github.io/talks/2019/Intro-SemWeb/rdf.html
			http://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.170/home/raiser/Diplomarbeit_Wasserthal2009.pdf
			https://stackoverflow.com/questions/52848013/how-can-i-visualize-graph-data-with-amazon-neptune
			http://organizingknowledge.blogspot.com/2014/05/diagramming-rdfxml-owl-ontology.html







rdf_triplestores.txt



	triplestores:

		important factors:
			automatic rest api?
				https://www.researchgate.net/publication/331541963_Building_a_Semantic_RESTFul_API_for_Achieving_Interoperability_between_a_Pharmacist_and_a_Doctor_using_JENA_and_FUSEKI

			non-rdf interfaces:
                https://comunica.github.io/Article-ISWC2018-Demo-GraphQlLD/
                    GraphQL to sparql and back, seems usable, recommended alternative to stardog's
                    - but no subscriptions

				stardog
				anzo
					OpenCypher
					sql: no
					inserting jsonld through python api

				neptune
					cypher
					? GraphQL:
						"If you're interested in enabling GraphQL for access to Amazon Neptune, there's an example application showing how to use AWS AppSync GraphQL and Amazon Neptune."
						???
					sql: no


		cool ones found so far:
				stardog
					- recommended
					- SQL: https://www.stardog.com/docs/#_sql_schema_mappings
					- GraphQL: "automagically provides a GraphQL endpoint over your existing RDF graphs"
					- virtual graphs
					- owl inference with explanations
					- no free version, no pricing
					
				allegro (+ gruff)
					- recommended, at least for gruff, but stardog has a lot more functionality useful for us
					
				https://terminusdb.com/
					versioning
		okay
			virtuoso
				URLBurner.
					could be used like this:
						create a django service to be accessed through a bookmarklet.
						service first submits a page to uriburner, then makes a request to add "x a bookmark; byUser koo"
						export from virtuoso, edit in protege?
						could be used to build a bookrmarking solution, but isn't one by itself, so far




			agraph
				transactions:
					* one possible way to implement? but i cannot find further info, so this seems as a too uncertain to bet on:
						"""This subclass is used for DELETE and INSERT queries. The result returned when the query is evaluated is a boolean that can be used to tell if the store has been modified by te operation."""
					* the bnode generator function is guaranteed to generate unique names


        ?
            https://github.com/terminusdb/terminus-server/tree/dev
            https://github.com/RecallGraph/RecallGraph

		experimental:
			dunno:
				https://github.com/Merck/Halyard

		not so excited about:
			blazegraph
				crashes, ooms, poor performance (in my tests...)
            orientdb
                not a hypergraph
                    https://github.com/orientechnologies/orientdb/issues/4078
                        haha

		dead
			http://opoirel.free.fr/strixDB/strixdb.html
			http://opoirel.free.fr/strixDB/VGR.html
				"""
				The user can request a RDF store with forms (similar to classical SQL/MS Access forms) without any SPARQL knowledge.
				The user can navigate through the graph returned by the request guided by his imperious information needs....
				These forms are build by a knowledge engineer who knows SPARQL.
				Each form is based on SPARQL (with a little modification: each $variable will automatically generate a request form field).
				"""

        unknown but interesting
            http://hypergraphdb.org/
            https://www.tigergraph.com/graphstudio/


	rdfox
	   transactions:
	       https://docs.oxfordsemantic.tech/transactions.html
        	   At each point in time the following transactions can be active in a data store:
	           a single read/write transaction; or
        	   multiple read-only transactions.



misc:

	pretty-print:
		- https://github.com/koo5/hackery2/blob/master/src/data/rdf_order/rdf_cleanup2.py
		- use pure rdflib instead of cwm, rdflib is maintained
		- make sure list nodes don't appear in extra triples, and are well-formed
		- if you want something nested, it must be a bnode
		https://github.com/AKSW/Xturtle
		https://atom.io/packages/language-rdf
		https://github.com/e-e-e/sublime-turtle-syntax

		for formatting our n3 files: https://github.com/koo5/hackery2/blob/master/src/data/rdf_order/rdf_cleanup2.py

		cwm: better to avoid in the beginning and use just rdflib, which keeps being developed.

		http://librdf.org/raptor/ - rapper cli tool is useful for format conversions


	conversion:
		cwm:
			better to avoid in the beginning and use just rdflib, which is still maintained
			`python2 ~/sw/dev/swap/cwm.py --n3 lodgeitrequest.n3  --rdf > rdf.rdf`
		http://librdf.org/raptor/ - rapper cli tool is useful for format conversions


	dead?
		http://www.visgraph3.org/
		https://sourceforge.net/projects/veudas/


	?
		https://marketplace.eclipse.org/content/komma-rdf-eclipse
		https://marketplace.eclipse.org/content/emf-triple
			https://github.com/ghillairet/emftriple


	misc
		https://www.w3.org/TR/swbp-n-aryRelations/

		https://github.com/AKSW/KBox
			KBox is the option for ontology dependency management

		http://ns.softwiki.de/req/2/index-en.html
			Semantic Web Ontology for Requirements Engineering (SWORE)

		ideas:
			https://github.com/timrdf/vsr/wiki/Recovering-Data-from-View
			https://github.com/timrdf/vsr/wiki/Linked-Data-Auger
			https://github.com/timrdf/vsr/wiki/2grph.xsl
			http://squin.sourceforge.net/index.shtml
			http://schema.theodi.org/odrs/
			https://github.com/timrdf/vsr/wiki/Related-Work
			https://github.com/timrdf/vsr/wiki/TiNG-Triples-in-Named-Graph
			https://github.com/timrdf/vsr/wiki/VisTrails
			https://www.semanticscholar.org/paper/Handling-the-Complexity-of-RDF-Data-%3A-Combining-and-Heim-Ziegler/fe40f2de08684299b3a6e7466d9420e977c9f420
			https://www.ontotext.com/blog/data-visualization-with-graphdb-how-to-turn-your-tabular-data-into-a-telling-visual/


    r2ml, mapping
        https://zazuko.com/blog/rdf-and-dsl-a-perfect-match/

    collaborative ontology development
        http://editor.zazuko.com/




misc, todo, more research needed:

    https://www.factil.io/
        CNL
        "Web-based Business Information Model editor
        Automated model inference from from source metadata
        Automated schema generation to relational, staging and data vault forms"
        schema generation -> nlsql
        recommended(schema generation)
        "information model is defined in an easily understood, controlled natural language. From the business information model, the platform can generate well-structured data schemas"

    https://github.com/CLARIAH/grlc
        grlc is a lightweight server that takes SPARQL queries curated in GitHub repositories, and translates them to Linked Data Web APIs

	https://www.d3web.de/
		expert system / diagnosis platform, flowcharts, stuff, possible replacement for our chat logic
		recommended(chat,catsys)
		long-lived project


	https://www.executable-english.com/internet_business_logic_FAQs.html
		http://www.reengineeringllc.com/
		Executable English LLC
		Backchain Iteration: Towards a Practical Inference Method that is Simple Enough to be Proved Terminating, Sound and Complete. Journal of Automated Reasoning, 11:1-22, 1993
		https://www.executable-english.com/IBL_tutorial_part1.html
		https://www.executable-english.com/rule_examples.html



	https://www.odaseontologies.com/how-it-works/
		"(OWL, RDF), extended with logic-based business rules (SWRL), define the business problem" ...


	https://www.researchgate.net/publication/323616656_SPARQL_Micro-Services_Lightweight_Integration_of_Web_APIs_and_Linked_Data




	https://www.honeycomb.io/microservices/
		"OBSERVABILITY FOR MICROSERVICES"

	https://developer.logicblox.com/using-modeler-js-applications/
		https://developer.logicblox.com/download/
		?

	https://gra.fo/
		simple mouse-oriented (RDF) graph builder / document manager
		"Everything you need to create, manage, and evolve your Knowledge Graphs: RDF & Property Graph. Invite your team to edit your documents with you in real-time."

	https://apis.guru/graphql-voyager/
		graphql explorer


	Maana
		KnowledgeModelAssist: Visually build knowledge models

	https://demos.qlik.com/qliksense




	graphql, etc
		https://comunica.dev/docs/query/advanced/graphql_ld/
		https://franz.com/agraph/support/documentation/current/graphql.html
		https://docs.stardog.com/query-stardog/graphql#graphql
		https://www.hypergraphql.org/documentation/
		http://vos.openlinksw.com/owiki/wiki/VOS/VirtGenerateR2RMLLinkedDataView




	storage - technically
		https://en.wikipedia.org/wiki/Lightning_Memory-Mapped_Database
		redis
		..
		kde project seems to have oscillated, from "nothing", to a generic triplestore, to a bunch of special-purpose stores (but eventually without the overarching model)..
		then there's all the r2rml implementations...
		~2010: "Internally, virtuoso may be looked at as a relational database, with some added RDF features. "



	https://github.com/BruJu/PREC
		PREC is a WIP set of tools to convert any Property Graph into RDF.
		


	versioning
		https://github.com/AKSW/QuitStore
		
		
	https://linkeddatafragments.org/	







currently irrelevant:
	visualization
		https://cambridge-intelligence.com/regraph/features/
			react

	https://ali1k.com/rdface/rdface06/tinymce/examples/rdface.html#
		browser-based text editor with rdf annotation

	https://chrome.google.com/webstore/detail/microstrategy-hyperintell/ikaoafechdeidffgniffdhdckeclcdhf?hl=en
		chrome extension
		scans every webpage and underlines relevant keywords

	https://www.datagalaxy.com/
		data gouvernance

	https://www.semanticweb.org/wiki/Wikidsmart.html
		interesting but not useful for us

	https://hume.graphaware.com/
		"Insights Engine"

	http://architector.co.uk/
		"data lineage metadata"

	data cleanup, transformation, mapping
		http://usc-isi-i2.github.io/karma/
			"""n this case study we used Karma to convert records of 44,000 of the museum’s holdings to Linked Open Data according to the Europeana Data Model (EDM). The records are stored in several tables in a SQL Server database. Using Karma we modeled these tables in terms of the EDM ontology and converted the data into RDF. We are creating a 5-star Linked Data, linked to DBpedia, the Getty Union List of Artist Names (ULAN)® and the NY Times Linked Data."""

	https://www.datagalaxy.com/

	http://www.factgem.com/
		"connects data from platforms and applications, separated by purpose, geography, or organization, into a unified, service-enabled, graph endpoint."


	Reltio
		neo4j

	www.omegawiki.org/
		dictionary and thesaurus
		https://www.semanticweb.org/wiki/OmegaWiki.html



    https://atomgraph.github.io/Linked-Data-Templates/
        something like the solid thing?




augmented_text.txt
	http://www.artificialmemory.net
		interesting wrt browser-based UI
		long-lived project
		just died?

	https://www.w3.org/wiki/HCLSIG/SWANSIOC/Actions/RhetoricalStructure/models/blocksontology
		https://www.w3.org/wiki/HCLSIG/SWANSIOC/Actions/RhetoricalStructure

	https://doriantaylor.com/
	iMapping,
	CDS,
	personal knowledge management,
	automatic entity annotation,
	https://github.com/timrdf/vsr/wiki/Discourse-ontologies
	https://idyll-lang.org/docs
		"""Idyll can be used to create explorable explanations, write data-driven stories, and add interactivity to blog engines and content management systems. The tool can generate standalone webpages or be embedded in existing pages."""
	http://worrydream.com/ClimateChange/#media
		interesting, wrt ideal browser-based accounting/exploration UI

	https://github.com/timrdf/vsr/wiki/Discourse-ontologies


	structured debate/decision making

		https://www.solipsys.co.uk/cgi-bin/DiscDAG.py?DiscussionID=AxiomOfChoice
		https://ibis.makethingsmakesense.com/52dea301-2e68-4c10-ab2d-bb0e0c95aa60

	macros	
		https://github.com/conartist6/macrome

	annotating free text

		https://github.com/celsowm/AutoMeta#autometa

		http://aksw.org/Projects/RDFaCE.html

		https://github.com/boberle/standoff2inline
		
		https://marketplace.eclipse.org/content/collage-framework-and-code-markup-tools		
		
		https://plugins.jetbrains.com/plugin/17541-code-annotation-tool/versions



mount solid pod data as a fuse fs?





URI vs URL:
	```
	Steve Pepper has written an article on how to cure the web's identity crisis [Pepper2004]. The argumentation there is sounds correct. He proposes to solve the distinction of Resource VS Concept by using Topic Map syntax. Topic Maps do determine between addressable subjects and non-addressable subjects. The use of resourceRef or subjectIndicatorRef state a clear message about the topic in question: it is addressable (its a document) or it is not addressable (it is a concept) and in the Topic Map Community, usually one URI is not used in both uses. Also, the Topic Map community treats all concepts in the context of a Topic Map - every resource (be it addressable or not) is first re-instantiated in a local Topic Map using a local identifier (usually something like <topic id="opera">).

	Pepper suggests to expand the use of rdf:about with rdf:subject and rdf:indicator to extend the identification. But Pepper didn't take the last needed step: to create a new view on RDF where each Resource is re-instantiated in the current ontology. He does not propose to create topics versus resources. We more tend towards SKOS: there, each Topic is called a Concept and is identified uniquely inside the SKOS ConceptScheme, using the URI of the concept scheme [SKOS-Effort].
	```
	- http://www.dfki.uni-kl.de/~sauermann/2006/01-pimo-report/pimOntologyLanguageReport.html








Web3 stuff
	theGraph
		- index IPFS-stored data
		https://github.com/graphprotocol/everest/tree/bbfc5296fbbe3f3323c4e385d105af0a4244681f
		
	https://comunica.dev/
		...


		
SPARQL
	https://ontologforum.org/index.php/KGSQL
		https://baclawski.s3.amazonaws.com/kgsql/Introduction+to+KGSQL.pdf

			
	
