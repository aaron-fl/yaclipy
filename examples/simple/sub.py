#!/usr/bin/env python
import sys
from yaclipy import boot, SubCmds


def donkey(*, _say, name__n="Gordon"):
    ''' Donkey Donkey
    '''
    print(_say, name__n)


def dog(*, _say, times__t=3):
    ''' Dogs barking
    '''
    return _say + ' bark!'*times__t


@SubCmds(dog, donkey)
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

