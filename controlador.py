import threading
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

from models.simulacion import (Simulacion, nuevo_log, montecarlo,
                               validar_rng, calcular_resumen_equilibrio)
from diseño import (NOMBRES, construir_animacion, construir_osciloscopio,
                    construir_metricas, construir_panel_matematico)
from modulo_matematico import construir_contenido_ecuaciones

SESIONES = {}
LOCK = threading.Lock()

def get_sesion(sid):
    if sid not in SESIONES:
        SESIONES[sid] = {'running': False, 'esc': None, 'sim': None,
                         'traces': {k: nuevo_log() for k in NOMBRES}, 'mc': None}
    return SESIONES[sid]

def num(x, d):
    try:
        return float(x) if x is not None else d
    except (TypeError, ValueError):
        return d

def armar_cfg(sp, kp, ki, kd, p_aire, tasa, dur, rng_tipo, seed, pwm, masa_g, rho):
    # Convierte la masa ingresada en gramos (g) a kilogramos (kg) para el motor físico
    masa_kg = max(0.0005, num(masa_g, 8.0) / 1000.0)
    return dict(sp=min(1.0, max(0.0, num(sp, 0.5))), kp=num(kp, 40.0), ki=num(ki, 2.0), kd=num(kd, 30.0),
                p_aire=num(p_aire, 2.5), tasa=max(0.0, num(tasa, 0.3)), dur=max(0.2, num(dur, 1.0)),
                rng_tipo=rng_tipo or 'LCG_CLASICO', seed=int(abs(num(seed, 202624))),
                pwm=min(100.0, max(0.0, num(pwm, 55.1))), masa=masa_kg,
                rho=max(0.5, num(rho, 0.95)))

def nueva_sim(s, esc, cfg):
    s['esc'] = esc
    s['sim'] = Simulacion(esc, cfg)
    s['running'] = False
    if esc in NOMBRES:
        s['traces'][esc] = s['sim'].log
    else:
        s['mc'] = montecarlo(cfg, num_runs=40, t_sim=8.0)

def procesar(sid, trig, esc, cfg):
    with LOCK:
        s = get_sesion(sid)
        if trig in ('btn-reset', 'select-escenario') or s['sim'] is None or s['esc'] != esc:
            nueva_sim(s, esc, cfg)
        elif trig == 'btn-play' and esc in NOMBRES:
            s['running'] = True
        elif trig == 'btn-pause':
            s['running'] = False

        sim = s['sim']
        if esc in NOMBRES:
            sim.actualizar(cfg)
            if s['running']:
                for _ in range(4):
                    sim.step()

        pl = sim.planta
        info = f"m = {pl.m * 1000:.1f} g ({pl.m:.4f} kg)  ·  v_eq = {pl.v_eq:.2f} m/s  ·  PWM equilibrio = {pl.u_eq:.1f} %  (ρ = {pl.rho} kg/m³)"
        ind = html.Div([html.Span(f"Altura: {pl.h:.3f} m", className="text-primary me-3"),
                        html.Span(f"Velocidad: {pl.v:.3f} m/s", className="text-info me-3"),
                        html.Span(f"PWM: {sim.vis['u']:.1f} %", className="text-success")])

        toast_alerta = dash.no_update
        if esc in ('3', '4') and s['running'] and len(sim.log['w']) >= 2:
            if sim.log['w'][-1] > 0 and sim.log['w'][-2] == 0:
                toast_alerta = dbc.Toast(
                    "Impacto de viento detectado. Evaluando error de posición...",
                    header="¡Alarma de Perturbación!",
                    is_open=True, dismissable=True, duration=3000, icon="danger",
                    style={"position": "fixed", "top": 20, "right": 20, "width": 350, "zIndex": 9999}
                )

        return (construir_animacion(sim, esc, cfg['sp']), construir_osciloscopio(s, esc, cfg['sp']),
                ind, construir_metricas(s, sim, esc, cfg['sp']), not s['running'], info, toast_alerta,
                construir_panel_matematico(sim, esc))


