# -*- coding: UTF-8 -*-
import os
import urllib2
import json
import time
import datetime
import write_excel#写xls数据封装
import hw_info#获取硬件信息封装

#***********************************************************************
#最大打开路数
g_max_num=30
#预估最大打开路数(不丢帧)
g_max_ablity=25

#打开视频类型
g_type='rtsp'
#跳帧参数 重点测试跳3帧和跳4帧情况
frame_skip=3
#离线文件数
g_file_num=50

#***********************************************************************
#服务器ssh信息
hostname='192.168.4.223'
hostport=22
hostuser='root'
#hostpswd='BoYun.1!2@'
hostpswd='boyun!123'

http_port=8711
video_start_url='http://%s:%d/structure/start' % (hostname,http_port)
video_sesson_list_url='http://%s:%d/session/list' %  (hostname,http_port)
video_stop_url='http://%s:%d/session/stop' %  (hostname,http_port)
server_info_url='http://%s:%d/test/info' %  (hostname,http_port)

g_session_num=0#全局session数
g_error_num=0#全局错误数
g_xxExit=False#全局退出标识

#***********************************************************************
#ipc
ipc_user='admin'
ipc_port=554
ipc_ip={}
ipc_pswd={}
#在此添加ipc信息 添加数量到达到 g_max_num 最大打开路数设置
ipc_ip[0]='192.168.2.101'
ipc_pswd[0]='aa12345678'

ipc_ip[1]='192.168.2.102'
ipc_pswd[1]='aa12345678'

ipc_ip[1]='192.168.2.103'
ipc_pswd[1]='aa12345678'

#***********************************************************************
#离线文件
#247 离线文件路径
#file_path='/data1/data_wmzt/vod/tts_%d.mp4'
#213 
file_path='/data/data_wmzt/vod/tts_%d.mp4'

#***********************************************************************

#格式化时间
def curTime(format='%Y-%m-%d %H:%M:%S'):
	now = datetime.datetime.now()
	time = now.strftime(format)
	return str(time)
#http请求
def reqUrl(requrl,reqdata=None):
	try:
		req = urllib2.Request(url=requrl, data=reqdata)
		result = urllib2.urlopen(req).read()
		return result
	except urllib2.URLError, e:
		print 'requrl error--->',str(e)
		return ''

#生成打开分析参数json
def getReqData(index):
	url={}
	url['channel_id']=str(index)
	#硬解参数 暂时不用
	#url['dxva']=bdxva
	url['frame_skip']=frame_skip
	if g_type=='rtsp':
		url['ip']=ipc_ip[index % len(ipc_ip)]
		url['username']=ipc_user
		url['port']=ipc_port
		url['password']=ipc_pswd[ index % len(ipc_pswd)]
	elif g_type=='file':
		url['file_path']=video_file.format(index % g_file_num)
		url['keep_fps']=True
		url['type']='file'
	return json.dumps(reqData)
	
#获取服务状态信息
def getServerInfo():
	info=reqUrl(server_info_url)
	if not info:
		return ''
	r=json.loads(info)
	if r['code'] == 0:
		global g_session_num
		g_session_num = r['usingct']
		return r
	else:
		return ''
#打开一路分析
def openVideo(index):
	reqData = getReqData(index)
	print reqData
	open=reqUrl(video_start_url, reqData)
	if not open:
		return False
	r=json.loads(open)
	if r['code'] == 0:
		global g_session_num
		g_session_num += 1
		return True
	else:
		global g_error_num
		g_error_num += 1
		print open
		return False
#获取测试信息
def getTestInfo(hw, xls, num=1):
	for i in range(0,num):
		pushFailCt=recvCt=avgPvcTime=avgRecoTime=0
		r=getServerInfo()
		if r and r['info']:
			for info in r['info']:
				pushFailCt+=info['pushFailCt']
				recvCt+=info['recvCt']
				avgPvcTime+=info['avgPvcTime']
				avgRecoTime+=info['avgRecoTime']
			avgPvcTime/=g_session_num
			avgRecoTime/=g_session_num
			dpp=0
			if recvCt != 0:
				dpp='%0.1f%%'%(100.0*pushFailCt/recvCt)
			if pushFailCt > 1000:
				print 'max_support session num:%d' % g_session_num
				global g_xxExit
				g_xxExit = True
		else:
			time.sleep(5)
			continue	

		xls_data=[]
		xls_data.append(curTime())
		xls_data.append('%.1f' % 1.0)
		xls_data.append(g_session_num)
	
		xls_data.append(pushFailCt)
		xls_data.append(dpp)
		xls_data.append(avgPvcTime)
		xls_data.append(avgRecoTime)

		cpu = hw.getCpuUsed()
		free,total,kk = hw.getMemUsed()
		gused,gmem = hw.getGpuUsed()	
		xls_data.append(cpu)
		xls_data.append(kk)
		xls_data.append(gused[0])
		xls_data.append(gmem[0])
		print xls_data	
		xls.write_data(xls_data)
		time.sleep(5)
#获取当前session数量下获取服务器状态信息次数
def getTestNum(max_support=30):
	if g_session_num <= max_support - 5:
		if g_session_num % 5:
			return 1
		else:
			return 10
	else:
		return 30
#停止所有session
def stopAllSession():
	session_list=reqUrl(video_sesson_list_url, '')
	if session_list:
		r=json.loads(session_list)
		if r['code']==0:
			for info in r['data']:
				stop_url={}
				stop_url['session_id']=info['session_id']
				print reqUrl(video_stop_url,json.dumps(stop_url))

if __name__=="__main__":
	#连接服务器
	hw=hw_info.GetHWInfo(hostname, hostport, hostuser, hostpswd)
	if not hw.isValid():
		exit(0)
	#创建excel(文件名，sheet名)
	xls_file_name='wmzt_report_%d_%s.xls' % (frame_skip, curTime('%Y%m%d-%H%M%S'))
	xls=write_excel.Excel_write(xls_file_name,u'结构化测试')
	#写入excel表头
	xls_title=[u'测试时间', u'解码倍速',u'线程数',u'跟踪丢帧数',u'跟踪丢帧率',u'跟踪耗时ms',u'检测耗时ms',u'CPU使用率',u'内存使用率',u'GPU使用率',u'GPU内存']
	xls.write_data(xls_title)

	#获取一次服务状态信息，同步当前session数
	getServerInfo()
	for index in range(1,1000):
		if g_error_num > 10:
			#错误次数超过10次退出
			break
		if (g_session_num >= g_max_num) or g_xxExit:
			#获取60次服务信息后退出
			getTestInfo(hw,xls,60)
			break

		#打开一路分析
		rt=openVideo(index)
		if not rt:
			print 'open video failed'
			time.sleep(5)
			continue
		getTestInfo(hw,xls,getTestNum(g_max_ablity))
	#保存excel
	xls.save_file()
	#测试完成 停止所有任务
	stopAllSession()
