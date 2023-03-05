import re
from print_ext import print
from yaclipy.arg_spec import ArgSpec


def _tst(spec, args):
    s = spec({}, args.split(' ') if args else [])
    if s.errors:
        print.pretty(s)
        assert(False)
    return s


def _tstkw(spec, args):
    s = _tst(spec, args)
    return [(k,s.kwargs[k]) for k in sorted(s.kwargs) if k]


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
        print(e)
    assert(matched == errs)



def test_parse_parg_simple():
    def f(a, b): pass
    spec = ArgSpec(f)
    assert(_tst(spec, '-- ---').args == ['-','--'])
    assert(_tst(spec, '-.1 -0').args == ['-.1','-0'])
    assert(_tst(spec, '1 2').args == ['1', '2'])
    assert(_tst(spec, '1 -2').args == ['1', '-2'])



def test_parse_parg_pargs():
    def f(a, *args): pass
    spec = ArgSpec(f)
    assert(_tst(spec, 'a - b c -- d').args == ['a','-','b','c','--','d'])



def test_parse_parg_sublists():
    def f(a:[], b, c=[2], *args): pass
    spec = ArgSpec(f)
    assert(_tst(spec, 'a b - c - d e').args == [['a','b'],'c',[2], 'd','e'])



def test_parse_parg_lacking():
    def f(*, a=1, b=2): pass
    spec = ArgSpec(f)
    assert(_tst(spec, '- a b').args == [])



def test_parse_parg_use_defaults():
    def f(a=3, b=4, *, c=1, d=2): pass
    spec = ArgSpec(f)
    assert(_tst(spec, '- - next').args == [3, 4])



def test_parse_kwargs_bools():
    def f(*, test__x=False, y=False): pass
    spec = ArgSpec(f)
    assert(_tstkw(spec, '-xxy --test --y -yyy next') == [('test__x',3), ('y',5)])



def test_parse_kwargs_kwargs():
    def f(*, x, y=9, **kwargs): pass
    spec = ArgSpec(f)
    assert(_tstkw(spec, '-x -x --and the --and bob -bt jim -bb - done') == [('and', ['the','bob']), ('b',3), ('t','jim'), ('x','-x'), ('y',9)])



def test_parse_kwargs_bool_val_mix():
    def f(*, x, y=9, z=False): pass
    spec = ArgSpec(f)
    assert(_tstkw(spec, '-zx -y 1') == [('x','-y'), ('y',9), ('z', True)])
    _tsterr(spec, '-xz 3', r'.*type mismatch.*', r'.*no value.*keyword.*parameter.*-x.*')



def test_parse_kwargs_ill_formed():
    def f(*, x, y=9, z=False): pass
    spec = ArgSpec(f)
    _tsterr(spec, '--x 3 ---y 3', r'.*invalid.*---y.*')
    _tsterr(spec, '--x 3 -- y 3', r'.*invalid.*--.*')
    assert(_tstkw(spec, '--x 3 - -zy 3') == [('x', '3'), ('y', 9), ('z', False)])



def test_parse_kwargs_overwrite():
    def f(*, x, y=9, z=False): pass
    spec = ArgSpec(f)
    assert(_tstkw(spec, '-x 3 -x 99') == [('x','99'),('y',9),('z',False)])



def test_parse_kwargs_unknown():
    def f(*, x, y=9, z=False): pass
    spec = ArgSpec(f)
    _tsterr(spec, '--x 3 -ztt --cats', r'.*unknown.*--cats.*true.*', r'.*unknown.*-t.*2.*')
    


def test_parse_kwargs_missing():
    def f(*, x, y=9, z=False): pass
    spec = ArgSpec(f)
    _tsterr(spec, '-zz -x - --y', r'.*--y.*missing.*')



def test_parse_kwargs_done():
    def f(*, x, y=9, z=False): pass
    spec = ArgSpec(f)
    assert(_tstkw(spec, '-x 3 -.3 -y 10') == [('x','3'),('y',9),('z',False)])
    assert(_tstkw(spec, '-x 3 done -y 10') == [('x','3'),('y',9),('z',False)])
    assert(_tstkw(spec, '-x 3 - -y 10') == [('x','3'),('y',9),('z',False)])
  


def test_parse_defaults_bypass_coerce():
    def f(*, x:[int]=34): pass
    spec = ArgSpec(f)
    assert(_tstkw(spec, '') == [('x',34)])



def test_parse_no_value():
    def f(def___if_, *, bob__x, y=9, z=False): pass
    spec = ArgSpec(f)
    _tsterr(spec, '-zz -y 3', r'.*no value.*--def.*--if.*', r'.*no value.*--bob.*-x.*')



def test_parse_unknown_missing():
    def f(**kwargs): pass
    spec = ArgSpec(f)
    _tsterr(spec, '--bob hi, --bob', r'.*--bob.*missing.*')
    assert(_tstkw(spec, '--bob') == [('bob',True)])
    assert(_tstkw(spec, '--bob --bob') == [('bob','--bob')])
    assert(_tstkw(spec, '-ax -a -a') == [('a',2), ('x','-a')])
    assert(_tstkw(spec, '--bob hi') == [('bob','hi')])
 


def test_parse_kw_array():
    def f(*, flag__f=False, a:[float], b:[]=[1,2,3]): pass
    spec = ArgSpec(f)
    assert(_tstkw(spec, '-a 1 -b 2') == [('a',[1]), ('b',['2']), ('flag__f',False)])
    assert(_tstkw(spec, '-a 1 --a 2 -b#1 2') == [('a',[1, 2]), ('b',['2']), ('flag__f',False)])
    assert(_tstkw(spec, '-fb#3 1 2 - -ffa# 2 -.3 8 3 -1') == [('a',[2,-0.3,8,3,-1]), ('b',['1','2','-']), ('flag__f',3)])



def test_parse_kw_bad_array():
    def f(*, flag__f=False, a:[float], b:[]=[1,2,3]): pass
    spec = ArgSpec(f)
    _tsterr(spec, '-a 1 -#3 1 1 1', r'.*invalid.*-#3.*')
    _tsterr(spec, '-a 1 -f#3 1 1 1', r'.*invalid.*-f#3.*')
    _tsterr(spec, '-a#4 1 2', r'.*expected.*4.*received.*2.*')
    _tsterr(spec, '-a 4 -a#4', r'.*expected.*4.*received.*0.*')
