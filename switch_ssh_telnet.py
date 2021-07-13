#配置文件 ip_config.xlsx  记录ip地址及用户名密码
##配置文件 default.conf  执行的命令
# 生成命令执行后获取的文件，以登录   ./result/IP.txt 命名
# 日志文件 ./log.log命名

#基础模块
#1、SSH登录 
#2、SSH执行命令
#3、telnet登录
#4、telnet执行命令
#5、配置文件获取
#6、日志写入
#7、命令执行结果写入


import xlrd
import os,sys
import logging
import telnetlib,paramiko
import time
from multiprocessing import Pool
import configparser


def readexcel(excelname):
    '''读取配置文件
       参数: 
        ename       excel文件名称
        ip_addr     登录IP地址
        ip_user     登录用户名
        ip_name     登录密码
    '''
    workbook = xlrd.open_workbook(excelname)
    sheet1 = workbook.sheet_by_index(0)
    replacedata = []
    key_list = sheet1.row_values(0)
    for j in range(1,sheet1.nrows):
        replacedata_dict = {}
        for i in range(len(key_list)):
            replacedata_dict[key_list[i]] = str(sheet1.cell(j,i).value)
        replacedata.append(replacedata_dict)
    return replacedata

def readconfig(configname):
    '''读取default.conf
    '''
    if os.path.exists(configname):
        config = configparser.RawConfigParser()
        config.read(configname)
        ssh_cmd = config.get('ssh',"cmd").split(",")
        #print(ssh_cmd[0])
        telnet_cmd = config.get("telnet","cmd").split(",")
        #print(telnet_cmd)
        return ssh_cmd,telnet_cmd
    else:
        logging.warning('%s 配置文件不存在' %configname)
        sys.exit()

def log_w(warnning):
    #创建日志文件
    print(warnning+'\n')
    log_file = open('log.log','a',encoding='utf-8')
    log_str = "%s ---> %s \n " % (Time_now(), warnning)
    log_file.write(log_str+'\n')
    


def result_w(result_name,string):
    #创建结果文件
    result_file=open('./result/'+result_name+'.txt','a',encoding='utf-8')
    result_file.write(string+'\n')
    #print('结果：\n %s' %string)

def Time_now():
    time_now = time.localtime()
    date_now = time.strftime('%Y-%m-%d %H:%M:%S', time_now)
    #print(date_now)
    return date_now


class Telnet_Client():
    def __init__(self,):
        self.tn = telnetlib.Telnet()

    def login_telnet(self,ip_addr,ip_user,ip_passwd):
        '''telnet登录
            登录后获取结果，
        '''
        try:
            ip_addr=ip_addr.strip()
            ip_user=ip_user.strip()
            ip_passwd=ip_passwd.strip()
            #print(ip_addr,ip_user,ip_passwd)
            self.tn.open(ip_addr,port=23)
            # 等待login出现后输入用户名，最多等待10秒
            self.tn.read_until(b'Username: ',timeout=3)
            self.tn.write(ip_user.encode('ascii') + b'\n')
            # 等待Password出现后输入用户名，最多等待10秒
            self.tn.read_until(b'Password: ',timeout=3)
            self.tn.write(ip_passwd.encode('ascii') + b'\n')
            # 延时两秒再收取返回结果，给服务端足够响应时间
            time.sleep(2)
            # 获取登录结果
            # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
            command_result = self.tn.read_very_eager().decode('ascii')
            if 'Login failed' not in command_result:
                log_w('%s telnet登录成功'%ip_addr)
                #logging.warning('%s telnet登录成功'%ip_addr)
                return command_result
            else:
                log_w('%s telnet登录失败，用户名或密码错误'%ip_addr)
                #logging.warning('%s telnet登录失败，用户名或密码错误'%ip_addr)
                return 0
        except:
            log_w('%s 网络连接失败 ' %ip_addr)
            logging.warning('%s 网络连接失败 ' %ip_addr)
            return 0

    def telnet_cmd(self,ip_addr,command):
        '''执行telnet命令
        '''
        #执行命令
        self.tn.write(command.encode('ascii')+b'\n')
        time.sleep(2)
        #获取结果
        command_result = self.tn.read_very_eager().decode('ascii')
        #写入执行结果写入文件
        result_w(ip_addr,command_result)
        #logging.warning('命令执行结果：\n%s' % command_result)
        return command_result
    
    def logout_telnet(self):
        self.tn.close()

    
