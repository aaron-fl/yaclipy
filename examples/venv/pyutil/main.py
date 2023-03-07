import logging
from yaclipy import sub_cmds

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
    

    
def deploy():
    ''' Deploy the project
    '''
    log.info('Deploying...')



@sub_cmds(run, build, deploy)
def main(*, verbose__v=False, quiet__q=False, target__t=''):
    ''' This is the sole entrypoint for this project.
    
    Parameters:
        --verbose, -v
            Increase the logging level by one notch
        --quiet, -q
            Decrease the logging level by one notch
    '''
    level = max(0, min(50, 20 - 10*(int(verbose__v) - int(quiet__q))))
    logging.basicConfig(style='{', format='{levelname:>7} {name:>10} {lineno:<3} | {message}', level=level)
