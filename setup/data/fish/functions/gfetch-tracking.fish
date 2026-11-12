function gfetch-tracking --description "fetch a checkout's remote-tracking refs (for remotes with no local branches)"
    if test (count $argv) -lt 1
        echo "usage: gfetch-tracking <remote> [<their-remote>=origin]" >&2
        return 2
    end
    set -l remote $argv[1]
    set -l theirs origin
    if test (count $argv) -ge 2
        set theirs $argv[2]
    end
    git fetch $remote "+refs/remotes/$theirs/*:refs/remotes/$remote/*"
end
