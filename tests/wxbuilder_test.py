import os.path

import wx

from xml_python.ext.wx import WXBuilder


def test_init():
    b = WXBuilder()
    assert b.parsers['frame'] == b.get_frame
    assert b.parsers['sizer'] == b.get_sizer
    assert b.parsers['input'] == b.get_control
    assert b.parsers['label'] == b.get_label
    assert b.parsers['event'] == b.get_event


def test_load():
    a = wx.App()
    assert isinstance(a, wx.App)  # Just to shut flake8 up.
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
