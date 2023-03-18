import traceback, os, copy, inspect, re, functools
from print_ext import print, Table, Text, Printer, PrettyException, pretty


class InvalidOption(PrettyException):
    def __pretty__(self, **kwargs):
        p = Printer()
        p(f'\berr {self.option}\b  is not a valid option.  Valid options are:')
        return p(f'\b1$', '    '.join(sorted(self.options)))



class ConfigOptionUnset(PrettyException): 
    def __pretty__(self, **kwargs):
        p = Printer()
        p(f"You cannot access config variables until \b1 Config.configure()\b  has been called.")
        p(self.tb.line, pad=-1)
        p(os.path.relpath(self.tb.filename), ':', self.tb.lineno)
        return p
    


class SuppressImportError():
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, tb):
        if not type: return
        if len(traceback.extract_tb(tb)) > 1: return
        if type in (ImportError, ModuleNotFoundError): return True
        


class ConfigVar():
    UNSET = object()
    NAME = re.compile(r'\s*(\w+)\s*=')
    
    def __init__(self, config, /, doc='', default=None, coerce=lambda x:x, **user):
        self.dfns = []
        self.doc = doc
        self.config = config
        self.coerce = coerce
        self.default = default
        self.user = user
        self.value = ConfigVar.UNSET
        self._value = ConfigVar.UNSET
        tb = traceback.extract_stack(limit=3)[0]
        name = ConfigVar.NAME.match(tb.line)
        name = name[1] if name else 'undefined'
        self.name = name if tb.name.startswith('<') else f"{tb.name}.{name}"
        self.dfns = [(os.path.relpath(tb.filename), tb.lineno)]


    def reset(self):
        self.set(copy.deepcopy(self.default))
        self.dfns[1:] = []
        

    def set(self, value, offset=0):
        self.value = value
        self._value = ConfigVar.UNSET
        tb = traceback.extract_stack(limit=3+offset)[0]
        self.dfns.append((os.path.relpath(tb.filename), tb.lineno))


    def __call__(self, value=UNSET):
        if self._value == ConfigVar.UNSET and self.value != ConfigVar.UNSET:
            self._value = self.coerce(self.value() if inspect.isroutine(self.value) else self.value)
        if value != ConfigVar.UNSET:
            self.set(value)
        elif self._value == ConfigVar.UNSET:
            tb = traceback.extract_stack(limit=2)[0]
            raise ConfigOptionUnset(tb=tb)
        return self._value
       

    def __lt__(self, other):
        return self.name.lower() < str(other).lower()


    def __str__(self):
        return self.name



class ConfigOption():

    def override(self, name=None): 
        def _override(fn):
            self.fn = functools.partial(fn, self.fn)
            self.set_name(name or fn.__name__)
            return self
        return _override


    def __init__(self, config, /, fn, name=None):
        self.fn = fn
        self.config = config
        self.name = None
        self.set_name(name or fn.__name__)


    def set_name(self, name):
        name = name.replace('_','-')
        if self.name != None and self.name.lower() != name.lower():
            del self.config.options[self.name.lower()]
        self.config.options[name.lower()] = self
        self.name = name


    def __hash__(self):
        return hash(self.name.lower())


    def __eq__(self, other):
        return self.name.lower() == str(other).lower()


    def __repr__(self):
        return self.name


    def __lt__(self, other):
        return self.name.lower() < str(other).lower()



class Configuration():
    def __init__(self):
        self.vars = []
        self.options = {}
        self.cur_option = None
        self.include = SuppressImportError()


    def configure(self, option=''):
        ''' Reconfigure all of the variables with the given `option`.

        Parameters:
            <str>, option=<str> ['']
                The option name to configure or '' to use the defaults
        
        '''
        option = option.lower().replace('_','-')
        if self.cur_option!=None and self.cur_option == option: return
        for v in self.vars: v.reset()
        if not option: return
        if option not in self.options:
            raise InvalidOption(option=option, options=self.options)
        self.options[option].fn()
        self.cur_option = option


    def var(self, *args, **kwargs):
        var = ConfigVar(self, *args, **kwargs)
        self.vars.append(var)
        return var


    def option(self, **kwargs):
        def _f(fn):
            return ConfigOption(self, fn, **kwargs)
        return _f


    def __pretty__(self, **kwargs):
        hide_all = set(name.lower() for name in kwargs.get('hide',[]))
        hide_prefix = set(n[:-1] for n in hide_all if n[-1] == '*')
        def is_hidden(name):
            if name in hide_all: return True
            for prefix in hide_prefix:
                if name.startswith(prefix): return True
        n_hidden = 0
        p = Printer()
        tbl = Table(1,1,2, tmpl='pad')
        tbl.cell('C0', style='1', just='>')
        tbl.cell('C1', style='em')
        for var in sorted(self.vars):
            if is_hidden(var.name.lower()):
                n_hidden += 1
                continue
            tbl(var.name,'\t', pretty(var(),**kwargs),'\t',var.doc,'\t')
        p(tbl, pad=1)
        if n_hidden: p(f'\bwarn {n_hidden} hidden')
        if not self.options: return p
        return p.card('Options\t','\b1$', '    '.join(sorted(self.options)))
        


# A single global configuration
Config = Configuration()
