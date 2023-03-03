import sys
from print_ext import print

def bootstrap(args):
    print.pretty(sys.path)
    print(f"Bootstrap {args}")
