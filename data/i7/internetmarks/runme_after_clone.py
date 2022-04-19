#!/usr/bin/python
from os import symlink, chdir, getcwd, mkdir, path
#a little tool to explode a git clone into a full inform project



def make(d):
    if not path.exists(d):
	print "making "+d
	mkdir(d)

def link(dst):
    if not path.lexists(dst):
	print "linking "+dst
	head,tail = path.split(dst)
	if tail == dst:
	    prefix = '../'
	else:
	    prefix = '../../'
	symlink(prefix+path.basename(dst),dst)



#supposing we are running in the project base directory
projectname = path.basename(getcwd())
print "my name is "+projectname+'     #supposing we are running in the project base directory'



make(projectname+".inform")
chdir(projectname+".inform")

make("Build")
make("Index")
make("Source")
link("Settings.plist")
link("uuid.txt")
link("Source/story.ni")
link("Build/output.ulx")



open("Build/Debug log.txt", 'a')
open("Index/Headings.xml", 'a')


