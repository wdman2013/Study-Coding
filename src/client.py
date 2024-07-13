import threading

import wx
from socket import socket,AF_INET,SOCK_STREAM
class ZsClient(wx.Frame):
    def __init__(self, client_name):
        # 调用父类的方法去初始化方法
        # None：没有父窗口
        # id 表示当前窗口的编号
        # pos：当前窗体的打开位置
        # size：窗体的大小，单位是像素，400宽，458高
        wx.Frame.__init__(self, None, id=1001,title=client_name+'的客户端界面', pos=wx.DefaultPosition,size=(400,450))
        # 创建面板对象
        pl = wx.Panel (self)
        # 在面板里放上盒子
        box = wx.BoxSizer(wx.VERTICAL)   #垂直方向布局
        # 可伸缩的网格布局
        fgz1=wx.FlexGridSizer(wx.HORIZONTAL) #水平方向布局

        #创建两个按钮
        conn_btn = wx.Button(pl, size=(200,40), label='连接')
        dis_conn_btn = wx.Button(pl, size=(200, 40), label='断开')

        # 把两个按钮放到可伸缩的网格布局
        fgz1.Add(conn_btn,1,wx.TOP | wx.LEFT)
        fgz1.Add(dis_conn_btn,1, wx.TOP | wx.RIGHT)

        # （可伸缩的网格布局）添加到box中
        box.Add(fgz1,1,wx.ALIGN_CENTRE)

        #只读文本框，显示聊天内容
        self.show_text=wx.TextCtrl(pl,size=(400,210),style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.show_text,1,wx.ALIGN_CENTRE)

        #创建聊天内容的文本框
        self.chat_text = wx.TextCtrl(pl, size=(400,120),style=wx.TE_MULTILINE)
        box.Add(self.chat_text,1,wx.ALIGN_CENTRE)

        # 可伸缩的网格布局
        fgz2=wx.FlexGridSizer(wx.HORIZONTAL) #水平方向布局

        #创建两个按钮
        reset_btn = wx.Button(pl, size=(200,40), label='重置')
        send_btn = wx.Button(pl, size=(200,40), label='发送')

        # 把两个按钮放到可伸缩的网格布局
        fgz2.Add(reset_btn,1,wx.TOP | wx.LEFT)
        fgz2.Add(send_btn,1, wx.TOP | wx.RIGHT)

        # （可伸缩的网格布局）添加到box中
        box.Add(fgz2,1,wx.ALIGN_CENTRE)

        # 将盒子放到面板中
        pl.SetSizer(box)

        '''----------------------以上代码是客户端界面的绘制----------------------'''
        self.Bind(wx.EVT_BUTTON,self.connect_to_server,conn_btn)
        self.client_name = client_name
        self.isConnected = False
        self.client_socket = None

        # 绑定发送按钮事件
        self.Bind(wx.EVT_BUTTON, self.sendmsg_to_server, send_btn)

        # 绑定断开服务器连接事件
        self.Bind(wx.EVT_BUTTON, self.disconnect_server, dis_conn_btn)

        # 绑定重置按钮事件
        self.Bind(wx.EVT_BUTTON, self.reset, reset_btn)

    def reset(self,event):
        self.chat_text.Clear()

    def disconnect_server(self, event):
        # 发送断开命令
        self.client_socket.send('disconnect'.encode('utf-8'))
        self.isConnected = False

    def sendmsg_to_server(self,event):
        # 判断一下是否和服务器建立了连接
        if self.isConnected:
            send_msg = self.chat_text.GetValue()

            if send_msg != '':
                self.client_socket.send(send_msg.encode('utf-8'))
                #数据发送完之后，清空文本框
                self.chat_text.SetValue('')

    def connect_to_server(self,event):
        print('连接服务器')

        if not self.isConnected:
            server_host_port =('127.0.0.1',8888)

            self.client_socket = socket(AF_INET, SOCK_STREAM)

            self.client_socket.connect(server_host_port)

            self.client_socket.send(self.client_name.encode('utf-8'))

            client_thread = threading.Thread(target=self.recv_data)

            client_thread.daemon = True

            client.isConnected = True

            client_thread.start()

    def recv_data(self):
         # 如果是接收状态
        while self.isConnected:
            data = self.client_socket.recv(1024).decode('utf-8')
            #显示到只读文本框
            self.show_text.AppendText('-'*40+'\n'+data+'\n')


if __name__ == '__main__':
    #初始化App
    app = wx.App()

    #创建自己的客户端界面
    client = ZsClient('Python树哥')
    client.Show()

    #循环刷新显示
    app.MainLoop()


