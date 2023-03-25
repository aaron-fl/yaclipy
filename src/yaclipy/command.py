import sys, inspect, asyncio
from inspect import Parameter
from print_ext import Printer, Line
from functools import partial
from .arg_spec import ArgSpec, sig_kinds, func_name
from .exceptions import AmbiguousCommand, CommandNotFound, CallError, CmdHelp
from .docs import CmdDoc


def sub_cmds(*args, **kwargs):
    ''' Use this decorator to explicitly set the sub commands for a function.

    If this decorator is not used then the ``dir()`` of the return value annotation is used.
    If there is no return value annotation then no sub commands are available

    The sub commands can be defined as positional parameters, in which case the command name will be the function.__name__.
    If the subcommand is specified as a keyword parameter then the name is used as an alias to the function.
    '''
    def _f(fn):
        fn._sub_cmds = {cmd.real_name:cmd for cmd in [Command(fn) for fn in args]}
        fn._sub_cmds.update({name:Command(fn,name) for name,fn in kwargs.items()})
        return fn
    return _f



class Command():

    def __init__(self, fn, name=None, method=False):
        if name == None: name = func_name(fn)
        self.real_name = name
        self.name = (name[:-1] if name[-1]=='_' else name).replace('_','-')
        self.fn = fn
        self.next_cmd = None
        self.run_spec = None
        self.is_method = method

    def __bool__(self):
        return bool(self.argspec)

    
    @property
    def argspec(self):
        if not hasattr(self, '_argspec'):
            self._argspec = ArgSpec(self.fn, self.is_method)
        return self._argspec
    

    def __call__(self, argv):
        argv = list(argv)
        self.run_spec = self.argspec(argv)
        if '' in self.run_spec.kwargs: raise CmdHelp(cmd=self)
        cmds = self.sub_cmds()
        if argv and not cmds:
            self.run_spec.error('UNUSED', f"Unused trailing parameters: \b1 {argv!r}")
        if self.run_spec.errors: raise CallError(self)
        if not argv: return self
        # Lookup sub-command
        cmd_name = argv[0].replace('_','-')
        cmds = {name:dfn for name, dfn in cmds.items() if dfn.name.startswith(cmd_name)}
        if not cmds:
            raise CommandNotFound(cmd=self, errors = [
                Line(f"Command not found: \b1 {cmd_name}"),
                Line("Valid commands are listed above."),
            ])
        if len(cmds) > 1:
            raise AmbiguousCommand(cmd=self, errors = [
                Line(f"Ambiguous \b1 {cmd_name}\b  matched multiple commands: ", ', '.join(f'\b1 {x}\b ' for x in cmds))
            ])
        self.next_cmd = next(iter(cmds.values()))(argv[1:])
        return self


    async def _run(self, input=None):
        spec = self.run_spec
        args = list(spec.args)
        kwargs = dict(spec.kwargs)
        sub_self = Parameter.empty
        if hasattr(input, 'items'):
            # Prune input to filter out un-acceptable values
            for k,v in input.items():
                if '**' not in spec.kinds:
                    if k not in spec.params: continue
                    if spec.params[k].kind == Parameter.POSITIONAL_ONLY: continue
                if kwargs.get(k, Parameter.empty) != Parameter.empty: continue
                kwargs[k] = v
        if '_input' in spec.params and spec.params['_input'].kind == Parameter.KEYWORD_ONLY:
            kwargs['_input'] = input
        if spec.has_self: kwargs.setdefault('self', input)
        # Fill in positional empty values
        for p in spec.params.values():         
            if not p.index: break
            if args[p.index-1] != Parameter.empty:
                if p.name in kwargs: del kwargs[p.name]
                continue
            kwargs.setdefault(p.name, p.default)
            if p.name not in kwargs: raise TypeError(f"No value supplied for {p.ordinal} positional parameter '{p.name}'")
            args[p.index-1] = kwargs.pop(p.name)
        # Make the call
        #print(f"CALL {self.name} -- {spec.kinds}")
        val = self.fn(*args, **kwargs)
        if 'generatorfunction' in spec.kinds:
            return [await self._call_next(y) for y in val]
        elif 'coroutinefunction' in spec.kinds:
            return await self._call_next(await val)
        elif 'asyncgenfunction' in spec.kinds:
            return [await self._call_next(y) async for y in val]
        else:
            return await self._call_next(val)
        

    async def _call_next(self, val):
        if self.next_cmd == None:
            if val != None: Printer().pretty(val)
            return val
        return await self.next_cmd._run(val)


    def run(self, input=None):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._run(input))
        task = loop.create_task(self._run(input), name=self.name)


    def doc(self, check=False):
        if not hasattr(self, '_doc'):
            self._doc = CmdDoc(inspect.getdoc(self.fn) or '')
        return self._doc


    def __pretty__(self, print, **kwargs):
        print(f"Command({self.name!r})")
        print.pretty(self.run_spec or self.argspec)
        for sub in self.sub_cmds().values():
            print(' * ',sub.name)


    def sub_cmds(self):
        if hasattr(self.fn, '_sub_cmds'): return self.fn._sub_cmds
        retval = self.argspec.retval
        if retval == Parameter.empty: return {}
        dfns = {name:Command(getattr(retval,name), name) for name in dir(retval) if not name.startswith('_')}
        return {name:dfn for name,dfn in dfns.items() if dfn}

