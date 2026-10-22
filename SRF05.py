from machine import Pin, time_pulse_us
import time

class SRF05:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        
    def read_distance_cm(self, temp_c=20.0):
        """Fires the sensor and returns distance in cm, adjusted for temperature."""
        # Ensure trigger is low before starting
        self.trig.value(0)
        time.sleep_us(5)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
        
        try:

            pulse_time = time_pulse_us(self.echo, 1, 30000)
        except OSError:
            return -1
            
        if pulse_time < 0:
            return -1
            
        # Dynamically calculate the exact speed of sound based on air temperature
        speed_of_sound_m_s = 331.3 + (0.606 * temp_c)
        speed_cm_us = speed_of_sound_m_s * 100 / 1000000
        
        # Calculate distance and divide by 2 for the round trip
        distance_cm = (pulse_time * speed_cm_us) / 2
        
        return distance_cm
