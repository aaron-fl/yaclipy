import pytest
from print_ext import print
from yaclipy.cmd_dfn import CmdDfn, sub_cmds
from yaclipy.exceptions import *
from .testutil import exe



class Parent():
    def boink(self):
        return 'boink'


class HasCmds(Parent):
    x = 33
    y = lambda x: x+1

    def __init__(self,**kwargs):
        for k,v in kwargs.items(): setattr(self, k,v)

    def __str__(self):
        return ''

    def foo_(self):
        return "There are two foo's"

    def foo(self, x=3):
        return 'foo'*x

    def break_(self, what='everything'):
        return 'break '+what



def test_cmd_retval_sub_cmds():
    def f() -> HasCmds: pass
    subs = CmdDfn('f',f).sub_cmds()
    assert(subs.keys() == {'boink', 'break_', 'foo', 'foo_', 'y'})



def test_cmd_sub_cmds():
    @sub_cmds(str, if_=str, bob_cob=str)
    def f(): pass
    subs = CmdDfn('f',f).sub_cmds()
    assert(subs.keys() == {'str', 'if_', 'bob_cob'})
