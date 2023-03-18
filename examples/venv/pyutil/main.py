import logging, yaml, time
from print_ext import print
from yaclipy import sub_cmds, Config

log = logging.getLogger('clipy-main')

def run():
    ''' Run the project
    '''
    log.info('Running...')
    log.warn('Uh-oh')
    log.debug('Fixing stuff')



def build():
    ''' Build the project
    '''
    log.info('Building...')
    p = print.progress(steps=42)
    for f in range(42):
        p('Process \b2$', f, '\b$ ...')
        time.sleep(0.1)
    p('Done!', done=True)


    
def deploy():
    ''' Deploy the project
    '''
    log.info('Deploying...')


def configuration():
    ''' Show the current configuration.
    '''
    return Config


@sub_cmds(run, build, deploy, configuration)
def main(*, verbose__v=False, quiet__q=False, config__c=''):
    ''' This is the sole entrypoint for this project.
    
    Parameters:
        --verbose, -v
            Increase the logging level by one notch
        --quiet, -q
            Decrease the logging level by one notch
        --config <option>, -c <option> | default='dev'
            Choose a configuration option
    '''
    level = max(0, min(50, 20 - 10*(int(verbose__v) - int(quiet__q))))
    logging.basicConfig(style='{', format='{levelname:>7} {name:>10} {lineno:<3} | {message}', level=level)
    import config
    Config.configure(config__c or 'dev')
