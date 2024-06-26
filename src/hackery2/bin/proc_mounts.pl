:- use_module(library(dcg/basics)).

/*
note:
according to https://bugs.launchpad.net/ubuntu/+source/update-manager/+bug/112272
it may be better to parse /etc/mtab than /proc/mounts

todo:
interpret escape sequences, such as space encoded as \040
*/

mounts(Mounts) :-
	phrase_from_file(proc_mounts(Mounts), '/etc/mtab').


is_disk_mounted(I) :-
	atomics_to_string(['/dev/mapper/bac',I], Dev),
	atomics_to_string(['/bac',I], Mountpoint),

	mounts(Mounts),
	member(mount(Dev, Mountpoint, _,_,_,_), Mounts).


proc_mounts([Mount|Mounts]) --> 
	proc_mount(Mount),
	proc_mounts(Mounts).

proc_mounts([]) --> eos.

proc_mount(mount(A, B, C, D, E, F)) --> 
	piece(A), blank, 
	piece(B), blank, 
	piece(C), blank, 
	piece(D), blank, 
	piece(E), blank, 
	piece(F), /*{gtrace},*/string_without(`\n`, _), "\n".

piece(P) -->
	string_without(" \t\n", P_codes), {string_codes(P, P_codes)}.
