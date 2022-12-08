function gclur
	mkdir -p ~/repos; cd ~/repos
	clone_into_username.py $argv[-1]
end
