function file_range

    set start $argv[1]
    set end $argv[2]
    set files $argv[3..-1]
    if test -z "$files"
        set files (ls | sort -V)
    end
    set span $files[(contains -i -- $start $files)..(contains -i -- $end $files)]
    for file in $span
        echo (rp $file)
    end

end

