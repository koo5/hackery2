:- ['disks'].


do_backup_i(I) :-
	start(I),
	do_backup(I),
	stop(I).

do_backup(I) :-
	shell2(['rm /.sxbackup; ln -s /.sxbackup-',I,' /.sxbackup; ~/.local/bin/btrfs-sxbackup run /']).

do_backup_ext(Disks) :-
	shell2(['virsh suspend xubuntu18_docker_raw_on_fat'], _), /*fixme, how to tell if it's suspended? */
	all(Disks,do_backup_ext2),
	shell2(['virsh resume xubuntu18_docker_raw_on_fat'], _).

do_backup_ext2(I) :-
	shell2(['cp --sparse=always -r /mnt/kingston240/ /bac', I, '/ext/`(date -u  "+%Y-%m-%dT%H:%M:%SZ")`']).

backup_offline_data(I) :-
	dif(I, 1), % 1 is the source
	shell2(['rm /bac1/offline_data/.sxbackup; ln -s /bac1/offline_data/.sxbackup-',I,' /bac1/offline_data/.sxbackup; ~/.local/bin/btrfs-sxbackup run /bac1/offline_data/']).
	
df :-
	shell2(['df -h -l -x loop -x tmpfs -x devtmpfs -x squashfs']).

all(Disks, Pred) :-
	foreach(member(I, Disks),call(Pred,I)).

do_backup_all :-
	start_and_find_disks(Disks),
	do_backup_with_disks(Disks).

start_and_find_disks(Disks) :-
	findall(X, 
		(
			between(0,3,X),
			try_ensure_mounted(X)
		),
		Disks).

do_backup_with_disks([]) :- !.

do_backup_with_disks(Disks) :-
	df,
	

	/* these three can be ordered in any way, everything could even be done in parallel if it wasnt for sxbackup symlink limitation */

	foreach( (dif(I,1),member(I,Disks)), backup_offline_data(I)),
	all(Disks,do_backup),
	do_backup_ext(Disks),
	

	df,
	all(Disks,stop).


run :-
	do_backup_all, halt.
