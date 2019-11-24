from pytest import fixture

from xml_python import Builder


@fixture(name='b')
def builder():
    return Builder()
