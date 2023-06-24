#if [ "x$session_record" = "x" ]

set ts (date -u '+%Y-%m-%dZ%H-%M-%S-%N')
set -gx SESSION_RECORD "/var/log/session/session.$USER.$fish_pid_$ts"
#script -t -f -q 2> "$ESSION_RECORD.timing" $SESSION_RECORD

script -q -e -T "$SESSION_RECORD.timing" -B $SESSION_RECORD

#fi
