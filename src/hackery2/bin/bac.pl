:- ['disks'].


do_backup_i(I) :-
	start(I),
	do_backup(I),
	stop(I).

do_backup(I) :-
	shell2(['df -h']),
	shell2(['rm /.sxbackup; ln -s /.sxbackup-',I,' /.sxbackup; ~/.local/bin/btrfs-sxbackup run /']),
	shell2(['df -h']).

do_backup_ext(I) :-
	shell2(['cp --sparse=always -r /mnt/kingston240/ /bac', I, '/ext/`(date -u  "+%Y-%m-%dT%H:%M:%SZ")`']).

do_backup_all :-
	start(0), start(1), start(2), start(3),
	shell2(['~/.local/bin/btrfs-sxbackup run /bac1/offline_data/']),
	do_backup_ext(0), do_backup_ext(1), do_backup_ext(2), do_backup_ext(3),
	do_backup(0), do_backup(1), do_backup(2), do_backup(3),
	shell2(['df -h']),
	stop(0), stop(1), stop(2), stop(3).


run :-
	do_backup_all, halt.
