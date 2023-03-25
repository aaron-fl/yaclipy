import traceback, os, inspect, re, functools, contextvars
from print_ext import Table, PrettyException, pretty, Line

class ConfigVarUnset(PrettyException): 
    def __pretty__(self, print, **kwargs):
        print(f"The configuration variable \berr {self.var.name}\b  is not set.")
        print(self.tb.line)
        print(os.path.relpath(self.tb.filename), ':', self.tb.lineno)

    def __repr__(self):
        return '*UNSET*'

    def __bool__(self):
        return False

UNSET = ConfigVarUnset()



class InvalidConfiguration(PrettyException):
    def __pretty__(self, print, **kwargs):
        print(self.tb.line)
        print(os.path.relpath(self.tb.filename), ':', self.tb.lineno)
        print('\n', f'\berr {self.name}\b  is not a valid configuration.')
        print.card('Configurations\t','\b1$', '    '.join(map(str, sorted(self.cfg.configurations))))



class ConfigVarNotFound(PrettyException): 
    def __pretty__(self, print, **kwargs):
        print(f"The configuration variable \berr {self.var.name}\b  cannot be accessed in the \berr {self.cfg}\b  configuration.")
        print(self.tb.line)
        print(os.path.relpath(self.tb.filename), ':', self.tb.lineno)
    


class SuppressImportError():
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, tb):
        if not type: return
        if len(traceback.extract_tb(tb)) > 1: return
        if type in (ImportError, ModuleNotFoundError): return True
        
include = SuppressImportError()


class ConfigVar():
    NAME = re.compile(r'\s*(\w+)\s*=')
    
    def __init__(self, **kwargs):
        kwargs.setdefault('cached', True)
        for k,v in kwargs.items(): setattr(self, k, v)
        tb = traceback.extract_stack(limit=4)[0]
        if not hasattr(self, 'name'):
            name = ConfigVar.NAME.match(tb.line)
            name = name[1] if name else 'unk'
            self.name = name if tb.name.startswith('<') else f"{tb.name}.{name}"
        self.dfns = [(os.path.relpath(tb.filename), tb.lineno)]


    def __call__(self, value=UNSET):
        cfg = get_config()
        try:
            val = cfg[self]
        except ConfigVarUnset as e:
            if value == UNSET: raise e
            val = UNSET
        if value != UNSET: cfg[self] = value
        return val

    
    def hide(self):
        cfg = get_config()
        cfg.vars.discard(self)


    def __lt__(self, other):
        return self.name.lower() < str(other).lower()


    def __str__(self):
        return self.name



class Configuration():

    def override(self, name=None): 
        def _override(fn):
            self.fn = functools.partial(fn, self.fn)
            self.set_name(name or fn.__name__)
            return self
        return _override


    def __init__(self, fn, name=''):
        self.fn = fn
        self.name = ''
        self.set_name(name or fn.__name__)


    def set_name(self, name):
        self.hide()
        self.name = name.replace('_','-')
        get_config().set_configuration(self)


    def hide(self):
        get_config().set_configuration(self, unset=True)


    def __hash__(self):
        return hash(self.name.lower())


    def __eq__(self, other):
        return self.name.lower() == str(other).lower()


    def __str__(self):
        return self.name


    def __repr__(self):
        return f"Configuration<{self.name}>"


    def __lt__(self, other):
        return self.name.lower() < str(other).lower()



