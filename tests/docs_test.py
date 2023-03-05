import pytest
from yaclipy.docs import short_cmd_list
from yaclipy.cmd_dfn import CmdDfn, SubCmds
from print_ext import Printer
from .has_cmds import HasCmds



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

    obj = SubCmds(bob_=bob, z=3, a_long_name=x, name={'a':'b'}, _hidden=cob)
    Printer()(short_cmd_list(CmdDfn.scrape(obj)))
    out, _ = capfd.readouterr()
    print(out)
    assert(out == '\n * a-long-name About time.\n\n * bob         Short description.\n\n')
