#!/usr/bin/env python
import sys, os
from yaclipy import boot


def f(*files, _cmd, upper__u=False):
    for f in files:
        print(f.upper() if upper__u else f)
    print(f'--- {_cmd} {len(files)} files ---')


if __name__=='__main__':
    print(type(boot), boot)
    boot(f, sys.argv[1:], _cmd=os.path.basename(sys.argv[0]))

