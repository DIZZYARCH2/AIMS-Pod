from machine import Pin
import time

class CapTouchSensor:
    def __init__(self, pwm_pin_id=2, in_pin_id=3, threshold=422, debounce=250):
        self.pwm_pin = Pin(pwm_pin_id, Pin.OUT)
        self.in_pin = Pin(in_pin_id, Pin.IN, None)
        self.Threshold = threshold
        self.Debounce = debounce
        self.last_press_time = 0

    def check_press(self):
        pressed_event = False
        self.pwm_pin.value(1)
        start_time = time.ticks_us()
        
        # 1. Wait the threshold
        while time.ticks_diff(time.ticks_us(), start_time) < self.Threshold:
            pass
            
        # 2. Check LM339 comparator
        comparator_state = self.in_pin.value()
        current_time_ms = time.ticks_ms()
        
        # 3. Process press & debounce
        if comparator_state == 0 and time.ticks_diff(current_time_ms, self.last_press_time) > self.Debounce:
            self.last_press_time = current_time_ms
            pressed_event = True  # Registers a valid tap
            
        # 4. Rest of the high half-cycle (approx 2.9 ms)
        time.sleep_us(2900)
        
        # 5. Drive low to drain the capacitor and reset for the full low half-cycle (3.3 ms)
        self.pwm_pin.value(0)
        time.sleep_us(3300)
        
        return pressed_event
