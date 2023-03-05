import pytest
from print_ext import print
from yaclipy.arg_spec import ArgSpec, ArgType




def test_underscore_args():
    def f(_hidden, help, h, /, cat__c, *, dog__d, _dont__show): pass
    spec = ArgSpec(f)
    print.pretty(spec)
    #assert(False)




def test_method_args():
    class T():
        def x(self, b=4): pass
    t = T()
    spec = ArgSpec(t.x)
    print.pretty(spec)
    #assert(False)
