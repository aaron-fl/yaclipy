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


def test_type_mismatch():
    def f(a:int, b:int, * c:int): pass
    s = ArgSpec(f)(['1','b','-c','9'])
    errs = set([e[0] for e in s.errors])
    assert(errs == {'NO_VALUE', 'TYPE_MISMATCH', 'UNK_PARAM'})
    estr = [e[1] for e in s.errors if e[0] == 'NO_VALUE'][0]
    assert('2nd' in str(estr))

