from yaclipy import Config

prefix = Config.var('A prefix to distinguish configurations.', '')
title = Config.var('The app title', 'Awesome App')


@Config.option()
def dev():
    prefix('dev')


@Config.option()
def prod():
    prefix('prod')


@Config.option()
def test():
    prefix('test')


with Config.include: import local.config
