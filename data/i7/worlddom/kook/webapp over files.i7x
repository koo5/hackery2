webapp over files by kook begins here.

"oct 2012"


Include Dynamic Tables by Jesse McGrew.

File of request (owned by another project) is called "input".
File of result (owned by another project) is called "output".
File of readiness (owned by another project) is called "outputisready".

table of arguments
name (indexed text)	value (indexed text)
with 10 blank rows

path is some indexed text that varies;
user is some indexed text that varies;
verb is some indexed text that varies;
nick is some indexed text that varies;

to fetch arguments:
	repeat through table of arguments:
		if name entry is "path":
			now path is value entry;
		if name entry is "user":
			now user is value entry;
		if name entry is "verb":
			now verb is value entry;
		if name entry is "nick":
			now nick is value entry;


Understand "request" as serving a request.
Serving a request is an ACTION applying to nothing.
processing the request is an ACTION applying to nothing.

Understand "list [text]" as listing;
Listing is an action applying to one topic;

generating response is an action applying to nothing;

Carry out serving a request:
	if the file of request exists:
		read file of request into table of arguments;
		process arguments;
		let count be number of filled rows in table of arguments;
		if count > 0:
			repeat through table of arguments:
				say "[name entry]: [value entry][line break]";
		generate response;
		blank out the whole of the table of arguments;
		write file of request from table of arguments;
		write "done" to the file of readiness;

processing arguments is an action applying to nothing.
to process arguments:
	repeat through table of arguments:
		if name entry is "path":
			now path is value entry;
		if name entry is "verb":
			now verb is value entry;
		if name entry is "nick":
			now nick is value entry;


To return (x - indexed text):
	append "[x]" to file of result;
	say "[x][line break]";
	

To return text (x - text):
	append "[x]" to file of result;
	say "[x][line break]";

webapp over files ends here.
