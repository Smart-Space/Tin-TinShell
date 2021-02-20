# -*- coding: utf-8 -*-
'''
Tin的可视化shell工具。专用格式：*.tinc
'''
from tkinter import Tcl,Tk,Frame,scrolledtext,Entry,Text,Label,Canvas,Toplevel
from tkinter.simpledialog import askstring
from tk_tools import groups
from tkinter.ttk import Button
import tkinter as tk
from tkinter import ttk
from tkinter import tix
from PIL import Image,ImageTk
from sys import argv
import threading
import multiprocessing
import os
import sys
import re
import base64
import time
import datetime
import subprocess
import requests
from tempfile import NamedTemporaryFile
from Upgrader import find_up
import win32gui
import ctypes
TinPath=os.path.split(os.path.abspath(argv[0]))[0]
user32=ctypes.windll.user32

version='2.2.9'#working---
#os.environ["CUDA_VISIBLE_DEVICES"] = "0"

#返回值类型
ReWord={
    'None':0,#过
    'Str':1,#返回并显示
    'Error':2,#错误
    'Nstr':3,#返回但不显示，区别None
}

glo={'TinPath':TinPath,#本文件目录
     'Tinc':TinPath+'\\data\\tinc\\',#tinc额外目录
     'ABOUT':'TinShell is for developers of TinGroup',#基本信息
     'returnword':'NONE',#函数返回值
}#全局变量表

list_glo={}#tinc列表格式变量表

dict_glo={}#tinc字典格式变量表

function={}#函数字典

uidict={}

def tin_msg(text):#转义Tin的特殊字符
    text=text.replace('@SEM@',';')#Semicolon, @SEM@->;
    text=text.replace('@VEB@','|')#Vertical bar, @VEB@->|
    return text


class myStdout():	# 重定向类
    def startout(self):#TinShell输出
    	# 将其备份
        self.stdoutbak = sys.stdout		
        self.stderrbak = sys.stderr
        # 重定向
        sys.stdout = self
        sys.stderr = self

    def write(self, info):
        # info信息即标准输出sys.stdout和sys.stderr接收到的输出信息
        output(info)

    def restoreStd(self):
        # 恢复标准输出
        sys.stdout = self.stdoutbak
        sys.stderr = self.stderrbak


def newinput(ask:str):
    return askstring('TinShell > input',ask,ico=TinPath+'\\Tin.ico')
input=newinput


def _addword(obj):
    word=''
    for i in obj:
        if i in glo.keys():
            word=word+glo[i]
        else:
            word=word+i
    return [word,'Nstr']
def _cmd(obj):
    for i in obj:
        call=subprocess.Popen(i,shell=True,stdout=subprocess.PIPE)
        out,err=call.communicate()
        if call.returncode:
            return['\nthe error code is returned>> {}'.format(i),'Error']
        for line in out.splitlines():
            output(line.decode('gbk')+'\n')
            text.update()
            text.see('end')
    return ['none','None']
def _calc(obj):
    if len(obj)!=1:
        return ['\n该命令只能计算一个数学算是','Error']
    try:
        r=str(eval(obj[0]))
    except Exception as err:
        return [str(err),'Error']
    return [r,'Nstr']
def _date(obj):
    dateframe=groups.Calendar(text)
    write('\n')
    text.window_create('end',window=dateframe)
    now_time=datetime.datetime.now().strftime('%Y-%m-%d')
    return [now_time,'Nstr']
def _dict(obj):
    if len(obj)<=1:
        return ['dict函数至少要有两个参数：字典名|映射1...','Error']
    num=1
    dict_glo[obj[0]]={}
    for i in obj[1:]:
        try:
            key,val=re.findall('^(.*?)[ ]{0,}=(.*)$',i)[0]
        except:
            return ['dict函数的第 '+str(num)+' 个 键-值 不符合字典规范，应为：[键]=[值]','Error']
        dict_glo[obj[0]][key]=val
        num+=1
    return ['none','None']
def _eval(obj):
    newobj=''
    for i in obj:
        newobj=newobj+i+'|'
    StartCode(newobj[:-1].split('%'))
    return ['none','None']
