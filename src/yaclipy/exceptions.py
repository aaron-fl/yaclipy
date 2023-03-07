import sys, os
from print_ext import print, pretty, Card, Flex

class PrettyError(Exception):
    def __init__(self, **kwargs):
        for k,v in kwargs.items(): setattr(self, k, v)

    def __str__(self):
        return print.to_str(pretty(self)).splitlines()[0]

    def pretty(self):
        return self.__class__.__name__

class CmdError(PrettyError): pass

class CommandNotFound(CmdError): pass

class CallError(CmdError):
    def __init__(self, cmd):
        self.cmd = cmd
        self.errors = [e[1] for e in cmd.run_spec.errors] if cmd.run_spec else []

class CallHelpError(CallError): pass

class AmbiguousCommand(CommandNotFound): pass

class DfnError(PrettyError): pass

class UsageError(PrettyError):
    def __init__(self, fn, *msg):
        import inspect
        lines, line = inspect.getsourcelines(fn)
        detail = ('\b2$', os.path.relpath(inspect.getsourcefile(fn)), f'\bdem :{line}\v', lines[0])
        super().__init__(detail=detail, msg=msg)

    def pretty(self):
        #print(self.cmd)
        return Flex(*self.msg,'\v\v', *self.detail)#,*self.detail)


def abort(*args, code=-1, **kwargs):
    print.card('\berr Error:\t', *args, border_style='r', **kwargs)
    sys.exit(code)
