import yaml, time, pathlib, asyncio
from print_ext import Printer
import yaclipy as CLI
import config

def run():
    ''' Run the project
    '''
    print = Printer('Running...', config.title())
    print('Uh-oh', tag='v:-1')
    print('Fixing stuff', tag='v:1')



async def build():
    ''' Build the project
    '''
    files = list(pathlib.Path('.').iterdir())
    with Printer().progress('Building...', config.prefix()) as update:  
        for i, fname in enumerate(files):
            update('Process \b2$', fname, '\b$ ...', tag={'progress':(i, len(files))})
            await asyncio.sleep(0.5)
    update('Done!', tag='progress:100')



def deploy():
    ''' Deploy the project
    '''
    Printer('Deploying...', config.prefix())



@CLI.sub_cmds(run, build, deploy)
def main(*, verbose__v=False, quiet__q=False, config__c=''):
    ''' This is the sole entrypoint for this project.
    
    Parameters:
        --verbose, -v
            Increase the verbosity filter by one notch
        --quiet, -q
            Decrease the verbosity filter by one notch
        --config <option>, -c <option> | default='dev'
            Choose a configuration option
    '''
    v = int(verbose__v) - int(quiet__q)
    Printer.replace(filter=lambda t: t.get('v',0) <= v)
    import config
    cfg = CLI.get_config()
    cfg[config__c or 'dev'].fn()
    return cfg