def _evalfile(obj):
    if len(obj)!=1:
        return ['\nevalfile [file] 只允许指定文件路径','Error']
    try:
        with open(obj[0],mode='r',encoding='utf-8') as f:
            word=f.read().split('\n')
    except:
        if not os.path.exists(obj[0]):
            return['\n不能存在文件：'+obj[0],'Error']
        return ['\n文件不是utf-8格式 OR 读取错误（已被打开锁定）','Error']
    StartCode(word)
    return ['none','None']
def _exit(obj):
    global q
    q=True
    return ['\nexit TinShell','Str']
def _funcname(obj):
    if len(obj)!=2:
        return ['\nfuncname必须用两个参数，funcname[原函数名|新函数名]','Error']
    funstr=function[obj[0]]
    del function[obj[0]]
    function[obj[1]]=funstr
    return ['none','None']
def _function(obj):
    if obj==['']:
        return ['\n'+str(function.keys()),'Str']
    else:
        word=''
        for i in obj:
            if i in function.keys():
                word=word+i+'   ::True'+'\n'
            else:
                word=word+i+'   ::False'+'\n'
        return ['\n'+word,'Str']
def _github(obj):
    return ['\n复制以下地址并访问，参与TinShell的完善\nhttps://github.com/Smart-Space/Tin-TinShell','Str']
def _help(obj):
    helpt=open(TinPath+'\\shell帮助文档.txt',encoding='utf-8').read()
    write(helpt)
    return ['none','None']
def _if(obj):
    if len(obj)<2 or len(obj)>3:
        return ['\n函数：if[条件|函数(|参数)]，至少要有可判断的字符条件和执行的函数，最多3个参数','Error']
    go=False
    try:
        if eval(obj[0]):
            go=True
    except Exception as err:
        return ['\n条件不能被判断：'+str(err),'Error']
    if len(obj)==2:
        if go==True:
            StartCode([obj[1]+'[]'])
    elif len(obj)==3:
        if go==True:
            args=''
            for i in obj[2].replace('、',',').split(','):
                args=args+i+'|'
            StartCode([obj[1]+'['+args[:-1]+']'])
    return ['none','None']
def _input(obj):
    if len(obj)<2 or len(obj)>3:
        return['\ninput [title|ask[|word]]至少需要两个参数，即标题和提示输入内容']
    mi=obj[2] if len(obj)==3 else ''
    a=askstring(obj[0],obj[1],initialvalue=mi,ico=TinPath+'\\Tin.ico')
    if a!=None:
        return[a,'Nstr']
    else:
        return['None','Nstr']
def _list(obj):
    if len(obj)<=1:
        return['\n建立列表必须要两个以及以上的参数，列表名、列表内容...','Error']
    listname=obj[0]
    list_glo[listname]=obj[1:]
    return ['none','None']
def _newver(obj):
    newver=find_up()
    if newver==0:
        return ['\n网络状态异常，无法建立远程连接。请检查网络','Error']
    return [newver,'Nstr']
def _pass(obj):
    return ['pass','None']
def _print(obj):
    word=''
    for i in obj:
        if i in glo.keys():
            word=word+glo[i]+' '
        else:
            word=word+i+' '
    return ['\n'+word.replace('\\n','\n'),'Str']
def _py_eval(obj):
    codes=''
    for i in obj:
        codes=codes+i+'\n'
    try:
        mystd.startout()
        exec(codes)
        mystd.restoreStd()
    except Exception as err:
        return ['\npy_eval PYTHON-ERROR\n'+str(err)+'\n','Error']
    return ['none','None']
def _pystr(obj):
    if len(obj)!=1:
        return ['\nfrom tinc str to python str, you can only change one word','Error']
    rew='"'+obj[0]+'"'
    return [rew,'Nstr']
def _readfile(obj):
    if len(obj) not in [1,2]:#文件|[编码]
            return ['\nreadfile [file|[type]] 至少要有文本参数','Error']
    if len(obj)==1:
        opentype='utf-8'
    else:
        opentype=obj[1]
    try:
        with open(obj[0],mode='r',encoding=opentype) as f:
            word=f.read()
    except:
        return ['\n文件打开编码错误：<'+opentype+'> OR 文件不存在','Error']
    return [word.replace('\n','\\n'),'Nstr']
