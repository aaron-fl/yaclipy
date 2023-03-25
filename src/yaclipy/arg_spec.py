import inspect, os, copy, json, re
from inspect import Parameter
from print_ext import Table, pretty, Line
from print_ext.widget import INFINITY
from .exceptions import UsageError


def sig_kinds(fn):
    kinds = set()
    for k in ['module', 'function', 'generatorfunction', 'generator', 'coroutinefunction', 'asyncgenfunction', 'asyncgen', 'coroutine', 'awaitable', 'class' , 'method',  'traceback', 'frame', 'code', 'builtin', 'methodwrapper', 'routine', 'abstract', 'methoddescriptor', 'datadescriptor', 'getsetdescriptor', 'memberdescriptor']:
        try:
            if getattr(inspect, 'is'+k)(fn): kinds.add(k)
        except:
            pass
    return kinds


def func_name(fn, attr='__name__'):
    try:
        return getattr(fn.__func__, attr)
    except AttributeError:
        try:
            return getattr(fn, attr)
        except AttributeError:
            return getattr(fn.__class__, attr)


def name_split(name):
    if name.startswith('_'): return
    for a in name.rsplit('__'):
        yield (a[:-1] if a[-1] == '_' else a).replace('_','-')



def dashed(name):
    return ('--' if len(name) > 1 else '-') + name


class ArgType():
    def __init__(self, val):
        self.repeated = False
        if isinstance(val, list):
            self.repeated = True
            val = val[0] if val else ''
        if not callable(val):
            val = type(val)
        self.coerce = str if val==type(None) or val==Parameter.empty else val
        self.is_flag = self.coerce == bool
        if self.coerce == dict: self.coerce = json.loads
        if self.repeated and self.is_flag: raise ValueError("We can't handle repeated bool arguments")


    def __repr__(self):
        return f'[{self.coerce.__name__}]' if self.repeated else self.coerce.__name__


    def merge(self, val, pval):
        if val == None: # append nothing to the list (but make sure it exists)
            return [] if pval == Parameter.empty else pval
        try:
            assert(not (self.is_flag and not isinstance(val, bool))) # Only True can be set on bools
            assert(not (self.coerce==str and not isinstance(val, str))) # Don't coerce None or True to a string
            val = self.coerce(val)
        except Exception as e:
            raise ValueError(Line(f"Couldn't coerce '\b2 {val}\b ' to '\b2 {self}\b '."))
        if self.repeated:
            return ([] if pval == Parameter.empty else pval) + [val]
        elif self.is_flag:
            return val if pval == Parameter.empty else int(pval)+1
        elif self.coerce == json.loads:
            if isinstance(pval, dict) and isinstance(val, dict):
                pval.update(val)
                return pval
            elif isinstance(pval, list) and isinstance(val, list):
                return pval + val
            return val
        else:
            return val
            


class ArgParam(dict):
    def __repr__(self):
        return f"{self.name}:{','.join(self.aliases)}@{self.index}<{self.type}>{self.value}"


    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    
    def set(self, val, index):
        try:
            self['value'] = self.type.merge(val, self.value)
        except ValueError as e:
            if isinstance(index, int):
                self.spec.error('TYPE_MISMATCH', f"Type mismatch on \b1 {ordinal(index)}\b  parameter.  {e}")
            else:
                self.spec.error('TYPE_MISMATCH', f"Parameter '\b1 {index}\b ' type mismatch.  {e}")


    @property
    def ordinal(self):
        n = self.index
        if not n: return ''
        if n%10==1 and n!=11: return f"{n}st"
        if n%10==2 and n!=12: return f"{n}nd"
        if n%10==3 and n!=13: return f"{n}rd"
        return f"{n}th"



    @staticmethod
    def new(spec, /, **kwargs):
        args = dict(index=0, aliases=[], type=None, default=Parameter.empty, kind=Parameter.KEYWORD_ONLY)
        args.update(kwargs)
        args['spec'] = spec
        args['value'] = Parameter.empty
        param = ArgParam(**args)
        spec.params[param.name] = param
        if param.aliases:
            aliases = set(param.aliases)
            aliases.add(param.name)
            aliases.update([a.replace('-','_') for a in aliases])
            for a in aliases: spec.set_alias(a, param)
        return param




