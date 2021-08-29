#!/usr/bin/env swipl

:- ['disks'].


/*do_backup_i(I) :-
	start(I),
	do_backup('/', I),
	do_backup('/z/', I),
	stop(I).
*/

do_backup(I) :-
	%do_backup('/', I),
	%do_backup('/home/', I),
	%do_backup('/z/', I).
	%do_backup('/intel500/', I),
	do_backup('/', I),
	do_backup('/d/', I),
	do_backup('/mx500data/', I),
	true.

do_backup(Src, I) :-
	shell2(['rm ',Src,'.sxbackup; ln -s ',Src,'.sxbackup-',I,' ',Src,'.sxbackup; nice -n 19 ionice -c 3 btrfs-sxbackup run ',Src]).

do_backup_ext(Disks) :-
	shell2(['virsh suspend xubuntu18_docker_raw_on_fat'], _), /*fixme, how to tell if it's suspended? */
	all(Disks,do_backup_ext2),
	shell2(['virsh resume xubuntu18_docker_raw_on_fat'], _).

do_backup_ext2(I) :-
	shell2(['cp --sparse=always -r /mnt/kingston240/ /bac', I, '/ext/`(date -u  "+%Y-%m-%dT%H:%M:%SZ")`']).

backup_offline_data(I) :-
	dif(I, 1), % 1 is the source
	shell2(['rm /bac1/offline_data/.sxbackup; ln -s /bac1/offline_data/.sxbackup-',I,' /bac1/offline_data/.sxbackup; btrfs-sxbackup run /bac1/offline_data/']).
	
df :-
	shell2(['df -h -l -x loop -x tmpfs -x devtmpfs -x squashfs']).

all(Disks, Pred) :-
	foreach(member(I, Disks),call(Pred,I)).

%do_backup_with_disks([]) :- !.

do_backup_with_disks(Disks) :-
	df,	
	/* everything could even be done in parallel if it wasnt for sxbackup symlink limitation */
	foreach( (dif(I,1),member(I,Disks)), do_backup(I)),
	foreach( (dif(I,1),member(I,Disks)), backup_offline_data(I)),
	df,
	all(Disks,stop).

start_and_find_disks(Disks) :-
	findall(X, 
		(
			between(0,8,X),
			try_ensure_mounted(X)
		),
		Disks).

do_backup_all :-
	start_and_find_disks(Disks),
	do_backup_with_disks(Disks).

run :-
	do_backup_all, halt.
