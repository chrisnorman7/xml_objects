import os.path

from flask import Flask

from xml_python.ext.flask import FlaskBuilder


def test_init():
    b = FlaskBuilder()
    assert b.parsers['app'] == b.get_app
    assert b.parsers['route'] == b.get_route


def test_load():
    b = FlaskBuilder()
    a = b.from_filename(os.path.join('examples', 'flask', 'app.xml'))
    assert isinstance(a, Flask)
    rules = [r.rule for r in a.url_map.iter_rules()]
    assert '/' in rules
    assert '/next/' in rules
