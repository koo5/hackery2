function g
	git $argv
end

function gs
	g status
end

function s
	g status
end
function a
	git add $argv
end
function c
	git commit $argv
end
function d
	git diff $argv
end
