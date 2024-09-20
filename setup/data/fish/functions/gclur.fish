function gclur

# make a temp file to store the output of the python script
	set tmp (mktemp)
	clone_into_username.py $argv | tee $tmp

# the machine-readable result is on the last line of it
	set result (cat $tmp | tail -n 1)
	echo 'gclur.fish got:' $result

	set path (echo $result | jq -r '.repo_fs_path')
	cd $path
end
