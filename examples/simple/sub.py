#!/usr/bin/env python
import sys
from yaclipy import boot, sub_cmds


def donkey(*, _say, name__n="Gordon") -> str:
    ''' Donkey Donkey
    '''
    return f'{name__n} says, "{_say}"'


def dog(*, _say, times__t=3) -> str:
    ''' Dogs barking
    '''
    return _say + ' bark!'*times__t


@sub_cmds(dog, donkey)
def main(say, /, *, verbose__v=False):
    ''' Say stuff

    Examples:
        $ ./sub.py "Hello world" -vv donkey

    '''
    if verbose__v: print("Ready? "*int(verbose__v))
    yield dict(_say=say)
    if verbose__v: print("Bye")


if __name__=='__main__':
    boot(main, sys.argv[1:])

