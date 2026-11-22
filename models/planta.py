import math
import random

class PlantaNeumatica:
    def __init__(self, rho=0.95, seed=None):
        self.m = 0.008          # Masa de la esfera (kg)
        self.D = 0.081          # Diámetro de la esfera (m)
        self.C_d = 0.47         # Coeficiente de arrastre aerodinámico
        self.rho = rho          # Densidad del aire (kg/m³) - Pasto ~0.95
        self.g = 9.81           # Gravedad (m/s²)
        self.K_f = 0.15         # Ganancia del ventilador ((m/s)/%)
        self.tau_f = 0.3        # Constante de tiempo del ventilador (s)
        self.H_max = 1.0        # Altura máxima del tubo (m)
        self.n_sub = 10         # Subpasos de integración Euler
        self.rng = random.Random(seed)
        self.debug_math = {
            'v_eq': 0.0, 'u_eq': 0.0, 'dv_a': 0.0,
            'v_rel': 0.0, 'F_d': 0.0, 'a': 0.0,
            'ruido_sensor': 0.0, 'ruido_viento': 0.0
        }
        self.reset()

    @property
    def A(self):
        return math.pi * (self.D / 2.0) ** 2

    @property
    def v_eq(self):
        return math.sqrt(2 * self.m * self.g / (self.rho * self.C_d * self.A))

    @property
    def u_eq(self):
        return self.v_eq / self.K_f

    def set_masa(self, m):
        self.m = max(1e-4, float(m))

    def set_rho(self, rho):
        self.rho = max(0.1, float(rho))

    def set_seed(self, seed):
        self.rng.seed(seed)

    def reset(self):
        self.h = 0.0
        self.v = 0.0
        self.v_a = 0.0
        self.debug_math['ruido_sensor'] = 0.0

    def medir(self, sigma=0.003, resolucion=0.003):
        ruido = self.rng.gauss(0, sigma) if sigma > 0 else 0.0
        self.debug_math['ruido_sensor'] = ruido
        z = self.h + ruido
        if resolucion > 0:
            z = round(z / resolucion) * resolucion
        return min(max(z, 0.0), self.H_max)

    def step(self, u, w_aire=0.0, dt=0.05, noise_std=0.0):
        u = max(0.0, min(100.0, u))
        ruido_viento = self.rng.gauss(0, noise_std) if noise_std > 0 else 0.0
        hs = dt / self.n_sub
        k = 0.5 * self.rho * self.C_d * self.A

        dv_a_last = 0.0
        v_rel = 0.0
        F_d = 0.0
        a = 0.0
        for _ in range(self.n_sub):
            dv_a_last = (-self.v_a + self.K_f * u) / self.tau_f
            self.v_a += dv_a_last * hs

            v_rel = (self.v_a + w_aire + ruido_viento) - self.v
            F_d = k * v_rel * abs(v_rel)
            a = F_d / self.m - self.g

            self.v += a * hs
            self.h += self.v * hs

            if self.h <= 0.0:
                self.h = 0.0
                if self.v < 0:
                    self.v = 0.0
            elif self.h >= self.H_max:
                self.h = self.H_max
                if self.v > 0:
                    self.v = 0.0

        self.debug_math.update({
            'v_eq': self.v_eq,
            'u_eq': self.u_eq,
            'dv_a': dv_a_last,
            'v_rel': v_rel,
            'F_d': F_d,
            'a': a,
            'ruido_viento': ruido_viento
        })
        return self.h, self.v, self.v_a
