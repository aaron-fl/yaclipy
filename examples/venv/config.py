import yaclipy as CLI

prefix = CLI.config_var('A prefix to distinguish configurations.')
title = CLI.config_var('The app title', 'Awesome App')


@CLI.configure()
def dev():
    prefix('dev')


@CLI.configure()
def prod():
    prefix('prod')


@CLI.configure()
def test():
    prefix('test')


with CLI.include: import local.config
