import sys, os, inspect
from print_ext import pretty, Table, HR, Text, PrettyException, Bdr


class CmdError(PrettyException):
        
    def pretty_help(self):
        cmd = self.cmd
        h = Text()
        tbl = Table(0.0, 0.0, 1, tmpl='')
        tbl.cell('ALL', cls=Bdr, border=(' ','m:1010'))
        #tbl.cell('R-1', border=('m:1010'))
        #tbl.cell('ALL', cls=Borders, border=(' ','m:1010'))
        tbl.cell('C1', style='1')
        #tbl.cell('R-1', border='m:1110')
        for cmd in sorted(self.cmd.sub_cmds().values(), key=lambda x: x.name):
            tbl('*\t', cmd.name,'\t', pretty(cmd.doc(), fmt='short'),'\t')
        h(tbl)
        if tbl: h('\v',HR(),'\v')
        h('\v', pretty(self.cmd.doc()), '\v')
        return h


    def pretty(self, **kwargs):
        h = self.pretty_help()
        h(HR(self.__class__.__name__, style='err'), '\v\v')
        for err in self.errors:
            h(' \berr * ', err, '\v')
        return h


class CmdHelp(CmdError):
    def pretty(self, **kwargs):
        return self.pretty_help()


class CommandNotFound(CmdError): pass

class AmbiguousCommand(CmdError): pass

class CallError(CmdError):
    def __init__(self, cmd):
        self.cmd = cmd
        self.errors = [e[1] for e in cmd.run_spec.errors] if cmd.run_spec else []


class UsageError(PrettyException):
    def __init__(self, fn, *msg):
        super().__init__(msg=msg, fn=fn)

    def pretty(self):
        lines, lno = inspect.getsourcelines(self.fn)
        t = Text('\v',lines[0],'\v')
        t('\b2$', os.path.relpath(inspect.getsourcefile(self.fn)), f'\bdem :{lno}\v')
        return t('\v', *self.msg,'\v')
