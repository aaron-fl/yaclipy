import pytest
from yaclipy.docs import short_cmd_list
from yaclipy.cmd_dfn import CmdDfn, sub_cmds
from print_ext import Printer


def test_short_cmd_list(capfd):
    def bob(jump__j):
        ''' Short description.

        Parameters:
            <how_high>, --jump <how_high>, -j <how_high>
        '''

    def x(razor__r):
        '''About time.'''

    def cob(*args):
        pass
    @sub_cmds(bob_=bob, a_long_name=x)
    def f():pass
    cmd = CmdDfn('f',f)
    Printer()(short_cmd_list(cmd.sub_cmds()))
    out, _ = capfd.readouterr()
    print(out)
    assert(out == '\n * a-long-name About time.\n\n * bob         Short description.\n\n')


@pytest.mark.xfail(reason='Not implemented')
def test_doc_testing():
    assert(False)
    