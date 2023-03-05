from print_ext import print, Table, pretty, Line, Flex
import inspect, os, copy
from inspect import Parameter
from .exceptions import abort


def name_split(name):
    if name.startswith('_'): return
    for a in name.rsplit('__'):
        yield (a[:-1] if a[-1] == '_' else a).replace('_','-')



def dashed(name):
    return ('--' if len(name) > 1 else '-') + name



def ordinal(n):
    if not n: return ''
    if n%10==1 and n!=11: return f"{n}st"
    if n%10==2 and n!=12: return f"{n}nd"
    if n%10==3 and n!=13: return f"{n}rd"
    return f"{n}th"



class ArgType():
    def __init__(self, val):
        self.repeated = False
        if isinstance(val, list):
            self.repeated = True
            val = val[0] if val else ''
        if not isinstance(val, type):
            val = type(val)
        self.coerce = str if val==type(None) or val==Parameter.empty else val
        self.is_flag = self.coerce == bool
        if self.repeated and self.is_flag: raise ValueError("We can't handle repeated bool arguments")


    def __repr__(self):
        return f'[{self.coerce.__name__}]' if self.repeated else self.coerce.__name__


    def merge(self, val, pval):
        try:
            assert(not (self.is_flag and not isinstance(val, bool)))
            assert(not (self.coerce==str and not isinstance(val, str)))
            val = self.coerce(val)
        except:
            raise ValueError(Line(f"Couldn't coerce '\b2 {val}\b ' to '\b2 {self}\b '."))
        if self.repeated:
            return ([] if pval == Parameter.empty else pval) + [val]
        elif self.is_flag:
            return val if pval == Parameter.empty else int(pval)+1
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
                self.spec.error(f"Type mismatch on \b1 {ordinal(index)}\b  parameter.  {e}")
            else:
                self.spec.error(f"Parameter '\b1 {index}\b ' type mismatch.  {e}")


    @staticmethod
    def new(spec, /, **kwargs):       
        def _set_alias(a, param):
            if a in spec.alias:
                lines, line = inspect.getsourcelines(spec.fn)
                detail = ('\b2$', os.path.relpath(inspect.getsourcefile(spec.fn)), f'\bdem :{line}\v', lines[0])
                if a in ['h','help']:
                    abort(f"You can't define a parameter with the name \b1 {a!r}\b.  That is reserved for the help flag.")
                abort('Argument ', f'\b1 {a!r}', ' was defined multiple times.\v\v', *detail)
            spec.alias[a] = param

        args = dict(index=0, aliases=[], default=Parameter.empty, kind=Parameter.KEYWORD_ONLY)
        args.update(kwargs)
        args['spec'] = spec
        args['value'] = Parameter.empty
        param = ArgParam(**args)
        spec.params[param.name] = param
        for a in param.aliases:
            _set_alias(a, param)
            if '-' in a: _set_alias(a.replace('-','_'), param)
        return param




