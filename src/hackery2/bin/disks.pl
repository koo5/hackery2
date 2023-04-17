:- [proc_mounts].

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


start(I) :-
	start(I, _, _).

start(I, Exit_status1, Exit_status2) :-
	shell2(['cryptdisks_start bac', I], Exit_status1),
	shell2(['cryptdisks_start bac', I, '_2'], Exit_status1_2),
	shell2(['mount /bac', I], Exit_status2).

start_or_fail(I) :-
	start(I, 0, 0).

try_ensure_mounted(I) :-
	is_disk_mounted(I),!.

try_ensure_mounted(I) :-
	start(I, _, _),
	is_disk_mounted(I).

stop(I) :-
	shell2(['umount /bac', I]),
	shell2(['cryptdisks_stop bac', I]),
	shell2(['cryptdisks_stop bac', I, '_2']).

my_disks_are([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]).

start :-
	my_disks_are(Disks),
	maplist(start, Disks),
	shell2(['df -h']),
	halt.

stop :-
	my_disks_are(Disks),
	maplist(stop, Disks),
	shell2(['df -h']),
	halt.




% diff --no-dereference  -rq /bac1/new_offline/ /bac2/new_offline/ | tee dif12



