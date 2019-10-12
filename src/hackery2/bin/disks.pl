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
	shell2(['cryptdisks_start bac', I]),
	shell2(['mount /bac', I]).

stop(I) :-
	shell2(['umount /bac', I]),
	shell2(['cryptdisks_stop bac', I]).	

start :-
	maplist(start, [1,2,3]),
	shell2(['df -h']),
	halt.

stop :-
	maplist(stop, [1,2,3]),
	shell2(['df -h']),
	halt.




% diff --no-dereference  -rq /bac1/new_offline/ /bac2/new_offline/ | tee dif12



