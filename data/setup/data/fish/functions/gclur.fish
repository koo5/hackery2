function gclur
	set r (clone_into_username.py $argv)
	echo 'got:' $r
	cd (echo $r | jq -r '.filesystem_path')
end