class SSH_Client():
    def __init__(self):
        self.sh = paramiko.SSHClient()
        self.sh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    
    
    def login_ssh(self,ip_addr,ip_user,ip_passwd):
        """ ssh登录
        """
        try:
            #ip_addr=ip_addr.encode('utf-8').strip()
            ip_user=ip_user.encode('utf-8').strip()
            ip_passwd=ip_passwd.encode('utf-8').strip()
            command_result=self.sh.connect(hostname = ip_addr,port = 22,username = ip_user,password = ip_passwd,allow_agent=False,look_for_keys=False)
            return command_result
        except :
            log_w('%s 网络连接失败 ' %ip_addr)
            logging.warning('%s 网络连接失败 ' %ip_addr)
            return 0
        
        
    
    def ssh_cmd(self,ip_addr,command):
        """ssh 执行命令 结果写入日志"""
        stdin,stdout,stderr=self.sh.exec_command(command)
        result = stdout.read().decode('utf-8')
        #result_w(ip_addr,stdin.read().decode('utf-8'))
        result_w(ip_addr,result)
        #log_w(stderr.read().decode('utf-8'))

    def logout_ssh(self):
        self.sh.close()




if __name__=='__main__':

    #读取IP文件
    excelname = "ip_config.xlsx"
    #filePath = os.path.join(os.getcwd(), excelname)
    # if getattr(sys, 'frozen', False):
    #     application_path = os.path.dirname(sys.executable)
    # elif __file__:
    #     application_path = os.path.dirname(__file__)
    # filePath = os.path.join(application_path, excelname)
    readexcel_list=readexcel(excelname)

    #读取命令配置文件
    cmdname = "default.conf"
    #filePath = os.path.join(sys.path[0], cmdname)
    cmd_config=readconfig(cmdname)
    #cmd_config[0] 为ssh命令
    #cmd_config[1] 为telnet命令

    change = input('请选择telnet或ssh方式登录，请输入telnet或ssh：').strip()
    if change == 'telnet':
        #print('telnet')
        #telnet方式登录并执行命令
        for readdata in readexcel_list:
            ip_number=readdata['ip_number']
            ip_addr=readdata['ip_addr']
            ip_user=readdata['ip_user']
            ip_passwd=readdata['ip_passwd']
            print(ip_number+' ---- '+ip_addr)
            #print(ip_user+':'+ip_passwd)
            telnet_login= Telnet_Client()
            telnet_flag=telnet_login.login_telnet(ip_addr,ip_user,ip_passwd)
            if telnet_flag == 0:
                log_w('%s telnet登录失败' %ip_addr)
                continue 
            else:
                log_w('%s telnet登录成功，开始执行命令>>>' %ip_addr)
                for i in range(len(cmd_config[1])):
                    telnet_login.telnet_cmd(ip_addr,cmd_config[1][i])
                #执行命令结束 断开连接
                telnet_login.logout_telnet()
    else:
        #ssh登录
        for readdata in readexcel_list:
            ip_number=readdata['ip_number']
            ip_addr=readdata['ip_addr']
            ip_user=readdata['ip_user']
            ip_passwd=readdata['ip_passwd']
            print(ip_number+' ---- '+ip_addr)
            #print(ip_user+':'+ip_passwd)
            ssh_login=SSH_Client()
            ssh_flag = ssh_login.login_ssh(ip_addr,ip_user,ip_passwd)
            if ssh_flag == 0:
                log_w('%s ssh登录失败' %ip_addr)
                continue
            else:
                log_w('%s ssh登录成功，开始执行命令 >>>>' %ip_addr)
                for i in range(len(cmd_config[0])):
                    ssh_login.ssh_cmd(ip_addr,cmd_config[0][i])
                #执行命令结束 断开连接
                ssh_login.logout_ssh()




        



