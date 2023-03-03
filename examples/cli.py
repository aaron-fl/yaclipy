#!/usr/bin/env python
import os, sys
from subprocess import call # Just in case the system python is crazy-old
from os.path import join, abspath, split, exists

VENV_DIR='.python' # This can be moved if needed

def abort(*reason):
    print('\n'+'!'*75,'\nERROR:', *reason)
    print('Look above for the specific error.','\n'+'!'*75,'\n')
    import shutil
    shutil.rmtree(VENV_DIR, ignore_errors=True)
    sys.exit(1)

os.chdir(split(abspath(__file__))[0]) # Make the cwd the same as this file
if sys.prefix == sys.base_prefix: # Not in the virtual env
    new = not exists(VENV_DIR)
    if new:
        if call(['python3', '-m','venv',VENV_DIR]):
            abort("Couldn't create python3 virtual environment at", VENV_DIR)
    os.environ['PATH'] = join(VENV_DIR,'bin') + os.pathsep + os.environ['PATH']
    if new: # Bootstrap new environment
        if call(['python', '-m', 'pip', 'install', '-e', '..']):
            abort("Couldn't install yaclipy into the virtual environment")
    os.execvp('python', ['python', './cli.py'] + sys.argv[1:])

# Now we are running in the virtual environment.  Turn control over to yaclipy
from yaclipy.boot import bootstrap
bootstrap(sys.argv[1:])

