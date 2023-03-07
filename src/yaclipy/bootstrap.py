import sys, os
from os.path import join, basename, splitext, exists
from print_ext import print, Table
from print_ext.borders import Borders
from subprocess import run
from .exceptions import CommandNotFound, AmbiguousCommand, CallError, CallHelpError, UsageError
from .cmd_dfn import CmdDfn
from .docs import short_cmd_list
from .exceptions import abort


def ensure_requirements(req, venv):
    req_lock = splitext(req)[0] + '.lock'
    cur_lock = join(venv, basename(req_lock))
    if run(['diff', req_lock, cur_lock]).returncode == 0: return
    print('\bwarn Requirements changed.')
    if run(['python', '-m', 'pip', 'install', '--require-virtualenv', '--compile', '-U', 'pip']).returncode: # yaclipy
        abort('Pip upgrade failed.')
    if not exists(req_lock):
        print('\vInstalling requirements rom \b2$', req)
        if run(['python', '-m', 'pip', 'install', '--require-virtualenv', '--compile', '-r', req]).returncode:
            abort('Failed to install some requirements.')
        print('\vFreezing to \b2$', req_lock)
        if run(f'python -m pip freeze --local > "{req_lock}"', shell=True).returncode:
            abort("Pip freeze failed")
    else:
        if run(['python', '-m', 'pip', 'install', '--require-virtualenv', '--compile', '-r', req_lock]).returncode:
            abort('Failed to install some requirements.')
    import shutil
    shutil.copy(req_lock, cur_lock)



def _help(cmd):
    tbl = short_cmd_list(cmd.sub_cmds())
    print(tbl)
    if tbl: print.hr()
    print(' ')
    print.pretty(cmd.doc())
    print(' ')


def boot(main, args, **incoming):
    try:
        CmdDfn('main', main)(args).run(incoming)
    except AmbiguousCommand as e:
        _help(e.cmd)
        abort(f"Ambiguous \b1 {e.name}\b  matched multiple commands ", ', '.join(f'\b1 {x}\b ' for x in e.choices))
    except CommandNotFound as e:
        _help(e.cmd)
        abort(f"Command not found: \b1 {e.name}", '.  Valid commands are listed above.')
    except CallHelpError as e:
        _help(e.cmd)
    except UsageError as e:
        print.pretty(e)
        sys.exit(2)
    except CallError as e:
        print(' ')
        print.hr('Call Error', style='err')
        print(' ')
        for err in e.errors:
            print(' \berr * ', err, '\v')
        sys.exit(1)    
