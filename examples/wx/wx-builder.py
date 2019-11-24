import wx

from xml_objects.ext.wx import builder

if __name__ == '__main__':
    a = wx.App()
    f = builder.from_args('frame.xml')
    f.Show(True)
    f.Maximize()
    a.MainLoop()