class ArgSpec():

    def __init__(self, fn):
        self.errors = []
        self.unknown = []
        self.alias = {}
        self.params = {}
        self.fn = fn
        self.kinds = set()
        self.args = None
        self.kwargs = None
        # Are we cloning?
        if isinstance(fn, ArgSpec):
            for param in fn.params.values():
                ArgParam.new(self, **param)
            self.kinds, self.fn, self.sig = fn.kinds, fn.fn, fn.sig
            return
        # We are not a clone
        try:
            self.sig = inspect.signature(self.fn)
        except:
            self.sig = None
            return
        # Figure out a set of kinds
        for k in ['module', 'class', 'method', 'function', 'generatorfunction', 'generator', 'coroutinefunction', 'coroutine', 'awaitable', 'asyncgenfunction', 'asyncgen', 'traceback', 'frame', 'code', 'builtin', 'methodwrapper', 'routine', 'abstract', 'methoddescriptor', 'datadescriptor', 'getsetdescriptor', 'memberdescriptor']:
            try:
                if getattr(inspect, 'is'+k)(fn): self.kinds.add(k)
            except:
                pass
        # The help parameter is always available
        ArgParam.new(self, name='', type=ArgType(bool), default=False, aliases=['help', 'h'])
        for i, name in enumerate(self.sig.parameters):
            p = self.sig.parameters[name]
            if p.kind == Parameter.VAR_POSITIONAL:
                self.kinds.add('*')
                continue
            if p.kind == Parameter.VAR_KEYWORD:
                self.kinds.add('**')
                continue
            ArgParam.new(self,
                name = name,
                type = ArgType(p.default if p.annotation == Parameter.empty else p.annotation),
                aliases = list(name_split(name)) if p.kind in [Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY] else [],
                default = p.default,
                index = 0 if p.kind==Parameter.KEYWORD_ONLY else i+1,
                kind = p.kind,
            )


    def positional(self):
        return [p for p in self.params.values() if p.index]


    def __call__(self, incoming, argv):
        spec = ArgSpec(self)
        spec.arg_bind(incoming, argv)
        return spec
        

    def error(self, *args, **kwargs):
        self.errors.append(Line(*args, **kwargs))


    def arg_bind(self, incoming, argv):
        self.argv = argv
        # Set incoming values
        for k, v in incoming.items():
            if k not in self.params: continue
            self.params[k]['value'] = v
        # Parse positional args
        for param in self.positional():
            while self._parse_parg(param, argv) and param.type.repeated: pass
        # Parse keyword args
        while self._parse_kwargs(argv): pass
        # Set default values
        for name, param in self.params.items():
            if param.value != Parameter.empty: continue
            param['value'] = copy.deepcopy(param.default) # bypass the coerce
            if param.value != Parameter.empty: continue
            # This parameter remains unset!
            index = ordinal(param.index)
            if not param.aliases and index:
                self.error(f"No value supplied for the \b1 {index}\b  positional parameter (\b2 {name}\b )")
            elif not param.aliases:
                self.error(f"No value supplied for the hidden parameter '\b1 {name}\b '.")
            else:
                aka = ' (\b1 '+ ' '.join(dashed(a) for a in param.aliases) + '\b )'
                pos = f'\b1 {index}\b  positional' if index else 'keyword-only'
                self.error(f"No value supplied for the {pos} parameter{aka}.")
        # Unknown parameters
        if '**' not in self.kinds and self.unknown:
            for param in sorted(self.unknown, key=lambda x: x.name):
                self.error(f"Unknown parameter: \b1 {dashed(param.name)}\b2  {param.value!r}")
        # De-list unknowns
        for param in self.unknown:
            if not isinstance(param.value, list): continue
            if len(param.value) > 1: continue
            param['value'] = param.value[0]
            param.type.repeated = False
        # Abort if errors
        if self.errors:
            self.error('Run with \b1 -h\b  or \b1 --help\b  to see documentation for this command.')
        # Build args, kwargs
        self.args = [p.value for p in self.positional()]
        self.kwargs = {p.name:p.value for p in self.params.values() if not p.index and p.name}
        if '*' in self.kinds:
            self.args += list(argv)
            argv[:] = []


    def _parse_kwargs(self, argv):
        ''' Try to take a keyword argument from argv
        '''
        if not argv: return False
        arg, dashes = argv[0], 0
        while arg and arg[0] == '-': arg, dashes = arg[1:], dashes+1
        if not arg and dashes != 1 or dashes > 2: return self.error(f"Invalid parameter: \b1 {argv[0]}\b")
        if not arg or not dashes or arg[0] in '0123456789.': return False
        argv.pop(0)
        arg = arg.rsplit('#',1)
        arg, count = arg if len(arg) == 2 else (arg[0], False)
        if not arg:
            return self.error(f"Invalid parameter array# usage \b1 {'-'*dashes}#{count}\b .  Use it like \b1 --key#3\b  or \b1 -k#")
        ks = [arg] if dashes==2 else list(arg)
        for i, k in enumerate(ks):
            last = i == len(ks)-1
            self._parse_kwarg(k, '-'*dashes + k, last, argv, last and count)
        return True


    def _parse_kwarg(self, k, kdash, last, argv, count):
        if count != False: kdash += f'#{count}'
        if k in self.alias:
            param = self.alias[k]
        else: # Unknown parameter
            param = ArgParam.new(self, name=k, aliases=[k], type=ArgType([] if last and argv else bool))
            self.unknown.append(param)
        if count != False and not param.type.repeated:
            return self.error(f"Invalid array# parameter \b1 {kdash}\b for a non-list type \b2 {param.type}\b .")  
        try:
            i = 1 if count==False else int(count) if count else 1000000000000
            assert(i > 0)
        except:
            self.error(f"Invalid array# parameter: \b1 {kdash}\b .")
        while (i:=i-1) >= 0:
            if not last or param.type.is_flag:
                param.set(True, kdash)
            elif not argv:
                if count != False:
                    if not count: return True # This is how --key# parameters terminate
                    return self.error(f"Expected \b1 {int(count)}\b  values but only received \b1 {int(count)-i-1}\b .")
                else:
                    return self.error(f"Keyword paramter \b1 {kdash}\b  is missing a value.")
            else:
                param.set(argv.pop(0), kdash)
        return True


    def _parse_parg(spec, param, argv):
        ''' Try to take a positional argument from argv
        '''
        def _consume(v):
            param.set(v, param.index)
            return True

        if not argv: return
        if argv[0][0] == '-':
            l = len(argv[0]) 
            if l == 1: return argv.pop(0) and None # This indicates that positional arguments are done
            if argv[0][1] in '0123456789.': return _consume(argv.pop(0)) # Negative number
            if argv[0] == '-'*l: return _consume(argv.pop(0)[1:])
            return # a keyword parameter
        return _consume(argv.pop(0))



    def pretty(self):
        tbl = Table(0,0,0,0,0)
        tbl.cell("C0", just='>')
        tbl.cell("C1", style='1', just='>')
        tbl.cell("R0", style='w!')
        tbl('Aliases\t', 'Name\t', 'Pos\t', 'Type\t', 'Default\t')
        for p in self.params.values():
            if p.name=='': continue # Skip help
            tbl(' '.join(sorted(p.aliases)) if p.aliases else ' ', '\t')
            tbl(p.name, '\t')
            tbl(p.index or ' ', '\t')
            tbl(p.type, '\t')
            tbl(pretty('\br *req*' if p.default == Parameter.empty else p.default), '\t')
        try:
            fname = self.fn.__qualname__
        except:
            fname = self.fn.__func__.__qualname__
        f = Flex(f"\b1 {fname}[\b2 {' '.join(self.kinds)}\b ]\b3 {self.args or '()'}{self.kwargs or '{}'}\v", tbl)
        for e in self.errors:
            f('\v',e)
        return f
