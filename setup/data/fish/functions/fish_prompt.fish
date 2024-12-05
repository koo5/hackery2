function fish_prompt --description 'Informative prompt'
    #Save the return status of the previous command
    set -l last_pipestatus $pipestatus
    set -lx __fish_last_status $status # Export for __fish_print_pipestatus.

	git rev-parse --short HEAD 2&> /dev/null
	if test $status -eq 0
	    set -l git_commit (git rev-parse --short HEAD)
    	if test -n "$git_commit"
        	echo -n (set_color green)"[$git_commit] "(set_color normal)
    	end
	end

# set -U __fish_git_prompt_show_informative_status 1
# set -U __fish_git_prompt_showupstream "informative"
# set -U __fish_git_prompt_showdirtystate "yes"
# set -U __fish_git_prompt_showstashstate "yes"
# set -U __fish_git_prompt_showuntrackedfiles "yes"\
# set -U __fish_git_prompt_describe_style haha


    set -l vcs_info (fish_vcs_prompt)

    if functions -q fish_is_root_user; and fish_is_root_user
        printf '%s@%s %s%s%s# ' $USER (prompt_hostname) (set -q fish_color_cwd_root
                                                         and set_color $fish_color_cwd_root
                                                         or set_color $fish_color_cwd) \
            (prompt_pwd) (set_color normal)
    else
        set -l status_color (set_color $fish_color_status)
        set -l statusb_color (set_color --bold $fish_color_status)

        
        set -l pipestatus_string (__fish_print_pipestatus "[" "]" "|" "$status_color" "$statusb_color" $last_pipestatus)

        printf '[%s] %s%s@%s %s%s%s%s %s%s%s\n \n' (date "+%H:%M:%S") (set_color brblue) \
            $USER (prompt_hostname) (set_color $fish_color_cwd) $PWD (set_color yellow) $vcs_info $pipestatus_string (set_color normal)
    end
end