def _require(obj):
    if len(obj)!=1 or obj[0]=='':
        return ['require [tinc_file] 只接受一个参数','Error']
    tincfile=glo['Tinc']+obj[0]+'.tinc'
    if not os.path.exists(tincfile):
        return['\nNo model named <'+tincfile+'>','Error']
    with open(tincfile,mode='r',encoding='utf-8') as f:
        codes=f.read().split('\n')
    StartCode(codes)
    return ['none','None']
def _set(obj):
    if len(obj)!=2:
        return ['\nset [chr|valua] 只有两个参数','Error']
    glo[obj[0]]=obj[1]
    return ['none','None']
def _stop(obj):
    if len(obj)!=1:
        return ['\nstop [time] 只接受一个参数，即暂停的时间','Error']
    try:
        t=float(obj[0])
        if t<=0:
            raise NumError('it is not allowed by time function')
    except:
        return ['\nstop [time] 的参数必须是正数']
    time.sleep(t)
    return ['none','None']
def _time(obj):
    now=time.strftime('%H : %M : %S',time.localtime())
    return [now,'Nstr']
def _tinpaint(obj):
    tinstr='Print Tin Mark from these>\n'
    for i in obj:
        tinstr=tinstr+i+'\n'
    if TinReader==True:
        tinfun(obj)
        return ['none','None']
    return [tinstr,'Str']
def _ver(obj):
    return [version,'Str']
def _window(obj):
    inframe=Frame(text,width=1170,height=520)
    write('\n')
    text.window_create('end',window=inframe)
    text.update()
    hid=inframe.winfo_id()
    for i in obj:
        try:
            cid=int(i)
        except:
            return ['\n嵌入窗口需要窗口句柄（十进制）','Error']
        user32.SetParent(cid,hid)
    return ['none','None']
def _writefile(obj):
    if len(obj)!=4:
        return['\nwritefile [文件|写入内容|写入模式|写入编码] 函数的参数必须是四个全部注入','Error']
    f=obj[0]
    w=obj[1]
    c=obj[2]
    d=obj[3]
    if d not in ['w','a']:
        return['\nwritefile函数的写入模式必须是 w（重写）或 a（追加）','Error']
    with open(f,encoding=c,mode=d) as fi:
        fi.write(w.replace('\\n','\n'))
    return ['None','None']
oralfunc={'addword':_addword,
          'cmd':_cmd,'calc':_calc,
          'date':_date,'dict':_dict,
          'eval':_eval,'evalfile':_evalfile,'exit':_exit,
          'funcname':_funcname,'function':_function,
          'github':_github,
          'help':_help,
          'if':_if,'input':_input,
          'list':_list,
          'newver':_newver,
          'pass':_pass,'print':_print,'py_eval':_py_eval,'pystr':_pystr,
          'readfile':_readfile,'require':_require,
          'set':_set,'stop':_stop,
          'time':_time,'tinpaint':_tinpaint,
          'ver':_ver,
          'window':_window,'writefile':_writefile,
}
mystd=myStdout()#定向输出TinShell

def GoCode(p,obj):
    #一般参数返回值格式为：[返回值,类型]
    global q
    q=False
    if p[0]=='%':#先判断是否使用外部库
        path,fun=re.findall('^%(.*)[\\\\|/](.*)$',p)[0]
        funsfile=glo['Tinc']+path+'.tinc'
        if not os.path.exists(funsfile):
            return ['\nThere is no file named '+funsfile,'Error']
        with open(funsfile,mode='r',encoding='utf-8') as f:
            codes=f.read()
        try:#使用正则表达式匹配函数命令集，避免导入过多函数
            funcode=re.findall('(\$[ ]{0,}'+fun+'[ ]{0,}\[.*?\][ ]{0,}\{\n.*?\n\})',codes,re.S)[0]
            word=funcode.split('\n')
        except:
            return ['\nThere is not function named '+fun+' in '+funsfile,'Error']
        #GoCode('evalfile',[funsfile])#-在requair [file]使用
        StartCode(word)
        #print(function.keys())
        p=fun
    else:
        fun=None
    if p in oralfunc.keys():#原生命令
        func=oralfunc[p]
        result=func(obj)
        return result
    else:
        if p not in function.keys():#是否有函数
            return ['\nno command>>> '+p+'\n','Error']
        args,codes=function[p]
        if len(args)!=len(obj) and (len(args)!=0 and obj[0]==''):
            return ['\nargs are:  '+str(args)+'\nbut gived: '+str(obj)+'\n','Error']
        new_args={}#参数字典
        for o,n in zip(args,obj):
            new_args[o]=n
        new_codes=[]
        for i in codes:
            for w in new_args.keys():
                i=i.replace(w,new_args[w])
            new_codes.append(i)
        #print(str(new_codes))
        StartCode(new_codes)
        if fun!=None:
            del function[fun]#删除导入函数，避免占内存
        return [glo['returnword'],'Nstr']#函数返回值通过set [returnword|chr] 修改


