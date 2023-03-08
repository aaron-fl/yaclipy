#!/usr/bin/env python
import sys
from print_ext import print, PrettyException
import yaclipy as CLI

def main(say, times__t=1) -> str:
    ''' Say something multiple times

    Parameters:
        <message>, --say <message>
            What you want to say
        <int>, --times <int>, -t <int>
            How many times you want to say it.
    '''
    return ' '.join([say] * times__t)


if __name__ == '__main__':
    try:
        CLI.Command(main)(sys.argv[1:]).run()
    except PrettyException as e:
        print.pretty(e)
