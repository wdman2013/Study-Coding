import threading
import time
import wx
from socket import socket,AF_INET,SOCK_STREAM

class ZsServer(wx.Frame):
    #服务器是否启动
    isOn = False
    #服务器地址和端口
    host_port = None
    #服务端socket
    server_socket = None
    #连接服务器的客户端会话线程集合
    session_thread_dict = {}

    def __init__(self):
        wx.Frame.__init__(self, None,id=1002,title='张树的服务器界面',pos=wx.DefaultPosition,size=(400,450))
        #窗口放一个面板
        pl = wx.Panel(self)
        #面板上放一个盒子
        box = wx.BoxSizer(wx.VERTICAL) #垂直方向自动排版
        #可伸缩的网格布局
        fgz1 = wx.FlexGridSizer(wx.HORIZONTAL) #水平布局

        start_server_btn = wx.Button(pl,size=(133,40),label='启动服务')
        record_btn = wx.Button(pl,size=(133,40),label='保存记录')
        stop_server_btn = wx.Button(pl,size=(133,40),label='停止服务')

        fgz1.Add(start_server_btn,1,wx.TOP | wx.LEFT)
        fgz1.Add(record_btn, 1, wx.TOP  |  wx.CENTER)
        fgz1.Add(stop_server_btn, 1, wx.TOP | wx.RIGHT)

        box.Add(fgz1,wx.ALIGN_CENTRE)

        #只读文本框，显示聊天记录
        self.show_text = wx.TextCtrl(pl,size=(400,410),style=wx.TE_MULTILINE | wx.TE_READONLY)
        box.Add(self.show_text,1,wx.ALIGN_CENTRE)
        pl.SetSizer(box)
        ''' 以上为界面绘制代码'''

        '''以下为必要的属性'''
        self.isOn = False  #服务器是否启动
        self.host_port =('',8888)  #空字符串代表所有的IP

        #创建socekt
        self.server_socket = socket(AF_INET,SOCK_STREAM)
        #绑定IP和端口号
        self.server_socket.bind(self.host_port)
        #监听
        self.server_socket.listen(5)
        #创建字典保存客户端回话进程
        self.session_thread_dict = {}  #key:客户端名称 value：会话线程

        # 以下为处理代码
        self.Bind(wx.EVT_BUTTON,self.start_server,start_server_btn)

        #绑定保存聊天记录按钮事件
        self.Bind(wx.EVT_BUTTON, self.save_record, record_btn)

        # 绑定断开服务按钮事件
        self.Bind(wx.EVT_BUTTON, self.stop_server, stop_server_btn)

    def stop_server(self,event):
        print('服务器已停止！')
        if self.isOn :
            self.show_info_and_send_client(data_source='服务器通知', data='服务器已停止！',
                                           data_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            self.isOn = False

            for client in self.session_thread_dict.values():
                if client.isWork:
                    client.isWork = False
                    # 服务器通知
                    client.client_socket.send('ServerStoped'.encode('utf-8'))

    def save_record(self,event):
        record_data = self.show_text.GetValue()

        with open('record.log','w',encoding='utf-8') as file:
            file.write(record_data)

    def start_server(self,event):
        print('服务器已启动！')
        self.show_info_and_send_client(data_source='服务器通知', data='服务器已启动！',
                                       data_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        # 判断服务器是否启动了服务
        if not self.isOn:  #如果没有启动服务
            self.isOn = True
            #创建主线程
            main_thread = threading.Thread(target=self.do_work)
            #设置为守护线程
            main_thread.daemon = True
            #启动线程
            main_thread.start()

    def do_work(self):
        while self.isOn:
            #接收客户端的连接请求
            session_socket, client_addr=self.server_socket.accept()
            #用客户端的名称作为字典的Key
            user_name = session_socket.recv(1024).decode('utf-8')
            #创建一个会话线程
            session_thread = SessionThread(session_socket,user_name,self)
            #存储到字典
            self.session_thread_dict[user_name] = session_thread
            #启动会话线程
            session_thread.start()

            self.show_info_and_send_client(data_source='服务器通知',data=f'欢迎{user_name}进入聊天室!', data_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        #服务停止时
        self.server_socket.close()

    def show_info_and_send_client(self,data_source,data,data_time):
        # 字符串的拼接
        send_data = f'{data_source}:{data}\n时间：{data_time}'

        self.show_text.AppendText(send_data+'\n' + '-'*40+'\n')

        for client in  self.session_thread_dict.values():
            if client.isWork:
                client.client_socket.send(send_data.encode('utf-8'))

class SessionThread(threading.Thread):
    #线程是否连接
    isWork = False
    #客户端连接Socket
    client_socket = None
    #客户端用户名
    user_name = ''
    #服务端对象
    server = None

    def __init__(self,client_socket,user_name,server):
        # 调用父类的初始方法
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.user_name = user_name
        self.server = server
        self.isWork = True

    def run(self) -> None:
        print(f'客户端：{self.user_name}已经和服务器连接成功，服务器启动了一个会话线程')
        while self.isWork:
            #从客户端接收数据
            data = self.client_socket.recv(1024).decode('utf-8')

            if data == 'disconnect':
                self.isWork = False
                # 服务器通知
                self.server.show_info_and_send_client( '服务器通知：', f'{self.user_name}离开了服务器',
                                                      time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            else:
                # 给服务器和各个客户端发送消息
                self.server.show_info_and_send_client(self.user_name,data,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

         #关闭socket
        self.client_socket.close()

if __name__ == '__main__':
    # 初始化APP
    app = wx.App()

    server = ZsServer()
    server.Show()

    #循环显示刷新
    app.MainLoop()


