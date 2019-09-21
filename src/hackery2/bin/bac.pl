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

do_backup(I) :-
	shell2(['cryptdisks_start bac', I]),
	shell2(['mount /bac', I]),
	shell2(['df -h']),
	shell2(['rm /.sxbackup; ln -s /.sxbackup-',I,' /.sxbackup; ~/.local/bin/btrfs-sxbackup run /']),
	shell2(['df -h']),
	shell2(['umount /bac', I]),
	shell2(['cryptdisks_stop bac', I]).

do_backup_all :-
	do_backup(1), do_backup(2).

run :-
	do_backup_all, halt.
	