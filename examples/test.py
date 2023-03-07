#!/usr/bin/env python
import sys
from yaclipy import boot

def foo(say, times__t=1) -> str:
    ''' Say something multiple times

    Parameters:
        <message>, --say <message>
            What you want to say
        <int>, --times <int>, -t <int>
            How many times you want to say it.
    '''
    return ' '.join([say] * times__t)

if __name__ == '__main__':
    boot(foo, sys.argv[1:])