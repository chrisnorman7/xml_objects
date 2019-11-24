import wx

from xml_python.ext.wx import builder

if __name__ == '__main__':
    a = wx.App()
    f = builder.from_args('frame.xml')

    def login():
        username = f.username.GetValue()
        password = f.password.GetValue()
        wx.MessageBox(
            f'Pretending to login as {username}:{password}.',
            caption='Pretend Login', parent=f
        )

    f.login = login
    f.Show(True)
    f.Maximize()
    a.MainLoop()
