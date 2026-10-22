from machine import Pin
import time

pwm_pin = Pin(2, Pin.OUT)
in_pin = Pin(3, Pin.IN, None) 

Threshold = 422

#states
system_state_is_on = False
last_press_time = 0
Debounce = 250  # ms

print("Current State: OFF")
try:
    while True:
        pwm_pin.value(1)
        start_time = time.ticks_us()
        #wait the threshold
        while time.ticks_diff(time.ticks_us(), start_time) < Threshold:
            pass
        #check lm339
        comparator_state = in_pin.value()
        current_time_ms = time.ticks_ms()
        
        if comparator_state == 0 and time.ticks_diff(current_time_ms, last_press_time) > Debounce:
            # Toggle the state
            system_state_is_on = not system_state_is_on
            
            # Update the cooldown timer
            last_press_time = current_time_ms
            #print state
            if system_state_is_on:
                print("Pressed: State => ON")
            else:
                print("Pressed: State => OFF")
                
        # 6. Rest of the high half-cycle (approx 2.9 ms)
        time.sleep_us(2900)
        
        # 7. Drive low to drain the capacitor and reset for the full low half-cycle (3.3 ms)
        pwm_pin.value(0)
        time.sleep_us(3300)

except KeyboardInterrupt:
    print("\nShutting down.")
    pwm_pin.value(0)
