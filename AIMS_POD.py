import network
import urequests
import time
from machine import Pin, I2C
from BMP280 import BMP280

SSID = 'andrew bigguy pants ok'
PASSWORD = 'password67'
API_KEY = '8GOXT1VU70RGTVIK'
BH1750_ADDR = 0x23
CONT_HI_RES_MODE = 0x10

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)
bmp = BMP280(i2c)

def read_bmp280():
    temp_c = bmp.temperature
    temp_f = (temp_c * 9/5) + 32
    pres = bmp.pressure
    return temp_f, pres

def read_bh1750():
    try:
        i2c.writeto(BH1750_ADDR, bytes([CONT_HI_RES_MODE]))
        time.sleep_ms(180)
        data = i2c.readfrom(BH1750_ADDR, 2)
        raw_val = (data[0] << 8) | data[1]
        fc = raw_val / 12.9168 
        return fc
    except Exception as e:
        print(e)
        return -1

def read_thermistor():
    therm_temp = 0.0 
    return therm_temp

def read_capacitive_input():
    user_triggered = False 
    return user_triggered

def log_to_thingspeak(field1, field2, field3=None):
    url = f"https://api.thingspeak.com/update?api_key={API_KEY}&field1={field1}&field2={field2}"
    if field3 is not None:
        url += f"&field3={field3}"
    try:
        response = urequests.get(url)
        print(f"Data logged! F1:{field1}, F2:{field2}, F3:{field3}")
        response.close()
    except Exception as e:
        print("IoT Connection Failed:", e)

def run_aims_pod():
    print("Initializing AIMS-Pod...")
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print("Network connected:", wlan.ifconfig())

    while True:
        bmp_temp_f, bmp_pres = read_bmp280()
        lux = read_bh1750()
        therm_temp = read_thermistor()
        cap_input = read_capacitive_input()
        
        print(f"{bmp_temp_f:.2f} F | {bmp_pres:.2f} hPa | {lux:.2f} Fc")
        
        log_to_thingspeak(bmp_temp_f, bmp_pres, lux)
        
        time.sleep(15)

run_aims_pod()
