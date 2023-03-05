import pytest
from yaclipy.exceptions import *
from yaclipy.cmd_dfn import CmdDfn
from .has_cmds import HasCmds


@pytest.mark.xfail(reason='Not implemented')
def test_uninstall_reqs():
    ''' When requirements are removed from requirements.txt make sure they are uninstalled
    '''
    assert(False)

