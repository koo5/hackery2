function alerts --description 'Show alerts raised by background jobs on any synced host'
    # Layout and write semantics are defined by
    # hackery2/src/hackery2/lib/alert.py -- read that first. Globbed directly
    # here rather than shelling out to it, so the identical glob in fish_prompt
    # stays fork-free on every prompt.
    set -l max 5
    # and a VM's share on this host (alert.py SHARES): /d/shared/dev44 is dev44's /shared44, /d2/u/shared/dev4 dev4-3's /shared43
    set -l files /d/sync/jj/host/*/alerts/*.alert /d/shared/dev44/alerts/*.alert /d2/u/shared/dev4/alerts/*.alert

    for f in $files
        set -l m (string match -r '/(?:host|shared)/([^/]+)/alerts/(.+)\.alert$' $f)
        set -l host $m[2]
        set -l name $m[3]

        set -l body (cat $f)
        set -l n (count $body)

        set_color -o yellow
        echo "⚠ $host/$name"
        set_color normal

        # Append-only alerts accumulate; show the newest and point at the file.
        if test $n -gt $max
            set_color brblack
            printf '  … %d earlier line(s)\n' (math $n - $max)
            set_color normal
            set body $body[(math $n - $max + 1)..-1]
        end
        printf '  %s\n' $body

        set_color brblack
        echo "  $f"
        set_color normal
    end

    # A VM's heartbeat past its age (alert.py stale_heartbeats): line 1 the age in seconds, line 2 the text.
    for hb in /d/shared/dev44/alerts/*.heartbeat /d2/u/shared/dev4/alerts/*.heartbeat
        set -l body (cat $hb)
        set -l age (path mtime -R $hb)
        test $age -gt $body[1]; or continue
        set -l m (string match -r '/shared/([^/]+)/alerts/(.+)\.heartbeat$' $hb)

        set_color -o yellow
        echo "⚠ $m[2]/$m[3] heartbeat stale"
        set_color normal
        printf '  last beat %d min ago (an alert past %d min)\n' (math -s0 $age / 60) (math -s0 $body[1] / 60)
        printf '  %s\n' $body[2..-1]

        set_color brblack
        echo "  $hb"
        set_color normal
    end
end
