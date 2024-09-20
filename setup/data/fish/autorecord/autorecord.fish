if status is-interactive

	#echo "we are $fish_pid"

	if [ "x$SESSION_RECORD" = "x" -a "x$MC_SID" = "x" ]

		set my (string join - /var/log/session/ $USER $ts $fish_pid)

		echo "$argv" > $my-argv
		env > $my-env

		set ts (date -u '+%Y-%m-%dZ%H-%M-%S-%N')

		# this variable will prevent the fish spawned on the next line to try to spawn another fish ad infinity
		set -gx SESSION_RECORD $my-session

		# User session happens inside the script command here, it invokes another instance of fish
		script -q --flush -e -T $SESSION_RECORD.timing -B $SESSION_RECORD

		set exit_status $status
		echo "exit $exit_status"

		# Make sure $fish_pid terminates. We cannot just call exit here, it would merely abort the sourcing of this file and $fish_pid would continue.
		function fish_prompt
			exit $exit_status
		end

	else
		#SESSION_RECORD is set, this means we are the fish invoked from within script
		echo scriptreplay -t $SESSION_RECORD.timing -B $SESSION_RECORD --maxdelay 0.5 --divisor 1
	end
	# we erase this before we get to the interactive shell, so that nested invocations of fish can do their own recording too
	set --erase SESSION_RECORD
end
