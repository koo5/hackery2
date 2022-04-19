#!/usr/bin/python
from os import symlink, chdir, getcwd, mkdir, path
#a little tool to explode a git clone into a full inform project

class folder:
    def __init__(self, name):
	self.d = name
        if not path.exists(self.d):
	    print "making "+self.d
	    mkdir(self.d)
    def __enter__(self):
	chdir(self.d)
	return self
    def __exit__(self, type, value, traceback):
	chdir('..')


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



with folder(projectname+".inform"):
    folder("Build")
    folder("Index")
    folder("Source")
    link("Settings.plist")
    open("uuid.txt", "w").write("f00df00d-f00d-f00d-f00d-f00df00df00d")
    link("Source/story.ni")
    link("Build/output.ulx")
    open("Build/Debug log.txt", 'a')
    open("Index/Headings.xml", 'a')


