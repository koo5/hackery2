#!/usr/bin/env python3


import os,time,datetime,subprocess,glob, fire

@fire.Fire
def action_camera_tiles(long_file,short_file1,short_file2=None):
	o = subprocess.check_output(['/home/koom/repos/bbc/audio-offset-finder/0/audio-offset-finder/venv/bin/audio-offset-finder',  '--find-offset-of', long_file, '--within', short_file1], text=True)
	print(o)
	oo = o.split()
	if oo[0] != 'Offset:' or oo[2] != '(seconds)': 
		raise Exception('unexpected output: ' + o + str(oo))
	offset = oo[1]
	
	if short_file2 is None:
		short_file2 = '~/Documents//bl.mp4'

	long_file_basename = os.path.basename(long_file).split('.')[0]
			
	cmd = f"""ffmpeg -i {long_file}  -r 118.008 -i {short_file1} -i {short_file2} -r 118.008 \
-filter_complex \
"[0:v]tpad=start_duration={offset}[v0]; \
[0:a]adelay={offset}|{offset}[a0]; \
[1:v:0][1:a:0][2:v:0][2:a:0]concat=n=2:v=1:a=1[vconcat][aconcat]; \
[vconcat]tpad=start_duration=0[v1]; \
[aconcat]adelay=0|0[a1]; \
[v0]setpts=2.0*PTS[v0slow]; \
[a0]atempo=0.5[a0slow]; \
[v1]setpts=2.0*PTS[v1slow]; \
[a1]atempo=0.5[a1slow]; \
[v0slow][v1slow]hstack=inputs=2[v]; \
[a0slow][a1slow]amix=inputs=2[a]" \
-map "[v]" -map "[a]"  -movflags +faststart  -preset slow  -crf 23  -y   stack_{long_file_basename}.mp4"""
	
	print(cmd)
	
	subprocess.run(cmd, shell=True)
	
	
	