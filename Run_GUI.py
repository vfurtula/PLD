#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 10:35:01 2019

@author: Vedran Furtula
"""

import os, sys, re, time, numpy, yagmail, shutil, configparser, traceback, mss, getpass
import matplotlib.cm as cm
import numpy.polynomial.polynomial as poly
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import pyqtgraph as pg
import pyqtgraph.exporters

from PyQt5.QtCore import Qt, QObject, QThreadPool, QTimer, QRunnable, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QMainWindow, QLCDNumber, QMessageBox, QGridLayout, QHeaderView, QFileDialog, QLabel, QLineEdit, QComboBox, QFrame, QTableWidget, QTableWidgetItem, QSlider, QInputDialog, QVBoxLayout, QHBoxLayout, QApplication, QMenuBar, QPushButton, QDialog)

import Email_settings_dialog, Send_email_dialog, Instruments_dialog, Load_config_dialog
from help_dialogs import Indicator_dialog
import asyncio


class WorkerSignals(QObject):
	# Create signals to be used
	
	update_compexpro = pyqtSignal(object,object)
	update_compexpro2 = pyqtSignal(object,object)
	update_pm100usb = pyqtSignal(object,object)
	update_pass_data = pyqtSignal(object,object)
	
	update_pulse_lcd = pyqtSignal(object)
	update_pulse_lcd2 = pyqtSignal(object)
	
	start_pm100usb = pyqtSignal()
	
	warning = pyqtSignal(object)
	critical = pyqtSignal(object)
	error = pyqtSignal(tuple)
	
	finished = pyqtSignal()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
class Email_Worker(QRunnable):
	"""
	Worker thread
	:param args: Arguments to make available to the run code
	:param kwargs: Keywords arguments to make available to the run code
	"""
	def __init__(self,*argv):
		super(Email_Worker, self).__init__()
		
		# constants	
		self.subject = argv[0].subject
		self.contents = argv[0].contents
		self.emailset_str = argv[0].settings
		self.emailrec_str = argv[0].receivers
		
		self.signals = WorkerSignals()
		
		
	@pyqtSlot()
	def run(self):
		asyncio.set_event_loop(asyncio.new_event_loop())
		"""
		Initialise the runner function with passed args, kwargs.
		"""
		# Retrieve args/kwargs here; and fire processing using them
		
		try:
			self.yag = yagmail.SMTP(self.emailset_str[0], getpass.getpass( prompt=''.join(["Password for ",self.emailset_str[0],"@gmail.com:"]) ))
			self.yag.send(to=self.emailrec_str, subject=self.subject, contents=self.contents)
			self.signals.warning.emit(''.join(["E-mail is sent to ", ' and '.join([i for i in self.emailrec_str]) ," including ",str(len(self.contents[1:]))," attachment(s)!"]))
		except Exception as e:
			self.signals.critical.emit(''.join(["Could not send e-mail from the gmail account ",self.emailset_str[0],"! Try following steps:\n1. Check your internet connection. \n2. Check the account username and password.\n3. Make sure that the account accepts less secure apps.\n4. Make sure that keyring.get_password(\"system\", \"username\") works in your operating system.\n\n",str(e)]))
		else:
			pass
		finally:
			self.signals.finished.emit()
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
class PM100USB_Worker(QRunnable):
	"""
	Worker thread
	:param args: Arguments to make available to the run code
	:param kwargs: Keywords arguments to make available to the run code
	"""
	def __init__(self,*argv):
		super(PM100USB_Worker, self).__init__()
		
		# constants	
		self.end_flag=False
		
		self.inst_list = argv[0]
		self.data_pm100usb = argv[1]
		self.pulse_time = argv[2]
		self.warmup_bool = argv[3]
		self.lbl8 = argv[4]
		self.stopButton = argv[5]
		
		self.signals = WorkerSignals()
		
		
	def warmup_on(self):
		
		for tal in range(480)[::-1]:
			if self.end_flag:
				self.end_flag=False
				return
			time.sleep(1)
			
			
	def abort(self):
		
		self.end_flag=True
		
		
	def close_thread(self):
		
		self.stopButton.setText("...Closing PM100USB...")
		self.inst_list.get('PM100USB').abort()
		self.inst_list.get('PM100USB').reset()
		self.stopButton.setText("STOP")
		
		
	def get_data(self):
		
		if self.inst_list.get('COMPexPRO') and self.warmup_bool:
			self.warmup_on()
			
		self.lbl8.setText(self.data_pm100usb)
		if self.inst_list.get('COMPexPRO'):
			with open(self.data_pm100usb, "w") as thefile:
				thefile.write("Your comment line - keep this line\n") 
				thefile.write("Col 0: Elapsed time [s]\n")
				thefile.write("Col 1: PM100USB beam energy [mJ]\n")
				thefile.write("Col 2: Current pulse rate [Hz]\n")
				thefile.write("Col 3: COMPexPRO beam energy [mJ]\n")
				thefile.write("Col 4: Voltage [kV]\n\n")
				thefile.write("%s\t\t%s\t%s\t%s\t%s\n" %(tuple("".join(["Col ",str(tal)]) for tal in range(5))))
		else:
			with open(self.data_pm100usb, "w") as thefile:
				thefile.write("Your comment line - keep this line\n") 
				thefile.write("Col 0: Elapsed time [s]\n")
				thefile.write("Col 1: PM100USB beam energy [mJ]\n\n")
				thefile.write("%s\t\t%s\n" %(tuple("".join(["Col ",str(tal)]) for tal in range(2))))
			
		# Power meter settings
		self.inst_list.get('PM100USB').setTimeoutValue(10000)
		self.inst_list.get('PM100USB').set_delay(self.pulse_time)
		
		self.inst_list.get('PM100USB').setAvgCnt(30)
		print("PM100USB average count:\n\t",self.inst_list.get('PM100USB').getAvgCnt(),"counts")
		
		self.inst_list.get('PM100USB').setWavelength(248)
		print("PM100USB wavelength:\n\t",self.inst_list.get('PM100USB').getWavelength(0),"nm")
		
		self.inst_list.get('PM100USB').setEnergyRange(0.017)
		print("PM100USB power range:\n\t",self.inst_list.get('PM100USB').getEnergyRange(0),"J")
		
		pm_energy = -1
		count=0
		time_start=time.time()
		while True:
			if self.end_flag:
				self.close_thread()
				return
			
			count+=1
			pm_energy=self.inst_list.get('PM100USB').measEnergy()*self.inst_list.get('PM100USB').getAvgCnt()
			
			if self.end_flag:
				self.close_thread()
				return
			
			time_elap=time.time()-time_start
			print(''.join(["Total energy(",str(count),"): ",str(pm_energy)]))
			#print("PM100USB set avg time: ",self.inst_list.get('PM100USB').getAvgTime(0))
			#print("PM100USB min avg time: ",self.inst_list.get('PM100USB').getAvgTime(1))
			#print("PM100USB max avg time: ",self.inst_list.get('PM100USB').getAvgTime(2))
			#print("PM100USB def avg time: ",self.inst_list.get('PM100USB').getAvgTime(3))
			#print("PM100USB avg count: ",self.inst_list.get('PM100USB').getAvgCnt())
			#print("PM100USB timeout: ",self.inst_list.get('PM100USB').getTimeoutValue(),"ms")
			self.signals.update_pm100usb.emit(time_elap, pm_energy)
			
			
	@pyqtSlot()
	def run(self):
		#asyncio.set_event_loop(asyncio.new_event_loop())
		"""
		Initialise the runner function with passed args, kwargs.
		"""
		# Retrieve args/kwargs here; and fire processing using them
		
		try:
			self.get_data()
		except Exception as e:
			self.signals.warning.emit(str(e))
		else:
			pass
		finally:
			self.signals.finished.emit()  # Done
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
class COMPexPro_Worker(QRunnable):
	
	def __init__(self,*argv):
		super(COMPexPro_Worker, self).__init__()
		# constants
		self.end_flag=False
		
		self.Rsweep = argv[0]
		self.Vsweep = argv[1]
		self.timeout_str = argv[2]
		self.warmup_bool = argv[3]
		self.warmup = argv[4]
		self.trigger_str = argv[5]
		self.gasmode_str = argv[6]
		self.pulse_time = argv[7]
		
		self.data_compexpro = argv[8]
		self.timetrace_str = argv[9]
		self.inst_list = argv[10]
		self.lbl7 = argv[11]
		self.stopButton = argv[12]
		
		self.signals = WorkerSignals()
		
		
	def abort(self):
		
		self.end_flag = True
		
		
	def close_thread(self):
		
		self.stopButton.setText("...Closing COMPexPRO...")
		str_onoff = self.inst_list.get('COMPexPRO').set_opmode("OFF")
		print("Stopped, ",str_onoff)
		while str_onoff[:2]=="ON":
			str_onoff = self.inst_list.get('COMPexPRO').set_opmode("OFF")
			print("Stopped, ",str_onoff)
			
		val_str=self.inst_list.get('COMPexPRO').set_trigger("EXT")
		if val_str=="EXT":
			print("COMPexPRO trigger set to external, ",val_str)
			
		self.stopButton.setText("STOP")
			
			
	@pyqtSlot()
	def run(self):
		
		try:
			self.start_source()
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			self.signals.error.emit((exctype, value, traceback.format_exc()))
		else:
			pass
		finally:
			self.signals.finished.emit()  # Done
		
		
	def warmup_on(self):
		
		self.stopButton.setText("SKIP warm-up")
		for tal in range(480)[::-1]:
			if self.end_flag:
				self.stopButton.setEnabled(False)
				self.stopButton.setText("STOP")
				self.end_flag=False
				return
			if tal==0:
				self.warmup.setStyleSheet("color: green")
			self.warmup.setText(str(tal))
			time.sleep(1)
			
			
	def start_source(self):
		
		# COMPexPRO laser settings
		self.inst_list.get('COMPexPRO').set_opmode("SKIP")
		self.inst_list.get('COMPexPRO').set_gasmode(self.gasmode_str)
		self.inst_list.get('COMPexPRO').set_timeout(self.timeout_str)
		self.inst_list.get('COMPexPRO').set_trigger(self.trigger_str)
		self.inst_list.get('COMPexPRO').set_delay(0.25)
			
		if self.warmup_bool:
			self.warmup_on()
		
		self.lbl7.setText(self.data_compexpro)
		with open(self.data_compexpro, "w") as thefile:
			thefile.write("Your comment line - keep this line\n") 
			thefile.write("Col 0: Elapsed time [s]\nCol 1: Total counter (1000)\n")
			thefile.write("Col 2: Current pulse rate [Hz]\nCol 3: Voltage [kV]\n")
			thefile.write("Col 4: COMPexPRO beam energy [mJ]\n\n")
			thefile.write("%s\t\t%s\t%s\t%s\t%s\n" %(tuple("".join(["Col ",str(tal)]) for tal in range(5))))
			
		for rate in self.Rsweep:
			if self.end_flag:
				self.close_thread()
				return
			
			self.inst_list.get('COMPexPRO').set_reprate(str(rate))
			
			for volt in self.Vsweep:
				if self.end_flag:
					self.close_thread()
					return
				
				self.inst_list.get('COMPexPRO').set_hv(str(volt))
				
				if self.end_flag:
					self.close_thread()
					return
				
				if rate==self.Rsweep[0] and volt==self.Vsweep[0]:
					counter = self.inst_list.get('COMPexPRO').get_counter()
					totalcounter = self.inst_list.get('COMPexPRO').get_totalcounter()
					time_start=time.time()
					str_onoff = self.inst_list.get('COMPexPRO').set_opmode("ON")
					print("Pulsing, ",str_onoff)
					self.signals.start_pm100usb.emit()
					self.stopButton.setText("STOP")
					self.stopButton.setEnabled(True)
				
				self.signals.update_compexpro2.emit(volt,rate)
				
				time_start_=time.time()
				while time.time()-time_start_<self.pulse_time:
					egy = -1000
					egy = self.inst_list.get('COMPexPRO').get_energy()
					time.sleep(0.1)
					
					if self.end_flag:
						self.close_thread()
						return
					
					time_elap=time.time()-time_start
					self.signals.update_compexpro.emit(time_elap,1e-3*egy)
					self.signals.update_pulse_lcd.emit(counter)
					self.signals.update_pulse_lcd2.emit(totalcounter)
					
					time_elap=format(time_elap, "010.4f")
					egy=format(egy, "05.3f")
					
					with open(self.data_compexpro, "a") as thefile:
						thefile.write("%s\t%s\t%s\t%s\t%s\n" %(time_elap,totalcounter,rate,volt,egy))
					
					if self.end_flag:
						self.close_thread()
						return
					
		self.close_thread()
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
			
class Run_COMPexPRO(QMainWindow):
	
	def __init__(self):
		super().__init__()
		
		self.cwd = os.getcwd()
		self.load_()
		
		# Enable antialiasing for prettier plots		
		pg.setConfigOptions(antialias=True)
		self.initUI()
		
		
	def initUI(self):
		
		################### MENU BARS START ##################
		
		MyBar = QMenuBar(self)
		fileMenu = MyBar.addMenu("File")
		self.fileLoadAs = fileMenu.addAction("Config section settings")        
		self.fileLoadAs.triggered.connect(self.load_config_dialog)
		fileSavePlt = fileMenu.addAction("Save plots")
		fileSavePlt.triggered.connect(self.save_plots)
		fileSavePlt.setShortcut("Ctrl+P")
		fileSaveSet = fileMenu.addAction("Save settings")        
		fileSaveSet.triggered.connect(self.save_) # triggers closeEvent()
		fileSaveSet.setShortcut("Ctrl+S")
		self.fileClose = fileMenu.addAction("Close")        
		self.fileClose.triggered.connect(self.close) # triggers closeEvent()
		self.fileClose.setShortcut("Ctrl+X")
		
		instMenu = MyBar.addMenu("Instruments")
		self.conMode = instMenu.addAction("Load instruments")
		self.conMode.triggered.connect(self.instrumentsDialog)
		
		self.emailMenu = MyBar.addMenu("E-mail")
		self.emailSet = self.emailMenu.addAction("E-mail settings")
		self.emailSet.triggered.connect(self.email_set_dialog)
		self.emailData = self.emailMenu.addAction("E-mail data")
		self.emailData.triggered.connect(self.email_data_dialog)
		
		################### MENU BARS END ##################
		
		lbl9 = QLabel("LOAD config section:", self)
		lbl9.setStyleSheet("QWidget {color: blue}")
		self.combo5 = QComboBox(self)
		self.mylist5=self.get_scan_sections()
		self.combo5.addItems(self.mylist5)
		self.combo5.setCurrentIndex(self.mylist5.index(self.last_used_scan))
		#self.combo5.setFixedWidth(75)
		
		timeout_lbl = QLabel("Timeout", self)
		self.combo0 = QComboBox(self)
		self.mylist0=["ON","OFF"]
		self.combo0.addItems(self.mylist0)
		self.combo0.setCurrentIndex(self.mylist0.index(self.timeout_str))
		
		warmup_lbll = QLabel("Warm-up", self)
		self.combo1 = QComboBox(self)
		self.mylist1=["ON","OFF"]
		self.combo1.addItems(self.mylist1)
		self.combo1.setCurrentIndex(self.mylist1.index(self.warmup_str))
		self.warmup_bool=self.bool_(self.warmup_str)
		
		trigger_lbl = QLabel("Trigger", self)
		self.combo2 = QComboBox(self)
		self.mylist2=["INT","EXT"]
		self.combo2.addItems(self.mylist2)
		self.combo2.setCurrentIndex(self.mylist2.index(self.trigger_str))
		
		gasmode_lbl = QLabel("Gasmode", self)
		self.combo3 = QComboBox(self)
		self.mylist3=["PREMIX","SINGLE GASES"]
		self.combo3.addItems(self.mylist3)
		self.combo3.setCurrentIndex(self.mylist3.index(self.gasmode_str))
		
		self.Vsweep_lbl = QLabel("".join(["Voltage (",str(self.volt),") [kV]"]), self)
		self.VsweepEdit = QLineEdit(",".join([i for i in self.Vsweep]),self)
		self.VsweepEdit.setFixedWidth(90)
		
		self.Rsweep_lbl = QLabel("".join(["Pulse rate (",str(self.rate),") [Hz]"]), self)
		self.RsweepEdit = QLineEdit(",".join([i for i in self.Rsweep]),self)
		self.RsweepEdit.setFixedWidth(90)
		
		pulse_time_lbl = QLabel("Pulsing time [s]",self)
		self.pulsetimeEdit = QLineEdit(str(self.pulse_time),self)
		self.pulsetimeEdit.setFixedWidth(90)
		
		#####################################################
		
		self.laser_type = QLabel("",self)
		self.laser_type.setStyleSheet("color: magenta")
		laser_type_lbl = QLabel("".join(["Type of laser:"]),self)
		
		self.gas_menu = QLabel("",self)
		self.gas_menu.setStyleSheet("color: magenta")
		gas_menu_lbl = QLabel("".join(["Gas menu no:"]),self)
		
		self.gas_wl = QLabel("",self)
		self.gas_wl.setStyleSheet("color: magenta")
		gas_wl_lbl = QLabel("Gas wavelength:",self)
		
		self.gas_mix = QLabel("",self)
		self.gas_mix.setStyleSheet("color: magenta")
		gas_mix_lbl = QLabel("Gas mixture:",self)
		
		self.pulse_counter = QLabel("",self)
		self.pulse_counter.setStyleSheet("color: magenta")
		pulse_lbl1 = QLabel("Counter (10^3):",self)
		
		self.pulse_tot = QLabel("",self)
		self.pulse_tot.setStyleSheet("color: magenta")
		pulse_lbl2 = QLabel("Total counter (10^3):",self)
		
		warmup_lbl2 = QLabel("Warm-up [s]:",self)
		self.warmup = QLabel("",self)
		if self.warmup_bool:
			self.warmup.setStyleSheet("color: red")
			self.warmup.setText("480")
		else:
			self.warmup.setStyleSheet("color: green")
			self.warmup.setText("0")
		
		self.resetButton = QPushButton("Reset counter",self)
		
		#####################################################
		
		lbl4 = QLabel("STORAGE with timetrace and schroll settings:", self)
		lbl4.setStyleSheet("color: blue")
		
		filename_lbl = QLabel(''.join(["Create folder",os.sep,"file:"]),self)
		self.filenameEdit = QLineEdit(str(self.filename_str),self)
		#self.filenameEdit.setFixedWidth(140)
		
		#####################################################
		
		schroll_lbl = QLabel("Schroll pts:",self)
		self.combo4 = QComboBox(self)
		self.mylist4=["100","200","500","1000","2000"]
		self.combo4.addItems(self.mylist4)
		# initial combo settings
		self.combo4.setCurrentIndex(self.mylist4.index(str(self.schroll)))
		#self.combo4.setFixedWidth(85)
		
		#####################################################
		
		lbl5 = QLabel("EXECUTE operation settings:", self)
		lbl5.setStyleSheet("color: blue")
		
		self.startButton = QPushButton("Start source",self)
		self.stopButton = QPushButton("",self)
		if self.warmup_bool:
			self.stopButton.setText("SKIP warm-up")
		else:
			self.stopButton.setText("STOP")
		
		#####################################################
		
		self.lcd = QLCDNumber(self)
		self.lcd.setStyleSheet("color: red")
		self.lcd.setFixedHeight(50)
		self.lcd.setSegmentStyle(QLCDNumber.Flat)
		self.lcd.setNumDigits(11)
		self.lcd.display(self.timetrace_str)
		
		#####################################################
		
		lbl6 = QLabel("DATA saved to file(s):", self)
		lbl6.setStyleSheet("color: blue")
		self.lbl7 = QLabel("--", self)
		self.lbl7.setStyleSheet("color: magenta")
		self.lbl8 = QLabel("--", self)
		self.lbl8.setStyleSheet("color: red")
		
		#####################################################
		#####################################################
		#####################################################
		
		# Add all widgets		
		g1_0 = QGridLayout()
		g1_0.addWidget(MyBar,0,0)
		
		g1_1 = QGridLayout()
		g1_1.addWidget(lbl9,0,0)
		g1_1.addWidget(self.combo5,0,1)
		
		g1_2 = QGridLayout()
		g1_2.addWidget(timeout_lbl,0,0)
		g1_2.addWidget(self.combo0,1,0)
		g1_2.addWidget(warmup_lbll,0,1)
		g1_2.addWidget(self.combo1,1,1)
		g1_2.addWidget(trigger_lbl,0,2)
		g1_2.addWidget(self.combo2,1,2)
		g1_2.addWidget(gasmode_lbl,0,3)
		g1_2.addWidget(self.combo3,1,3)
		
		g1_3 = QGridLayout()
		g1_3.addWidget(self.Rsweep_lbl,0,0)
		g1_3.addWidget(self.RsweepEdit,1,0)
		g1_3.addWidget(self.Vsweep_lbl,0,1)
		g1_3.addWidget(self.VsweepEdit,1,1)
		g1_3.addWidget(pulse_time_lbl,0,2)
		g1_3.addWidget(self.pulsetimeEdit,1,2)
		
		g1_4 = QGridLayout()
		g1_4.addWidget(gas_mix_lbl,0,0)
		g1_4.addWidget(self.gas_mix,0,1)
		g1_4.addWidget(laser_type_lbl,0,2)
		g1_4.addWidget(self.laser_type,0,3)
		g1_4.addWidget(gas_menu_lbl,1,0)
		g1_4.addWidget(self.gas_menu,1,1)
		g1_4.addWidget(gas_wl_lbl,1,2)
		g1_4.addWidget(self.gas_wl,1,3)
		g1_4.addWidget(pulse_lbl1,2,0)
		g1_4.addWidget(self.pulse_counter,2,1)
		g1_4.addWidget(pulse_lbl2,2,2)
		g1_4.addWidget(self.pulse_tot,2,3)
		g1_4.addWidget(self.resetButton,3,0)
		g1_4.addWidget(warmup_lbl2,3,2)
		g1_4.addWidget(self.warmup,3,3)
		
		v1 = QVBoxLayout()
		v1.addLayout(g1_0)
		v1.addLayout(g1_1)
		v1.addLayout(g1_2)
		v1.addLayout(g1_3)
		v1.addLayout(g1_4)
		
		#####################################################
		
		g3_0 = QGridLayout()
		g3_0.addWidget(lbl4,0,0)
		
		g3_1 = QGridLayout()
		g3_1.addWidget(filename_lbl,0,0)
		g3_1.addWidget(self.filenameEdit,1,0)
		g3_1.addWidget(schroll_lbl,0,1)
		g3_1.addWidget(self.combo4,1,1)
		
		g3_2 = QGridLayout()
		g3_2.addWidget(self.lcd,0,0)
		
		v3 = QVBoxLayout()
		v3.addLayout(g3_0)
		v3.addLayout(g3_1)
		v3.addLayout(g3_2)
		
		#####################################################
		
		g5_0 = QGridLayout()
		g5_0.addWidget(lbl5,0,0)
		
		g5_1 = QGridLayout()
		g5_1.addWidget(self.startButton,0,1)
		g5_1.addWidget(self.stopButton,0,2)
		
		v5 = QVBoxLayout()
		v5.addLayout(g5_0)
		v5.addLayout(g5_1)
		
		#####################################################
		
		# add ALL groups from v1 to v6 in one vertical group v7
		v7 = QVBoxLayout()
		v7.addLayout(v1)
		v7.addLayout(v3)
		v7.addLayout(v5)
	
		#####################################################
		
		# set GRAPHS and TOOLBARS to a new vertical group vcan
		vcan0 = QGridLayout()
		win = pg.GraphicsWindow()
		vcan0.addWidget(win,0,0)
		
		# SET ALL HORIZONTAL COLUMNS TOGETHER
		hbox = QHBoxLayout()
		hbox.addLayout(v7)
		hbox.addLayout(vcan0)
		
		vbox = QVBoxLayout()
		vbox.addLayout(hbox)
		vbox.addWidget(lbl6)
		vbox.addWidget(self.lbl7)
		vbox.addWidget(self.lbl8)
		
		##############################################
		
		# INITIAL SETTINGS PLOT 1
		self.pi1 = win.addPlot()
		self.curve1=self.pi1.plot(pen="m")
		
		# create plot and add it to the figure
		self.vb1 = pg.ViewBox()
		self.curve1_1=pg.PlotCurveItem(pen="y")
		self.vb1.addItem(self.curve1_1)
		
		# connect respective axes to the plot 
		self.pi1.scene().addItem(self.vb1)
		self.pi1.getAxis("left").linkToView(self.vb1)
		self.pi1.getAxis('left').setPen('y')
		self.pi1.getAxis('right').setPen('m')
		self.vb1.setXLink(self.pi1)
		# Use automatic downsampling and clipping to reduce the drawing load
		self.pi1.setDownsampling(mode="peak")
		self.pi1.setClipToView(True)
		self.pi1.enableAutoRange()
		# Labels and titels are placed here since they change dynamically
		self.pi1.setTitle(''.join(["Current rate ",str(self.rate)," Hz, Voltage ",str(self.volt)," kV"]))
		self.pi1.setLabel("right","COMPexPRO", units="J", color="white")
		self.pi1.setLabel("left", "Voltage", units="V", color="white")
		#self.pi1.setLabel("bottom", "Elapsed time", units="s", color="white")
		self.pi1.enableAutoRange()
		
		win.nextRow()
		##############################################
		
		# INITIAL SETTINGS PLOT 2
		self.pi2 = win.addPlot()
		self.curve2=self.pi2.plot(pen="r")
		
		# create plot and add it to the figure
		self.vb2 = pg.ViewBox()
		self.curve2_1=pg.PlotCurveItem(pen="y")
		self.vb2.addItem(self.curve2_1)
		
		# connect respective axes to the plot 
		self.pi2.scene().addItem(self.vb2)
		self.pi2.getAxis("left").linkToView(self.vb2)
		self.pi2.getAxis('left').setPen('y')
		self.pi2.getAxis('right').setPen('r')
		self.vb2.setXLink(self.pi2)
		# Use automatic downsampling and clipping to reduce the drawing load
		self.pi2.setDownsampling(mode="peak")
		self.pi2.setClipToView(True)
		self.pi2.enableAutoRange()
		# Labels and titels are placed here since they change dynamically
		#self.pi2.setTitle(''.join(["Current rate ",str(self.rate)," Hz, Voltage ",str(self.volt)," kV"]))
		self.pi2.setLabel("right","PM100USB", units="J", color="white")
		self.pi2.setLabel("left", "Voltage", units="V", color="white")
		self.pi2.setLabel("bottom", "Elapsed time", units="s", color="white")
		self.pi2.enableAutoRange()
		
		
		self.inst_list = {}
		
		self.threadpool = QThreadPool()
		print("Multithreading in Run_COMPexPRO with maximum %d threads" % self.threadpool.maxThreadCount())
		
		# reacts to drop-down menus
		self.combo0.activated[str].connect(self.onActivated0)
		self.combo1.activated[str].connect(self.onActivated1)
		self.combo2.activated[str].connect(self.onActivated2)
		self.combo3.activated[str].connect(self.onActivated3)
		self.combo4.activated[str].connect(self.onActivated4)
		self.combo5.activated[str].connect(self.onActivated5)
		
		# run the main script
		self.resetButton.clicked.connect(self.set_reset)
		
		# run the main script
		self.startButton.clicked.connect(self.set_run)
		
		# cancel the script run
		self.stopButton.clicked.connect(self.set_stop)
		
		self.clear_vars_graphs()
		self.allFields(False)
		self.stopButton.setEnabled(False)
		self.startButton.setEnabled(False)
		self.fileLoadAs.setEnabled(True)
		
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.set_disconnect)
		self.timer.setSingleShot(True)
		
		##############################################
		
		self.setGeometry(30, 80, 900, 400)
		self.setWindowTitle("COMPexPRO Photon Source Controller")
		# re-adjust/minimize the size of the e-mail dialog
		# depending on the number of attachments
		#hbox1.setSizeConstraint(hbox1.SetFixedSize)
		
		w = QWidget()
		w.setLayout(vbox)
		self.setCentralWidget(w)
		self.show()
		
		
	def instrumentsDialog(self):
		
		self.Inst = Instruments_dialog.Instruments_dialog(self,self.inst_list,self.timer,self.gas_menu,self.gas_wl,self.gas_mix,self.laser_type,self.pulse_counter,self.pulse_tot,self.cwd)
		self.Inst.exec()
		
		if self.inst_list.get("COMPexPRO"):
			self.allFields(True)
		elif self.inst_list.get("PM100USB") and not self.inst_list.get("COMPexPRO"):
			self.allFields(False)
			self.combo4.setEnabled(True)
			self.filenameEdit.setEnabled(True)
		else:
			self.allFields(False)
			
		if not self.inst_list.get("COMPexPRO") and not self.inst_list.get("PM100USB"):
			self.startButton.setText("Load instrument!")
			self.startButton.setEnabled(False)
		else:
			self.startButton.setText("Scan")
			self.startButton.setEnabled(True)
			
			
	def get_scan_sections(self):
		
		mylist=[]
		for i in self.config.sections():
			if i not in ["LastScan","Instruments"]:
				mylist.extend([i])
				
		return mylist
	
	
	def initUI_(self):
		
		self.combo0.setCurrentIndex(self.mylist0.index(self.timeout_str))
		self.combo1.setCurrentIndex(self.mylist1.index(self.warmup_str))
		self.combo2.setCurrentIndex(self.mylist2.index(self.trigger_str))
		self.combo3.setCurrentIndex(self.mylist3.index(self.gasmode_str))
		self.combo4.setCurrentIndex(self.mylist4.index(str(self.schroll)))
		
		self.Rsweep_lbl.setText("".join(["Pulse rate (",str(self.rate),") [Hz]"]))
		self.RsweepEdit.setText(",".join([i for i in self.Rsweep]))
		
		self.Vsweep_lbl.setText("".join(["Voltage (",str(self.volt),") [kV]"]))
		self.VsweepEdit.setText(",".join([i for i in self.Vsweep]))
		
		self.filenameEdit.setText(self.filename_str)
		self.pulsetimeEdit.setText(str(self.pulse_time))
		
		self.mylist5=self.get_scan_sections()
		self.combo5.clear()
		self.combo5.addItems(self.mylist5)
		self.combo5.setCurrentIndex(self.mylist5.index(self.last_used_scan))
		
		
	def update_pulse_lcd(self,i):
		
		self.pulse_counter.setText(str(i))
		
		
	def update_pulse_lcd2(self,i):
		
		self.pulse_tot.setText(str(i))
		
		
	def set_reset(self):
		
		self.pulse_counter.setText(str(self.inst_list.get("COMPexPRO").set_counter_reset()))
		
		
	def set_disconnect(self):
		
		##########################################
		
		if self.inst_list.get("COMPexPRO"):
			if self.inst_list.get("COMPexPRO").is_open():
				self.inst_list.get("COMPexPRO").close()
			self.inst_list.pop('COMPexPRO', None)
				
		##########################################
		
		if self.inst_list.get("PM100USB"):
			if self.inst_list.get("PM100USB").is_open():
				self.inst_list.get("PM100USB").close()
			self.inst_list.pop('PM100USB', None)
			
		##########################################
		
		print("All ports DISCONNECTED")
		
		self.allFields(False)
		self.conMode.setEnabled(True)
		self.fileLoadAs.setEnabled(True)
		self.stopButton.setEnabled(False)
		self.startButton.setText("Load instrument!")
		self.startButton.setEnabled(False)
		
		
	def allFields(self,trueorfalse):
		
		self.combo0.setEnabled(trueorfalse)
		self.combo1.setEnabled(trueorfalse)
		self.combo2.setEnabled(trueorfalse)
		self.combo3.setEnabled(trueorfalse)
		self.combo4.setEnabled(trueorfalse)
		self.combo5.setEnabled(trueorfalse)
		
		self.RsweepEdit.setEnabled(trueorfalse)
		self.VsweepEdit.setEnabled(trueorfalse)
		
		self.filenameEdit.setEnabled(trueorfalse)
		self.pulsetimeEdit.setEnabled(trueorfalse)
		self.resetButton.setEnabled(trueorfalse)
		
		
	def onActivated0(self, text):
		
		self.timeout_str=str(text)
		
		if str(text)=="ON":
			QMessageBox.warning(self, "Message","Serial disruptions are present in ON mode. It is recommeneded to set timeout in OFF mode.")
		
	
	def bool_(self,txt):
		
		if txt=="ON":
			return True
		elif txt=="OFF":
			return False
		
	
	def onActivated1(self, text):
		
		self.warmup_str=str(text)
		self.warmup_bool=self.bool_(str(text))
		
		if self.warmup_bool:
			self.stopButton.setText("SKIP warm-up")
			self.warmup.setStyleSheet("color: red")
			self.warmup.setText("480")
		else:
			self.stopButton.setText("STOP")
			self.warmup.setStyleSheet("color: green")
			self.warmup.setText("0")
			
			
	def onActivated2(self, text):
		
		self.trigger_str=str(text)
		
		if str(text)=="EXT":
			QMessageBox.warning(self, "Message","Setting trigger to external mode requires external TTL signal for pulse triggering.")
			
			
	def onActivated3(self, text):
		
		self.gasmode_str=str(text)
		
		
	def onActivated4(self, text):
		
		self.schroll=int(text)
		
		
	def onActivated5(self, text):
		
		self.last_used_scan = str(text)
		self.config.set("LastScan", "last_used_scan", self.last_used_scan)
		with open(''.join([self.cwd,os.sep,"config.ini"]), 'w') as configfile:
			self.config.write(configfile)
			
		self.load_()
		self.initUI_()
		
		
	############################################################
	# Check input if a number, ie. digits or fractions such as 3.141
	# Source: http://www.pythoncentral.io/how-to-check-if-a-string-is-a-number-in-python-including-unicode/
	def is_number(self,s):
		try:
			float(s)
			return True
		except ValueError:
			pass

		try:
			import unicodedata
			unicodedata.numeric(s)
			return True
		except (TypeError, ValueError):
			pass
		
		return False
	
	
	def set_run(self):
		# MINIMUM REQUIREMENTS for proper run
		if not self.inst_list.get("PM100USB") and not self.inst_list.get("COMPexPRO"):
			QMessageBox.critical(self, 'Message',"No instruments connected. At least 1 instrument is required.")
			return
			
		########################################################
		
		try:
			self.pulse_time = int(self.pulsetimeEdit.text())
			if self.pulse_time<=0:
				QMessageBox.warning(self, "Message","Pulse time is a positive and a non-zero integer!")
				return
		except Exception as e:
			QMessageBox.warning(self, "Message","Pulse time is a single integer!")
			return
		
		########################################################
		
		try:
			Vsss = [float(i) for i in self.VsweepEdit.text().split(',')]
			for tals in Vsss[:2]:
				if tals<19 or tals>30:
					QMessageBox.warning(self, "Message","Applied voltage should be in the range from 19 to 30 kV.")
					return
				
			if len(Vsss)==3:
				hv = numpy.arange(10*Vsss[0],10*Vsss[1],10*Vsss[2])/10
				if hv.size==0:
					QMessageBox.warning(self, "Message","The voltage sweep list is empty! Check your start, stop, and step values.")
					return
				if hv[-1]+Vsss[2]<=30:
					hv=numpy.append(hv,hv[-1]+Vsss[2])
			elif len(Vsss)==1:
				hv = Vsss
			else:
				QMessageBox.warning(self, "Message","Enter a single voltage value or 3 voltage values (start,stop,step) separated by comma(,) to perform a voltage sweep!")
				return
			
		except Exception as e:
			QMessageBox.warning(self, "Message","All voltages should be real numbers.")
			return
		
		########################################################
		
		try:
			Rsss = [int(i) for i in self.RsweepEdit.text().split(',')]
			for tals in Rsss[:2]:
				if tals<1 or tals>50:
					QMessageBox.warning(self, "Message","The pulse rate should be in the range from 1 to 50 Hz.")
					return
				
			if len(Rsss)==3:
				rate = numpy.arange(Rsss[0],Rsss[1],Rsss[2])
				if rate.size==0:
					QMessageBox.warning(self, "Message","The pulse rate sweep list is empty! Check your start, stop, and step values.")
					return
				if rate[-1]+Rsss[2]<=50:
					rate=numpy.append(rate,rate[-1]+Rsss[2])
			elif len(Rsss)==1:
				rate = Rsss
			else:
				QMessageBox.warning(self, "Message","Enter a single pulse rate or 3 pulse rates (start,stop,step) separated by comma(,) to perform a pulse rate sweep!")
				return
			
		except Exception as e:
			QMessageBox.warning(self, "Message","The pulse rate should be an integer.")
			return
		
		self.clear_vars_graphs()
		self.allFields(False)
		self.conMode.setEnabled(False)
		self.stopButton.setEnabled(True)
		self.startButton.setEnabled(False)
		self.fileClose.setEnabled(False)
		self.fileLoadAs.setEnabled(False)
		
		#self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
		self.timer.stop()
		
		# COMPexPRO worker thread
		if self.inst_list.get('COMPexPRO'):
			# For SAVING data
			if "\\" in self.filenameEdit.text():
				self.filenameEdit.setText(self.filenameEdit.text().replace("\\",os.sep))
			if "/" in self.filenameEdit.text():
				self.filenameEdit.setText(self.filenameEdit.text().replace("/",os.sep))
				
			if not self.filenameEdit.text():
				self.filenameEdit.setText(''.join(["data",os.sep,"data"]))
			elif not os.sep in self.filenameEdit.text():
				self.filenameEdit.setText(''.join(["data", os.sep, self.filenameEdit.text()]))
			self.data_compexpro="".join([self.create_file("".join([self.filenameEdit.text(),"_COMPexPRO"])),".txt"])
			self.lbl7.setText("--")
		
			self.comp_worker = COMPexPro_Worker(rate,hv,self.timeout_str,self.warmup_bool,self.warmup,self.trigger_str, self.gasmode_str,self.pulse_time,self.data_compexpro,self.timetrace_str,self.inst_list,self.lbl7,self.stopButton)
			
			self.comp_worker.signals.update_pulse_lcd.connect(self.update_pulse_lcd)
			self.comp_worker.signals.update_pulse_lcd2.connect(self.update_pulse_lcd2)
			self.comp_worker.signals.update_compexpro.connect(self.update_compexpro)
			self.comp_worker.signals.update_compexpro2.connect(self.update_compexpro2)
			self.comp_worker.signals.start_pm100usb.connect(self.start_pm100usb)
			self.comp_worker.signals.warning.connect(self.warning)
			self.comp_worker.signals.finished.connect(self.finished)
			# Execute
			self.threadpool.start(self.comp_worker)
			
		# PM100USB worker thread
		if self.inst_list.get('PM100USB'):
			# For SAVING data
			if "\\" in self.filenameEdit.text():
				self.filenameEdit.setText(self.filenameEdit.text().replace("\\",os.sep))
			if "/" in self.filenameEdit.text():
				self.filenameEdit.setText(self.filenameEdit.text().replace("/",os.sep))
				
			if not self.filenameEdit.text():
				self.filenameEdit.setText(''.join(["data",os.sep,"data"]))
			elif not os.sep in self.filenameEdit.text():
				self.filenameEdit.setText(''.join(["data", os.sep, self.filenameEdit.text()]))
			self.data_pm100usb= "".join([self.create_file("".join([self.filenameEdit.text(),"_PM100USB"])),".txt"])
			self.lbl8.setText("--")
		
			self.pm_worker = PM100USB_Worker(self.inst_list, self.data_pm100usb, self.pulse_time, self.warmup_bool, self.lbl8, self.stopButton)
			
			self.pm_worker.signals.update_pm100usb.connect(self.update_pm100usb)
			self.pm_worker.signals.finished.connect(self.finished)
			# Execute
			if self.inst_list.get('COMPexPRO'):
				pass
			else:
				self.threadpool.start(self.pm_worker)
				
	"""
	def surf_line_plot(self):
		
		if self.scan_mode=="ywise":
			n = len(self.x_fields)
			x = self.x_fields
			y = self.y_fields
			z = self.acc_volt.reshape((len(self.x_fields),len(self.y_fields) ))
			for i in range(n):
				pts = (x,y,z[i,:])
				self.plt1.setData(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
				self.pw4.addItem(self.plt1)
				
		elif self.scan_mode=="xwise":
			n = len(self.y_fields)
			x = self.x_fields
			y = self.y_fields
			z = self.acc_volt.reshape((len(self.x_fields),len(self.y_fields) ))
			for i in range(n):
				pts = (x,y,z[:,i])
				self.plt1.setData(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
				self.pw4.addItem(self.plt1)
	"""
	
	
	def email_data_dialog(self):
		
		self.Send_email_dialog = Send_email_dialog.Send_email_dialog(self, self.cwd)
		self.Send_email_dialog.exec()
		
		
	def email_set_dialog(self):
		
		self.Email_dialog = Email_settings_dialog.Email_dialog(self, self.lcd, self.cwd)
		self.Email_dialog.exec()
		
		
	def load_config_dialog(self):
		
		self.Load_config_dialog = Load_config_dialog.Load_config_dialog(self, self.config, self.load_, self.initUI_, self.cwd)
		self.Load_config_dialog.exec()
		
		#self.load_()
		#self.initUI_()
		
		
	def create_file(self,mystr):
		
		head, ext = os.path.splitext(mystr)
		
		totalpath = ''.join([self.cwd,os.sep,head,'_',self.timetrace_str])
		
		my_dir = os.path.dirname(totalpath)
		if not os.path.isdir(my_dir):
			QMessageBox.warning(self, "Message","".join(["Folder(s) named ",my_dir," will be created!"]))
			
		try:
			os.makedirs(my_dir, exist_ok=True)
		except Exception as e:
			QMessageBox.critical(self, "Message","".join(["Folder named ",head," not valid!\n\n",str(e)]))
			return ""
		
		return totalpath
		
		
	def update_compexpro(self,time_elap,energy):
		
		self.all_energy_comp.extend([ energy ])
		if len(self.all_energy_comp)>self.schroll:
			self.plot_time_comp[:-1] = self.plot_time_comp[1:]  # shift data in the array one sample left
			self.plot_time_comp[-1] = time_elap
			self.plot_energy_comp[:-1] = self.plot_energy_comp[1:]  # shift data in the array one sample left
			self.plot_energy_comp[-1] = energy
			self.plot_volt_comp[:-1] = self.plot_volt_comp[1:]  # shift data in the array one sample left
			self.plot_volt_comp[-1] = self.volt
		else:
			self.plot_time_comp.extend([ time_elap ])
			self.plot_energy_comp.extend([ energy ])
			self.plot_volt_comp.extend([ self.volt ])
		
		## Handle view resizing 
		def updateViews():
			## view has resized; update auxiliary views to match
			self.vb1.setGeometry(self.pi1.vb.sceneBoundingRect())
			
			## need to re-update linked axes since this was called
			## incorrectly while views had different shapes.
			## (probably this should be handled in ViewBox.resizeEvent)
			self.vb1.linkedViewChanged(self.pi1.vb, self.vb1.XAxis)
		
		updateViews()
		self.pi1.vb.sigResized.connect(updateViews)
		self.curve1.setData(self.plot_time_comp, self.plot_energy_comp)
		self.curve1_1.setData(self.plot_time_comp, self.plot_volt_comp)
		
		
	def start_pm100usb(self):
		
		if self.inst_list.get('PM100USB'):
			if hasattr(self,"pm_worker"):
				self.threadpool.start(self.pm_worker)
			else:
				QMessageBox.warning(self, "Message", "PM100USB thread does no exist yet.\nCheck delays in the code!")
		
		
	def update_compexpro2(self,hv,rate):
		
		self.volt = hv
		self.Vsweep_lbl.setText("".join(["Voltage (",str(self.volt),") [kV]"]))
		self.rate = rate
		self.Rsweep_lbl.setText("".join(["Pulse rate (",str(self.rate),") [Hz]"]))
		
		self.pi1.setTitle("".join(["Current rate ",str(self.rate)," Hz, Voltage ",str(self.volt)," kV"]))
		
		
	def update_pm100usb(self,time_elap,pm_energy):
		
		# Start checking that all shared variables do exit and have non zero length
		if self.inst_list.get('COMPexPRO'):
			if hasattr(self,'plot_time_comp'):
				if len(self.plot_time_comp)>0:
					time_elap = self.plot_time_comp[-1]
				else:
					print("COMPexPRO elapsed time vector created but empty!")
					return
			else:
				print("COMPexPRO elapsed time vector not created yet!")
				return
				
			if hasattr(self,'plot_energy_comp'):
				if len(self.plot_energy_comp)>0:
					plot_energy_comp = self.plot_energy_comp[-1]
				else:
					print("COMPexPRO elapsed time vector created but empty!")
					return
			else:
				print("COMPexPRO beam energy vector not created yet!")
				return
			
		self.all_energy_pm.extend([ pm_energy ])
		if len(self.all_energy_pm)>self.schroll:
			self.plot_time_pm[:-1] = self.plot_time_pm[1:]  # shift data in the array one sample left
			self.plot_time_pm[-1] = time_elap
			self.plot_energy_pm[:-1] = self.plot_energy_pm[1:]  # shift data in the array one sample left
			self.plot_energy_pm[-1] = pm_energy
			self.plot_volt_pm[:-1] = self.plot_volt_pm[1:]  # shift data in the array one sample left
			self.plot_volt_pm[-1] = self.volt
		else:
			self.plot_time_pm.extend([ time_elap ])
			self.plot_energy_pm.extend([ pm_energy ])
			self.plot_volt_pm.extend([ self.volt ])
		
		time_elap=format(time_elap, "010.4f")
		pm_energy=format(1000*pm_energy, "05.3f")
		if self.inst_list.get('COMPexPRO'):
			egy=format(1000*plot_energy_comp, "05.3f")
			with open(self.data_pm100usb, "a") as thefile:
				thefile.write("%s\t%s\t%s\t%s\t%s\n" %(time_elap,pm_energy,self.rate,egy,self.volt))
		else:
			with open(self.data_pm100usb, "a") as thefile:
				thefile.write("%s\t%s\n" %(time_elap,pm_energy))
			
		## Handle view resizing 
		def updateViews():
			## view has resized; update auxiliary views to match
			self.vb2.setGeometry(self.pi2.vb.sceneBoundingRect())
			
			## need to re-update linked axes since this was called
			## incorrectly while views had different shapes.
			## (probably this should be handled in ViewBox.resizeEvent)
			self.vb2.linkedViewChanged(self.pi2.vb, self.vb2.XAxis)
			
		updateViews()
		self.pi2.vb.sigResized.connect(updateViews)
		self.curve2.setData(self.plot_time_pm, self.plot_energy_pm)
		if self.inst_list.get('COMPexPRO'):
			self.curve2_1.setData(self.plot_time_pm, self.plot_volt_pm)
			
			
	def set_stop(self):
		
		self.stopButton.setEnabled(False)
		
		if self.inst_list.get('COMPexPRO'):
			self.comp_worker.abort()
			
		if self.inst_list.get('PM100USB'):
			self.pm_worker.abort()
		
		self.stop_pressed = True
		
		
	def clear_vars_graphs(self):
		
		# PLOT 1 initial canvas settings
		self.all_energy_comp=[]
		self.all_energy_pm=[]
		
		self.plot_time_comp=[]
		self.plot_energy_comp=[]
		self.plot_volt_comp = []
		
		self.plot_time_pm=[]
		self.plot_energy_pm=[]
		self.plot_volt_pm = []
		
		self.stop_pressed = False
		self.exit_count = 0
		
		self.curve1.clear()
		self.curve1_1.clear()
		self.curve2.clear()
		self.curve2_1.clear()
		
		
	def load_(self):
		
		# Initial read of the config file
		self.config = configparser.ConfigParser()
		try:
			self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
			self.last_used_scan = self.config.get("LastScan","last_used_scan")
			
			self.rate = int(self.config.get(self.last_used_scan,"rate"))
			self.Rsweep = self.config.get(self.last_used_scan,"Rsweep").strip().split(',')
			self.volt = float(self.config.get(self.last_used_scan,"volt"))
			self.Vsweep = self.config.get(self.last_used_scan,"Vsweep").strip().split(',')
			self.pulse_time = int(self.config.get(self.last_used_scan,"pulse_time"))
			self.schroll = int(self.config.get(self.last_used_scan,"schroll"))
			
			self.timeout_str = self.config.get(self.last_used_scan,"timeout")
			self.warmup_str = self.config.get(self.last_used_scan,"warmup")
			self.trigger_str = self.config.get(self.last_used_scan,"trigger")
			self.gasmode_str = self.config.get(self.last_used_scan,"gasmode")
			
			self.filename_str = self.config.get(self.last_used_scan,"filename")
			self.timetrace_str = self.config.get(self.last_used_scan,"timetrace")
			
			self.emailrec_str = self.config.get(self.last_used_scan,"emailrec").strip().split(",")
			self.emailset_str = self.config.get(self.last_used_scan,"emailset").strip().split(",")
		except configparser.NoOptionError as nov:
			QMessageBox.critical(self, "Message","".join(["Main FAULT while reading the config.ini file\n",str(nov)]))
			raise
		
		
	def save_(self):
		
		self.timetrace_str=time.strftime("%y%m%d-%H%M")
		self.lcd.display(self.timetrace_str)
		
		self.config.set("LastScan","last_used_scan", self.last_used_scan )
		
		self.config.set(self.last_used_scan,"rate", str(self.rate) )
		self.config.set(self.last_used_scan,"Rsweep", self.RsweepEdit.text() )
		self.config.set(self.last_used_scan,"volt", str(self.volt) )
		self.config.set(self.last_used_scan,"Vsweep", self.VsweepEdit.text() )
		self.config.set(self.last_used_scan,"pulse_time", self.pulsetimeEdit.text() )
		self.config.set(self.last_used_scan,"schroll", str(self.schroll) )
		
		self.config.set(self.last_used_scan,"timeout", str(self.timeout_str) )
		self.config.set(self.last_used_scan,"warmup", str(self.warmup_str) )
		self.config.set(self.last_used_scan,"trigger", str(self.trigger_str) )
		self.config.set(self.last_used_scan,"gasmode", self.gasmode_str )
		
		self.config.set(self.last_used_scan,"filename", self.filenameEdit.text() )
		self.config.set(self.last_used_scan,"timetrace",self.timetrace_str)
		
		with open(''.join([self.cwd,os.sep,"config.ini"]), "w") as configfile:
			self.config.write(configfile)
		
		
	def finished(self):
		
		self.exit_count+=1
		
		if not self.stop_pressed:
			self.stopButton.setEnabled(False)
			if self.inst_list.get("COMPexPRO"):
				self.comp_worker.abort()
				
			if self.inst_list.get("PM100USB"):
				self.pm_worker.abort()
			
			self.stop_pressed = True
		
		if self.inst_list.get("COMPexPRO") and self.inst_list.get("PM100USB"):
			tal = 2
		else:
			tal = 1
			
		if self.exit_count==tal:
			try:
				self.config.read(''.join([self.cwd,os.sep,"config.ini"]))
				self.emailset_str = self.config.get(self.last_used_scan,"emailset").strip().split(",")
			except configparser.NoOptionError as nov:
				QMessageBox.critical(self, "Message","".join(["Main FAULT while reading the config.ini file\n",str(nov)]))
				return
			
			self.allFields(True)
			self.conMode.setEnabled(True)
			self.startButton.setEnabled(True)
			self.fileClose.setEnabled(True)
			self.fileLoadAs.setEnabled(True)
			
			if self.emailset_str[1] == "yes":
				self.send_notif()
			if self.emailset_str[2] == "yes":
				self.send_data()
			
			self.stopButton.setText("STOP")
			
			if self.inst_list.get("COMPexPRO"):
				self.allFields(True)
			elif self.inst_list.get("PM100USB") and not self.inst_list.get("COMPexPRO"):
				self.allFields(False)
				self.combo4.setEnabled(True)
				self.filenameEdit.setEnabled(True)
			else:
				self.allFields(False)
				
			if not self.inst_list.get("PM100USB") and not self.inst_list.get("COMPexPRO"):
				self.startButton.setText("Load instrument!")
				self.startButton.setEnabled(False)
			else:
				self.startButton.setText("Scan")
				self.startButton.setEnabled(True)
			
			self.timer.start(1000*300)
		
		
	def warning(self, mystr):
		
		QMessageBox.warning(self, "Message", mystr)
		
		
	def critical(self, mystr):
		
		QMessageBox.critical(self, "Message", mystr)
		
		
	def send_notif(self):
		
		self.md = Indicator_dialog.Indicator_dialog(self, "...sending notification...", "indicators/ajax-loader-ball.gif")
		
		contents=["The scan is done. Please visit the experiment site and make sure that all light sources are switched off."]
		subject="The scan is done"
		
		obj = type("obj",(object,),{"subject":subject, "contents":contents, "settings":self.emailset_str, "receivers":self.emailrec_str})
		worker=Email_Worker(obj)
		
		worker.signals.warning.connect(self.warning)
		worker.signals.critical.connect(self.critical)
		worker.signals.finished.connect(self.finished1)
		
		# Execute
		self.threadpool.start(worker)
		
		
	def send_data(self):
		
		self.md = Indicator_dialog.Indicator_dialog(self, "...sending files...", "indicators/ajax-loader-ball.gif")
		
		contents=["The scan is  done and the logged data is attached to this email. Please visit the experiment site and make sure that all light sources are switched off.", self.data_compexpro, self.data_pm100usb]
		subject="The scan data from the latest scan!"
		
		obj = type("obj",(object,),{"subject":subject, "contents":contents, "settings":self.emailset_str, "receivers":self.emailrec_str})
		worker=Email_Worker(obj)
		
		worker.signals.warning.connect(self.warning)
		worker.signals.critical.connect(self.critical)
		worker.signals.finished.connect(self.finished1)
		
		# Execute
		self.threadpool.start(worker)
		
		
	def finished1(self):
		
		self.md.close_()
		
		
	def closeEvent(self, event):
		reply = QMessageBox.question(self, "Message", "Quit now? Any changes not saved will stay unsaved!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		
		if reply == QMessageBox.Yes:
			
			if self.inst_list.get('COMPexPRO'):
				if not hasattr(self, "comp_worker"):
					if self.inst_list.get('COMPexPRO').is_open():
						self.inst_list.get('COMPexPRO').close()
				else:
					if not self.stop_pressed:
						QMessageBox.warning(self, "Message", "Pulsing in progress. Stop the photon source then quit!")
						event.ignore()
						return
					else:
						if self.inst_list.get('COMPexPRO').is_open():
							self.inst_list.get('COMPexPRO').close()
			
			
			if self.inst_list.get('PM100USB'):
				if not hasattr(self, "pm_worker"):
					if self.inst_list.get('PM100USB').is_open():
						self.inst_list.get('PM100USB').close()
				else:
					if not self.stop_pressed:
						QMessageBox.warning(self, "Message", "Pulsing in progress. Stop the photon source then quit!")
						event.ignore()
						return
					else:
						if self.inst_list.get('PM100USB').is_open():
							self.inst_list.get('PM100USB').close()
							
							
			if hasattr(self, "timer"):
				if self.timer.isActive():
					self.timer.stop()
							
			event.accept()
		else:
		  event.ignore()
		  
		  
	##########################################
	
	
	def save_plots(self):
		
		if "\\" in self.filenameEdit.text():
			self.filenameEdit.setText(self.filenameEdit.text().replace("\\",os.sep))
		if "/" in self.filenameEdit.text():
			self.filenameEdit.setText(self.filenameEdit.text().replace("/",os.sep))
				
		if not self.filenameEdit.text():
			self.filenameEdit.setText(''.join(["data",os.sep,"data"]))
		elif not os.sep in self.filenameEdit.text():
			self.filenameEdit.setText(''.join(["data", os.sep, self.filenameEdit.text()]))
			
		self.filename_str=self.filenameEdit.text()
		
		# For SAVING data
		save_plot1="".join([self.create_file(self.filename_str),"_Time_vs_Energy.png"])
		# generate something to export
		
		# create an exporter instance, as an argument give it
		# the item you wish to export
		with mss.mss() as sct:
			sct.shot(output=save_plot1)
		
		
#########################################
#########################################
#########################################

#########################################
#########################################
#########################################
	
	
def main():
	
	app = QApplication(sys.argv)
	ex = Run_COMPexPRO()
	#sys.exit(app.exec())

	# avoid message "Segmentation fault (core dumped)" with app.deleteLater()
	app.exec()
	app.deleteLater()
	sys.exit()
	
	
if __name__ == "__main__":
		
	main()
