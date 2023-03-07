from print_ext import print
from yaclipy.cmd_dfn import CmdDfn, sub_cmds
from yaclipy.exceptions import CallError
from yaclipy.arg_spec import ArgSpec

DEBUG = True # Show more verbose info

def _to_args(v):
    if not v: return []
    if isinstance(v, str): return v.split(' ')
    return v

def bind(fn, args):
    try:
        cmd = CmdDfn('main', fn)
        cmd(_to_args(args))
        if DEBUG:
            print('--------- cmd.run_spec -----------')
            print.pretty(cmd.run_spec)
            print.pretty(cmd.run_spec.argv)
        return cmd.run_spec.args, [(k,cmd.run_spec.kwargs[k]) for k in sorted(cmd.run_spec.kwargs)]
    except Exception as e:
        print(f'\v---------- {e} --------------\v')
        for k,v in e.__dict__.items():
            print(f'\v\berr {k}\v')
            print.pretty(v)
        raise e
    


def bind_unused(fn, args):
    try:
        cmd = CmdDfn('main', fn)
        cmd(_to_args(args))
        if DEBUG:
            print('--------- cmd.run_spec -----------')
            print.pretty(cmd.run_spec)
            print.pretty(cmd.run_spec.argv)
        return []
    except Exception as e:
        if DEBUG:
            print(f'\v---------- {e} --------------\v')
            for k,v in e.__dict__.items():
                print(f'\v\berr {k}\v')
                print.pretty(v)
        return cmd.run_spec.argv



def bind_err(fn, args):
    try:
        cmd = CmdDfn('main', fn)(_to_args(args))
        if DEBUG:
            print('--------- cmd.run_spec -----------')
            print.pretty(cmd.run_spec)
            print.pretty(cmd.run_spec.argv)
        return set()
    except Exception as e:
        if DEBUG:
            print(f'\v---------- {e} --------------\v')
            for k,v in e.__dict__.items():
                print(f'\v\berr {k}\v')
                print.pretty(v)
        errs = {}
        if hasattr(e, 'cmd'):
            for e in e.cmd.run_spec.errors:
                errs[e[0]] = errs.get(e[0],0) + 1
        errs = set([k + (f'x{v}' if v > 1 else '') for k,v in errs.items()])
        errs.discard('HELP')
        return errs



def exe(fn, args, **incoming):
    try:
        cmd = CmdDfn('main', fn)(_to_args(args))
        return cmd.run(incoming)        
    except Exception as e:
        if DEBUG:
            print(f'\v---------- {e} --------------\v')
            for k,v in e.__dict__.items():
                print(f'\v\berr {k}\v')
                print.pretty(v)
        raise e
