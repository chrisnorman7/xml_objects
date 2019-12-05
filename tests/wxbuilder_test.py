import os.path

import wx

from pytest import raises
from xml_python import InvalidParent
from xml_python.ext.wx import WXBuilder


def test_init():
    b = WXBuilder()
    assert b.parsers['frame'].func == b.get_frame
    assert b.parsers['sizer'].func == b.get_sizer
    assert b.parsers['input'].func == b.get_control
    assert b.parsers['label'].func == b.get_label
    assert b.parsers['event'].func == b.get_event


def test_load():
    b = WXBuilder()
    f = b.from_filename(os.path.join('examples', 'wx', 'frame.xml'))
    assert isinstance(f, wx.Frame)
    assert f.GetTitle() == 'xml_objects wxPython Demo'
    assert isinstance(f.main_sizer, wx.BoxSizer)
    assert f.main_sizer.GetOrientation() == wx.VERTICAL
    assert isinstance(f.username_sizer, wx.BoxSizer)
    assert f.username_sizer.GetOrientation() == wx.HORIZONTAL
    username_label, username = f.username_sizer.GetChildren()
    username_label = username_label.GetWindow()
    username = username.GetWindow()
    assert username_label is f.username_label
    assert isinstance(username_label, wx.StaticText)
    assert username_label.GetLabel() == 'Username'
    assert username is f.username
    assert isinstance(username, wx.TextCtrl)
    assert username.GetWindowStyle() == wx.TE_PROCESS_ENTER
    assert username.GetValue() == 'pretendusername'
    assert isinstance(f.password_sizer, wx.BoxSizer)
    assert f.password_sizer.GetOrientation() == wx.HORIZONTAL
    password_label, password = f.password_sizer.GetChildren()
    password_label = password_label.GetWindow()
    password = password.GetWindow()
    assert password_label is f.password_label
    assert isinstance(password_label, wx.StaticText)
    assert password_label.GetLabel() == 'Password'
    assert password is f.password
    assert isinstance(password, wx.TextCtrl)
    assert password.GetWindowStyle() == (wx.TE_PROCESS_ENTER | wx.TE_PASSWORD)
    assert password.GetLabel() == ''
    assert isinstance(f.button_sizer, wx.BoxSizer)
    assert f.button_sizer.GetOrientation() == wx.HORIZONTAL
    ok, cancel = f.button_sizer.GetChildren()
    ok = ok.GetWindow()
    cancel = cancel.GetWindow()
    assert ok is f.ok
    assert cancel is f.cancel
    assert isinstance(ok, wx.Button)
    assert ok.GetLabel() == 'OK'
    assert isinstance(cancel, wx.Button)
    assert cancel.GetLabel() == 'Cancel'
    username_sizer, password_sizer, button_sizer = f.main_sizer.GetChildren()
    assert username_sizer.GetSizer() is f.username_sizer
    assert password_sizer.GetSizer() is f.password_sizer
    assert button_sizer.GetSizer() is f.button_sizer
    mb = f.GetMenuBar()
    assert isinstance(mb, wx.MenuBar)
    assert mb.GetMenuCount() == 1
    fm = mb.GetMenu(0)
    assert isinstance(fm, wx.Menu)
    assert fm is f.file_menu
    assert mb.GetMenuLabel(0) == fm.GetTitle()
    assert fm.GetTitle() == 'File'
    items = fm.GetMenuItems()
    assert len(items) == 1
    item = items[0]
    assert item.GetItemLabel() == 'Quit\tCTRL+Q'
    assert item.GetId() == wx.ID_EXIT


def test_valid_frame(wxb):
    xml = '<frame></frame>'
    f = wxb.from_string(xml)
    children = f.GetChildren()
    assert len(children) == 1
    assert isinstance(children[0], wx.Panel)
    assert children[0] is f.panel
    assert f.GetTitle() == 'Untitled Frame'


def test_invalid_frame(wxb):
    xml = '<frame><frame></frame></frame>'
    with raises(InvalidParent) as exc:
        wxb.from_string(xml)
    parser, parent = exc.value.args
    assert parser is wxb.parsers['frame']
    assert isinstance(parent, wx.Frame)
