# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 19:40:35 2018

@author: Vedran Furtula
"""

import sys, subprocess, argparse, time, re, serial, random
import numpy as np
import matplotlib.pyplot as plt


class COMPexPRO:
	
	def __init__(self,my_ser,testmode):
		
		#subprocess.call(["sudo","chown","vfurtula:vfurtula","/dev/ttyUSB0"])
		# activate the serial. CHECK the serial port name!
		self.my_ser=my_ser
		self.delay=0.05
		self.timeout=1
		self.testmode = testmode
		
		if self.testmode:
			print("Testmode: COMPexPRO port opened")
			self.isopen = True
		elif not self.testmode:
			self.ser=serial.Serial(my_ser,baudrate=9600)
			time.sleep(0.5)
			print("COMPexPRO serial port:",my_ser)
			self.isopen = True
		
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
  
  # Pyserial readline() function reads until "\n" is sent (other EOLs are ignored).
  # Therefore changes to readline() are required to match it with EOL character "\r".
  # See: http://stackoverflow.com/questions/16470903/pyserial-2-6-specify-end-of-line-in-readline
	def _readline(self):
		eol=b"\r"
		leneol=len(eol)
		line=bytearray()
		while True:
			c=self.ser.read(1)
			if c:
				line+=c
				if line[-leneol:]==eol:
					break
			else:
				break
		
		return bytes(line)[:-1].decode()
	
	####################################################################
  # COMPexPRO functions
  ####################################################################
  
	def set_delay(self,val):
		self.timeout=val
		
		
	def set_timeout_(self,val):
		if self.testmode:
			pass
		elif not self.testmode:
			self.ser.timeout=val
		
		
	def get_timeout(self):
		if self.testmode:
			return "Testmode: TIMEOUT?"
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["TIMEOUT?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if val in ["ON","OFF"]:
					return val
			
			raise ValueError("No return from TIMEOUT? command")
		
		
	def set_timeout(self,val):
		if self.testmode:
			return self.get_timeout()
		elif not self.testmode:
			my_string="".join(["TIMEOUT=",val,"\r"])
			self.ser.write(my_string.encode())
			time.sleep(self.delay)
			return self.get_timeout()
		
		
	def set_opmode(self,val):
		if self.testmode:
			return self.get_opmode()
		elif not self.testmode:
			my_string="".join(["OPMODE=",val,"\r"])
			self.ser.write(my_string.encode())
			if val=="ON":
				time.sleep(4.5)
			elif val=="OFF":
				time.sleep(1.5)
			else:
				time.sleep(0.05)
				
			return self.get_opmode()
		
		
	def get_opmode(self):
		if self.testmode:
			return "Testmode: OPMODE?"
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["OPMODE?\r"])
				self.ser.write(my_string.encode())
				time.sleep(self.delay)
				val=self._readline()
				if val:
					if val[0]=="O":
						return val
					
			raise ValueError("No return from OPMODE? command")
		
		
	def set_counter_reset(self):
		if self.testmode:
			return self.get_counter()
		elif not self.testmode:
			my_string="".join(["COUNTER=RESET\r"])
			self.ser.write(my_string.encode())
			time.sleep(self.delay)
			return self.get_counter()
		
		
	def get_counter(self):
		if self.testmode:
			return -1
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["COUNTER?\r"])
				self.ser.write(my_string.encode())
				time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return int(val)
				
			raise ValueError("No return from COUNTER? command")
		
		
	def get_totalcounter(self):
		if self.testmode:
			return -1
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["TOTALCOUNTER?\r"])
				self.ser.write(my_string.encode())
				time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return int(val)
					
			raise ValueError("No return from TOTALCOUNTER? command")
		
		
	def set_reprate(self,val):
		if self.testmode:
			return self.get_reprate()
		elif not self.testmode:
			my_string="".join(["REPRATE=",val,"\r"])
			self.ser.write(my_string.encode())
			time.sleep(self.delay)
			return self.get_reprate()
		
		
	def get_reprate(self):
		if self.testmode:
			return random.randint(1,50)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["REPRATE?\r"])
				self.ser.write(my_string.encode())
				time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return float(val)
					
			raise ValueError("No return from REPRATE? command")
		
		
	def set_hv(self,val):
		if self.testmode:
			return self.get_hv()
		elif not self.testmode:
			my_string="".join(["HV=",val,"\r"])
			self.ser.write(my_string.encode())
			time.sleep(self.delay)
			return self.get_hv()
		
		
	def get_hv(self):
		if self.testmode:
			return random.uniform(19,30)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["HV?\r"])
				self.ser.write(my_string.encode())
				time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return float(val)
					
			raise ValueError("No return from HV? command")
		
		
	def set_inlo(self,val):
		if self.testmode:
			return self.get_inlo()
		elif not self.testmode:
			my_string="".join(["INTERLOCK=",val,"\r"])
			self.ser.write(my_string.encode())
			#time.sleep(self.delay)
			return self.get_inlo()
	
	
	def get_inlo(self):
		if self.testmode:
			return "Testmode: INTERLOCK?"
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["INTERLOCK?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				return val
			
			raise ValueError("No return from INTERLOCK? command")
		
		
	def set_trigger(self,val):
		if self.testmode:
			return self.get_trigger()
		elif not self.testmode:
			my_string="".join(["TRIGGER=",val,"\r"])
			self.ser.write(my_string.encode())
			time.sleep(self.delay)
			return self.get_trigger()
		
		
	def get_trigger(self):
		if self.testmode:
			return "INT"
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["TRIGGER?\r"])
				self.ser.write(my_string.encode())
				time.sleep(self.delay)
				val=self._readline()
				if val in ["INT","EXT"]:
					return val
				
			raise ValueError("No return from TRIGGER? command")
		
		
	def get_menu(self):
		if self.testmode:
			return ['-1','-1','-1']
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["MENU?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val[0]):
					return val.split(" ")
			
			raise ValueError("No return from MENU? command")
		
		
	def set_gasmode(self,val):
		if self.testmode:
			return self.get_gasmode()
		elif not self.testmode:
			my_string="".join(["GASMODE=",val,"\r"])
			self.ser.write(my_string.encode())
			time.sleep(self.delay)
			return self.get_gasmode()
		
		
	def get_gasmode(self):
		if self.testmode:
			return random.choice(["PREMIX","SINGLE GASES"])
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["GASMODE?\r"])
				self.ser.write(my_string.encode())
				time.sleep(self.delay)
				val=self._readline()
				if val in ["PREMIX","SINGLE GASES"]:
					return val
			
			raise ValueError("No return from GASMODE? command")
		
		
	def set_cod(self,val):
		if self.testmode:
			return self.get_cod()
		elif not self.testmode:
			my_string="".join(["COD=",val,"\r"])
			self.ser.write(my_string.encode())
			#time.sleep(self.delay)
			return self.get_cod()
		
		
	def get_cod(self):
		if self.testmode:
			return -1
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["COD?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if val:
					if val[0]=="0":
						return val
			
			raise ValueError("No return from COD? command")
		
		
	def get_buffer_press(self):
		if self.testmode:
			time.sleep(0.025)
			return random.uniform(-1,0)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["BUFFER?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return float(val)
		
			raise ValueError("No return from BUFFER? command")
		
		
	def get_lt_press(self):
		if self.testmode:
			time.sleep(0.025)
			return random.uniform(-1,0)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["PRESSURE?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return float(val)
					
			raise ValueError("No return from PRESSURE? command")
		
		
	def get_lt_temp(self):
		if self.testmode:
			time.sleep(0.025)
			return random.uniform(-1,0)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["RESERVOIR TEMP?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return float(val)
					
			raise ValueError("No return from RESERVOIR TEMP? command")
		
		
	def get_f2_press(self):
		if self.testmode:
			time.sleep(0.025)
			return random.uniform(-1,0)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["LEAKRATE?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return float(val)
					
			raise ValueError("No return from LEAKRATE? command")
		
		
	def get_f2_temp(self):
		if self.testmode:
			time.sleep(0.025)
			return random.uniform(-1,0)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["TEMP?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if self.is_number(val):
					return float(val)
					
			raise ValueError("No return from TEMP? command")
		
		
	def get_pulse_diff(self):
		if self.testmode:
			time.sleep(0.025)
			return random.uniform(-1,0)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["PULSE DIFF?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				#print("return from PULSE DIFF?\t",val)
				if self.is_number(val):
					return float(val)
					
			raise ValueError("No return from PULSE DIFF? command")
		
		
	def get_energy(self):
		if self.testmode:
			time.sleep(0.025)
			return 1000*random.uniform(-1,0)
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["EGY?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				#print("return from EGY?\t",val)
				if self.is_number(val):
					return float(val)
					
			raise ValueError("No return from EGY? command")
		
		
	def get_pow_stab(self):
		if self.testmode:
			time.sleep(0.025)
			return random.choice(["YES","NO"])
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["POWER STABILIZATION ACHIEVED?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if val in ["YES","NO"]:
					return val
					
			raise ValueError("No return from POWER STABILIZATION ACHIEVED? command")
		
		
	def get_version(self):
		if self.testmode:
			time.sleep(0.025)
			return "-1"
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["VERSION?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if val:
					if val[0]=="V":
						return val
					
			raise ValueError("No return from VERSION? command")
		
		
	def get_lasertype(self):
		if self.testmode:
			time.sleep(0.025)
			return "-1"
		elif not self.testmode:
			time_start=time.time()
			while time.time()-time_start<self.timeout:
				my_string="".join(["TYPE OF LASER?\r"])
				self.ser.write(my_string.encode())
				#time.sleep(self.delay)
				val=self._readline()
				if val:
					return val
					
			raise ValueError("No return from TYPE OF LASER? command")
		
		
	# clean up serial
	def close(self):
		if self.testmode:
			print("Testmode: COMPexPRO port closed")
			self.isopen=False
		elif not self.testmode:
			# flush and close serial
			self.ser.flush()
			self.ser.close()
			print("Serial port flushed and closed")
			self.isopen=False
		
		
	def is_open(self):
		# flush and close serial
		return self.isopen
		
		
		
		
		
def main():
  
	# call the COMPexPRO port
	COMPexPRO_laser = COMPexPRO("COM5",False)
	COMPexPRO_laser.set_timeout_(None)
	
	print(COMPexPRO_laser.set_timeout("OFF"))
	print(COMPexPRO_laser.set_trigger("INT"))
	
	#print COMPexPRO_laser.get_timeout()
	#print COMPexPRO_laser.get_opmode()
	
	#print COMPexPRO_laser.get_version()		
	#print COMPexPRO_laser.get_gasmode()
	#COMPexPRO_laser.set_gasmode("PREMIX")
	#print COMPexPRO_laser.get_gasmode()
	
	#print COMPexPRO_laser.get_reprate("5")
	#print COMPexPRO_laser.set_reprate("5")
	
	#print COMPexPRO_laser.get_hv("19.0")
	#print COMPexPRO_laser.set_hv("19.0")
	
	#val = COMPexPRO_laser.get_trigger()
	#print val

	#val = COMPexPRO_laser.get_inlo()
	#print val

	print(COMPexPRO_laser.get_opmode())
	print(COMPexPRO_laser.set_opmode("SKIP"))
	print(COMPexPRO_laser.set_opmode("ON"))
	
	print(COMPexPRO_laser.get_counter())
	
	time_start=time.time()
	while time.time()-time_start<5:
		print(COMPexPRO_laser.get_energy())
	
	print(COMPexPRO_laser.get_counter())
	
	print(COMPexPRO_laser.set_opmode("OFF"))
	COMPexPRO_laser.close()
	
 
if __name__ == "__main__":
	
  main()
  
