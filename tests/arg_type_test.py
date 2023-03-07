import pytest
from inspect import Parameter
from yaclipy.arg_spec import ArgType



def test_ArgType_str():
    assert(str(ArgType(3)) == 'int')
    assert(str(ArgType(int)) == 'int')
    assert(str(ArgType(None)) == 'str')
    assert(str(ArgType(Parameter.empty)) == 'str')
    assert(str(ArgType(3.1)) == 'float')
    assert(str(ArgType([])) == '[str]')
    assert(str(ArgType([int])) == '[int]')
    assert(str(ArgType([3.3])) == '[float]')



def test_argtype_coerce():
    assert(ArgType(3).coerce('-33') == -33)
    assert(ArgType(int).coerce('-33') == -33)
    assert(ArgType(None).coerce('-33') == '-33')
    assert(ArgType(3.1).coerce('-3.3') == -3.3)



def test_argtype_merge_bool_to_str():
    a = ArgType(None)
    with pytest.raises(ValueError):
        a.merge(True, Parameter.empty)



def test_argtype_merge_list_str():
    a = ArgType([])
    assert(a.merge('a', Parameter.empty) == ['a'])
    assert(a.merge('a', ['b']) == ['b', 'a'])
    with pytest.raises(ValueError):
        assert(a.merge(3, ['1','2']) == ['1','2','3'])
    assert(a.merge('3', ['1','2']) == ['1','2','3'])



def test_argtype_merge_bool():
    a = ArgType(True)
    assert(a.merge(False, Parameter.empty) == False)
    assert(a.merge(True, False) == 1)
    assert(a.merge(True, True) == 2)
    with pytest.raises(ValueError):
        print(a.merge('x', 1))



def test_argtype_merge_flaot():
    a = ArgType([3.14])
    assert(a.merge("3.1", [2.1]) == [2.1, 3.1])



def test_argtype_dict():
    a = ArgType({'k':3})
    print(a)
    assert(a.merge('{"a":[1,2,3]}', {'b':[6]}).keys() == {'a','b'})
    assert(a.merge('33.3', {'b':[6]}) == 33.3)
    assert(a.merge('[1,2,3]', ['a','b','c']) == ['a','b','c',1,2,3])



def test_argtype_custom():
    class Custom(type):
        def __new__(self, sval):
            return 'x'
    a = ArgType(Custom)
    assert(a.merge('{"a":[1,2,3]}',None) == 'x')

    def custom(sval):
        return 'y'
    a = ArgType(custom)
    assert(a.merge('{"a":[1,2,3]}',None) == 'y')
