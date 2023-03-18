from print_ext import Printer
from docstring_parser import parse as docstring_parse



class CmdDoc():
    def __init__(self, doc):
        self.doc = docstring_parse(doc)


    def __pretty__(self, fmt='full', **kwargs):
        return getattr(self, f'pretty_{fmt}')()


    def pretty_short(self):
        return self.doc.short_description


    def pretty_full(self):
        p = Printer()
        if self.doc.short_description: p('\bem$',self.doc.short_description, pad=(0,1))
        if self.doc.long_description: p(self.doc.long_description, pad=-1)
        return p
