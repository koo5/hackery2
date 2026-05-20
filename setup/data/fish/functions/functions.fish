alias dvr 'docker volume remove'
alias rp realpath
alias mc 'mc -b'
alias ccs 'python3 /home/koom/hackery2/src/hackery2/bin/cc_sessions.py'
alias ro 'chmod u-w'
alias rw 'chmod u+w'
alias x 'chmod u+x'
function nox
    for f in $argv
        if test -f $f
            chmod u-x $f
        end
    end
end