def registrar_callbacks(app):
    # Cambio entre Módulo 1 (Simulador) y Módulo 2 (Modelo Matemático)
    @app.callback(
        [Output("main-content-sim", "style"), Output("main-content-math", "style")],
        Input("main-tabs", "active_tab")
    )
    def switch_main_tab(tab):
        if tab == "main-tab-math":
            return {'display': 'none'}, {'display': 'block'}
        return {'display': 'block'}, {'display': 'none'}

    # Cambio de sub-pestañas en el Módulo Matemático
    @app.callback(
        [Output("math-content-newton", "style"), Output("math-content-euler", "style"),
         Output("math-content-pid", "style"), Output("math-content-estoc", "style"),
         Output("math-content-mc", "style")],
        Input("math-tabs", "active_tab")
    )
    def switch_math_tab(tab):
        mostrar, ocultar = {'display': 'block'}, {'display': 'none'}
        return tuple(mostrar if tab == t else ocultar for t in
                     ("math-newton", "math-euler", "math-pid", "math-estoc", "math-mc"))

    # Explicación dinámica del motor RNG seleccionado en Perturbaciones
    @app.callback(Output("info-rng-desc", "children"), Input("sel-rng", "value"))
    def actualizar_info_rng(rng_tipo):
        if rng_tipo == "VON_NEUMANN":
            return dbc.Alert([
                html.B("Von Neumann (Cuadrados Medios): "),
                "Eleva la semilla al cuadrado y toma los dígitos centrales para generar R. Es un método histórico que puede ",
                html.B("degenerar en ciclos cortos o caer a cero"),
                ", provocando ráfagas repetitivas o fallando la prueba χ² de uniformidad."
            ], color="warning", className="py-2 px-3 mb-0 small")
        return dbc.Alert([
            html.B("LCG Clásico (Congruencial Lineal): "),
            "Usa X_(n+1) = (1664525·X_n + 1013904223) mod 2³². Produce una secuencia ",
            html.B("uniforme y de periodo largo"),
            ", logrando tiempos entre ráfagas (Transformada Inversa) estadísticamente realistas que aprueban χ²."
        ], color="info", className="py-2 px-3 mb-0 small")

    # Actualización en vivo de los valores sustituidos en las ecuaciones del Módulo Matemático
    @app.callback(
        [Output("math-content-newton", "children"), Output("math-content-euler", "children"),
         Output("math-content-pid", "children"), Output("math-content-estoc", "children"),
         Output("math-content-mc", "children")],
        [Input("inp-m", "value"), Input("inp-rho", "value")]
    )
    def actualizar_ecuaciones_vivas(masa_g, rho):
        masa_kg = max(0.0005, num(masa_g, 8.0) / 1000.0)
        eq = calcular_resumen_equilibrio(masa_kg, num(rho, 0.95))
        return construir_contenido_ecuaciones(eq)

    @app.callback([Output("content-pid", "style"), Output("content-pert", "style"),
                   Output("content-fisica", "style"), Output("content-rng", "style")], Input("tabs", "active_tab"))
    def switch_tab(tab):
        mostrar, ocultar = {'display': 'block'}, {'display': 'none'}
        return tuple(mostrar if tab == t else ocultar for t in ("tab-pid", "tab-pert", "tab-fisica", "tab-rng"))

    @app.callback(
        [Output('grafica-animacion', 'figure'), Output('grafica-osciloscopio', 'figure'),
         Output('indicadores-estado', 'children'), Output('metricas-panel', 'children'),
         Output('sim-interval', 'disabled'), Output('info-eq', 'children'),
         Output('toast-container', 'children'), Output('panel-matematico', 'children')],
        [Input('sim-interval', 'n_intervals'), Input('btn-play', 'n_clicks'), Input('btn-pause', 'n_clicks'),
         Input('btn-reset', 'n_clicks'), Input('select-escenario', 'value')],
        [State('sid', 'data'), State('slider-sp', 'value'), State('inp-kp', 'value'), State('inp-ki', 'value'),
         State('inp-kd', 'value'), State('inp-pert-aire', 'value'), State('inp-tasa', 'value'), State('inp-dur', 'value'),
         State('sel-rng', 'value'), State('inp-seed', 'value'), State('slider-pwm', 'value'),
         State('inp-m', 'value'), State('inp-rho', 'value')])
    def update_sim(n_int, b_pl, b_pa, b_re, esc, sid, sp, kp, ki, kd, p_aire, tasa, dur, rng_tipo, seed, pwm, masa_g, rho):
        cfg = armar_cfg(sp, kp, ki, kd, p_aire, tasa, dur, rng_tipo, seed, pwm, masa_g, rho)
        return procesar(sid, ctx.triggered_id, esc, cfg)

    @app.callback(Output("download-dataframe-csv", "data"), Input("btn-csv", "n_clicks"),
                  [State('sid', 'data'), State('select-escenario', 'value')], prevent_initial_call=True)
    def func_csv(n, sid, esc):
        lg = get_sesion(sid)['traces'].get(esc)
        if not lg or not lg['t']:
            return dash.no_update
        df = pd.DataFrame({'Tiempo_s': lg['t'], 'Altura_m': lg['h'], 'Altura_medida_m': lg['hm'], 'PWM_pct': lg['u'],
                           'Referencia_m': lg['sp'], 'Perturbacion_w_ms': lg['w']})
        return dcc.send_data_frame(df.to_csv, f"telemetria_CB1979_esc{esc}.csv", index=False)

    @app.callback([Output("graf-rng", "figure"), Output("graf-exp", "figure"), Output("txt-rng", "children")], Input("btn-rng", "n_clicks"),
                  [State("sel-rng", "value"), State("inp-seed", "value"), State("inp-tasa", "value")], prevent_initial_call=True)
    def probar_rng(n, tipo, seed, tasa):
        obs, chi2, unicos, ok, T, K, N = validar_rng(tipo, seed, tasa)

        fig_u = go.Figure(go.Bar(x=[f"{i / K:.1f}" for i in range(K)], y=obs, marker_color='#3498db'))
        fig_u.add_hline(y=N / K, line_dash="dash", line_color="red")
        fig_u.update_layout(margin=dict(l=40, r=10, t=30, b=30), yaxis_title="Frecuencia", xaxis_title="R", title="1. Distribución Uniforme U(0,1)")

        fig_e = go.Figure(go.Histogram(x=T, nbinsx=20, marker_color='#e67e22'))
        fig_e.update_layout(margin=dict(l=40, r=10, t=30, b=30), yaxis_title="Frecuencia", xaxis_title="Tiempo de espera (s)", title="2. Tiempos de Ráfagas (Exponencial)")

        explicacion_chi = (
            "Aprobada (χ² < 16.919): los 2000 números se reparten de forma pareja en los 10 intervalos; el azar es válido."
            if ok else
            "Fallida (χ² ≥ 16.919): los números se amontonan en pocos intervalos; el generador NO es uniforme."
        )
        explicacion_ef = (
            f"Efectividad Semilla ({unicos:.0f} %): porcentaje de valores únicos sin repetirse "
            + ("(ciclo saludable)." if unicos >= 80 else "(baja: el generador cayó en un ciclo repetitivo o degeneró).")
        )
        txt = dbc.Alert([
            html.Div(f"Prueba Uniformidad (χ² = {chi2:.1f}) → {'Aprobada' if ok else 'Fallida'}  |  Efectividad Semilla: {unicos:.0f} %",
                     className="fw-bold mb-1"),
            html.Div(explicacion_chi, className="small"),
            html.Div(explicacion_ef, className="small")
        ], color="success" if ok else "danger", className="py-2 px-3 mb-2 text-start")
        return fig_u, fig_e, txt