class Config():

    def __init__(self, name='', *, parent=None):
        self.parent = parent
        self.name = name
        self.vars = set(parent.vars) if parent else set()
        self.configurations = set(parent.configurations) if parent else set()
        self._values = {}
        self._cache = {}


    def __repr__(self):
        vars = ' '.join(v.name for v in self.vars)
        cfgs = ' '.join(c.name for c in self.configurations)
        return f"Config<{hex(id(self))}> Name:{self} Vars:[{vars}]  Configurations:[{cfgs}]  -->  {hex(id(self.parent))}"


    def create_var(self, **kwargs):
        var = ConfigVar(**kwargs)
        self.vars.add(var)
        return var


    def __getitem__(self, var):
        if isinstance(var, str): return self.get_configuration(var)
        if var not in self.vars:
            tb = traceback.extract_stack(limit=3)[0]
            raise ConfigVarNotFound(tb=tb, var=var, cfg=self)
         # First check our cache.  Then get our value (or our parent's).  Maybe cache the result in our object.
        try:
            return self._cache[var]
        except KeyError:
            try: # Do we have the value?
                val = self._values[var]
                val = var.coerce(val() if inspect.isroutine(val) else val)
            except KeyError:
                try: # Does our parent have the value?
                    val = self.parent[var]
                except (TypeError, ConfigVarNotFound):
                    # Use the default value
                    val = var.default
                    val = var.coerce(val() if inspect.isroutine(val) else val)
        if val == UNSET:
            tb = traceback.extract_stack(limit=3)[0]
            raise ConfigVarUnset(var=var, tb=tb)
        # Cache it for next time?
        if var.cached: self._cache[var] = val
        return val


    def __setitem__(self, var, val):
        tb = traceback.extract_stack(limit=3)[0]
        if var not in self.vars:
            raise ConfigVarNotFound(tb=tb, var=var, cfg=self)
        self._values[var] = val
        try: del self._cache[var]
        except: pass
        var.dfns.append((os.path.relpath(tb.filename), tb.lineno))


    def get_configuration(self, name, stack_offset=0):
        name = name.replace('_','-')
        for cfg in self.configurations:
            if cfg == name: return cfg
        else:
            tb = traceback.extract_stack(limit=3+stack_offset)[0]
            raise InvalidConfiguration(name=name, cfg=self, tb=tb)


    def set_configuration(self, cfg, unset=False):
        if unset:
            self.configurations.discard(cfg)
        else:
            self.configurations.add(cfg)


    def __str__(self):
        return self.name or '<default>'


    def __pretty__(self, print, **kwargs):
        hide_all = set(name.lower() for name in kwargs.get('hide',[]))
        hide_prefix = set(n[:-1] for n in hide_all if n[-1] == '*')
        def is_hidden(name):
            if name in hide_all: return True
            for prefix in hide_prefix:
                if name.startswith(prefix): return True
        n_hidden = 0
        tbl = Table(1,1,2, tmpl='pad')
        tbl.cell('C0', style='1', just='>')
        tbl.cell('C1', style='em')
        for var in sorted(self.vars):
            if is_hidden(var.name.lower()):
                n_hidden += 1
                continue
            try:
                val = var()
            except ConfigVarUnset:
                val = Line(style='err').insert(0, 'UNSET')
            tbl(var.name,'\t', pretty(val, **kwargs),'\t',var.doc,'\t')
        print(tbl)
        if n_hidden: print(f'\bwarn {n_hidden} hidden')
        if self.configurations:
            print.card('Configurations\t','\b1$', '    '.join(map(str, sorted(self.configurations))))


# The configuration is accessed through a ContextVar
config_contextvar = contextvars.ContextVar('Config', default=Config())

def get_config():
    return config_contextvar.get()


def copy_config(configuration='', *, context=None):
    ''' Create a new Config() that is in the given `configuration`.
    The new Config() is set in a copy of the given `context` and the new context is returned.
    '''
    ctx = context.copy() if context else contextvars.copy_context()
    cfg = Config(configuration, parent=get_config())
    def in_ctx():
        config_contextvar.set(cfg)
        if configuration:
            cfg.get_configuration(configuration,stack_offset=1).fn()
    ctx.run(in_ctx)
    return ctx


def config_var(doc='', default=UNSET, coerce=lambda x:x, **kwargs):
    ''' Create a new ConfigVar in the current context.
    '''
    return get_config().create_var(default=default, doc=doc, coerce=coerce, **kwargs)
    


def configure(**kwargs):
    ''' A decorator for a function that sets ConfigVars to put the program in a certain configuration.
    '''
    def _f(fn):
        return Configuration(fn, **kwargs)
    return _f
