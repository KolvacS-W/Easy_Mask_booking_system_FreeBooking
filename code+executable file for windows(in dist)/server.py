import threading
import socket
import random
from tkinter import *
#EE82EE Violet

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serveraddr = ('127.0.0.1', 41234)
s.bind(serveraddr)

booker = {}
bookerids = {}
bkerstat = {}
bookerips = {}
districts = []
status={}
booknum={}
bkernum={}


bookerids["admin"] = 999999
bkerstat["admin"] = "admin"
booker["admin"] = None


def parsedata(cmd):
    data = cmd
    if data.count(" : "):  # contain command
        return data.partition(" : ")
    else:  # just name
        return 0


def parsecmd(cmd):
        return cmd.partition(" ")


#用来处理客户端信息的
def MainContact(cmd, ipaddr):
    result = parsedata(cmd)
    #登录
    if result == 0:  
        if cmd in bookerips.values():
            reString = "Sorry,bookername have been used.\n"
            s.sendto(reString.encode('utf-8'), ipaddr)
        else:
            reString = "You have logged in successfully.\n"
            s.sendto(reString.encode('utf-8'), ipaddr)
            bookerips[ipaddr] = cmd
            #刚刚登陆，暂时无预约
            bkerstat[cmd] = None
            #保证生成唯一的bookerid
            bookerid = random.randint(0, 4096)
            while bookerid in bookerids.values():
                bookerid = random.randint(0, 4096)
            bookerids[cmd] = bookerid

    elif result[2][0] == "/":
        bookerCommand = parsecmd(result[2])
        # list all districts
        if bookerCommand[0] == "/listdis":
            if bookerCommand[2] != "":  # check arguments' amount
                reString = "cmd wrong format\n"
                s.sendto(reString.encode('utf-8'), ipaddr)
                return
            else:
                reString = "All districts are as following:\n"
                s.sendto(reString.encode('utf-8'), ipaddr)
                print("list all dis\n")
                for i in districts:
                    s.sendto(i.encode('utf-8'), ipaddr)
                    s1=" "
                    s.sendto(s1.encode('utf-8'), ipaddr)
                    s2="状态："
                    s.sendto(s2.encode('utf-8'), ipaddr)
                    String = status[i]
                    s.sendto(String.encode('utf-8'), ipaddr)
                    s3="\n"
                    s.sendto(s3.encode('utf-8'), ipaddr)
                reString = "All districts have been shown\n"
                s.sendto(reString.encode('utf-8'), ipaddr)
                return
            #用户加入行政区并预约口罩
        elif bookerCommand[0] == "/join":
            print("see join\n")
            args = bookerCommand[2].partition("_")
            print(args)
            if args[2] == "":
                # print("error in")
                reString = "cmd wrong format\n"
                s.sendto(reString.encode('utf-8'), ipaddr)
                return
            else:
                if districts.count(args[0]) == 0:
                    print("dis error sent\n")
                    reString = "district doesn't existed! Please try again.\n"
                    s.sendto(reString.encode('utf-8'), ipaddr)
                    return
                else:
                    if status[args[0]]=="非预约中":
                        print("status\n")
                        reString = "This district is not available\n"
                        s.sendto(reString.encode('utf-8'), ipaddr)
                        return
                    else:
                        if int(args[2])>50:
                            print("too much\n")
                            reString = "sorry, the maximum number you can book once is 50\n"
                            s.sendto(reString.encode('utf-8'), ipaddr)
                        else:
                            if bkerstat[result[0]] is not None:
                                print("already in \n")
                                reString = "You have joined one district. Please leave it first.\n"
                                s.sendto(reString.encode('utf-8'), ipaddr)
                            else:
                                print("join success\n")
                                #更新预约口罩数量和人数
                                booknum[args[0]]=str(int(booknum[args[0]])+int(args[2]))
                                bkernum[args[0]]=str(int(bkernum[args[0]])+1)

                                #给其他用户推送这个消息
                                re1="attention:booker:"+result[0]+"has booked "+args[2]+"facemasks in"+args[0]+"\n"
                                for k in booker.keys():
                                    if booker[k]==args[0]:
                                        for m in bookerips.keys():
                                            if bookerips[m]==k:
                                                adTobooker(re1,m)



                                for i in districts:
                                    if i == args[0]:
                                        #bkerstat[result[0]] = args[2]
                                        booker[result[0]] = i
                                    # print("sMsg sent")
                                        reString = "You have joined the district and booked successfully. May you have a good time!\n"
                                        s.sendto(reString.encode('utf-8'), ipaddr)
                                        return
        elif bookerCommand[0] == "/list":
            if bookerCommand[2] == "":
                reString = "cmd wrong format\n"
                s.sendto(reString.encode('utf-8'), ipaddr)
                return

            else:
                if status[bookerCommand[2]]=="非预约中":
                    reString ="当前行政区预约已经结束！\n"
                    s.sendto(reString.encode('utf-8'), ipaddr)

                else:
                    reString1 = bookerCommand[2]
                    s.sendto(reString1.encode('utf-8'), ipaddr)
                    reString2=  "预约总人数："
                    s.sendto(reString2.encode('utf-8'), ipaddr)
                    reString3=bkernum[bookerCommand[2]]
                    s.sendto(reString3.encode('utf-8'), ipaddr)
                    reString4="预约口罩总数:"
                    s.sendto(reString4.encode('utf-8'), ipaddr)
                    reString5=booknum[bookerCommand[2]]+"\n"
                    s.sendto(reString5.encode('utf-8'), ipaddr)
                return
        #用户发送消息
        elif bookerCommand[0] == "/msg":
            re1="msg from booker:"+result[0]+" in "+booker[result[0]]+":\n"
            chatMsg.insert(END, re1)
            re2 = bookerCommand[2]+"\n"
            chatMsg.insert(END,re2)
            for i in bookerips.keys():
                adTobooker(re1+re2,i)

        #用户退出登陆
        elif bookerCommand[0] == "/out":
            print(result[0])

            for i in bookerips.keys():
                if bookerips[i]==result[0]:
                    del bookerips[i]
                    re="you have logged out sucessfully.goodbye!\n"
                    adTobooker(re,i)

        return

