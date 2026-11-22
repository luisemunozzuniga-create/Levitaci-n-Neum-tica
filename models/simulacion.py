import math
import numpy as np
from .planta import PlantaNeumatica
from .pid import ControladorPID

DT = 0.05

def nuevo_log():
    return {'t': [], 'h': [], 'hm': [], 'u': [], 'sp': [], 'w': []}

class GeneradorAleatorio:
    def __init__(self, tipo='LCG_CLASICO', semilla=202624):
        self.tipo = tipo
        self.semilla = int(semilla)
        self.reset()

    def reset(self):
        self.estado = self.semilla
        self.n = max(6, len(str(abs(self.semilla))))
        self.ultimo = 0.0

    def uniforme(self):
        if self.tipo == 'VON_NEUMANN':
            n = self.n
            cuadrado = str(self.estado ** 2).zfill(2 * n)
            nuevo = int(cuadrado[n // 2: n // 2 + n])
            if nuevo == 0:
                nuevo = self.semilla
            self.estado = nuevo
            R = nuevo / 10 ** n
        else:
            a, c, m = 1664525, 1013904223, 2 ** 32
            self.estado = (a * self.estado + c) % m
            R = self.estado / m
        R = min(max(R, 1e-4), 1 - 1e-6)
        self.ultimo = R
        return R

    def exponencial(self, tasa):
        return -math.log(self.uniforme()) / tasa

class ProcesoRafagas:
    def __init__(self, gen, tasa, amp, dur_media):
        self.gen = gen
        self.tasa = tasa
        self.amp = amp
        self.dur_media = dur_media
        self.activa = None
        self.t_next = self._programar(0.0)

    def _programar(self, t):
        return t + self.gen.exponencial(self.tasa) if self.tasa > 0 else math.inf

    def valor(self, t):
        if self.activa is None and t >= self.t_next:
            dur = min(max(-self.dur_media * math.log(self.gen.uniforme()), 0.4), 3.0)
            A = self.amp * (0.8 + 0.4 * self.gen.uniforme())
            self.activa = (t, dur, A)
        if self.activa is not None:
            t0, dur, A = self.activa
            if t >= t0 + dur:
                self.activa = None
                self.t_next = self._programar(t)
                return 0.0, False
            return A * math.sin(math.pi * (t - t0) / dur) ** 2, True
        return 0.0, False

    def tiempo_a_proxima(self, t):
        return max(0.0, self.t_next - t)

class Simulacion:
    def __init__(self, esc, cfg):
        self.esc = esc
        self.cfg = dict(cfg)
        self.planta = PlantaNeumatica(rho=cfg['rho'], seed=cfg['seed'])
        self.planta.set_masa(cfg['masa'])
        self.pid = ControladorPID(cfg['kp'], cfg['ki'], cfg['kd'], self.planta.u_eq)
        self.gen = GeneradorAleatorio(cfg['rng_tipo'], cfg['seed'])
        self.rafagas = ProcesoRafagas(self.gen, cfg['tasa'], cfg['p_aire'], cfg['dur'])
        self.t = 0.0
        self.log = nuevo_log()
        self.vis = {'w': 0.0, 'activa': False, 'u': 0.0,
                    'flow_phase': 0.0, 'gust_phase': 0.0, 'fan_angle': 0.0}
        self.debug_math = {'R': 0.0, 't_next': 0.0}

    def actualizar(self, cfg):
        for k in ('sp', 'kp', 'ki', 'kd', 'p_aire', 'tasa', 'dur', 'pwm', 'masa', 'rho'):
            self.cfg[k] = cfg[k]
        pl = self.planta
        pl.set_masa(cfg['masa'])
        pl.set_rho(cfg['rho'])
        self.pid.set_gains(cfg['kp'], cfg['ki'], cfg['kd'], pl.u_eq)
        self.rafagas.tasa = cfg['tasa']
        self.rafagas.amp = cfg['p_aire']
        self.rafagas.dur_media = cfg['dur']

    def step(self):
        c, pl, esc = self.cfg, self.planta, self.esc
        con_viento = esc in ('3', '4')
        con_pid = esc in ('2', '4')

        w, activa = self.rafagas.valor(self.t) if con_viento else (0.0, False)

        if con_pid:
            hm = pl.medir()
            u, _ = self.pid.compute(c['sp'], hm, DT)
            sp = c['sp']
        else:
            hm, u, sp = pl.h, c['pwm'], None

        pl.step(u, w, DT, noise_std=0.03 if con_viento else 0.0)
        self.t += DT

        self.debug_math['R'] = self.gen.ultimo
        self.debug_math['t_next'] = self.rafagas.t_next if con_viento else 0.0

        lg = self.log
        lg['t'].append(self.t)
        lg['h'].append(pl.h)
        lg['hm'].append(hm)
        lg['u'].append(u)
        lg['sp'].append(sp)
        lg['w'].append(w)

        v = self.vis
        v['w'], v['activa'], v['u'] = w, activa, u
        v['flow_phase'] = (v['flow_phase'] + pl.v_a * DT * 0.12) % 1.0
        v['fan_angle'] += (0.3 + pl.v_a) * DT * 6
        if activa:
            v['gust_phase'] = (v['gust_phase'] + abs(w) * DT * 0.5) % 1.0

def metricas_lazo(log, sp):
    if len(log['t']) < 5 or not sp or sp <= 0:
        return None
    t = np.asarray(log['t'])
    h = np.asarray(log['h'])
    u = np.asarray(log['u'])
    w = np.asarray(log['w'])
    idx = np.nonzero(w != 0)[0]
    n_tr = idx[0] if (len(idx) and idx[0] >= 20) else len(t)
    tt, ht = t[:n_tr], h[:n_tr]

    sobre = max(0.0, (ht.max() - sp) / sp * 100)
    m10, m90 = ht >= 0.1 * sp, ht >= 0.9 * sp
    t_sub = (tt[np.argmax(m90)] - tt[np.argmax(m10)]) if (m10.any() and m90.any()) else None
    fuera = np.abs(ht - sp) > 0.05 * sp
    if not fuera.any():
        t_asent = tt[0]
    else:
        last = np.nonzero(fuera)[0][-1]
        t_asent = tt[last + 1] if last + 1 < len(tt) else None
    iae = float(np.sum(np.abs(h - sp)) * DT)
    sat = float(np.mean((u >= 99.99) | (u <= 0.01)) * 100)
    return {'sobreimpulso': sobre, 't_subida': t_sub, 't_asent': t_asent,
            'iae': iae, 'u_max': float(u.max()), 'sat': sat}

def montecarlo(cfg, num_runs=100, t_sim=10.0):
    n = int(t_sim / DT) + 1
    H, tapa, sat, fuera, iae, err_fin = [], 0, 0, 0, [], []
    sp = cfg['sp']
    t_ref = None
    for i in range(num_runs):
        c = dict(cfg)
        c['seed'] = int(cfg['seed']) + 7919 * i
        sim = Simulacion('4', c)
        for _ in range(n):
            sim.step()
        h = np.asarray(sim.log['h'])
        u = np.asarray(sim.log['u'])
        t = np.asarray(sim.log['t'])
        t_ref = t
        H.append(h)
        tapa += bool((h >= sim.planta.H_max - 1e-9).any())
        sat += bool(((u >= 99.99) | (u <= 0.01)).any())
        fuera += bool((np.abs(h[t > 4.0] - sp) > 0.10).any())
        iae.append(float(np.sum(np.abs(h - sp)) * DT))
        err_fin.append(float(np.mean(np.abs(h[t > t_sim - 2.0] - sp))))
    H = np.vstack(H)
    p5, p50, p95 = np.percentile(H, [5, 50, 95], axis=0)
    return {'t': t_ref.tolist(), 'p5': p5.tolist(), 'p50': p50.tolist(), 'p95': p95.tolist(),
            'n': num_runs,
            'p_tapa': 100 * tapa / num_runs, 'p_sat': 100 * sat / num_runs,
            'p_fuera': 100 * fuera / num_runs,
            'iae': float(np.mean(iae)), 'err_fin': float(np.mean(err_fin))}

def validar_rng(tipo, semilla, tasa):
    N, K = 2000, 10
    g = GeneradorAleatorio(tipo or 'LCG_CLASICO', int(abs(semilla if semilla is not None else 202624)))
    R = np.array([g.uniforme() for _ in range(N)])
    tasa_val = max(0.001, float(tasa) if tasa is not None else 0.3)
    T = -np.log(R) / tasa_val
    obs, _ = np.histogram(R, bins=K, range=(0, 1))
    chi2 = float(np.sum((obs - N / K) ** 2 / (N / K)))
    unicos = len(set(np.round(R, 6))) / N * 100
    ok = chi2 < 16.919
    return obs, chi2, unicos, ok, T, K, N

def calcular_resumen_equilibrio(masa, rho):
    """Calcula parámetros derivados en vivo desde el modelo físico para el Módulo Matemático."""
    pl = PlantaNeumatica(rho=max(0.1, float(rho)))
    pl.set_masa(max(1e-4, float(masa)))
    return {
        'm': pl.m, 'rho': pl.rho, 'D': pl.D, 'C_d': pl.C_d,
        'g': pl.g, 'A': pl.A, 'v_eq': pl.v_eq, 'u_eq': pl.u_eq,
        'peso': pl.m * pl.g, 'K_f': pl.K_f, 'tau_f': pl.tau_f, 'dt': DT
    }
