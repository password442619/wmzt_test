# -*- coding: UTF-8 -*-
import xlrd
import xlwt
#-----------
class Excel_write:
	def __init__(self, file_name, sheet_name = 'Sheet1'):
		self.file_name = file_name
		self.workbook = xlwt.Workbook(encoding='utf-8')
		self.rows={}
		self.rows[sheet_name] = 0
		self.columns={}
		self.columns[sheet_name] = 0
		self.sheet_names=[]
		self.sheet_names.append(sheet_name)
		self.data_sheet={}
		self.data_sheet[sheet_name] = self.workbook.add_sheet(sheet_name)
			
	def __del__(self):
		self.save_file()

	def save_file(self):
		self.workbook.save(self.file_name)

	def add_sheet(self, sheet_name):
		if sheet_name in self.data_sheet.keys():
			return False
		self.data_sheet[sheet_name] = self.workbook.add_sheet(sheet_name)
		self.sheet_names.append(sheet_name)
		self.rows[sheet_name] = 0
		self.columns[sheet_name] = 0
		return True
	
	def write_data(self, row_data, sheet_name = None):
		if(sheet_name == None):
			sheet_name = self.sheet_names[0]
		else:
			if sheet_name not in self.data_sheet.keys():
				return False
		for i in range(len(row_data)):
			self.data_sheet[sheet_name].write(self.rows[sheet_name], i, row_data[i])
		self.rows[sheet_name] += 1
		return True
		
'''
#demo
if __name__=="__main__":
	file='c.xls'
	ti=['name','sex','num']
	fxls=Excel_write(file)
	fxls.write_data(ti)
	fxls.add_sheet('ttt2')
	fxls.write_data(['susu','man',18])
	fxls.write_data(['susu','man',18], 'ttt2')
	#fxls.save_file()
'''
