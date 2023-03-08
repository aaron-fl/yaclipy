import pytest
from yaclipy import sub_cmds
from yaclipy.exceptions import CmdError
from .testutil import exe


def foo(say, times__t=1) -> str:
    ''' Say something multiple times

    Parameters:
        <message>, --say <message>
            What you want to say
        <int>, --times <int>, -t <int>
            How many times you want to say it.
    '''
    return ' '.join([say] * times__t)


def test_intro_0():
    assert(exe(foo,'-t 3 --say Ho') == 'Ho Ho Ho')


def test_intro_1():
    assert(exe(foo, ['Hello World', '2']) == 'Hello World Hello World')


def test_intro_2():
    assert(exe(foo, 'go --times 3 upper') == 'GO GO GO')


def test_intro_3():
    assert(exe(foo, '\\--times') == '--times')


def test_posvkw():
    def f(a=3, /, banana__b='hi', *, carrot__c:int=None): return a, banana__b, carrot__c
    assert(exe(f, '4 bye --carrot 42') == (4, 'bye', 42))
    assert(exe(f, '4 -c 42 -b bye') == (4, 'bye', 42))


def test_flags():
    def f(*, verbose__v=False, times__t:int): return verbose__v, times__t
    assert(exe(f, '-vt 3 --verbose') == (2,3))
    assert(exe(f, '-vv --times 3') == (2,3))

def test_names():
    def f(*, if_=1, happy_days=2, lots__of__aliases__t__q=3, _hidden=4): return if_,happy_days,lots__of__aliases__t__q, _hidden
    assert(exe(f, '--if 10 --happy-days 20 --happy_days 200 --lots 30 --of 40 --aliases 50 -t 60 -q 70') == (10, 200, 70, 4))
    

def test_subcmds():

    def foo(*, name, _value): return 'foo', name, _value

    def bar(*, name, _value): return 'bar', name, _value

    @sub_cmds(foo, baz=bar)
    def root(*, verbose__v=False):
        return dict(name='jim', _value = 'hi' * int(verbose__v))

    with pytest.raises(CmdError):
        exe(root, '-v foo -h') == ('foo', 'jim', 'hi')
    assert(exe(root, '-vv baz --name bob') == ('bar', 'bob', 'hihi'))


def test_readme_generator(capfd):
    def show(*, _input):
        x, xxx = _input
        print(f'3^{x} == {xxx}')

    @sub_cmds(show)
    def foo(*, times__t=3):
        for i in range(times__t):
            yield i, pow(3,i)

    exe(foo, '-t 4 show')
    out, _ = capfd.readouterr()  
    assert(out == '3^0 == 1\n3^1 == 3\n3^2 == 9\n3^3 == 27\n')


def test_readme_lists():
    def f(a:int, b:[float], c=[]): return a,b,c
    assert(exe(f, '3 1.1 -.1 1e3 - 66 \\-apples') == (3, [1.1, -0.1, 1e3], ['66', '-apples']))
    assert(exe(f, '-c 66 -c \\-apples -b#3 1.1 -0.1 1e3 -a 3') == (3, [1.1, -0.1, 1e3], ['66', '-apples']))
    assert(exe(f, '3 1.1 - -c# 66 \\-apples - -b#2 -.1 1e3') == (3, [1.1, -0.1, 1e3], ['66', '-apples']))


def test_readme_json():
    def f(*, x={}, y:dict): return x, y
    assert(exe(f, ['-x','{"x":[1,2,3]}','-y','null']) == ({'x':[1,2,3]}, None))
    

def test_readme_argv():
    def f(first=None, *files, verbose__v=False): return first, files, verbose__v
    assert(exe(f, 'a b c') == ('a', ('b','c'), False))
    assert(exe(f, '- a b c') == (None, ('a', 'b','c'), False))
    assert(exe(f, '- - -v b c') == (None, ('-v', 'b','c'), False))
    assert(exe(f, '-- -v b c') == (None, ('-v', 'b','c'), False))


def test_readme_kwargs():
    def f(a=False, **kwargs) -> str:
        a == True
        kwargs == {'x':True, 'd':['33','44'], 'apple':'x', 'banana':True}
        return f'{a} {kwargs}'
    assert(exe(f, '-axd 33 -d 44 --apple x --banana - upper') == "TRUE {'X': TRUE, 'D': ['33', '44'], 'APPLE': 'X', 'BANANA': TRUE}")
        