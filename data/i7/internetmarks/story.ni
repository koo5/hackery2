"wrooom" by kook.



include dynamic objects by jesse mcgrew;




part ? - some synonyms


to disable (rule - a rule):
    ignore the rule;

to place (x - something) in (y - a room):
    move x to y;





book x - bookmarks

part 1 - definitions



a bookmark is a kind of thing;
a bookmark has an indexed text called url;
the bookmark prototype is a bookmark;
new bookmark is a bookmark that varies;
a folder is a kind of container; it is lit;
a folder has an indexed text called title;
the folder prototype is a folder;
new folder is a folder that varies;
the root folder is in internetmarks;
the root folder is a folder;
the title of the root folder is "root folder";

new folder is the root folder;
the player is in the root folder;




part 2 - functions



to add a new bookmark (this is adding a new bookmark):
	let the copy be a new object cloned from the bookmark prototype;  
	place the copy in internetmarks;
	now the new bookmark is the copy;
	move the new bookmark to the new folder;


understand "add [text]" or "a [text]" as adding a bookmark;
adding a bookmark is an action applying to one topic;
carry out adding a bookmark:
	add a new bookmark;
	now the url of new bookmark is the topic understood;
	say "you added [url of the new bookmark]";


understand "enter folder [text]" or "f [text]" as adding a folder;
adding a folder is an action applying to one topic;
carry out adding a folder:
	let the created folder be a new object cloned from the folder prototype;
	move the created folder to internetmarks;
	move the created folder to the new folder;
	now the new folder is the created folder;
	now the title of the new folder is the topic understood;





after printing the name of a bookmark (called b) (this is the what the fuck is going on here rule):
    say " - [url of b][line break]";

rule for printing the name of a folder (called f):
    say "[title of f]";


internetmarks is a room;





a bookmark called inform7 is here;
a bookmark called intfiction is here;
url of inform7 is "inform7.com";
url of intfiction is "interactive-fiction.com/forum";