class ArgSpec():
    kw_re = re.compile(r'--?[a-zA-Z][-\w]*(#([1-9][0-9]*)?)?$')

    def __init__(self, fn, is_method=False):
        self.errors = []
        self.unknown = []
        self.alias = {}
        self.params = {}
        self.fn = fn
        self.kinds = set()
        self.args = None
        self.kwargs = None
        self.has_self = False
        # Are we cloning?
        if isinstance(fn, ArgSpec):
            for param in fn.params.values():
                ArgParam.new(self, **param)
            self.has_self, self.kinds, self.fn, self.sig = fn.has_self, fn.kinds, fn.fn, fn.sig
            return
        # We are not a clone
        try:
            self.sig = inspect.signature(self.fn)
        except:
            self.sig = None
            return
        # Figure out a set of kinds
        self.kinds.update(sig_kinds(fn))
        for i, name in enumerate(self.sig.parameters):
            p = self.sig.parameters[name]
            if p.kind == Parameter.VAR_POSITIONAL:
                self.kinds.add('*')
                continue
            if p.kind == Parameter.VAR_KEYWORD:
                self.kinds.add('**')
                continue

            if name.startswith('_') and p.kind == Parameter.POSITIONAL_ONLY:
                raise UsageError(fn, f"Private parameter '{name}' must be a keyword parameter.")
            ArgParam.new(self,
                name = name,
                type = ArgType(p.default if p.annotation == Parameter.empty else p.annotation),
                aliases = list(name_split(name)) if p.kind in [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY] else [],
                default = p.default,
                index = 0 if p.kind==Parameter.KEYWORD_ONLY else i+1,
                kind = p.kind,
            )
        # The help parameter is always available
        ArgParam.new(self, name='', type=ArgType(bool), default=False, aliases=['help', 'h'])
        self.has_self = 'self' in self.params and self.params['self'].index == 1


    def __bool__(self):
        return self.sig != None


    @property
    def retval(self):
        return Parameter.empty if self.sig==None else self.sig.return_annotation


    def __call__(self, argv):
        spec = ArgSpec(self)
        spec.arg_bind(argv)
        return spec
        

    def error(self, code, *args, **kwargs):
        self.errors.append((code, Line(*args, **kwargs)))


    def set_alias(self, a, param):
        if a == 'self' and (param.index != 1 or param.name != 'self'):
            raise UsageError(self.fn, f"Invalid parameter \b1 {param.name}\b .\v\b1 self\b  is reserved.")
        if a in self.alias:
            prev = self.alias[a]
            if a in ['h','help']:
                raise UsageError(self.fn, f"Invalid parameter \b1 {prev.name}\b .  The alias \b1 {a}\b  is reserved for the help flag.")
            raise UsageError(self.fn, f"Argument \b1 {a}\b  was defined multiple times. \b2 {prev.name} {param.name} ")  
        self.alias[a] = param


    def arg_bind(self, argv):
        self.argv = argv
        # Parse positional args
        for param in self.params.values():
            if not param.index: break
            while self._parse_parg(param, argv) and param.type.repeated: pass
        # Parse keyword args
        while self._parse_kwargs(argv): pass
        # Set default values
        for name, param in self.params.items():
            if param.value != Parameter.empty: continue
            #param['value'] = copy.deepcopy(param.default) # bypass the coerce
            if param.default != Parameter.empty: continue
            # This parameter remains unset!
            if param.name.startswith('_') or (self.has_self and param.index==1):
                continue # self or hidden parameters will be supplied at runtime
            elif not param.aliases and param.ordinal:
                self.error('NO_VALUE', f"No value supplied for the \b1 {param.ordinal}\b  positional parameter (\b2 {name}\b )")
            else:
                aka = ' (\b1 '+ ' '.join(dashed(a) for a in param.aliases) + '\b )'
                pos = f'\b1 {param.ordinal}\b  positional' if param.ordinal else 'keyword-only'
                self.error('NO_VALUE', f"No value supplied for the {pos} parameter{aka}.")
        # De-list unknowns
        for param in self.unknown:
            if not isinstance(param.value, list): continue
            if len(param.value) > 1: continue
            param['value'] = param.value[0]
            param.type.repeated = False
        # Unknown parameters
        if '**' not in self.kinds and self.unknown:
            for param in sorted(self.unknown, key=lambda x: x.name):
                self.error('UNK_PARAM', f"Unknown parameter: \b1 {dashed(param.name)}\b2  {param.value!r}")
        # Build args, kwargs
        self.args, self.kwargs = [], {}
        for p in self.params.values():
            if p.index:
                self.args.append(p.value)
            elif p.value != Parameter.empty:
                self.kwargs[p.name] = p.value
        if '*' in self.kinds:
            self.args += list(argv)
            argv[:] = []


    def _parse_kwargs(self, argv):
        ''' Try to take a keyword argument from argv
        '''
        if not argv: return
        if argv[0][0] != '-': return # A potential command name
        if len(argv[0]) == 1: return argv.pop(0) and False # End of kwargs
        if not ArgSpec.kw_re.match(argv[0]):
            return self.error('BAD_KW', f"Invalid keyword argument \b1 {argv[0]}\b.")
        arg = argv.pop(0)
        dashes = 1 + int(arg[1] == '-')
        arg = arg.rsplit('#',1)
        arg, count = arg[0][dashes:], (arg[1] if len(arg) == 2 else False)
        ks = [arg] if dashes==2 else list(arg)
        for i, k in enumerate(ks):
            if k == 'self':
                self.error('SELF', f"\b1 self\b  can not be set from the command line.  It must be set from the parent's return value.")
                continue
            last = i == len(ks)-1
            if not self._parse_kwarg(k, '-'*dashes + k, last, argv, last and count): return # abort
        return True


    def _parse_kwarg(self, k, kdash, last, argv, count):
        if count != False: kdash += f'#{count}'
        if k in self.alias:
            param = self.alias[k]
        else: # Unknown parameter
            param = ArgParam.new(self, name=k, aliases=[k], type=None if last else ArgType(bool))
            self.unknown.append(param)
        # Are we trying to use -k#3 with a non-repeated value?
        if count != False and param.type and not param.type.repeated:
            return self.error('NOT_LIST', f"Invalid array# parameter \b1 {kdash}\b for a non-list type \b2 {param.type}\b .")
        # Turn count into a valid number of items to get
        try:
            need = 1 if count==False else int(count) if count else INFINITY
            assert(need > 0)
        except:
            self.error('BAD_LIST', f"Invalid array# parameter: \b1 {kdash}\b .")
        # If we know that we are a flag then don't bother to grab one
        if not last or param.type and param.type.is_flag:
            param.set(True, kdash)
            return True
        # We probably need a value so grab one
        val = self._grab_one(argv)
        if param.type == None:
            # We know the unknown parameter type now
            if val == None:
                param.type = ArgType(bool)
                param.set(True, kdash)
                return True
            param.type = ArgType([])
        # Do we only need a single value?
        if count == False:
            if val == None: return self.error('KW_VAL_MISSING', f"Keyword parameter \b1 {kdash}\b  is missing a value.")
            param.set(val, kdash)
            return True
        # We want `need` values
        got = 0
        while True: # Grab multiple values for our array
            if val == None:
                if need == INFINITY: # --key# terminated
                    param.set(None, kdash)
                    break 
                # Didn't get enough values
                return self.error('LIST_TOO_FEW', f"Expected \b1 {need}\b  values but only received \b1 {got}\b .")
            param.set(val, kdash)
            got += 1
            if got == need: break
            val = self._grab_one(argv)
        return True


    def _parse_parg(self, param, argv):
        ''' Try to take a positional argument from argv
        '''
        if param.name.startswith('_'): return
        v = self._grab_one(argv)
        if v == None: return
        param.set(v, param.index)
        return True


    def _grab_one(self, argv):
        if not argv: return
        arg = argv.pop(0)
        if arg[0] == '-':
            l = len(arg)
            if l == 1: return # This indicates that arguments are done
            if arg[1] not in '0123456789.': # Not negative number
                argv.insert(0, arg[1:] if arg == '-'*l else arg)
                return # A keyword parameter
            # Negative number
        if arg.startswith('\\'): arg = arg[1:]
        return arg


    def __pretty__(self, print, *, _depth, depth, **kwargs):
        print(f"\b1 {func_name(self.fn,'__qualname__')}[\b2 {' '.join(self.kinds)}\b ]\b3 {self.args or '()'}{self.kwargs or '{}'}")
        tbl = Table(0,0,0,0,0)
        tbl.cell("C0", just='>')
        tbl.cell("C1", style='1', just='>')
        tbl.cell("R0", style='w!')
        tbl('Aliases\tName\tPos\tType\tDefault\t')
        for v in self.params.values():
            if v.name=='': continue # Skip help
            tbl(' '.join(sorted(v.aliases)) if v.aliases else ' ', '\t')
            tbl(v.name, '\t')
            tbl(v.index or ' ', '\t')
            tbl(v.type, '\t')
            tbl(pretty('\br *req*' if v.default == Parameter.empty else v.default, _depth=_depth+1, depth=depth-1, **kwargs), '\t')
        print(tbl)
        for e in self.errors:
            print(e[1])
