import time
from machine import Pin, I2C
from Thermistor import Thermistor
from LDR import LDR
from BMP280 import BMP280


mux_select = Pin(22, Pin.OUT)
thermistor = Thermistor(pin_num=26)
ldr = LDR(pin_num=26)


i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
bmp = BMP280(i2c, addr=0x76)

BH1750_ADDR = 0x23
CONT_HI_RES_MODE = 0x10 

def read_bh1750():
    i2c.writeto(BH1750_ADDR, bytes([CONT_HI_RES_MODE]))
    time.sleep_ms(180)  
    data = i2c.readfrom(BH1750_ADDR, 2)
    raw_val = (data[0] << 8) | data[1]
    return raw_val / 12.9168 



tick_counter = 0
print("Starting CD4053 MUX Sensor Stream...")

while True:
    mux_select.high()
    time.sleep_ms(5)  # Stabilization delay
    raw_counts, r_s, final_temp_f, smoothed_temp_f, uncertainty = thermistor.read()


    mux_select.low()
    time.sleep_ms(5)  # Stabilization delay
    ldr_fc = ldr.read_foot_candles()
        
 
    tick_counter += 1
    if tick_counter >= 10:
        # Read the I2C control sensors
        bmp_temp_c = bmp.temperature - 1.2
        bmp_temp_f = (bmp_temp_c * 9.0 / 5.0) + 32.0
        bh_fc = read_bh1750()
        
        # Print unified line
        print(f"[Thermistor: {smoothed_temp_f:6.2f} ± {uncertainty:.2f} °F | BMP280: {bmp_temp_f:5.2f} °F]  ||  [LDR: {ldr_fc:4d} FC | BH1750: {bh_fc:6.2f} FC]")
        
        tick_counter = 0
        
    # Run the background sampling loop at roughly 10Hz
    time.sleep(0.1)
