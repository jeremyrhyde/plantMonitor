from ina219 import INA219
import time

class Battery_Sensor(INA219):
    """#Main class for battery measurement.
    #Works with Robot.py and INA219 library
    #pip3 install pi-ina219.
    #Shunt resistor value, and maximum expected current are required parameters
    #Device address is in decimal format, default value is 64
    #>>>help(ina219): to see detailed register calibration values
    """

    def __init__(self,shunt_ohms, max_expected_amps, busnum, address, log_level):
        super().__init__(shunt_ohms, max_expected_amps, busnum=None, address=65, log_level=40)

    #allows us to configure without invoking ina219, as we see fit
    def INA_config(self,voltage_range, gain, bus_adc, shunt_adc):
        super().configure(voltage_range, gain, bus_adc, shunt_adc)

    #returns voltage sampled result
    def measure_voltage(self):
        return self.voltage()

    #returns current sampled result
    def measure_current(self):
        return self.current()

    #returns power sampled result
    def measure_power(self):
        return self.power()

    #puts ina219 to sleep, to avoide unnecessary battery drain
    def power_save(self):
        self.sleep()

    #wakes ina219 from sleep
    def wake_up(self):
        self.wake()

    #resets ina219 register values
    def INA219_reset(self):
        self.reset()


SHUNT_OHMS=0.1
MAX_EXPECTED_AMPS=0.75


def main():
    measure=Battery(SHUNT_OHMS,MAX_EXPECTED_AMPS,None,65,40)
    measure.INA_config(0,-1,15,15)
    tri_values=[]
    volt=measure.measure_voltage()
    current=measure.measure_current()
    power=measure.measure_power()
    tri_values=[volt,current,power]
    print(" Voltage is:{}".format(tri_values[0]))
    #return tri_values

if __name__=="__main__":
    main()
