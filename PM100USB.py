import time, visa, subprocess
from numpy import array

from ThorlabsPM100 import ThorlabsPM100, USBTMC

class PM100USB:
	
	def __init__(self,my_usb):
		
		if "/dev" in my_usb:
			subprocess.call(['sudo','chown','vfurtula:vfurtula',my_usb])
			inst = USBTMC(device=my_usb)
			self.power_meter = ThorlabsPM100(inst=inst)
		else:
			rm = visa.ResourceManager()
			print(rm.list_resources())
			inst = rm.open_resource(my_usb, write_termination='\n', timeout=1)
			self.power_meter = ThorlabsPM100(inst = inst)

	def idn(self):
		return self.power_meter.system.sensor.idn
	
	
	def wavelength(self):
		return self.power_meter.sense.correction.wavelength
	
	def set_wavelength(self,val):
		self.power_meter.sense.correction.wavelength = val
		return self.wavelength()
	
	
	def config_power(self):
		self.power_meter.configure.scalar.power()
	
	def power(self):
		return self.power_meter.measure.scalar.power()
	
	
	def config_energy(self):
		self.power_meter.configure.scalar.energy()
	
	def energy(self):
		return self.power_meter.measure.scalar.energy()
	
	
	def config_temp(self):
		self.power_meter.configure.scalar.temperature()
	
	def temp(self):
		return self.power_meter.measure.scalar.temperature()
	
	
	
	def dc_ref(self):
		return self.power_meter.sense.power.dc.range.auto
	
	def fetch(self):
		return self.power_meter.fetch
	
	def read(self):
		return self.power_meter.read
	
	def config(self):
		return self.power_meter.getconfigure
	
	def group_init(self):
		self.power_meter.initiate.immediate()
	
	def beep(self):
		return self.power_meter.system.beeper.immediate()
	
	
	
def main():
  
	# call the MS257 port
	
	#pm = PM100USB("/dev/usbtmc0")
	pm = PM100USB('USB0::0x1313::0x8072::P2001111::INSTR')
	print(pm.idn())
	'''
	pm.config_power()
	print(pm.power())
	
	pm.set_wavelength(248)
	print(pm.wavelength())
	print(pm.config())
	'''
	
	
if __name__ == "__main__":
	
  main()
