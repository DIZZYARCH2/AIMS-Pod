import time

class BH1750:
    def __init__(self, i2c, address=0x23):
        self.i2c = i2c
        self.address = address
        self.CONT_HI_RES_MODE = 0x10

    def read(self):
        """Triggers a reading and returns (raw_value, footcandles)"""
        # Send command to start measuring
        self.i2c.writeto(self.address, bytes([self.CONT_HI_RES_MODE]))
        time.sleep_ms(180) # Wait for the sensor to complete measurement
        
        # Read the 2 bytes of data
        data = self.i2c.readfrom(self.address, 2)
        raw_val = (data[0] << 8) | data[1]
        
        # Calculate footcandles
        fc = raw_val / 12.9168 
        
        return raw_val, fc
