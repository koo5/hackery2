:- ['disks'].

shell2(Cmd) :-
        shell2(Cmd, _).

shell2(Cmd_In, Exit_Status) :-
        flatten([Cmd_In], Cmd_Flat),
        atomic_list_concat(Cmd_Flat, Cmd),
        format(user_error, '~w\n\n', [Cmd]),
        shell(Cmd, Exit_Status).

halt_on_err :-
        Err_Grep = 'grep -q -E -i "Warn|err" err',
        (shell2(Err_Grep, 0) -> halt ; true).

x :-
	Expected_Args = [Disk_Id],
        current_prolog_flag(argv, Argv), 
        (
                (
                        Argv=Expected_Args
                ;
                        Argv=['--' |Expected_Args] % swipl 8.1.11 weirdness
                )
        ->
                true
        ;
                (
                        format(user_error, 'argument parsing failed.', []),
                        halt
                )
        ),
	do_backup(Disk_Id),
	halt.

do_backup_i(I) :-
	start(I),
	do_backup(I),
	stop(I).

do_backup(I) :-
	shell2(['df -h']),
	shell2(['rm /.sxbackup; ln -s /.sxbackup-',I,' /.sxbackup; ~/.local/bin/btrfs-sxbackup run /']),
	shell2(['df -h']).

do_backup_all :-
	start(1), start(2), start(3),
	do_backup(1), do_backup(2), do_backup(3),
	shell2(['cp --sparse=always -r /mnt/kingston240/ /bac1/ext/`(date -u  "+%Y-%m-%dT%H:%M:%SZ")`'])
	shell2(['cp --sparse=always -r /mnt/kingston240/ /bac2/ext/`(date -u  "+%Y-%m-%dT%H:%M:%SZ")`'])
	shell2(['cp --sparse=always -r /mnt/kingston240/ /bac3/ext/`(date -u  "+%Y-%m-%dT%H:%M:%SZ")`'])
	stop(1), stop(2), stop(3).


run :-
	do_backup_all, halt.
	