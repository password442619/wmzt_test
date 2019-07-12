# -*- coding: UTF-8 -*-
import sys
import paramiko
#yum install python-paramiko python2-numpy sysstat -y
class GetHWInfo:
	def __init__(self ,hostname, port, username, password,timeout=None):
		try:
			self.client = paramiko.SSHClient()
			self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			self.client.connect(hostname, port, username, password, timeout)
		except:
			print "conn host error"
			self.client = None
			
	def __del__(self):
		if self.client:
			self.client.close()
	
	def isValid(self):
		return self.client
	
	def exec_cmd(self, cmd):
		if self.client == None:
			print "client is invalid"
			return ""
		try:
			stdin, stdout, sterr = self.client.exec_command(cmd)
			return stdout.read()
		except:
			print "client is vainvalid"
			return ""
	
	def getMemUsed(self):
		cmdMem="cat /proc/meminfo"
		mem = self.exec_cmd(cmdMem)
		if not mem:
			return ''
		mem = mem.replace(' ', '')
		mem=mem.split('\n')
		MemTotal= float(mem[0][9:-2])
		MemFree=float(mem[1][8:-2])
		Buffers=float(mem[3][8:-2])
		Cached=float(mem[4][7:-2])
		Mem=MemFree+Buffers+Cached
		neicun="%.2f%%" % (100 - Mem / MemTotal * 100)
		#print neicun
		return MemFree,MemTotal,neicun
	
	def getGpuUsed(self, isP4=False):
		cmdGpu="nvidia-smi"
		gpu = self.exec_cmd(cmdGpu)
		if not gpu:
			return ''
		gpu=gpu.split()
		gmem=[];gused=[]
		mi=0;ui=0
		for s in gpu:
			if "%" in s:
				ui=ui+1
				if isP4:#p4系列
					gused.append(s)
				else:
					if ui%2 == 0:
						gused.append(s)
					
			if "MiB" in s:
				mi=mi+1
				if mi%2 == 1:
					gmem.append(s)
		while len(gmem) > len(gused):
			del gmem[len(gmem)-1]
		return gused,gmem	
	
	def getCpuUsed(self):
		cmdCpu="iostat -c 1 2"
		cpu = self.exec_cmd(cmdCpu)
		if not cpu:
			return ''
		cpu= cpu.split('\n')
		cpu=cpu[6].split(' ')
		while '' in cpu:
			cpu.remove('')
		#%user   %nice %system %iowait  %steal   %idle
		usage="%.2f%%" % (float(100 -  float(cpu[5])))
		return usage

'''
#demo
if __name__=="__main__":
	hw=GetHWInfo('192.168.4.220',10022,'root','boyun!123')
	if not hw.isValid():
		print 'conn is invalid'
		exit(0)
	print hw.getCpuUsed()
	print hw.getMemUsed()
	#p4系列显卡 参数为True hw.getGpuUsed(True)
	print hw.getGpuUsed()
'''
