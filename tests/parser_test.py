from pytest import raises

from xml_python import Builder, NoSuchParser, no_parent

xml = """<root>
<first>%s</first>
<second test="true">%s</second>
</root>"""


class RootObject:
    def __init__(self):
        self.strings = []


def test_builder(b):
    assert isinstance(b, Builder)
    assert b.parsers == {}


def test_parser(b):
    b.parser('test')(print)
    assert b.parsers == {'test': print}


def test_nosuchparser(b):
    with raises(NoSuchParser) as exc:
        b.from_string('<root></root>')
    assert exc.value.args[0] == 'root'


def test_parsers(b):
    strings = ['This is the first node.', 'This is the second node.']
    code = xml % tuple(strings)

    @b.parser('root')
    def root(parent, text):
        assert text == '\n'
        assert parent is no_parent
        return RootObject()

    @b.parser('first')
    def first(parent, text):
        assert isinstance(parent, RootObject)
        assert not parent.strings
        parent.strings.append(text)

    @b.parser('second')
    def second(parent, text, test=None):
        assert test == 'true'
        assert isinstance(parent, RootObject)
        assert parent.strings == [strings[0]]
        parent.strings.append(text)

    res = b.from_string(code)
    assert isinstance(res, RootObject)
    assert res.strings == strings


def test_valid_generator(b):

    class PlaceHolder:
        def __init__(self):
            self.value = 1

    @b.parser('first')
    def do_first(parent, text):
        ph = PlaceHolder()
        yield ph
        assert ph.value == 2
        ph.value += 1

    @b.parser('second')
    def do_second(parent, text):
        assert parent.value == 1  # Should be, it's just been created.
        parent.value += 1

    ph = b.from_string('<first><second></second></first>')
    assert isinstance(ph, PlaceHolder)
    assert ph.value == 3


def test_invalid_generator(b):
    @b.parser('fails')
    def failure(parent, text):
        yield 1
        yield 2
        yield 3

    with raises(RuntimeError):
        b.from_string('<fails></fails>')


def test_convert_attribute_names(b):

    @b.parser('test')
    def do_test(parent, text, file_number=None):
        return file_number

    n = b.from_string('<test file-number="1"></test>')
    assert n == '1'
