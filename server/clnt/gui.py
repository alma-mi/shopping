"""
alma miller
gui
"""

import wx
from client import *

RANGE_ONE = 0
RANGE_TWO = 2


class GUI(wx.Frame):

    def __init__(self):
        super(GUI, self).__init__(None, title='שרת טכנאי', size=(300, 250))
        self.params = []
        self.combo_box = None
        self.client = None
        self.InitUI()

    def InitUI(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        menu_item = file_menu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menu_bar.Append(file_menu, 'Menu&')
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.OnQuit, menu_item)
        pnl = wx.Panel(self)
        sb = wx.StaticBox(pnl, label='Parameters')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        text_one = wx.StaticText(pnl, label='Param 1')
        text_two = wx.StaticText(pnl, label='Param 2')
        param_one = wx.TextCtrl(pnl)
        param_two = wx.TextCtrl(pnl)
        self.params.append(param_one)
        self.params.append(param_two)
        sbs.Add(text_one)
        sbs.Add(self.params[0], flag=wx.LEFT, border=5)
        sbs.Add(text_two)
        sbs.Add(self.params[1], flag=wx.LEFT, border=5)
        pnl.SetSizer(sbs)
        commands = ['DIR', 'TAKE_SCREENSHOT', 'SEND_FILE',
                    'DELETE', 'COPY', 'EXECUTE',
                    'EXIT', 'HISTORY']
        wx.StaticText(pnl, pos=(130, 50), label="Command")
        self.combo_box = wx.ComboBox(pnl, pos=(130, 70), choices=commands,
                                     style=wx.CB_READONLY)
        cbtn = wx.Button(pnl, label='Send', pos=(140, 150))
        cbtn.Bind(wx.EVT_BUTTON, self.on_send)
        self.client = None
        self.Centre()
        self.Show(True)
        self.client = Client(IP, PORT)

    def OnQuit(self, e):
        """when the user presses the quit button,
        the function is called, ending the GUI loop"""
        self.Close()

    def on_send(self, e):
        """
         when the user presses the send button,
         this function is called, which in turn
         generates the query by combining all parameters
         given by the user, and transfers them to the client.
         after client returns the response, the function creates
         a message box containing it.
         """
        command = self.combo_box.GetStringSelection()
        params = ""
        for x in range(RANGE_ONE, RANGE_TWO):
            params += self.params[x].GetLineText(RANGE_ONE)
            params += ' '
        response = self.client.send_command(command + ' ' + params)
        wx.MessageBox(response, 'Response', wx.OK | wx.ICON_INFORMATION)
        if response == "server is down":
            self.Close()


def main():
    """begins an app loop, creates a GUI.
    when user quits, ends loop."""
    ex = wx.App()
    GUI()
    ex.MainLoop()


if __name__ == "__main__":
    main()