def startListen():
    while True:
        recv = s.recvfrom(1024)
        recvmsg = recv[0].decode('utf-8')
        recvipaddr = recv[1]
        if recv:
            UsersThread = threading.Thread(target=MainContact, args=(recvmsg, recvipaddr,))
            UsersThread.start()

def AdLogin():
    CtrlMsg.insert(END, "Admin logged in successfully\n")
    bookerThread = threading.Thread(target=startListen)
    bookerThread.start()



def adTobooker(Content, ipaddr):
    s.sendto(Content.encode('utf-8'), ipaddr)

def enterdistrict():
    selecteddistrict = enterEntry.get()
    print(enterEntry.get())
    if booker["admin"] is None:
        if selecteddistrict in districts:
            booker["admin"] = selecteddistrict
            String = "You have enter the district: %s successfully\n" % selecteddistrict
            CtrlMsg.insert(END, String)
        else:
            String = "district: %s doesn't exist.\n" % selecteddistrict
            CtrlMsg.insert(END, String)
    else:
        CtrlMsg.insert(END, "You already a district.\nplease leave it first.\n")


def leavedis():
    #selecteddistrict = leaveEntry.get()
    #print(leaveEntry.get())
    if booker["admin"] is None:
            String = "You are not in any districts\n"
            CtrlMsg.insert(END,"You are not in any districts\n")

    else:
        booker["admin"] =None
        CtrlMsg.insert(END,"You have left districts successfully\n")



def addistrict():
    distoadd = addEntry.get()
    print(addEntry.get())
    if distoadd in districts:
        String = "district: %s has existed, please check your command and try again.\n" % distoadd
        CtrlMsg.insert(END, String)
    elif distoadd == "":
        String = "Please enter the name \n"
        CtrlMsg.insert(END, String)
    else:
        districts.append(distoadd)
        status[distoadd]="非预约中"
        booknum[distoadd ]="0"
        bkernum[distoadd]="0"
        String = " %s has been added.\n" % distoadd
        CtrlMsg.insert(END, String)


def deleteistrict():
    distodelets = deleteEntry.get()
    print(deleteEntry.get())
    temp1 = []
    temp2 = []
    if distodelets not in districts:
        String = "district: %s doesn't exist.\n" % distodelets
        CtrlMsg.insert(END, String)
    else:
        for x in range(len(districts)):
            if districts[x] == distodelets:
                t = x
                String = "You have close the district: %s successfully\n" % distodelets

                for i in booker.keys():
                    if booker[i] == distodelets and i != "admin":
                        temp2.append(i)

                for p in temp2:
                    del booker[p]
                booker["admin"] = None
                del status[distodelets]
                CtrlMsg.insert(END, String)
        del districts[t]


