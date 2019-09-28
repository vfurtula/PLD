#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 09:06:01 2018

@author: Vedran Furtula
"""


import os, re, serial, time, yagmail, configparser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QMessageBox, QGridLayout, QCheckBox, QLabel, QLineEdit, QComboBox, QFrame, QVBoxLayout, QHBoxLayout, QMenuBar, QPushButton)

import COMPexPRO, PM100USBdll



class Instruments_dialog(QDialog):
	
	def __init__(self, parent, inst_list, timer,gas_menu,gas_wl,gas_mix,laser_type,pulse_counter,pulse_tot,cwd):
		super().__init__(parent)
		
		# Initial read of the config file
		self.config = configparser.ConfigParser()
		self.cwd = cwd
		
		try:
			self.config.read(''.join([self.cwd,"/config.ini"]))
			
			self.compexproport_str=self.config.get("Instruments","compexproport").strip().split(",")[0]
			self.compexproport_check=self.bool_(self.config.get("Instruments","compexproport").strip().split(",")[1])
			self.pm100usbport_str=self.config.get("Instruments","pm100usbport").strip().split(",")[0]
			self.pm100usbport_check=self.bool_(self.config.get("Instruments","pm100usbport").strip().split(",")[1])
			self.testmode_check=self.bool_(self.config.get("Instruments","testmode"))
			self.COMPexPRO_tm=self.bool_(self.config.get("Instruments","COMPexPRO_tm"))
			self.PM100USB_tm=self.bool_(self.config.get("Instruments","PM100USB_tm"))
			
		except configparser.NoOptionError as e:
			QMessageBox.critical(self, "Message","".join(["Main FAULT while reading the config.ini file\n",str(e)]))
			raise
			
		
		# Enable antialiasing for prettier plots
		self.inst_list = inst_list
		self.timer = timer
		self.gas_menu = gas_menu
		self.gas_wl = gas_wl
		self.gas_mix = gas_mix
		self.laser_type = laser_type
		self.pulse_counter = pulse_counter
		self.pulse_tot = pulse_tot
				
		self.initUI()
		
		
	def bool_(self,txt):
		
		if txt=="True":
			return True
		elif txt=="False":
			return False
		
		
	def initUI(self):
		
		empty_string = QLabel("",self)
		
		compexPro_lbl = QLabel("COMPexPRO serial port",self)
		compexPro_lbl.setStyleSheet("color: blue")
		self.compexProEdit = QLineEdit(self.compexproport_str,self)
		self.compexProEdit.textChanged.connect(self.on_text_changed)
		self.compexProEdit.setEnabled(self.compexproport_check)
		self.compexProEdit.setFixedWidth(325)
		self.cb_compexPro = QCheckBox("",self)
		self.cb_compexPro.toggle()
		self.cb_compexPro.setChecked(self.compexproport_check)
		self.compexPro_status = QLabel("",self)
		
		pm100usb_lbl = QLabel("PM100USB serial port",self)
		pm100usb_lbl.setStyleSheet("color: blue")
		self.pm100usbEdit = QLineEdit(self.pm100usbport_str,self)
		self.pm100usbEdit.textChanged.connect(self.on_text_changed)
		self.pm100usbEdit.setEnabled(self.pm100usbport_check)
		self.pm100usbEdit.setFixedWidth(325)
		self.cb_pm100usb = QCheckBox("",self)
		self.cb_pm100usb.toggle()
		self.cb_pm100usb.setChecked(self.pm100usbport_check)
		self.pm100usb_status = QLabel("",self)
		
		testmode_lbl = QLabel("Connect instruments using the TESTMODE",self)
		testmode_lbl.setStyleSheet("color: magenta")
		self.cb_testmode = QCheckBox("",self)
		self.cb_testmode.toggle()
		self.cb_testmode.setChecked(self.testmode_check)
		
		self.connButton = QPushButton("Connect to selected ports",self)
		#self.connButton.setFixedWidth(150)
		
		self.saveButton = QPushButton("Save settings",self)
		self.saveButton.setEnabled(False)
		#self.saveButton.setFixedWidth(150)
		
		self.closeButton = QPushButton("CLOSE",self)
		self.closeButton.setEnabled(True)
		
		##############################################
		
		# Add all widgets
		g0_0 = QGridLayout()
		
		g0_0.addWidget(compexPro_lbl,0,0)
		g0_0.addWidget(self.cb_compexPro,0,1)
		g0_0.addWidget(self.compexProEdit,1,0)
		g0_0.addWidget(self.compexPro_status,2,0)
		g0_0.addWidget(empty_string,3,0)
		
		g0_0.addWidget(pm100usb_lbl,4,0)
		g0_0.addWidget(self.cb_pm100usb,4,1)
		g0_0.addWidget(self.pm100usbEdit,5,0)
		g0_0.addWidget(self.pm100usb_status,6,0)
		g0_0.addWidget(empty_string,7,0)
		
		g0_0.addWidget(testmode_lbl,24,0)
		g0_0.addWidget(self.cb_testmode,24,1)
		
		g1_0 = QGridLayout()
		g1_0.addWidget(self.connButton,0,0)
		g1_0.addWidget(self.saveButton,0,1)
		
		g2_0 = QGridLayout()
		g2_0.addWidget(self.closeButton,0,0)
		
		v0 = QVBoxLayout()
		v0.addLayout(g0_0)
		v0.addLayout(g1_0)
		v0.addLayout(g2_0)
		
		self.setLayout(v0) 
    
    ##############################################
	
		# run the main script
		self.connButton.clicked.connect(self.set_connect)
		self.saveButton.clicked.connect(self.save_)
		self.closeButton.clicked.connect(self.close_)
		
		self.cb_compexPro.stateChanged.connect(self.compexPro_stch)
		self.cb_pm100usb.stateChanged.connect(self.pm100usb_stch)
		
		##############################################
		
		# Connection warnings
		if self.inst_list.get("COMPexPRO"):
			if self.COMPexPRO_tm:
				self.compexPro_status.setText("Status: TESTMODE")
				self.compexPro_status.setStyleSheet("color: magenta")
			else:
				self.compexPro_status.setText("Status: CONNECTED")
				self.compexPro_status.setStyleSheet("color: green")
		else:
			self.compexPro_status.setText("Status: unknown")
			self.compexPro_status.setStyleSheet("color: black")
			
		if self.inst_list.get("PM100USB"):
			if self.PM100USB_tm:
				self.pm100usb_status.setText("Status: TESTMODE")
				self.pm100usb_status.setStyleSheet("color: magenta")
			else:
				self.pm100usb_status.setText("Status: CONNECTED")
				self.pm100usb_status.setStyleSheet("color: green")
		else:
			self.pm100usb_status.setText("Status: unknown")
			self.pm100usb_status.setStyleSheet("color: black")
			
		##############################################
		
		# Check boxes
		"""
		if not self.checked_list.get("COMPexPRO"):
			self.cb_compexPro.setChecked(False)
		
		if not self.checked_list.get("PM100USB"):
			self.cb_pm100usb.setChecked(False)
		
		if not self.checked_list.get("Oriel"):
			self.cb_oriel.setChecked(False)
		
		if not self.checked_list.get("K2001A"):
			self.cb_k2001a.setChecked(False)
		
		if not self.checked_list.get("Agilent34972A"):
			self.cb_a34972a.setChecked(False)
		
		if not self.checked_list.get("GUV"):
			self.cb_guv.setChecked(False)
		"""
		
		self.setWindowTitle("Pick-up instruments and connect")
		
		# re-adjust/minimize the size of the e-mail dialog
		# depending on the number of attachments
		v0.setSizeConstraint(v0.SetFixedSize)
		
		
	def compexPro_stch(self, state):
		
		self.on_text_changed()
		if state in [Qt.Checked,True]:
			self.compexProEdit.setEnabled(True)
		else:
			self.compexProEdit.setEnabled(False)
			
			
	def pm100usb_stch(self, state):
		
		self.on_text_changed()
		if state in [Qt.Checked,True]:
			self.pm100usbEdit.setEnabled(True)
		else:
			self.pm100usbEdit.setEnabled(False)
			
			
	def on_text_changed(self):
		
		self.saveButton.setText("*Save settings*")
		self.saveButton.setEnabled(True)
		
		
	def set_connect(self):
		
		# Connect or disconnect COMPexPRO laser gun
		self.compexpro()
		
		# Connect or disconnect PM100USB power meter
		self.pm100usb()
		
		# Set the testmode check box correctly for the next run
		if self.PM100USB_tm and self.cb_pm100usb.isChecked():
			if self.COMPexPRO_tm and self.cb_compexPro.isChecked():
				self.cb_testmode.setChecked(True)
			elif not self.cb_compexPro.isChecked():
				self.cb_testmode.setChecked(True)
			else:
				self.cb_testmode.setChecked(False)
		elif not self.cb_pm100usb.isChecked():
			if self.COMPexPRO_tm and self.cb_compexPro.isChecked():
				self.cb_testmode.setChecked(True)
			elif not self.cb_compexPro.isChecked():
				self.cb_testmode.setChecked(False)
			else:
				self.cb_testmode.setChecked(False)
		else:
			self.cb_testmode.setChecked(False)
			
		if not self.inst_list.get("PM100USB") and not self.inst_list.get("COMPexPRO"):
			QMessageBox.critical(self, "Message","No instruments connected. At least 1 instrument is required.")
			return
		else:
			self.save_()
				
				
	def pm100usb(self):
		
		# CLOSE the PM100USB port before doing anything with the port
		if self.inst_list.get("PM100USB"):
			if self.inst_list.get("PM100USB").is_open():
				self.inst_list.get("PM100USB").close()
				self.inst_list.pop("PM100USB", None)
				self.pm100usb_status.setText("Status: device disconnected!")
				self.pm100usb_status.setStyleSheet("color: red")
				
		if self.cb_testmode.isChecked() and self.cb_pm100usb.isChecked():
			self.PM100USB_tm = True
			self.PM100USB = PM100USBdll.PM100USBdll(str(self.pm100usbEdit.text()), self.PM100USB_tm)
			self.pm100usb_status.setText("Testmode: CONNECTED")
			self.pm100usb_status.setStyleSheet("color: magenta")
			self.inst_list.update({"PM100USB":self.PM100USB})
			
		elif not self.cb_testmode.isChecked() and self.cb_pm100usb.isChecked():
			try:
				self.PM100USB_tm = False
				self.PM100USB = PM100USBdll.PM100USBdll(str(self.pm100usbEdit.text()), self.PM100USB_tm)
			except Exception as e:
				reply = QMessageBox.critical(self, 'PM100USB testmode', ''.join(["PM100USB could not return valid echo signal. Check the port name and check the connection.\n\n",str(e),"\n\nProceed into the testmode?"]), QMessageBox.Yes | QMessageBox.No)
				if reply == QMessageBox.Yes:
					self.PM100USB_tm = True
					self.PM100USB = PM100USBdll.PM100USBdll(str(self.pm100usbEdit.text()), self.PM100USB_tm)
					self.pm100usb_status.setText("Testmode: CONNECTED")
					self.pm100usb_status.setStyleSheet("color: magenta")
					self.inst_list.update({"PM100USB":self.PM100USB})
				else:
					self.cb_pm100usb.setChecked(False)
			else:
				self.inst_list.update({"PM100USB":self.PM100USB})
				self.pm100usb_status.setText("Status: CONNECTED")
				self.pm100usb_status.setStyleSheet("color: green")
				
				val = self.inst_list.get("PM100USB").findRsrc()
				print("PM100USB power meter ID:\n\t",self.inst_list.get("PM100USB").getRsrcName(val-1))
			
			
	def compexpro(self):
		
		# CLOSE the COMPexPRO port before doing anything with the port
		if self.inst_list.get("COMPexPRO"):
			if self.inst_list.get("COMPexPRO").is_open():
				self.inst_list.get("COMPexPRO").close()
				self.inst_list.pop("COMPexPRO", None)
				self.compexPro_status.setText("Status: device disconnected!")
				self.compexPro_status.setStyleSheet("color: red")
				
		if self.cb_testmode.isChecked() and self.cb_compexPro.isChecked():
			self.COMPexPRO_tm = True
			self.COMPexPRO = COMPexPRO.COMPexPRO(str(self.compexProEdit.text()), self.COMPexPRO_tm)
			self.compexPro_status.setText("Testmode: CONNECTED")
			self.compexPro_status.setStyleSheet("color: magenta")
			self.inst_list.update({"COMPexPRO":self.COMPexPRO})
			
		if not self.cb_testmode.isChecked() and self.cb_compexPro.isChecked():
			try:
				self.COMPexPRO_tm = False
				self.COMPexPRO = COMPexPRO.COMPexPRO(str(self.compexProEdit.text()), self.COMPexPRO_tm)
				self.COMPexPRO.set_timeout_(2)
				self.COMPexPRO.get_version()
			except Exception as e:
				reply = QMessageBox.critical(self, 'COMPexPRO testmode', ''.join(["COMPexPRO could not return valid echo signal. Check the port name and check the connection to the laser.\n\n",str(e),"\n\nProceed into the testmode?"]), QMessageBox.Yes | QMessageBox.No)
				if reply == QMessageBox.Yes:
					self.COMPexPRO_tm = True
					self.COMPexPRO = COMPexPRO.COMPexPRO(str(self.compexProEdit.text()), self.COMPexPRO_tm)
					self.compexPro_status.setText("Testmode: CONNECTED")
					self.compexPro_status.setStyleSheet("color: magenta")
					self.inst_list.update({"COMPexPRO":self.COMPexPRO})
				else:
					self.cb_compexPro.setChecked(False)
			else:
				self.inst_list.update({"COMPexPRO":self.COMPexPRO})
				self.compexPro_status.setText("Status: CONNECTED")
				self.compexPro_status.setStyleSheet("color: green")
				
				self.inst_list.get("COMPexPRO").set_timeout_(1)
				menu = self.inst_list.get("COMPexPRO").get_menu()
				self.gas_menu.setText(menu[0])
				self.gas_wl.setText(menu[1])
				self.gas_mix.setText(menu[2])
				self.laser_type.setText(self.inst_list.get("COMPexPRO").get_lasertype())
				self.pulse_counter.setText(str(self.inst_list.get("COMPexPRO").get_counter()))
				self.pulse_tot.setText(str(self.inst_list.get("COMPexPRO").get_totalcounter()))
				print("COMPexPRO ",self.inst_list.get("COMPexPRO").get_version()," ready")
				
				
	def save_(self):
		
		self.config.set("Instruments", 'testmode', str(self.cb_testmode.isChecked()) )
		self.config.set("Instruments", "compexproport", ",".join([str(self.compexProEdit.text()), str(self.cb_compexPro.isChecked()) ]) )
		self.config.set("Instruments", "pm100usbport", ",".join([str(self.pm100usbEdit.text()), str(self.cb_pm100usb.isChecked())]) )
		self.config.set("Instruments", 'COMPexPRO_tm', str(self.COMPexPRO_tm) )
		self.config.set("Instruments", 'PM100USB_tm', str(self.PM100USB_tm) )
		
		with open(''.join([self.cwd,"/config.ini"]), "w") as configfile:
			self.config.write(configfile)
			
		self.saveButton.setText("Settings saved")
		self.saveButton.setEnabled(False)
	
	
	def close_(self):
		
		self.close()
			
			
	def closeEvent(self,event):
		
		if self.inst_list:
			self.timer.start(1000*60*5)
		event.accept()
	

