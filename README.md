# switch_ssh_telnet
#本程序用于批量SSH登录或telnet登录交换机，并批量执行命令。

ip_config.xlsx 为IP配置文件，共有四列
	ip_number    序号
	ip_addr      登录IP地址
	ip_user      登录用户名
	ip_password  登录密码    登录密码如果为全数字，请在前加’ 转化为文本格式。
	
default.conf   命令配置文件 其中有ssh和telnet 两种登录方式执行的命令
     cmd = ls，pwd     命令可以写多条，但需要用,(逗号)分隔

注意：
	使用telnet登录时，
	华为交换机，第一条命令必须为screen-length 0 temporary，
	思科交换机第一条命令必须为 terminal length 0,
	其他交换机的请查询手册。防止more分屏显示
	
log.log 为日志文件，登录出现的错误信息将记录在日志文件中


/result 文件夹为结果存放文件，在每个交换机上执行的命令结果，将以IP.txt的形式保存。
