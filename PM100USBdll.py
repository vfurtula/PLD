# -*- coding: utf-8 -*-
"""
Spyder Editor

@author: Vedran Furtula
"""

import os, sys, time, ctypes, random

class PM100USBdll:
    
	def __init__(self, my_str, testmode):
		self.testmode = testmode
		self.timeout = 5
		self.end_flag = False
		
		if self.testmode:
			print("Testmode: PM100USB port opened")
			self.isopen = True
		elif not self.testmode:
			try:
				#os.chdir('C:/Program Files (x86)/IVI Foundation/VISA/WinNT/Bin/') #pointer to TLPM_32.dll
				os.chdir('C:\Program Files\IVI Foundation\VISA\Win64\Bin')
				self.PM100USB = ctypes.cdll.LoadLibrary('TLPM_64.dll')
			except Exception as e:
				raise ValueError('PM100USB ValueError raised!\nDirectory where the dll file is placed does not exist!')
			
			inst = self.PM100USB.TLPM_init
			# prepare the constants and their type
			resourceName = my_str.encode()
			IDQuery = ctypes.c_bool(True)
			resetDevice = ctypes.c_bool(True)
			# prepare the pointer and its type
			self.instrumentHandle = ctypes.c_ulong()
			# call dll init function
			self.get_inst = inst(resourceName, IDQuery, resetDevice, ctypes.byref(self.instrumentHandle))
			print('TLPM_init\n\tdll reply code:', self.get_inst, '\n\t', self.errorMessage(self.get_inst))
			
			if self.get_inst!=0:
				raise ValueError( ''.join(['PM100USB ValueError raised!\nTLPM_init returned ',str(self.get_inst),', 0 was expected!']) )
			self.isopen = True
			
			
	def set_delay(self,val):
		self.timeout=val
			
			
	def findRsrc(self):
		if self.testmode:
			return 0
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_findRsrc
				# prepare the pointer and its type
				resourceCount = ctypes.c_ulong()
				# call dll function
				get_inst = inst(self.instrumentHandle, ctypes.byref(resourceCount))
				print('TLPM_findRsrc\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				return resourceCount.value
		
		
	def getRsrcName(self, val):
		if self.testmode:
			return "Testmode: TLPM_getRsrcName"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_getRsrcName
				# prepare constants, pointers and their types
				index=ctypes.c_ulong(val)
				readout = ctypes.create_string_buffer(512)
				# call dll function
				get_inst = inst(self.instrumentHandle, index, ctypes.byref(readout))
				print('TLPM_getRsrcName\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				return readout.value.decode()
		
		
	def reset(self):
		if self.testmode:
			return "Testmode: TLPM_reset"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_reset
				# call dll function
				get_inst = inst(self.instrumentHandle)
				print('TLPM_reset\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				
				
	def abort(self):
		self.end_flag = True
		
		
	def setWavelength(self, val):
		if self.testmode:
			return "Testmode: TLPM_setWavelength"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_setWavelength
				# prepare constants and their types
				wavelength=ctypes.c_double(val)
				# call dll function
				get_inst = inst(self.instrumentHandle, wavelength)
				print('TLPM_setWavelength\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				
				
	def setTimeoutValue(self, val):
		if self.testmode:
			return "Testmode: TLPM_setTimeoutValue"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_setTimeoutValue
				# prepare constants and their types
				timeout=ctypes.c_uint32(val)
				# call dll function
				get_inst = inst(self.instrumentHandle, timeout)
				print('TLPM_setTimeoutValue\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
			
			
	def getTimeoutValue(self):
		if self.testmode:
			return "Testmode: TLPM_getTimeoutValue"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_getTimeoutValue
				# prepare constants and their types 
				timeout=ctypes.c_uint32()
				# call dll function
				get_inst = inst(self.instrumentHandle, ctypes.byref(timeout) )
				#print('TLPM_getTimeoutValue\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				print("PM100USB timeout:",timeout.value)
				return timeout.value
			
			
	def setPowerRange(self, val):
		if self.testmode:
			return "Testmode: TLPM_setPowerRange"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_setPowerRange
				# prepare constants and their types
				powerToMeasure=ctypes.c_double(val)
				# call dll function
				get_inst = inst(self.instrumentHandle, powerToMeasure)
				print('TLPM_setPowerRange\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
			
			
	def setEnergyRange(self, val):
		if self.testmode:
			return "Testmode: TLPM_setEnergyRange"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_setEnergyRange
				# prepare constants and their types
				energyToMeasure=ctypes.c_double(val)
				# call dll function
				get_inst = inst(self.instrumentHandle, energyToMeasure)
				print('TLPM_setEnergyRange\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				
				
	def getWavelength(self,val):
		if self.testmode:
			return "Testmode: TLPM_getWavelength"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_getWavelength
				# prepare constants and their types 
				if val in [0,1,2]:
					attribute=ctypes.c_int16(val) #args are 0, 1 or 2
				else:
					return ValueError('Arg should be 0, 1 or 2')
				wavelength=ctypes.c_double()
				# call dll function
				get_inst = inst(self.instrumentHandle, attribute, ctypes.byref(wavelength) )
				print('TLPM_getWavelength\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				return wavelength.value
		
		
	def getPowerRange(self,val):
		if self.testmode:
			return "Testmode: TLPM_getPowerRange"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_getPowerRange
				# prepare constants and their types 
				if val in [0,1,2]:
					attribute=ctypes.c_int16(val) #args are 0, 1 or 2
				else:
					return ValueError('The arg should be 0, 1 or 2')
				powerValue=ctypes.c_double()
				# call dll function
				get_inst = inst(self.instrumentHandle, attribute, ctypes.byref(powerValue) )
				print('TLPM_getPowerRange\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				return powerValue.value
			
			
	def getEnergyRange(self,val):
		if self.testmode:
			return "Testmode: TLPM_getEnergyRange"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_getEnergyRange
				# prepare constants and their types 
				if val in [0,1,2]:
					attribute=ctypes.c_int16(val) #args are 0, 1 or 2
				else:
					return ValueError('The arg should be 0, 1 or 2')
				energyValue=ctypes.c_double()
				# call dll function
				get_inst = inst(self.instrumentHandle, attribute, ctypes.byref(energyValue) )
				print('TLPM_getEnergyRange\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				return energyValue.value
			
			
	def getAvgTime(self,val):
		if self.testmode:
			return "Testmode: TLPM_getAvgTime"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_getAvgTime
				# prepare constants and their types 
				if val in [0,1,2,3]:
					attribute=ctypes.c_int16(val) #args are 0, 1, 2 or 3
				else:
					return ValueError('The arg should be 0, 1, 2 or 3')
				avgTime=ctypes.c_double()
				# call dll function
				get_inst = inst(self.instrumentHandle, attribute, ctypes.byref(avgTime) )
				print('TLPM_getAvgTime\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				return avgTime.value
		
		
	def getAvgCnt(self):
		if self.testmode:
			return 1
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_getAvgCnt
				# prepare constants and their types 
				avgCnt=ctypes.c_int16()
				# call dll function
				get_inst = inst(self.instrumentHandle, ctypes.byref(avgCnt) )
				print('TLPM_getAvgCnt\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				return avgCnt.value
			
			
	def setAvgCnt(self, val):
		if self.testmode:
			return "Testmode: TLPM_setAvgCnt"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_setAvgCnt
				# prepare constants and their types
				AvgCnt=ctypes.c_int16(val)
				# call dll function
				get_inst = inst(self.instrumentHandle, AvgCnt)
				print('TLPM_setAvgCnt\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				
				
	def measPower(self):
		get_inst=1
		if self.testmode:
			time.sleep(random.uniform(0,1))
			return random.uniform(-1,0)
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_measPower
				# prepare constants, pointers and their types
				power = ctypes.c_double()
				# call dll function
				count=0
				time_start=time.time()
				while time.time()-time_start<self.timeout and get_inst!=0:
					count+=1
					if self.end_flag:
						return 0
					get_inst = inst(self.instrumentHandle, ctypes.byref(power))
					#print('TLPM_measPower\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
					print(''.join(["PM100USB power(",str(count),"): ",str(power.value)]))
					time.sleep(0.1)
				else:
					return power.value
				
				
	def measEnergy(self):
		get_inst=1
		if self.testmode:
			time.sleep(random.uniform(0,1))
			return random.uniform(-1,0)
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_measEnergy
				# prepare constants, pointers and their types
				energy = ctypes.c_double()
				# call dll function
				count=0
				time_start=time.time()
				while time.time()-time_start<self.timeout and get_inst!=0:
					count+=1
					if self.end_flag:
						return 0
					get_inst = inst(self.instrumentHandle, ctypes.byref(energy))
					#print(''.join(['TLPM_measEnergy\n\tdll reply code: ', str(get_inst), '\n\t', self.errorMessage(get_inst)]))
					print(''.join(["PM100USB energy(",str(count),"): ",str(energy.value)]))
					#time.sleep(0.1)
				else:
					return energy.value
				
				
	def measFreq(self):
		if self.testmode:
			return -1
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_measFreq
				# prepare constants, pointers and their types
				freq = ctypes.c_double()
				# call dll function
				get_inst = inst(self.instrumentHandle, ctypes.byref(freq))
				print('TLPM_measFreq\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				return freq.value
			
			
	def errorMessage(self, statusCode):
		if self.testmode:
			return "Testmode: TLPM_errorMessage"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_errorMessage
				# prepare constants, pointers and their types
				readout = ctypes.create_string_buffer(512)
				# call dll function
				get_inst = inst(self.instrumentHandle, statusCode, ctypes.byref(readout))
				#print('errorMessage\n\t dll reply code:', get_inst)
				return readout.value.decode()
			
			
	def writeRaw(self, my_str):
		if self.testmode:
			return "Testmode: TLPM_writeRaw"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_writeRaw
				# call dll function
				get_inst = inst(self.instrumentHandle, my_str)
				print('TLPM_writeRaw\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
			
			
	def readRaw(self):
		if self.testmode:
			return "Testmode: TLPM_readRaw"
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_readRaw
				# prepare constants, pointers and their types
				string = ctypes.create_string_buffer(256)
				size = ctypes.c_ulong(256)
				returnCount = ctypes.c_ulong()
				# call dll function
				get_inst = inst(self.instrumentHandle, ctypes.byref(string),  size, ctypes.byref(returnCount))
				print('TLPM_readRaw\n\tdll reply code:', get_inst)
				print('Number of bytes returned from TLPM_readRaw:\n\t', returnCount.value, '\n\t', self.errorMessage(get_inst))
				return string.value.decode()
			
			
	def close(self):
		if self.testmode:
			print("Testmode: PM100USB port closed")
			self.isopen=False
		elif not self.testmode:
			if self.get_inst==0:
				inst = self.PM100USB.TLPM_close
				# call dll function
				get_inst = inst(self.instrumentHandle)
				print('TLPM_close\n\tdll reply code:', get_inst, '\n\t', self.errorMessage(get_inst))
				self.isopen=False
				self.end_flag = False
			
	def is_open(self):
		return self.isopen
			
			
class Test:

	def __init__(self):
		self.pm100usb = PM100USBdll('USB0::0x1313::0x8072::P2001111::INSTR')
		val = self.pm100usb.findRsrc()
		print(self.pm100usb.getRsrcName(val-1))
		
	def main(self):
		self.pm100usb.setWavelength(350)
		print(self.pm100usb.getWavelength(0))
		
		self.pm100usb.setWavelength(248)
		print(self.pm100usb.getWavelength(0))
		
		self.pm100usb.measFreq()
		self.pm100usb.setPowerRange(5)
		print(self.pm100usb.getPowerRange(0))
		
	def close(self):
		self.pm100usb.close()
			
			
			
			
if __name__=='__main__':
	
	try:
		run_test = Test()
		
		run_test.main()
		
		run_test.close()
	except KeyboardInterrupt:
		run_test.close()
		
		
