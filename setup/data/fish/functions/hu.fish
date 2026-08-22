function hu
	set -l dir $argv[1]
	test -n "$dir"; or set dir .
	hugin $dir/*_pto_canvas*/pano.pto
end
