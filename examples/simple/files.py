#!/usr/bin/env python
import sys, os
from print_ext import PrettyException, Printer, Table
import yaclipy as CLI


def main(*files, _input, upper__u=False):
    ''' List files

    Parameters:
        --upper, -u
            Make the names all uppercase
    '''
    tbl = Table(0,1,tmpl='kv')
    for f in files:
        name,ext = os.path.splitext(f)
        tbl(name.upper() if upper__u else name, '\t', ext, '\t')
    Printer(tbl, f'\v--- \b2 {_input}\b  {len(files)} files ---')


if __name__ == '__main__':
    try:
        CLI.Command(main)(sys.argv[1:]).run(os.path.basename(sys.argv[0]))
    except PrettyException as e:
        Printer().pretty(e)
