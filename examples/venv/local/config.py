import yaclipy as CLI
import config

me = CLI.config_var('My own private variable', "'sup")

@config.test.override()
def test(super):
    super()
    config.title('local')
