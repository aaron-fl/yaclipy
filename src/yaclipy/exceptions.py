import sys, os, inspect
from print_ext import pretty, Table, Printer, PrettyException, Bdr


class CmdError(PrettyException):
        
    def pretty_help(self):
        cmd = self.cmd
        p = Printer()
        tbl = Table(0.0, 0.0, 1, tmpl='')
        tbl.cell('ALL', cls=Bdr, border=(' ','m:1010'))
        #tbl.cell('R-1', border=('m:1010'))
        #tbl.cell('ALL', cls=Borders, border=(' ','m:1010'))
        tbl.cell('C1', style='1')
        #tbl.cell('R-1', border='m:1110')
        for cmd in sorted(self.cmd.sub_cmds().values(), key=lambda x: x.name):
            tbl('*\t', cmd.name,'\t', pretty(cmd.doc(), fmt='short'),'\t')
        p(tbl)
        if tbl: p.hr(pad=1)
        p.pretty(self.cmd.doc(), pad=1)
        return p


    def __pretty__(self, **kwargs):
        p = self.pretty_help()
        p.hr(self.__class__.__name__, style='err', pad=1)
        for err in self.errors:
            p(' \berr * ', err)
        return p



class CmdHelp(CmdError):
    def __pretty__(self, **kwargs):
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

    def __pretty__(self, **kwargs):
        lines, lno = inspect.getsourcelines(self.fn)
        p = Printer(lines[0])
        p('\b2$', os.path.relpath(inspect.getsourcefile(self.fn)), f'\bdem :{lno}')
        return p(*self.msg, pad=1)
