import pytest, traceback
from yaclipy.config import Configuration, ConfigOptionUnset, InvalidOption
from print_ext import pretty
from .testutil import printer, tostr


@pytest.fixture()
def Config():
   return Configuration()



def test_config_var_user(Config):
    v1 = Config.var(mydata=3)
    assert(Config.vars[0].user['mydata'] == 3)



def test_config_var(Config):
    v1 = Config.var()
    v2 = Config.var()
    assert(len(Config.vars) == 2)



def test_config_var_name(Config):
    ab = Config.var()
    a,b = Config.var(), Config.var()
    class Bob():
        jim = Config.var()
    assert(ab.name == 'test_config_var_name.ab')
    assert(a.name == 'test_config_var_name.undefined')
    assert(b.name == 'test_config_var_name.undefined')
    assert(Bob.jim.name == 'Bob.jim')



def test_config_var_coerce(Config):
    v = Config.var('asdf', '123', lambda x: int(x))
    v.reset()
    assert(v() == 123)
    v('asdf')
    with pytest.raises(ValueError):
        v()



def test_config_var_cached(Config):
    x = 1
    def side_effects():
        nonlocal x
        x += 1
        return x
    v = Config.var(default=side_effects)
    v.reset()
    assert(v() == 2)
    assert(v() == 2)
    assert(x == 2)
    v(9)
    assert(v() == 9)
    assert(x == 2)



def test_ConfigOptionUnset(Config):
    v = Config.var(default=3)
    def useit():
        v()
    try:
        useit()
    except ConfigOptionUnset as e:
        v = tostr(pretty(e))
        assert('config_test.py' in v)
        assert('v()' in v)
        return
    assert(False)
    


def test_config_override(Config):
    @Config.option(name='JIM_BO')
    def x(): return 'x'
    assert(Config.options['jim-bo'].fn == x.fn)
    @x.override()
    def Happy_Days(z): return z() == 'x'
    assert('jim-bo' not in Config.options)
    print(Config.options)
    assert(Config.options['happy-days'].fn == Happy_Days.fn)
    assert(Happy_Days.fn())
    @Happy_Days.override(name='zZ_ZZ')
    def asdf(zz): return str(zz())
    assert('happy-days' not in Config.options)
    assert(Config.options['zz-zz'].fn() == 'True')



def test_config_pretty(Config):
    class Bob():
        a = Config.var('desc', 33)
        b = Config.var('d2')
    Config.configure()
    c = tostr(pretty(Config))
    assert(c == '\nBob.a 33   desc\nBob.b None d2\n\n')
    c = tostr(pretty(Config, hide=['Bob.b']))
    assert(c == '\nBob.a 33 desc\n\n1 hidden\n')
    c = tostr(pretty(Config, hide=['Bo*']))
    assert(c == '\n\n2 hidden\n')

    @Config.option()
    def bob(): pass
    @Config.option()
    def d(): pass
    v = tostr(pretty(Config, hide=['Bob.a']))
    assert('d2\n' in v)
    assert('1 hidden' in v)
    assert('Bob.b None' in v)
    assert('bob    d' in v)



def test_config_InvalidOption(Config):
    @Config.option()
    def The_Quick_Fox(): pass
    @Config.option()
    def h(): pass
    
    try:
        Config.configure('jim_Bob')
    except InvalidOption as e:
        v = tostr(pretty(e))
        assert('jim-bob' in v)
        assert('h    the-quick-fox' in v)
        return
    assert(False)



def test_config_include(Config):
    with Config.include: import doesnt.exist
    with Config.include: from . import testutil
    with Config.include: from . import config_import_error
    with pytest.raises(ImportError):
        with Config.include: from .notest import config_import_error
