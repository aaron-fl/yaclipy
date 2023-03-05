from print_ext import print, Table, pretty, Flex
from print_ext.borders import Borders
from docstring_parser import parse as docstring_parse



class CmdDoc():
    def __init__(self, doc):
        self.doc = docstring_parse(doc)

    def pretty(self, fmt='full'):
        return getattr(self, f'pretty_{fmt}')()

    def pretty_short(self):
        return self.doc.short_description

    def pretty_full(self):
        f = Flex()
        f(self.doc.short_description)
        if self.doc.long_description: f('\v', self.doc.long_description,'\v')
        for p in self.doc.params:
            f(pretty(p))
        return f



def short_cmd_list(cmds):
    tbl = Table(0.0, 0.0, 1, tmpl='')
    tbl.cell('ALL', cls=Borders, border=(' ','m:1010'))
    tbl.cell('C1', style='1')
    tbl.cell('R-1', border='m:1110')
    for cmd in sorted(cmds.values(), key=lambda x: x.name):
        tbl('*\t', cmd.name,'\t', pretty(cmd.doc(), fmt='short'),'\t')
    return tbl
