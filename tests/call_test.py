import pytest
from yaclipy import sub_cmds
from .testutil import exe
from yaclipy.arg_spec import sig_kinds

def nope(*, _input):
    s = f"Nope: {_input}"
    print(s)
    return s


class Bob():
    def __init__(self):
        self.s = ''

    @classmethod
    def classy(cls, y):
        s = f'A Classy function {cls.__name__} {y}'
        print(s)
        return s

    @staticmethod
    def cling(x):
        print(f'cling {x}')
        return f'cling {x}'


    def yes(self, times__t=1, *args):
        self.s += 'w'+'e'*times__t + ' '.join(args)

    @sub_cmds(yes)
    def maybe(self, number__n=3):
        self.s += 'maybe'
        yield 'x'*number__n
        self.s += 'bye'
        return 'zz'

    def mayday(self, number__n=3):
        self.s += 'mayday ' * number__n
        print(f'mayday {self.s}')
        return self

    @sub_cmds(maybe, mayday, nope, cling)
    def call_me(self, my__m='3', z:int=3, **kwargs):
        print(f"---- call_me {id(self)}  {kwargs}  {z}{type(z)}")
        if 'raise' in kwargs: raise RuntimeError(kwargs['raise'])
        self.s += f'{my__m} {z} {kwargs}'
        if 'num' in kwargs:
            return {'self':self, 'number__n':int(kwargs['num'])}



def test_hundred():
    @sub_cmds(Bob.call_me, Bob.mayday)
    def hundred(_a_bob):
        _a_bob.s += 'hundred '
        yield dict(self=_a_bob, number__n=100)
    b = Bob()
    exe(hundred, 'call-me --train tracks', _a_bob=b, zzz=3)
    assert(b.s == "hundred 3 3 {'train': 'tracks', 'number__n': 100}")



def test_vargs_with_defaults():
    def f(pos1=0, pos2=3, *args): pass
    exe(f, '-- and the rest', pos1=1)



def test_bind_array_double_dash():
    def f(a:[int], *, b:[int]) -> list: return a+b
    assert(exe(f, '1 2 3 -b# 4 5 6 -- pop') == 6)




def test_call_func():
    def funky(first__f, *, name__n='sarah', _hidden) -> str:
        return f"FUNKY {first__f}, {name__n} {_hidden}"
    z = exe(funky, 'chair -n high', _hidden=42)
    assert(z == 'FUNKY chair, high 42')
    z = exe(funky, 'chair -n high upper', _hidden=42)
    assert(z == 'FUNKY CHAIR, HIGH 42')



def test_call_input_trumps_default():
    def f(a:int,/,b=3,*,c=4): return (a,b,c)
    assert(exe(f, '1', b=9) == (1,9,4))


def test_call_cmdline_trumps_input():
    def f(a:int,/,b=3,*,c=4): return (a,b,c)
    assert(exe(f, '1 2', b=9) == (1,2,4))



def test_cmd_execute_method_alias():
    def f(my__m='3', **kwargs): return my__m
    assert(exe(f, '') == '3')
    assert(exe(f, 'happy') == 'happy')
    assert(exe(f, 'happy --my__m 99') == '99')



def test_raises():
    with pytest.raises(RuntimeError):
        exe(Bob().call_me, '-m happy --raise bad')
    
    

def test_cmd_subcall():
    bob = Bob()
    r = exe(bob.call_me, '--num 1 mayday')
    assert(bob.s == "3 3 {'num': '1'}mayday ")



def test_cmd_incoming():
    bob = Bob()
    exe(bob.mayday, '4', number__n=2)
    assert(bob.s == 'mayday mayday mayday mayday ')
    bob.s = ''
    exe(bob.mayday, '', number__n=2)
    assert(bob.s == 'mayday mayday ')



def test_cmd_generator():
    s = []
    def get(v=None):
        print(f"Collect {v} + {s}")
        s.append(v)

    @sub_cmds(get)
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



def test_call_async():
    async def f(times__t=3):
        return 'hi'*times__t
    v = exe(f, '-t 2')
    assert(v == 'hihi')



def test_call_sub_async():
    async def g(*, _input):
        return f"VALUE:{_input}"

    @sub_cmds(g)
    async def f(times__t=3):
        return 'hi'*times__t

    v = exe(f, '-t 2 g')
    assert(v == 'VALUE:hihi')



def test_call_sub_async_gen():
    async def g(*, _input):
        return f"VALUE:{_input}"
    @sub_cmds(g)
    async def f(times__t=3):
        yield 'a'
        yield 'b'
    v = exe(f, '-t 2 g')
    assert(v == ['VALUE:a','VALUE:b'])



def test_call_sub3():
    def h(*, _input):
        yield 'h'
    @sub_cmds(h)
    async def g(*, _input):
        yield 'g'
    @sub_cmds(g)
    def f():
        yield 'f'
    v = exe(f, 'g h')
    assert(v == [[['h']]])



def test_call_class():
    class Jim():
        def __init__(self, x):
            self.x = x
        def g(self):
            return f"jim:{self.x*self.x}"
    class Bob(Jim):
        def __call__(self) -> Jim:
            return self
    
    v = exe(Bob(3), 'g')
    assert(v == 'jim:9')
