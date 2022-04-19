webapp over files with openid by kook begins here.

The praha is a room.

Include webapp over files by kook.

File of users (owned by another project) is called "users";

table of users
nick (indexed text)	id (indexed text)
with 100 blank rows

user is some indexed text that varies;

after processing arguments:
	repeat through table of arguments:
		if name entry is "user":
			now user is value entry;

When play begins:
	read file of users into table of users;

Carry out listing "users":
	list users;
To list users:
	repeat through table of users:
		say "[id entry]: [nick entry][line break]";
	say "[number of filled rows in the table of users] users.[line break]";


Before generating response:
	if there is an id of user in table of users:
		actualize nickname;
	else:
		add new user;

to actualize nickname:
	let old nick be nick corresponding to id of user in table of users;
	if old nick is not nick:
		say "old nick: [old nick], new nick: [nick], updating nick...[line break]";
		choose row with id of user in table of users;
		now nick corresponding to id of user in table of users is nick;
		write file of users from table of users;

to add new user:
	say "adding new user[line break]";
	choose a blank row in table of users;
	now id entry is user;
	now nick entry is nick;
	write file of users from table of users;

to add user div:
	return "<div>";
	if the path is "/_ah/login_required":
		return "<login>";
	return "</div>";


webapp over files with openid ends here.
