import sys, inspect
from print_ext import print, Flex, pretty
from functools import partial
from .arg_spec import ArgSpec
from .exceptions import AmbiguousCommand, CommandNotFound, CallError, CallHelpError
from .docs import CmdDoc


class SubCmds():
    ''' This is a decorator that marks a function as accepting an explicit set of sub-commands.

    The sub commands can be defiend as positionional parameters, in which case the command name will be the function.__name__.
    If the subcommand is specifed as a named parameter then the name is used as an alias to the function.
    '''
    def __init__(self, *args, **kwargs):
        #self._incoming_args_dfn = kwargs.pop('with_args') if 'with_args' in kwargs else []
        for fn in args: setattr(self, fn.__name__, fn)
        for name, fn in kwargs.items(): setattr(self, name, fn)
            
    def __call__(self, fn):
        fn._subcmds = self
        return fn




class CmdDfn():
    null = object()
    

    @staticmethod
    def scrape(obj):
        ''' Search dir(obj) for potential commands.
        '''
        dfns = {name:CmdDfn(name, getattr(obj,name)) for name in dir(obj) if not name.startswith('_')}
        return {name:dfn for name,dfn in dfns.items() if dfn.argspec.sig != None}


    def __init__(self, name, fn):
        self.name = (name[:-1] if name[-1]=='_' else name).replace('_','-')
        self.fn = fn
        #self.incoming_args = obj._incoming_args if hasattr(self.obj, '_incoming_args') else {}
        

    @property
    def argspec(self):
        if not hasattr(self, '_argspec'):
            self._argspec = ArgSpec(self.fn)
        return self._argspec
    

    def __call__(self, incoming, argv):
        argv = list(argv)
        spec = self.argspec(incoming, argv)
        # Check for errors
        if spec.params[''].value: raise CallHelpError(cmd=self, spec=spec)
        if spec.errors: raise CallError(cmd=self, spec=spec)
        # Call based on kind
        if 'generatorfunction' in spec.kinds:
            ret = None
            for val in self.fn(*spec.args, **spec.kwargs):
                ret = self._sub_call(val, argv)
            return ret
        else:
            return self._sub_call(self.fn(*spec.args, **spec.kwargs), argv)
        

    def _sub_call(self, rval, argv):
        if not argv:
            if rval != None: print.pretty(rval)
            return rval
        # Lookup the next CmdDfn
        cmds = CmdDfn.scrape(self.fn._subcmds if hasattr(self.fn, '_subcmds') else rval)
        cmd_name = argv[0].replace('-','_')
        #print(f"lookup_and_execute {incoming} {fn} {obj} {args}")
        cmds = {name:dfn for name, dfn in cmds.items() if dfn.name.startswith(cmd_name)}
        if not cmds: raise CommandNotFound(cmd=self, name=cmd_name)
        if len(cmds) > 1: raise AmbiguousCommand(cmd=self, name=cmd_name, choices=cmds)
        dfn = next(iter(cmds.values()))
        return dfn(rval if isinstance(rval, dict) else {}, argv[1:])


    def doc(self, check=False):
        if not hasattr(self, '_doc'):
            self._doc = CmdDoc(inspect.getdoc(self.fn) or '')
        return self._doc
        

    def check_doc(self):
        doc = self.doc()
        self.doc_args = {'':0}
        #doc.parse(0, 0, )
        for k in self.args:
            for k in k.split('__'):
                if k.replace('_','-') not in self.doc_args: self.error('Undocumented paramter: ', k)
        for k in self.doc_args:
            if not k:
                lpos = 0 if self.name == 'cli' else len(self.pos)
                if self.doc_args[k] != lpos and self.doc_args[k] != lpos + int(self.var):
                    self.error("Documented positional arguments doesn't match number of positional args: %s!=%s"%(self.doc_args[k], lpos))
            elif k.replace('-','_') not in self.alias:
                self.error('Documentation for non-existant parameter: ', k)
        return doc


    def pretty(self):
        return Flex(f"CmdDfn({self.name!r})\v", pretty(self.argspec))


    def execute(self, *argv, **incoming):
        
        #print.card(f"EXECUTE {incoming!r} {args} {dfn}\t", pretty(dfn.argspec))
        return dfn(incoming if isinstance(incoming,dict) else {}, args[1:])

