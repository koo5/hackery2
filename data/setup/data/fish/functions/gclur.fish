function gclur
	set tmp (mktemp)
	clone_into_username.py $argv | tee $tmp
	set result (cat $tmp | tail -n 1)
	echo 'gclur.fish got:' $result
	cd (echo $result | jq -r '.repo_fs_path')
end
