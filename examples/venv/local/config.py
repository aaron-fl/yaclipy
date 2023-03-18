from yaclipy import Config
import config

me = Config.var('My own private variable', "'sup")

@config.test.override()
def test(super):
    super()
    config.title('local')
