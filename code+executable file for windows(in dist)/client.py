import threading
import socket
import random
from tkinter import *
#EE82EE Violet

#处理来自server的信息
def analyse(data):
    String =data
    print("analyze:" + String)
    if data.startswith("notice from administrator: "):
        noticeMsg.insert(END,data)
        noticeMsg.insert(END,"\n")


    elif data.startswith("msg from booker:"):
        noticeMsg.insert(END,data)

    elif data.startswith("booker:"):
        noticeMsg.insert(END, data)

    elif data.startswith("attention:"):
        noticeMsg.insert(END, data)

    else:
        CtrlMsg.insert(END,data)

def recv():
    while True:
        data = s.recvfrom(1024)
        analyse(data[0].decode('utf-8'))

#发送名字登陆
def bookerlogin():
    bookername[0] = nameEntry.get()
    data = bookername[0].encode('utf-8')
    print("name:"+bookername[0]+"\n")
    s.sendto(data, server)

    receiveThread = threading.Thread(target=recv)
    receiveThread.start()

#列出当前行政区的具体信息
def listthis():
    msg = "/list " + listdisEntry.get()
    toSend = bookername[0] + " : " + msg
    print(toSend)
    data = toSend.encode('utf-8')
    s.sendto(data, server)

#列出行政区
def listdistricts():
    msg = "/listdis"
    toSend = bookername[0] + " : " + msg
    print(toSend)
    data=toSend.encode('utf-8')
    s.sendto(data, server)

#加入行政区并预定口罩
def joindistricts():
    msg = "/join " + joinEntry.get()
    toSend = bookername[0] + " : " + msg
    print(toSend)
    data = toSend.encode('utf-8')
    s.sendto(data, server)

#发送聊天消息
def sendMsg():
    #print("msg\n")
    string=enterEntry.get()
    toSend=bookername[0] +" : "+"/msg "+string
    data = toSend.encode('utf-8')
    s.sendto(data, server)
    noticeMsg.insert(END,"msg sent successfully\n")

#退出登录
def bookerlogout():
    toSend = bookername[0] + " : " + "/out "
    data = toSend.encode('utf-8')
    s.sendto(data, server)




s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server = ("127.0.0.1", 41234)
bookername={}



window = Tk()
window.title('Free Booking')
window.geometry('960x700')
window.resizable(width=True, height=True)

# Control Area 
CtrlArea = Frame(relief="sunken", bg='#fafafa')
CtrlArea.place(relx=0.01, rely=0.01, relwidth=0.6, relheight=0.98)

caLabel = Label(CtrlArea, text="Control Area", font='Arial -%d' % 20, bg='#fafafa')
caLabel.place(relx=0.15, rely=0.01, relwidth=0.7, relheight=0.05)

outButton = Button(CtrlArea, text="Log out", font='Arial -%d' % 14, command=bookerlogout)
outButton.place(relx=0.01, rely=0.01, relwidth=0.2, relheight=0.04)


CtrlMsg = Text(CtrlArea, font='等线 -%d' % 16)
CtrlMsg.place(relx=0.02, rely=0.07, relwidth=0.9, relheight=0.45)

nameLabel = Label(CtrlArea, text="Booker Name:", font='Arial -%d' % 16, bg='#fafafa')
nameLabel.place(relx=0.01, rely=0.5, relwidth=0.8, relheight=0.025)

nameEntry = Entry(CtrlArea, font='Arial -%d' % 14)
nameEntry.place(relx=0.02, rely=0.55, relwidth=0.6, relheight=0.04)
nameButton = Button(CtrlArea, text="Log in", font='Arial -%d' % 14, command=bookerlogin)
nameButton.place(relx=0.68, rely=0.55, relwidth=0.2, relheight=0.04)


listButton = Button(CtrlArea, text="list districts", font='等线 -%d' % 16, command=listdistricts)
listButton.place(relx=0.02, rely=0.65, relwidth=0.85, relheight=0.055)


nameLabel = Label(CtrlArea, text="cmd format:districtname_numbers", font='等线 -%d' % 16, bg='#fafafa')
nameLabel.place(relx=0.2, rely=0.82, relwidth=0.8, relheight=0.025)

joinEntry = Entry(CtrlArea, font='等线 -%d' % 22)
joinEntry.place(relx=0.4, rely=0.86, relwidth=0.45, relheight=0.05)
joinButton = Button(CtrlArea, text="join district and book：", font='等线 -%d' % 15, command=joindistricts)
joinButton.place(relx=0.02, rely=0.86, relwidth=0.3, relheight=0.05)

listdisEntry = Entry(CtrlArea, font='等线 -%d' % 22)
listdisEntry.place(relx=0.3, rely=0.75, relwidth=0.55, relheight=0.05)
listdisButton = Button(CtrlArea, text="list district:：", font='等线 -%d' % 15, command=listthis)
listdisButton.place(relx=0.02, rely=0.75, relwidth=0.2, relheight=0.05)

# noticeboard
ctrlArea = Frame(relief="sunken", bg='#fafafa')
ctrlArea.place(relx=0.55, rely=0.01, relwidth=0.43, relheight=0.98)

ctrlLabel = Label(ctrlArea, text="Notice Board", font='Arial -%d' % 16, bg='#fafafa')
ctrlLabel.place(relx=0.1, rely=0.01, relwidth=0.9, relheight=0.04)

noticeMsg = Text(ctrlArea, font='Arial -%d' % 16)
noticeMsg.place(relx=0.1, rely=0.07, relwidth=0.8, relheight=0.6)

scroll = Scrollbar()

scroll.pack(side=RIGHT, fill=Y)


scroll.config(command=noticeMsg.yview)
noticeMsg.config(yscrollcommand=scroll.set)

scroll.config(command=CtrlMsg.yview)
noticeMsg.config(yscrollcommand=scroll.set)

noticeMsg.pack()

enterEntry = Entry(ctrlArea, font='等线 -%d' % 22)
enterEntry.place(relx=0.1, rely=0.7, relwidth=0.55, relheight=0.15)
enterButton = Button(ctrlArea, text="Send", font='等线 -%d' % 15,command=sendMsg)
enterButton.place(relx=0.7, rely=0.7, relwidth=0.2, relheight=0.05)

CtrlMsg.insert(END, "Welcome to Free Booking! \n")
noticeMsg.insert(END, "Messages from admin and other bookers will shown here\n")

window.mainloop()