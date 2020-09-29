#!/usr/bin/python
import sys
sys.path+='.'
import swap.term
import __builtin__

class BI_Python(term.HeavyBuiltIn,term.ReverseFunction):
    def __init__(self, resource, fragid,func):
        term.Term.__init__(self, resource.store)
        self.resource = resource
        self.fragid = fragid
        self.pythonCallFunc=func

    def evalSubj(self, obj, queue, bindings, proof, query):
        func=self.pythonCallFunc
        return self.store._fromPython(func(*obj.value()))

    def value(self):
        return self.pythonCallFunc

def newinternFrag(self, fragid, thetype):
    if fragid and self.uri.startswith('python://') and \
           not (self.fragments.has_key(fragid) \
                and isinstance(self.fragments[fragid],BI_Python)):
        imports=self.uri.split('python://',1) # import optional module from python://MODULE
        subvars=fragid.split('.')
	print "yo", self.uri, imports, subvars
        if len(imports)>1 and imports[1]:
            module=__import__(imports[1])
            func=getattr(module,subvars[0])
        else:
            func=getattr(__builtin__,subvars[0]) # no module. Ex: python://#int
        for subvar in subvars[1:]: # to support a.b.c.d Ex: python://#str.rplit
            func=getattr(func,subvar)
        self.fragments[fragid]=BI_Python(self,fragid,func)
        return self.fragments[fragid]
    else:
        return self._oldinternFrag(fragid, thetype)
        

def monkeyPatch(module):
    if not hasattr(module.Symbol,'_oldinternFrag'):
        module.Symbol._oldinternFrag=module.Symbol.internFrag
        module.Symbol.internFrag=newinternFrag

monkeyPatch(term)
sys.modules['swap.term']=term
sys.modules['swap.swap.term']=term

if __name__=='__main__':
    import cwm
    cwm.doCommand()
