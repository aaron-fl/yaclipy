import pytest
from yaclipy import Command, sub_cmds
from yaclipy.exceptions import CmdError
from print_ext import Printer, Line
from .testutil import printer


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
    o,p = printer(color=False, ascii=True)
    p.pretty(err)
    print(o.getvalue())
    assert(o.getvalue() == '''
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
    