import io
from print_ext import Printer, StringPrinter, PrettyException
from yaclipy import Command, sub_cmds
from yaclipy.arg_spec import ArgSpec

DEBUG = False # Show more verbose info

def _to_args(v):
    if not v: return []
    if isinstance(v, str): return v.split(' ')
    return v



def bind(fn, args):
    try:
        cmd = Command(fn)
        cmd(_to_args(args))
        if DEBUG:
            print = Printer('--------- cmd.run_spec -----------')
            print.pretty(cmd.run_spec)
            print.pretty(cmd.run_spec.argv)
        return cmd.run_spec.args, [(k,cmd.run_spec.kwargs[k]) for k in sorted(cmd.run_spec.kwargs)]
    except PrettyException as e:
        if DEBUG: print.pretty(e)
        raise e
    


def bind_unused(fn, args):
    try:
        cmd = Command(fn)
        cmd(_to_args(args))
        if DEBUG:
            print = Printer('--------- cmd.run_spec -----------')
            print.pretty(cmd.run_spec)
            print.pretty(cmd.run_spec.argv)
        return []
    except PrettyException as e:
        if DEBUG: print.pretty(e)
        return e.cmd.run_spec.argv



def bind_err(fn, args):
    try:
        cmd = Command(fn)(_to_args(args))
        if DEBUG:
            print = Printer('--------- cmd.run_spec -----------')
            print.pretty(cmd.run_spec)
            print.pretty(cmd.run_spec.argv)
        return set()
    except PrettyException as e:
        if DEBUG: print.pretty(e)
        errs = {}
        if hasattr(e, 'cmd'):
            for e in e.cmd.run_spec.errors:
                errs[e[0]] = errs.get(e[0],0) + 1
        errs = set([k + (f'x{v}' if v > 1 else '') for k,v in errs.items()])
        errs.discard('HELP')
        return errs



def exe(fn, args, **incoming):
    try:
        cmd = Command(fn)(_to_args(args))
        return cmd.run(incoming)        
    except PrettyException as e:
        if DEBUG: Printer().pretty(e)
        raise e


def tostr(*args, **kwargs):
    p = StringPrinter(**kwargs)
    p(*args, **kwargs)
    return str(p)

    