def getToken(code):
    u=re.findall('^(.*?)[ ]{0,}\[(.*?)\]$',code)[0]
    if u[0][0]==' ':
        raise TincError('no command')
    return u

def StartCode(us_list):
    line_command=False#多行命令，用于赋值
    line_return=[]
    command=''#多行命令的初始命令
    fun_command=False#函数开头
    fun_arglist=[]#参数
    fun_go=[]#函数命令列表
    for us in us_list:
        if us=='':
            write('\n>>> ')
            text.update()
            text.see('end')
            continue
        if us[0]=='/':
            continue
        #先决判断，是否函数定义、多行显示
        #函数定义-working--
        if us[0]=='$' and us[-1]=='{':
            fun_command=True
            try:
                u=re.findall('^\$[ ]{0,}(.*?)[ ]{0,}\[(.*)\][ ]{0,}{$',us)[0]
            except Exception as err:
                error('\nTINSHELL can\'t read this function in a right way\ntry>>>$ function_name [args...]{\n')
                return
            if len(u)==0:
                error('\nTINSHELL can\'t read this function in a right way\ntry>>>$ function_name [args...]{\n')
                return
            fun,args=u[0],u[1]
            if len(args)==0:
                continue
            for i in args.split('|'):
                if (i[0] and i[-1])=='%':
                    fun_arglist.append(i)
                else:
                    error('\n<'+i+'>\nTINSHELL can\'t read this arg of the function\nit should be %name%\n')
                    return
            continue
        if us=='}':#函数结束
            function[fun]=[fun_arglist,fun_go]
            fun_command=False
            fun_arglist=[]
            fun_go=[]
            continue
        if fun_command==True:
            fun_go.append(us)
            continue
        #多行显示
        if us[-1]=='[':
            line_command=True
            command=us
            continue
        if us==']':
            for i in line_return:
                command=command+i+'|'
            us=command[:-1]+']'#整合命令
            line_command=False
            line_return=[]
            command=''
        if line_command==True:
            #print('us is '+us)
            try:
                u=getToken(us)
                parent=u[0]
                objlist=[]
                obj=u[1].split('|')
                for i in obj:
                    if i in glo.keys():
                        objlist.append(glo[i])
                    else:
                        objlist.append(tin_msg(i))
                result,ty=GoCode(parent,objlist)
                #print('result is '+result)
                if ty=='Error':#抛出错误
                    error('\n命令语句内出错\n'+us+'\n'+result)
                else:
                    line_return.append(result)
            except Exception as err:
                line_return.append(us)
            continue
        #开始
        if us[0]=='#':
            continue
        try:
            u=getToken(us)
            #print(u)
        except:
            error('{}\nTINSHELL can\'t read this command. It should be "command [arg...]"\n'.format(us))
            write('>>> ')
            text.see('end')
            continue
        if len(u)==0:
            error('{}\nTINSHELL can\'t read this command. It should be "command [arg...]"\n'.format(us))
        else:
            parent=u[0]
            objlist=[]
            obj=u[1].split('|')
            for i in obj:
                if i in glo.keys():
                    objlist.append(glo[i])
                else:
                    objlist.append(tin_msg(i))
            result,ty=GoCode(parent,objlist)
            #处理返回值结果：[返回值(result),类型(ty)]
            if ReWord[ty] in [0,3]:#空
                pass
            elif ReWord[ty]==1:#字符
                output(result)
            elif ReWord[ty]==2:#错误
                error('\n错误命令：'+us+'\n')
                error(result)
            write('\n')
        write('\n>>> ')
        text.update()
        text.see('end')
        if q==True:
            exit_window()

