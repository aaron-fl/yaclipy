from print_ext import print, Table, pretty, Text
from docstring_parser import parse as docstring_parse



class CmdDoc():
    def __init__(self, doc):
        self.doc = docstring_parse(doc)

    def pretty(self, fmt='full'):
        return getattr(self, f'pretty_{fmt}')()

    def pretty_short(self):
        return self.doc.short_description

    def pretty_full(self):
        f = Text()
        if self.doc.short_description: f('\bem$',self.doc.short_description,'\v\v')
        if self.doc.long_description: f(self.doc.long_description,'\v')
        return f



