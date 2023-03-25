import pytest
from print_ext import Printer
from yaclipy.arg_spec import ArgSpec, ArgType
from yaclipy.exceptions import UsageError


def test_underscore_args():
    def f(help, h, /, cat__c, *, dog__d, _dont__show): pass
    spec = ArgSpec(f)
    Printer().pretty(spec)
    names = set()
    for p in spec.params.values():
        names.update(p.aliases)
    
    assert(names == {'cat','c','dog','d','help','h'})



def test_hidden_must_be_keyword():
    def f(_ok): pass
    spec = ArgSpec(f)
    def f(_bad,/): pass
    with pytest.raises(UsageError):
        spec = ArgSpec(f)


def test_no_self_aliases():
    def f(_self): pass
    assert(ArgSpec(f).params['_self'].aliases == [])

    def f(self): pass
    assert(ArgSpec(f).params['self'].index == 1)

    def g(bob__self): pass
    with pytest.raises(UsageError):
        spec = ArgSpec(g)

    def h(x__self): pass
    with pytest.raises(UsageError):
        spec = ArgSpec(h)
