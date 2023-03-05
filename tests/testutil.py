from print_ext import print
from yaclipy.cmd_dfn import CmdDfn, SubCmds
from yaclipy.exceptions import CallError


def exe(fn, args, **incoming):
    try:
        return CmdDfn('main', fn)(incoming, args.split(' ') if args else [])
    except CallError as e:
        print('\vspec\v')
        print.pretty(e.spec)
        raise e

