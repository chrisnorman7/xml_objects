from pytest import fixture

from xml_objects import Builder


@fixture(name='b')
def builder():
    return Builder()
