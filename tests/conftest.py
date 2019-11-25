from pytest import fixture

import wx

from xml_python import Builder
from xml_python.ext.wx import WXBuilder

a = wx.App()


@fixture(name='b')
def builder():
    return Builder()


@fixture(name='wxb')
def get_wxbuilder():
    return WXBuilder()
