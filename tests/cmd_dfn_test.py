import pytest
from print_ext import print
from yaclipy.cmd_dfn import CmdDfn, SubCmds
from yaclipy.exceptions import *
from .has_cmds import HasCmds
from .testutil import exe

def test_obj_cmds():
    o1 = HasCmds(z=[1,2,3], def_={'k':'v'})
    
    assert(CmdDfn.scrape(o1).keys() == {'boink', 'break_','foo_', 'foo'})


class Bob():
    def __init__(self):
        self.s = ''

    

    def yes(self, times__t=1, *args):
        self.s += 'w'+'e'*times__t + ' '.join(args)


    @SubCmds(yes)
    def maybe(self, number__n=3):
        self.s += 'maybe'
        yield 'x'*number__n
        self.s += 'bye'
        return 'zz'


    def mayday(self, number__n=3):
        print(f"MAYDAY {number__n} {self.s}")
        self.s += 'mayday' * number__n
        print(f'?????? {self.s}')
        return self


    @SubCmds(maybe, mayday)
    def call_me(self, my__m='3', z:int=3, **kwargs):
        print(f"---- call_me {id(self)}  {kwargs}  {z}{type(z)}")
        if 'raise' in kwargs: raise ValueError(kwargs['raise'])
        self.s += my__m
        if 'num' in kwargs:
            return {'self':self, 'number__n':int(kwargs['num'])}


def test_cmd_execute_function():
    def funky(first__f, *, name__n='sarah', _hidden):
        print('hi')
        return f"FUNKY {first__f}, {name__n} {_hidden}"
    z = exe(funky, 'chair -n high', _hidden=42)
    assert(z == 'FUNKY chair, high 42')
    z = exe(funky, 'chair -n high upper', _hidden=42)
    assert(z == 'FUNKY CHAIR, HIGH 42')



def test_cmd_execute_method_alias():
    bob = Bob()
    with pytest.raises(TypeError):
        exe(bob.call_me, '-m happy --my__m 99')
    with pytest.raises(TypeError):
        exe(bob.call_me, '-m happy --self bad')
    with pytest.raises(ValueError):
        exe(bob.call_me, '-m happy --raise bad')
    
    

def test_cmd_subcall():
    bob = Bob()
    r = exe(bob.call_me, '--num 1 mayday')
    assert(bob.s == '3mayday')



def test_cmd_incoming():
    bob = Bob()
    exe(bob.mayday, '4', number__n=2)
    assert(bob.s == 'maydaymaydaymaydaymayday')
    bob.s = ''
    exe(bob.mayday, '', number__n=2)
    assert(bob.s == 'maydaymayday')





def test_cmd_generator():
    s = []
    def get(v):
        print(f"Collect {v} + {s}")
        s.append(v)

    @SubCmds(get)
    def f(times__t=3):
        print(f"f {times__t}")
        for i in range(times__t):
            yield dict(v = i+3)
        return 'x'

    exe(f, '- get')
    assert(s == [3,4,5])
    s[:]=[]
    exe(f, '2 get')
    assert(s == [3,4])

