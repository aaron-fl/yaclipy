import re
from inspect import Parameter
from print_ext import Printer
from yaclipy.arg_spec import ArgSpec
from .testutil import bind, bind_err, bind_unused


def _tsterr(spec, args, *errs):
    matcherrs = list(errs)
    matched = []
    s = spec({}, args.split(' ') if args else [])
    if not s.errors: raise Exception("No errors thrown")
    errs = list(errs)
    def _match(e):
        if not (errs and re.match(matcherrs[0], str(e).lower())): return
        matched.append(matcherrs.pop(0))
        return True
    errors = [e for e in s.errors[:-1] if not _match(e)]
    for e in errors:
        Printer(e)
    assert(matched == errs)



def test_bind_positional():
    def f(a, b, /): pass
    assert(bind(f, '\\ -33') == (['','-33'], []))
    assert(bind(f, '-.1 -0') == (['-.1','-0'], []))



def test_bind_pargs():
    def f(a, *args): pass
    assert(bind(f, 'a - b c -- d') == (['a','b','c','--','d'], []))



def test_bind_pos_slists():
    def f(a:[], b, c=[2], *args): pass
    assert(bind(f, 'a b - c -- -k -') == ([['a','b'],'c', Parameter.empty, '-k','-'], []))



def test_bind_parg_lacking():
    def f(*, a=1, b=2): pass
    assert(bind(f, '-') == ([],[]))
    


def test_bind_parg_use_defaults():
    def f(a=3, b=4): pass
    assert(bind(f, '- -4 -a 1') == ([1, -4], []))



def test_bind_kwargs_bools():
    def f(*, test__x=False, y=False): pass
    assert(bind(f, '-xxy --test --y -yyy') == ([], [('test__x',3), ('y',5)]))



def test_bind_kwargs_kwargs():
    def f(*, x, y=9, **kwargs): pass
    assert(bind(f, '-x \\ --and the --and bob -bt jim -bbz -') == ([], [('and', ['the','bob']), ('b',3), ('t','jim'), ('x',''), ('z',True)]))



def test_bind_triple_dash():
    def f(a=1, b=2, c=3, d=[0], *args): pass
    assert(bind(f, '--- 5 6 - 7') == ([Parameter.empty,Parameter.empty,Parameter.empty,[5,6],'7'], []))



def test_bind_kwargs_bool_val_mix():
    def f(*, x, y=9, z=False): pass
    assert(bind(f, '-zx 3') == ([], [('x','3'), ('z', True)]))
    assert(bind_err(f, '-xz 3') == {'NO_VALUE', 'UNUSED', 'TYPE_MISMATCH'})



def test_bind_kwargs_ill_formed():
    def f(*, x, y=9, z=False): pass
    assert(bind_err(f, '--x 3 ---y 3') == {'BAD_KW', 'UNUSED'})



def test_bind_kwargs_overwrite():
    def f(*, x, y=9, z=False): pass
    assert(bind(f, '-x 3 -x 99') == ([], [('x','99')]))



def test_parse_kwargs_unknown():
    def f(*, x, y=9, z=False): pass
    assert(bind_err(f, '--x 3 -ztt --cats') == {'UNK_PARAMx2'})
    


def test_bind_KW_VAL_MISSING():
    def f(*, x, y=9, z=False): pass
    assert(bind_err(f, '-zz -x - --y') == {'NO_VALUE', 'UNUSED','KW_VAL_MISSING'})



def test_bind_kwargs_done():
    def f(*, x, y=9, z=False): pass
    assert(bind_unused(f, '-x 3 -.3 -y 10') == ['-.3','-y','10'])
    assert(bind_unused(f, '-x 3 done -y 10') == ['done', '-y', '10'])
    assert(bind_unused(f, '-x 3 - -y 10') == ['-y','10'])
  


def test_bind_defaults_bypass_coerce():
    def f(*, x:[int]=34): pass
    assert(bind(f, '') == ([], []))



def test_bind_no_value():
    def f(def___if_, *, _hidden, bob__x, y=9, z=False): pass
    assert(bind_err(f, '-zz -y 3') == {'NO_VALUEx2'})



def test_bind_unknown_missing():
    def f(**kwargs): pass
    assert(bind_err(f, '--bob hi --bob') == {'KW_VAL_MISSING'})
    assert(bind(f, '--bob') == ([],[('bob',True)]))
    assert(bind(f, '--bob --bob') == ([], [('bob',2)]))
    assert(bind(f, '-ax -a -a') == ([], [('a',3), ('x',True)]))
    assert(bind(f, '--bob hi') == ([], [('bob','hi')]))
 


def test_bind_kw_array():
    def f(*, flag__f=False, a:[float], b:[]=[1,2,3]): pass
    assert(bind(f, '-a 1 -b 2') == ([], [('a',[1]), ('b',['2'])]))
    assert(bind(f, '-a 1 --a 2 -b#1 2') == ([],[('a',[1, 2]), ('b',['2'])]))
    assert(bind(f, '-fb#3 1 2 \\- -ffa# 2 -.3 8 3 -1') == ([],[('a',[2,-0.3,8,3,-1]), ('b',['1','2','-']), ('flag__f',3)]))



def test_bind_kw_bad_array():
    def f(*, flag__f=False, a:[float]): pass
    assert(bind(f, '-a 1 --a#3 1 1 1') == ([], [('a',[1,1,1,1])]))
    assert(bind_err(f, '-a 1 -f#3 1 1 1') == {'NOT_LIST', 'UNUSED'})



def test_bind_LIST_TOO_FEW():
    def f(a:[int]): pass
    assert(bind_err(f, '-a#4 1 2') == {'LIST_TOO_FEW'})
    assert(bind_err(f, '-a 4 -a#1') == {'LIST_TOO_FEW'})



def test_bind_pos_array():
    def f(a:[], *, t=None): pass
    assert(bind(f, 'a b -t c') == ([['a','b']], [('t','c')]))



def test_bind_args_and_kwargs():
    def f(*args, **kwargs): pass
    assert(bind(f, 'a --bob c d e - f') == (['a','--bob','c','d','e','-','f'], []))
    assert(bind(f, '-ax --bob - -x d - f') == (['d','-','f'], [('a',True),('bob',True), ('x',2)]))
    

def test_bind_self():
    def f(self, my__m='3', **kwargs): pass
    assert(bind_err(f, '-m happy --self bad') == {'SELF', 'UNUSED'})


def test_bind_empty_array():
    def f(a:[]): pass
    assert(bind(f, '-a# -') == ([[]], []))