def listdistricts():
    CtrlMsg.insert(END, "All districts are following:\n")
    for i in districts:
        CtrlMsg.insert(END,i)
        CtrlMsg.insert(END, "    ")
        String = status[i]
        CtrlMsg.insert(END,"状态：")
        CtrlMsg.insert(END,String)
        CtrlMsg.insert(END,"\n")


def openround():
    disname = booker["admin"]
    print(status.get(disname))
    if  status[disname]!='预约中':
        status[disname] = '预约中'
        CtrlMsg.insert(END, "你已经开启该行政区新一轮预约\n")

    else:
        CtrlMsg.insert(END, "当前行政区已在预约中\n")




def listdisstatus():
    disname=booker["admin"]
    if (status[disname] !='预约中'):
        CtrlMsg.insert(END,"当前行政区不在预约中\n")
    else:
        reString1 = disname
        CtrlMsg.insert(END, reString1)
        reString2 = "预约总人数："
        CtrlMsg.insert(END, reString2)
        reString3 = bkernum[disname]
        CtrlMsg.insert(END, reString3)
        reString4 = "预约口罩总数:"
        CtrlMsg.insert(END, reString4)
        reString5 = booknum[disname] + "\n"
        CtrlMsg.insert(END, reString5)
        return


def handout():
    disname = booker["admin"]
    if (status[disname] != '预约中'):
        CtrlMsg.insert(END, "当前行政区不在预约中\n")

    else:
        status[disname]='非预约中'
        CtrlMsg.insert(END, "您已成功向该地区预约者分发口罩\n")
        #将预约人数和口罩数清零
        bkernum[disname]=0
        booknum[disname]=0

        for i in booker.keys():
            if booker[i]==disname:
                reString ="恭喜您，您预约的口罩已经成功发货\n"
                for j in bookerips.keys():
                    if bookerips[j]==i:
                        adTobooker(reString,j)
                        break
        return

def send():
    Msg=sendMsg.get()
    print("send:"+Msg+"\n")
    sendid=Msg.partition(" ")
    print((sendid[0])[1:-1])
    s=(sendid[0])[1:-1]
    if s=="all":
        for i in bookerips:
            adTobooker((("notice from administrator: "+sendid[2]+"\n")),i)
        chatMsg.insert(END, "msg sent successfully\n")
    else:
        if s in bookerips.values():
            for j in bookerips.keys():
                if bookerips[j]==s:
                    adTobooker((("notice from administrator: " + sendid[2]+"\n")), j)
                    chatMsg.insert(END, "msg sent successfully\n")
        else:
            chatMsg.insert(END,"this booker is offline\n")


def kickout():
    bookerToKick = kickEntry.get()
    if booker["admin"] is None:
        CtrlMsg.insert(END, "You haven't entered a district, please enter one first.\n")
    else:
        if bookerToKick in booker.keys():
            reString = "You have been kicked out by Administrator!"

            for j in bookerips.keys():
                if bookerips[j] == bookerToKick:
                    break
            adTobooker(reString, j)
            #将该用户移除
            del booker[bookerToKick]
            #通知在该行政区里的所有人
            for j in booker.keys():
                if booker[j]==booker["admin"]:
                    for k in bookerips.keys():
                        if bookerips[k] ==j:
                            s1="booker:"+bookerToKick+"has been kicked out\n"
                            adTobooker(s1,k)

            CtrlMsg.insert(END, "booker has been kicked out successfully\n")
        else:
            CtrlMsg.insert(END, "booker doesn't exist!\n")

window = Tk()
window.title('Free Booking')
window.geometry('960x700')
window.resizable(width=True, height=True)

# Control Area
CtrlArea = Frame(relief="sunken", bg='#fafafa')
CtrlArea.place(relx=0.01, rely=0.01, relwidth=0.7, relheight=0.98)

caLabel = Label(CtrlArea, text="Control Area", font='Arial -%d' % 20, bg='#fafafa')
caLabel.place(relx=0.2, rely=0.01, relwidth=0.6, relheight=0.05)

