function alerts --description 'Show alerts raised by background jobs on any synced host'
    # Layout and write semantics are defined by
    # hackery2/src/hackery2/lib/alert.py -- read that first. Globbed directly
    # here rather than shelling out to it, so the identical glob in fish_prompt
    # stays fork-free on every prompt.
    set -l max 5
    set -l files /d/sync/jj/host/*/alerts/*.alert

    for f in $files
        set -l m (string match -r '/host/([^/]+)/alerts/(.+)\.alert$' $f)
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
end
