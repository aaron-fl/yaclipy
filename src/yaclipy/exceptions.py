import sys
from print_ext import print

class CmdError(Exception):
    def __init__(self, **kwargs):
        for k,v in kwargs.items(): setattr(self, k, v)

class CommandNotFound(CmdError): pass

class CallError(CmdError): pass

class CallHelpError(CallError): pass

class AmbiguousCommand(CommandNotFound): pass

class DfnError(Exception): pass

class ClipyExit(Exception): pass


def abort(*args, code=-1, **kwargs):
    print.card('\berr Error:\t', *args, border_style='r', **kwargs)
    sys.exit(code)
