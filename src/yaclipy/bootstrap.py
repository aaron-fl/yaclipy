import sys, os, shutil
from print_ext import Printer, PrettyException
from subprocess import run


class EnvSetup(PrettyException): pass


def ensure_requirements(req, venv):
    print = Printer()
    req_lock = os.path.splitext(req)[0] + '.lock'
    cur_lock = os.path.join(venv, os.path.basename(req_lock))
    if run(['diff', req_lock, cur_lock]).returncode == 0: return
    print('\bwarn Requirements changed.')
    if run(['python', '-m', 'pip', 'install', '--require-virtualenv', '--compile', '-U', 'pip']).returncode: # yaclipy
        raise EnvSetup(msg='Pip upgrade failed.')
    if not os.path.exists(req_lock):
        print('\vInstalling requirements rom \b2$', req)
        if run(['python', '-m', 'pip', 'install', '--require-virtualenv', '--compile', '-r', req]).returncode:
            raise EnvSetup(msg='Failed to install some requirements.')
        print('\vFreezing to \b2$', req_lock)
        if run(f'python -m pip freeze --local > "{req_lock}"', shell=True).returncode:
            raise EnvSetup(msg="Pip freeze failed")
    else:
        if run(['python', '-m', 'pip', 'install', '--require-virtualenv', '--compile', '-r', req_lock]).returncode:
            raise EnvSetup(msg='Failed to install some requirements.')
    shutil.copy(req_lock, cur_lock)
