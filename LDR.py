class LDR:
    def __init__(self, pin_num=27, v_in=3.3, r_fixed=7000.0, gamma=0.840, a_constant=241177.0):
        self.adc = ADC(pin_num)
        self.v_in = v_in
        self.r_fixed = r_fixed
        self.gamma = gamma
        self.a_constant = a_constant
        
        self.adc_max_val = 65535.0
        self.adc_v_ref = 3.3
        self.kalman = SimpleKalmanFilter(2.0, 2.0, 0.01)

    def read_raw(self):
        return self.adc.read_u16()

    def read_voltage(self):
        return self.read_raw() * (self.adc_v_ref / self.adc_max_val)

    def read_resistance(self):
        v_out = self.read_voltage()
        if v_out >= self.v_in:
            v_out = self.v_in - 0.001
        if v_out <= 0:
            v_out = 0.001
        return self.r_fixed * ((self.v_in / v_out) - 1.0)

    def read_foot_candles(self):
        r_ldr = self.read_resistance()
        lux = (self.a_constant / r_ldr) ** (1.0 / self.gamma)
        fc = lux / 10.764
        # Round the filtered output to the nearest whole number
        return round(self.kalman.update(fc))
