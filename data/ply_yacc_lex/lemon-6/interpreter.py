#!/usr/bin/python
#-*- coding: utf-8 -*-


import simplejson
import parser


class parser_callbacks():
    def syntax_error(self, token):
	print "syntax error on token ", token
    def accept(self):
	print "accept"
    def parse_failed(self):
	print "parse_failed"


x = aaa.Parser(parser_callbacks())


code = simplejson.loads(open(sys.argv[0], "r").read())


code = [[parser.__dict__[x[0]],x[1]] for x in code] 


print code


x.parse(code)




#program interpreter environment
environment = {
	"rules":
	{	
		"program begins": [],
		"program ends": []
	}
	"variables":
	{
		"banana color" : "yellow"
	}
}



def interpret(ast):
	for x in ast:
##		if type(x) is ThingDeclaration:
#			if x.kind == "array"
	    pass

