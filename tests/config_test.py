import pytest, traceback, contextvars
from yaclipy.config import *
from print_ext import pretty, StringPrinter
from .testutil import tostr


def test_UNSET():
    assert(str(UNSET) == '*UNSET*')
    assert(not UNSET)
    def in_ctx():
        v1 = config_var()
        try:
            print(v1())
            assert(False)
        except ConfigVarUnset as e:
            v = tostr(pretty(e))
            print(v)
            assert('in_ctx.v1' in v)
            assert('config_test.py' in v)
    copy_config().run(in_ctx)



def test_config_var_user():
    def in_ctx():
        v1 = config_var(mydata=3)
        cfg = get_config()
        assert(set(v.name for v in cfg.vars) == {'in_ctx.v1'})
        assert(v1.mydata == 3)
    copy_config().run(in_ctx)


def test_config_sub_var_count():
    def in_ctx():
        v1 = config_var()
        def sub_ctx():
            v2 = config_var()
            assert(set(v.name for v in get_config().vars) == {'in_ctx.v1', 'sub_ctx.v2'})
        copy_config().run(sub_ctx)
        assert(set(v.name for v in get_config().vars) == {'in_ctx.v1'})
    copy_config().run(in_ctx)



def test_config_var_name():
    def in_ctx():
        ab = config_var()
        a,b = config_var(), config_var(name='ab.c')
        class Bob():
            jim = config_var()
        assert(ab.name == 'in_ctx.ab')
        assert(a.name == 'in_ctx.unk')
        assert(b.name == 'ab.c')
        assert(Bob.jim.name == 'Bob.jim')
    copy_config().run(in_ctx)



def test_config_var_coerce():
    def in_ctx():
        v = config_var('asdf', '123', lambda x: int(x))
        assert(v() == 123)
        v('asdf')
        with pytest.raises(ValueError):
            v()
    copy_config().run(in_ctx)



def test_config_var_cached():
    x = 0
    def side_effects():
        nonlocal x
        x += 1
        return x
    
    def in_ctx():
        cached = config_var('', side_effects)
        not_cached = config_var('', side_effects, cached=False)
        assert(not_cached() == 1)
        assert(cached() == 2)
        assert(cached() == 2)
        assert(not_cached() == 3)
        assert(not_cached() == 4)
        assert(x == 4)
        assert(not_cached(9) == 5)
        assert(cached() == 2)
        assert(not_cached() == 9)

    copy_config().run(in_ctx)



def test_ConfigOptionUnset():
    def in_ctx():
        a = config_var(default='a')
        x = config_var(default=9)
        def sub_ctx():
            y = config_var(default=3)
            y(44)
            assert(a() == 'a')
            a.hide()
            try:
                a()
                assert(False)
            except ConfigVarNotFound as e:
                v = tostr(pretty(e))
                print(v)
                assert('config_test.py' in v)
                assert('a()' in v)
                assert('<default>' in v)
                assert('in_ctx.a' in v)
            def sub_sub_ctx():
                z = config_var(default=3)
                with pytest.raises(ConfigVarNotFound):
                    a()
                assert(y() == 44)
                assert(x() == 9)
            copy_config().run(sub_sub_ctx)
        copy_config().run(sub_ctx)
    copy_config().run(in_ctx)



def test_config_dfns():
    def in_ctx():
        a = config_var(default='a')
        a('hi')
        assert('config_test.py' in a.dfns[0][0])
        assert('config_test.py' in a.dfns[1][0])
    copy_config().run(in_ctx)
 


def test_configuration_name():
    def in_ctx():
        @configure()
        def AB_c_d(): pass
        assert(AB_c_d != 'ab-C_d')
        assert(str(AB_c_d) == 'AB-c-d')
        assert(AB_c_d == 'ab-C-D')
    copy_config().run(in_ctx)



def test_config_override():
    def in_ctx():
        cfg = get_config()
        @configure(name='JIM_B-O')
        def x(): return 'x'
        assert(isinstance(x, Configuration))
        print(cfg.configurations)
        assert('jim-b-o' in cfg.configurations)
        assert(cfg['jim-B-O'].fn == x.fn)
        @x.override()
        def Happy_Days(z): return z() == 'x'
        assert('jim-b-o' not in cfg.configurations)
        assert(cfg['happy-days'].fn == Happy_Days.fn)
        assert(Happy_Days.fn())
        @Happy_Days.override(name='zZ_ZZ')
        def asdf(zz): return str(zz())
        assert('happy-days' not in cfg.configurations)
        assert(cfg['zz-zz'].fn() == 'True')
    copy_config().run(in_ctx)



def test_config_pretty():
    def in_ctx():
        cfg = get_config()
        class Bob():
            a = config_var('desc', 33)
            b = config_var('d2')

        c = tostr(pretty(cfg))
        assert(c == 'Bob.a 33    desc\nBob.b UNSET d2\n')
        c = tostr(pretty(cfg, hide=['Bob.b']))
        assert(c == 'Bob.a 33 desc\n1 hidden\n')
        c = tostr(pretty(cfg, hide=['Bo*']))
        assert(c == '\n2 hidden\n')

        @configure()
        def bob(): pass
        @configure()
        def d(): pass
        v = tostr(pretty(cfg, hide=['Bob.a']))
        assert('d2\n' in v)
        assert('1 hidden' in v)
        assert('Bob.b UNSET' in v)
        assert('bob    d' in v)
    copy_config().run(in_ctx)



def test_config_InvalidConfiguration():
    def in_ctx():
        @configure()
        def The_Quick_Fox(): pass
        @configure()
        def h(): pass

        try:
            get_config()['bob']
        except InvalidConfiguration as e:
            v = tostr(pretty(e))
            print(v)
            assert('config_test.py' in v)
        
        try:
            copy_config('james')
        except InvalidConfiguration as e:
            v = tostr(pretty(e))
            print(v)
            assert('james' in v)
            assert('h    The-Quick-Fox' in v)
            assert('config_test.py' in v)
            return
        assert(False)
    copy_config().run(in_ctx)



def test_config_include():
    with include: import doesnt.exist
    with include: from . import testutil
    with include: from . import config_import_error    
    with pytest.raises(ImportError):
        with include: from .notest import config_import_error


def test_copy_config():
    def in_ctx():
        v = config_var(default=3)
        @configure()
        def abc():
            v(33)
        def sub_ctx():
            assert(v() == 33)
            v(44)
        copy_config('abc').run(sub_ctx)
        assert(v() == 3)
    copy_config().run(in_ctx)


def test_config_set_unset():
    def in_ctx():
        v = config_var()
        with pytest.raises(ConfigVarUnset):
            v()
        assert(v(33) == UNSET)


    copy_config().run(in_ctx)