

class Parent():

    def boink(self):
        return 'boink'


class HasCmds(Parent):

    def __init__(self,**kwargs):
        for k,v in kwargs.items(): setattr(self, k,v)

    def __str__(self):
        return ''

    def foo_(self):
        return "There are two foo's"

    def foo(self, x=3):
        return 'foo'*x

    def break_(self, what='everything'):
        return 'break '+what