CtrlMsg = Text(CtrlArea, font='等线 -%d' % 16)
CtrlMsg.place(relx=0.02, rely=0.07, relwidth=0.96, relheight=0.25)


# start server
startButton = Button(CtrlArea, text="服务端登陆", font='等线 -%d' % 15, activebackground='Violet',command=AdLogin)
startButton.place(relx=0.05, rely=0.89, relwidth=0.9, relheight=0.05)

# show districts
listallButton = Button(CtrlArea, text="列出所有行政区情况", font='等线 -%d' % 15, activebackground='Violet',command=listdistricts)
listallButton.place(relx=0.05, rely=0.8, relwidth=0.9, relheight=0.05)
addEntry = Entry(CtrlArea, font='等线 -%d' % 22)
addEntry.place(relx=0.3, rely=0.66, relwidth=0.55, relheight=0.05)
addButton = Button(CtrlArea, text="添加行政区：", font='等线 -%d' % 15, command=addistrict)
addButton.place(relx=0.05, rely=0.66, relwidth=0.2, relheight=0.05)

deleteEntry = Entry(CtrlArea, font='等线 -%d' % 22)
deleteEntry.place(relx=0.3, rely=0.73, relwidth=0.55, relheight=0.05)
deleteButton = Button(CtrlArea, text="删除行政区：", font='等线 -%d' % 15, command=deleteistrict)
deleteButton.place(relx=0.05, rely=0.73, relwidth=0.2, relheight=0.05)

# msg Area
chatArea = Frame(relief="sunken", bg='#fafafa')
chatArea.place(relx=0.6, rely=0.01, relwidth=0.5, relheight=0.98)

chatLabel = Label(chatArea, text="Messages", font='Arial -%d' % 20, bg='#fafafa')
chatLabel.place(relx=0.1, rely=0.01, relwidth=0.7, relheight=0.05)

chatMsg = Text(chatArea, font='等线 -%d' % 16)
chatMsg.place(relx=0.02, rely=0.07, relwidth=0.96, relheight=0.73)

sendLabel = Label(chatArea, text="Please enter: [bookerID] message", font='等线 -%d' % 20, bg='#fafafa')
sendLabel.place(relx=0.02, rely=0.8, relwidth=0.7, relheight=0.05)

sendMsg = Entry(chatArea, font='等线 -%d' % 16)
sendMsg.place(relx=0.02, rely=0.85, relwidth=0.53, relheight=0.1)

sendButton = Button(chatArea, text='Send', font='等线 -%d' % 20, command=send)
sendButton.place(relx=0.60, rely=0.85, relwidth=0.15, relheight=0.1)

enterEntry = Entry(CtrlArea, font='等线 -%d' % 22)
enterEntry.place(relx=0.3, rely=0.39, relwidth=0.55, relheight=0.05)
enterButton = Button(CtrlArea, text="进入行政区:", font='等线 -%d' % 15, command=enterdistrict)
enterButton.place(relx=0.05, rely=0.39, relwidth=0.2, relheight=0.05)

listButton = Button(CtrlArea, text="list", font='等线 -%d' % 15, command=listdisstatus)
listButton.place(relx=0.05, rely=0.49, relwidth=0.2, relheight=0.05)

openButton = Button(CtrlArea, text="open new round", font='等线 -%d' % 15, command=openround)
openButton.place(relx=0.26, rely=0.49, relwidth=0.2, relheight=0.05)

handButton = Button(CtrlArea, text="handout", font='等线 -%d' % 15, command=handout)
handButton.place(relx=0.47, rely=0.49, relwidth=0.2, relheight=0.05)

leaveButton = Button(CtrlArea, text="leave", font='等线 -%d' % 15, command=leavedis)
leaveButton.place(relx=0.68, rely=0.49, relwidth=0.2, relheight=0.05)


#  kick out booker
kickEntry = Entry(CtrlArea, font='等线 -%d' % 22)
kickEntry.place(relx=0.3, rely=0.59, relwidth=0.55, relheight=0.05)
kickButton = Button(CtrlArea, text="kick out:", font='等线 -%d' % 15, command=kickout)
kickButton.place(relx=0.05, rely=0.59, relwidth=0.2, relheight=0.05)

chatMsg.insert(END, "Messages from bookers will shown here\n")
window.mainloop()
