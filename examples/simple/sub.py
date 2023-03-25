#!/usr/bin/env python
import sys
from print_ext import Printer, PrettyException
import yaclipy as CLI


def donkey(*, _say, name__n="Gordon") -> str:
    ''' Donkey Donkey
    '''
    return f'{name__n} says, \b1 "{_say}"'


def dog(*, _say, times__t=3) -> str:
    ''' Dogs barking
    '''
    return _say + ' bark!'*times__t


@CLI.sub_cmds(dog, donkey)
def main(say, /, *, verbose__v=False):
    ''' Say stuff

    $ ./sub.py "Hello world" -vv donkey

    '''
    print = Printer.replace(filter=lambda t: t.get('v',0) <= int(verbose__v))
    print('\b2$', ' Ready?'*int(verbose__v), tag='v:1')
    yield dict(_say=say)
    print("\b_ Bye")


if __name__ == '__main__':
    try:
        CLI.Command(main)(sys.argv[1:]).run()
    except PrettyException as e:
        Printer().pretty(e)
