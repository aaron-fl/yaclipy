from print_ext import Printer
from docstring_parser import parse as docstring_parse



class CmdDoc():
    def __init__(self, doc):
        self.doc = docstring_parse(doc)


    def __pretty__(self, print, fmt='full', **kwargs):
        getattr(self, f'pretty_{fmt}')(print)


    def pretty_short(self, print):
        print(self.doc.short_description)


    def pretty_full(self, print):
        if self.doc.short_description: print('\bem$', self.doc.short_description)
        if self.doc.long_description: print(self.doc.long_description)
