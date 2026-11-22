class ControladorPID:
    def __init__(self, kp=40.0, ki=2.0, kd=30.0, u_eq=55.1, tau_d=0.05):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.u_eq = u_eq
        self.tau_d = tau_d
        self.u_min = 0.0
        self.u_max = 100.0
        self.debug_math = {
            'error': 0.0, 'alpha': 0.0, 'h_f': 0.0, 'dh': 0.0,
            'p_term': 0.0, 'i_term': 0.0, 'd_term': 0.0, 'integral': 0.0
        }
        self.reset()

    def set_gains(self, kp, ki, kd, u_eq):
        self.kp, self.ki, self.kd, self.u_eq = kp, ki, kd, u_eq

    def reset(self):
        self.integral = 0.0
        self._h_f = None
        self.dh = 0.0

    def compute(self, setpoint, h_meas, dt):
        error = setpoint - h_meas

        if self._h_f is None:
            self._h_f = h_meas
        alpha = dt / (self.tau_d + dt)
        h_f_nuevo = self._h_f + alpha * (h_meas - self._h_f)
        self.dh = (h_f_nuevo - self._h_f) / dt
        self._h_f = h_f_nuevo

        integral_try = self.integral + error * dt
        u_try = self.u_eq + self.kp * error + self.ki * integral_try - self.kd * self.dh
        saturando = (u_try > self.u_max and error > 0) or (u_try < self.u_min and error < 0)

        if not saturando:
            self.integral = integral_try

        u = self.u_eq + self.kp * error + self.ki * self.integral - self.kd * self.dh
        u = max(self.u_min, min(self.u_max, u))

        self.debug_math = {
            'error': error,
            'alpha': alpha,
            'h_f': self._h_f,
            'dh': self.dh,
            'p_term': self.kp * error,
            'i_term': self.ki * self.integral,
            'd_term': -self.kd * self.dh,
            'integral': self.integral
        }
        return u, error