main_option=''#多行命令名称
option=[]#多行参数
more_option=False
def get_call(event):
    global main_option,option,more_option
    us=user.get()
    if len(us)==0:
        return
    if us[-1]=='[':
        main_option=us
        write(us+'\n···· ')
        more_option=True
        user.delete(0,'end')
        text.update()
        text.see('end')
        return
    if more_option==True and us==']':
        us=main_option
        option.insert(0,us)
        option.append(']')
        write(']\n')
        user.delete(0,'end')
        StartCode(option)
        main_option=''
        option=[]
        more_option=False
        return
    if more_option==True:
        option.append(us)
        write(us+'\n···· ')
        user.delete(0,'end')
        text.update()
        text.see('end')
        return
    write(us+'\n')
    user.delete(0,'end')
    StartCode([us])


def output(*word):
    for i in word:
        text['state']='normal'
        text.insert('end',i,'output')
        text['state']='disabled'
def error(*word):
    for i in word:
        text['state']='normal'
        text.insert('end',i,'error')
        text['state']='disabled'
def write(*word):
    for i in word:
        text['state']='normal'
        text.insert('end',i,'shell')
        text['state']='disabled'
def exit_window():
    root.destroy()
    if TinOut==True:
        sys.exit(0)
TinOut=False

def go_test(event):#专用测试
    StartCode(['evalfile ['+TinPath+'\\data\\tinc\\test.tinc'+']'])


def main(Tin='',isexit=False,code=[]):
    global root,user,text,tinfun,TinReader,TinOut
    if Tin!='':
        tinfun=Tin
        TinReader=True
    else:
        tinfun=''
        TinReader=False
    if isexit==True:
        TinOut=True
    root=Toplevel()
    if TinReader==True:
        root.withdraw()
    sw = root.winfo_screenwidth()
    #得到屏幕宽度
    sh = root.winfo_screenheight()
    #得到屏幕高度
    root.title('Tin-shell')
    root['background']='grey'
    root.geometry("1200x625+%d+%d" % ((sw-1200)/2,(sh-625)/2))
    root.resizable(0,0)
    root.protocol('WM_DELETE_WINDOW',exit_window)
    root.iconbitmap(TinPath+'\\Tin.ico')

    user=Entry(root,font=('微软雅黑',14),insertbackground='lightblue',bg='black',fg='lightblue',insertwidth=1)
    user.bind('<Control-g>',go_test)#测试命令
    user.place(x=0,y=0,relwidth=1,height=26)
    user.bind('<Return>',get_call)
    text=scrolledtext.ScrolledText(root,font=('楷体',14),bg='black')
    text.place(x=0,y=29,relwidth=1,height=596)
    text.tag_configure('error',foreground='red')
    text.tag_configure('shell',foreground='orange')
    text.tag_configure('output',foreground='lightblue',font='微软雅黑')
    text.insert('end',''' __________________     ___     ____            ___  writen by Smart-Space
/_________________/    /__/    /    \          /  /  for creaters for Tin
       /   /          ___     /  /\  \        /  /   to control Tin-units
      /   /          /  /    /  /  \  \      /  /    =====================
     /   /          /  /    /  /    \  \    /  /     The same as using Tin
    /   /          /  /    /  /      \  \  /  /      as a poster. Also can
   /   /          /  /    /  /        \  \/  /       oprate the exefile in
  /___/          /__/    /__/          \____/        an easy way.
[version|TinShell-{}][By|Smart-Space 🐲][filetype|*.tinc][language|TinCode]\n\n'''.format(version),'shell')
    text.insert('end','>>> ','shell')
    text['state']='disabled'
    if TinReader==False:
        root.mainloop()
    else:
        StartCode(code)

TinReader=False#默认在命令行中渲染tin
if __name__=='__main__':
    main(isexit=True)