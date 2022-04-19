"smazak" by prazak

Praha is a room.

Include Dynamic Tables by Jesse McGrew.
Use MAX_STATIC_DATA of 3800000.

Include webapp over files with openid by kook.

File of data (owned by another project) is called "database".

table of data
user (indexed text)	gps (indexed text)	popis (indexed text)
with 100 blank rows

When play begins:
	read file of data into table of data;

To generate response:
	write "<html><body>" to file of result;
	add user div;
	if path is "/":
		if nick is not empty:
			return "hello [nick]! nice to see you here.";
			return "<logout>";
	[]
	return "[line break]<br><br><br>page source:<br><pre><page source></pre><a href='https://github.com/koo5/melon/blob/master/melon.inform/Source/story.ni'><img style='position: absolute; top: 0; right: 0; border: 0;' src='https://d3nwyuy0nl342s.cloudfront.net/img/abad93f42020b733148435e2cd92ce15c542d320/687474703a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f677265656e5f3030373230302e706e67' alt='Fork me on GitHub'></a></body></html>";

