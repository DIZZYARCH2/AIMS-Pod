import network
import time
import ubinascii
import machine
import json
from machine import Pin, I2C
from MQTTdriver import MQTTClient

# Load sensors
from BMP280 import BMP280
from BH1750 import BH1750
from Thermistor import Thermistor
from LDR import LDR
from SRF05 import SRF05
from Cap import CapTouchSensor

# Config
SSID = 'andrew bigguy pants ok'
PASSWORD = 'password67'

# Adafruit IO Config
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_HOST = "io.adafruit.com"
MQTT_PORT = 1883
MQTT_USER = b"DIZZYARCH" 
MQTT_PASSWORD = b"aio_ZRTu59sjksxS44nQaO38xXYUJyi7" # Ensure this is your fresh key
MQTT_TOPIC = b"DIZZYARCH/feeds/aims-pod-test"

print("Loading...")

# Setup hardware
status_led = Pin("LED", Pin.OUT) # Initialize onboard LED

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
bmp = BMP280(i2c, addr=0x76)
bh1750 = BH1750(i2c, address=0x23)

mux_select = Pin(22, Pin.OUT)
thermistor = Thermistor(pin_num=26)
ldr = LDR(pin_num=26)

sonar = SRF05(trig_pin=6, echo_pin=7)
cap_sensor = CapTouchSensor(pwm_pin_id=2, in_pin_id=3)

# Main loop
def run_aims_pod():
    # Connect WiFi with Auto-Retry
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("Searching for WiFi...")
    while not wlan.isconnected():
        print("Attempting connection...")
        wlan.connect(SSID, PASSWORD)
        
        # Wait up to 10 seconds for the handshake
        for _ in range(20): 
            if wlan.isconnected():
                break
            status_led.toggle()
            time.sleep(0.5)
            
        if not wlan.isconnected():
            print("Network not found. Restarting radio...")
            wlan.disconnect()
            time.sleep(1)
            
    status_led.value(1) # Turn LED solid ON when connected
    print("WiFi connected.")
    
    # Connect MQTT
    print("Connecting to Adafruit IO...")
    client = MQTTClient(
        client_id=MQTT_CLIENT_ID, 
        server=MQTT_HOST, 
        port=MQTT_PORT, 
        user=MQTT_USER, 
        password=MQTT_PASSWORD,
        keepalive=60
    )
    try:
        client.connect()
        print("SUCCESS: Authenticated with Adafruit IO!")
    except Exception as e:
        print("MQTT Connect Failed:", e)
        status_led.value(0) 
        return

    last_iot_push = 0
    print("\n--- AIMS-Pod Ready ---")
    print("Tap the capacitive sensor to take a reading and push to the cloud.")

    while True:
        # Check touch
        if cap_sensor.check_press():
            current_time = time.ticks_ms()
            
            # Safety check: enforce a 2-second minimum between taps for Adafruit's rate limit
            if time.ticks_diff(current_time, last_iot_push) < 2000:
                print("Tap ignored: Please wait 2 seconds between pushes to avoid ban.")
                time.sleep_ms(200) # Debounce
                continue
                
            print("\nTap detected! Reading sensors...")
            
            # Read MUX sensors
            mux_select.high()
            time.sleep_ms(5)
            _, _, _, smoothed_temp_f, _ = thermistor.read()
            
            mux_select.low()
            time.sleep_ms(5)
            ldr_fc = ldr.read_foot_candles()
            
            # Read I2C & Digital
            bmp_temp_c = bmp.temperature
            bmp_temp_f = (bmp_temp_c * 9.0 / 5.0) + 32.0
            bmp_pres = bmp.pressure
            
            _, bh_fc = bh1750.read()
            dist_cm = sonar.read_distance_cm(temp_c=bmp_temp_c)
            
            # Print data locally
            print(f"BMP: {bmp_temp_f:.1f}F, {bmp_pres:.1f}hPa | BH: {bh_fc:.1f}Fc | LDR: {ldr_fc}Fc | Therm: {smoothed_temp_f:.1f}F | Dist: {dist_cm:.1f}cm")
            
            # Pack all data into a JSON structure
            payload = {
                "bmp_f": round(bmp_temp_f, 1),
                "bmp_pres": round(bmp_pres, 1),
                "bh_fc": round(bh_fc, 1),
                "therm_f": round(smoothed_temp_f, 1),
                "ldr_fc": round(ldr_fc, 1),
                "dist": round(dist_cm, 1)
            }
            
            # Encode and publish
            json_data = json.dumps(payload).encode('utf-8')
            try:
                client.publish(MQTT_TOPIC, json_data)
                print(f"Cloud Push -> {json_data.decode('utf-8')}")
            except Exception as e:
                print("Cloud push failed:", e)
                
            last_iot_push = time.ticks_ms()
            
            # Brief delay to prevent a single long tap from registering multiple times
            time.sleep_ms(500)
            print("Ready for next tap...")
            
        time.sleep_ms(50) 

run_aims_pod()
