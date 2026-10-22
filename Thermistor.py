import math
from machine import ADC, Pin

# GITHUB Denys Sene's "SimpleKalmanFilter" minipython version
class SimpleKalmanFilter:
    def __init__(self, mea_e, est_e, q):
        self._err_measure = mea_e
        self._err_estimate = est_e
        self._q = q
        self._current_estimate = 0.0
        self._last_estimate = 0.0
        self._kalman_gain = 0.0
        self._is_initialized = False

    def update_estimate(self, mea):
        if not self._is_initialized:
            self._last_estimate = mea
            self._is_initialized = True
            
        self._kalman_gain = self._err_estimate / (self._err_estimate + self._err_measure)
        self._current_estimate = self._last_estimate + self._kalman_gain * (mea - self._last_estimate)
        self._err_estimate = (1.0 - self._kalman_gain) * self._err_estimate + abs(self._last_estimate - self._current_estimate) * self._q
        self._last_estimate = self._current_estimate
        
        return self._current_estimate

# thermistor
class Thermistor:
    def __init__(self, pin_num=26):
        self.V_IN = 3.3
        self.ADC_MAX = 65535.0
        self.GAIN = 1.5
        self.BIAS = 1.65
        self.V_MINUS = 3.3 * (1165.0 / 2200.0)
        self.R3 = 1100.0
        self.BETA = 2950.0
        self.R0 = 1100.0
        self.T0 = 298.15
        self.CAL_OFFSET_F = 0.0
        self.DELTA_ADC = 75.0

        self.adc = ADC(Pin(pin_num))
        
        self.kf = SimpleKalmanFilter(2.0, 2.0, 0.01)

    def read(self):
        raw_counts = self.adc.read_u16()
        
        v_out = (raw_counts / self.ADC_MAX) * self.V_IN
        v_diff = (v_out - self.BIAS) / self.GAIN
        v_pos = v_diff + self.V_MINUS
        
        r_s = (self.R3 * v_pos) / (self.V_IN - v_pos)
        
        temp_k = self.BETA / (math.log(r_s / self.R0) + (self.BETA / self.T0))
        temp_c = temp_k - 273.15
        temp_f = (temp_c * 9.0 / 5.0) + 32.0
        
        final_temp_f = temp_f + self.CAL_OFFSET_F
        
        # Update the Kalman filter with the new measurement
        smoothed_temp_f = self.kf.update_estimate(final_temp_f)
        
        # Uncertainty Propagation
        delta_v_out = self.DELTA_ADC * (self.V_IN / self.ADC_MAX)
        delta_v_pos = delta_v_out / self.GAIN
        d_rs_dvpos = (self.R3 * self.V_IN) / ((self.V_IN - v_pos) ** 2)
        delta_rs = d_rs_dvpos * delta_v_pos
        x = math.log(r_s / self.R0) + (self.BETA / self.T0)
        d_tk_drs = self.BETA / ((x ** 2) * r_s)
        delta_tf = (d_tk_drs * delta_rs) * 1.8
        
        return raw_counts, r_s, final_temp_f, smoothed_temp_f, delta_tf
