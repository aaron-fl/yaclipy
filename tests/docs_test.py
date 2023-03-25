import pytest
from yaclipy import Command, sub_cmds
from yaclipy.exceptions import CmdError
from print_ext import StringPrinter, Line


def test_CmdError_pretty():
    def bob(jump__j):
        '''bobby'''

    def x(razor__r):
        '''About time.'''

    def cob(*args):
        pass

    @sub_cmds(bob_=bob, a_long_name=x)
    def f():
        ''' Short description.
        Log description starts here



        '''

    cmd = Command(f)
    err = CmdError(cmd=cmd, errors=[Line('bad')])
    p = StringPrinter(color=False, ascii=True)
    p.pretty(err)
    assert(str(p) == '''
 * a-long-name About time.

 * bob         bobby
---
Short description.
Log description starts here
-[ CmdError ]-
 * bad
''')


@pytest.mark.xfail(reason='Not implemented')
def test_doc_testing():
    assert(False)
    