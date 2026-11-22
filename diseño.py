import math
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash import html
import dash_bootstrap_components as dbc
from models.simulacion import metricas_lazo

NOMBRES = {'1': '1. Lazo abierto', '2': '2. PID', '3': '3. Abierto + viento', '4': '4. PID + viento'}
COLORES = {'1': '#00d2d3', '2': '#1dd1a1', '3': '#ff9f43', '4': '#feca57'}
VENTANA = 600

def _streaks(xs, H, phase, largo, h_bola=None, r_bola=0.0):
    X, Y = [], []
    n = 9
    for ci, x in enumerate(xs):
        for k in range(n):
            y0 = ((k / n) + phase + ci * 0.37) % 1.0 * H
            y1 = min(y0 + largo, H)
            if h_bola is not None and abs(x) < r_bola + 0.003 and (h_bola - r_bola - 0.04) < y0 < (h_bola + r_bola + 0.04):
                continue
            X += [x, x, None]
            Y += [y0, y1, None]
    return X, Y

def construir_animacion(sim, esc, sp):
    pl, vis = sim.planta, sim.vis
    H, r, W = pl.H_max, pl.D / 2, 0.05
    w, impacto, va = vis['w'], vis['activa'], pl.v_a
    hay_pid = esc in ('2', '4')
    fig = go.Figure()

    fig.add_shape(type="rect", x0=-0.32, x1=0.32, y0=-0.2, y1=1.22, layer="below", line_width=0,
                  fillcolor="rgba(243,156,18,0.12)" if impacto else "rgba(236,240,241,0.6)")
    fig.add_shape(type="rect", x0=-W - 0.004, x1=W + 0.004, y0=0, y1=H,
                  line=dict(color="#7f8c8d", width=3), fillcolor="rgba(174,214,241,0.15)")
    fig.add_shape(type="rect", x0=-0.08, x1=0.08, y0=-0.09, y1=0, fillcolor="#2c3e50", line_color="#1a252f")
    for k in range(3):
        xk = 0.04 * math.cos(vis['fan_angle'] + k * 2 * math.pi / 3)
        fig.add_trace(go.Scatter(x=[xk, xk], y=[-0.08, -0.01], mode='lines', line=dict(color='#ecf0f1', width=4),
                                 showlegend=False, hoverinfo='skip'))
    fig.add_annotation(x=0, y=-0.125, text=f"u (PWM) = {vis['u']:.0f} %", showarrow=False, font=dict(size=12))

    inten = max(0.15, min(1.0, va / 12.0))
    if va > 0.3:
        X, Y = _streaks([-0.045, -0.02, 0.02, 0.045], H, vis['flow_phase'], 0.04 + 0.08 * inten, pl.h, r)
        fig.add_trace(go.Scatter(x=X, y=Y, mode='lines', line=dict(color=f"rgba(52,152,219,{0.35 + 0.5 * inten:.2f})", width=3),
                                 showlegend=False, hoverinfo='skip'))
    fig.add_annotation(x=0.17, y=0.16, ax=0.17, ay=0.0, xref='x', yref='y', axref='x', ayref='y',
                       showarrow=True, arrowhead=3, arrowwidth=2 + 4 * inten, arrowcolor="#3498db", text="")
    fig.add_annotation(x=0.17, y=0.22, text=f"v_a = {va:.1f} m/s", showarrow=False, font=dict(size=11, color="#2980b9"))

    fig.add_shape(type="rect", x0=-0.05, x1=0.05, y0=H, y1=H + 0.05, fillcolor="#34495e", line_color="#2c3e50")
    fig.add_annotation(x=0, y=H + 0.085, text="HC-SR04", showarrow=False, font=dict(size=11))
    fig.add_trace(go.Scatter(x=[0, 0], y=[H, pl.h + r], mode='lines',
                             line=dict(color='rgba(231,76,60,0.7)', width=2, dash='dot'), showlegend=False, hoverinfo='skip'))
    fig.add_annotation(x=0.065, y=(H + pl.h) / 2, text=f"h = {pl.h:.2f} m<br>(d = {H - pl.h - r:.2f} m)", showarrow=False,
                       font=dict(size=10, color="#c0392b"), xanchor='left', align='left')

    wx, wy = [0.05, 0.27, 0.27, 0.08], [H + 0.025, H + 0.025, -0.045, -0.045]
    if hay_pid:
        fig.add_trace(go.Scatter(x=wx, y=wy, mode='lines', line=dict(color='#2ecc71', width=3), showlegend=False, hoverinfo='skip'))
        if sim.t > 0:
            p = 1.0 - ((sim.t * 1.5) % 1.0)
            fig.add_trace(go.Scatter(x=[0.27], y=[p * (H + 0.07) - 0.045], mode='markers',
                                     marker=dict(symbol='square', size=8, color='#2ecc71'), showlegend=False, hoverinfo='skip'))
        fig.add_annotation(x=0.27, y=0.55, text="DATOS<br>PID", showarrow=False, bgcolor="white", font=dict(size=10, color="#27ae60"))
    else:
        fig.add_trace(go.Scatter(x=wx, y=wy, mode='lines', line=dict(color='#bdc3c7', width=3, dash='dot'), showlegend=False, hoverinfo='skip'))

    if impacto and w != 0:
        sgn = 1 if w > 0 else -1
        X, Y = _streaks([-0.03, 0.03], H, (sgn * vis['gust_phase']) % 1.0, 0.07, pl.h, r)
        fig.add_trace(go.Scatter(x=X, y=Y, mode='lines', line=dict(color='rgba(243,156,18,0.9)', width=4), showlegend=False, hoverinfo='skip'))
        for i in range(4):
            yy = pl.h - 0.18 + i * 0.12
            off = ((vis['gust_phase'] * 3 + i * 0.25) % 1.0) * 0.08
            fig.add_trace(go.Scatter(x=[-0.22 + off, -0.12 + off], y=[yy, yy], mode='lines',
                                     line=dict(color='rgba(243,156,18,0.75)', width=3), showlegend=False, hoverinfo='skip'))
        fig.add_annotation(x=-0.28, y=pl.h + 0.2 * sgn, ax=-0.28, ay=pl.h - 0.2 * sgn, xref='x', yref='y', axref='x', ayref='y',
                           showarrow=True, arrowhead=3, arrowwidth=6, arrowcolor="#e67e22", text="")
        fig.add_annotation(x=0, y=1.18, text=f"RÁFAGA  w = {w:+.1f} m/s", showarrow=False,
                           font=dict(size=13, color="white"), bgcolor="#e67e22", borderpad=4)
    elif esc in ('3', '4') and sim.t > 0:
        fig.add_annotation(x=0, y=1.18, text=f"próxima ráfaga en {sim.rafagas.tiempo_a_proxima(sim.t):.1f} s",
                           showarrow=False, font=dict(size=11, color="#7f8c8d"))

    ox = 0.004 * math.sin(sim.t * 50) if impacto else 0.0
    fig.add_shape(type="circle", x0=ox - r, x1=ox + r, y0=pl.h - r, y1=pl.h + r,
                  fillcolor='#e74c3c' if impacto else '#3498db',
                  line=dict(color='#c0392b' if impacto else '#2980b9', width=3))

    if hay_pid:
        fig.add_hline(y=sp, line_dash="dash", line_color="#e74c3c", line_width=2,
                      annotation_text=f"SP {sp:.2f} m", annotation_position="top left", annotation_font=dict(color="#e74c3c", size=12))

    fig.add_annotation(x=-0.31, y=-0.15, text="━ aire del ventilador", showarrow=False, xanchor='left', font=dict(size=10, color="#3498db"))
    fig.add_annotation(x=-0.31, y=-0.19, text="━ ráfaga / perturbación", showarrow=False, xanchor='left', font=dict(size=10, color="#e67e22"))

    fig.update_layout(xaxis=dict(range=[-0.32, 0.32], visible=False, constrain='domain'),
                      yaxis=dict(range=[-0.2, 1.22], visible=False, scaleanchor='x', scaleratio=1, constrain='domain'),
                      margin=dict(l=0, r=0, t=5, b=0), showlegend=False, plot_bgcolor="white", uirevision='anim')
    return fig

def construir_osciloscopio(s, esc, sp):
    con_w = esc in ('3', '4')
    fig = make_subplots(rows=2 if con_w else 1, cols=1, shared_xaxes=True,
                        row_heights=[0.72, 0.28] if con_w else [1.0], vertical_spacing=0.07)

    if esc == 'MC' and s['mc']:
        mc = s['mc']
        fig.add_trace(go.Scatter(x=mc['t'], y=mc['p95'], mode='lines', line_color='rgba(29,209,161,0.15)', name='P95'))
        fig.add_trace(go.Scatter(x=mc['t'], y=mc['p5'], fill='tonexty', mode='lines', line_color='rgba(29,209,161,0.25)', name='P5'))
        fig.add_trace(go.Scatter(x=mc['t'], y=mc['p50'], mode='lines', line=dict(color='#1dd1a1', width=3), name='P50 (mediana)'))
        fig.add_hline(y=sp, line_dash="dash", line_color="#ff6b6b", line_width=2)
    else:
        for k, lg in s['traces'].items():
            if lg['t']:
                fig.add_trace(go.Scatter(x=lg['t'][-VENTANA:], y=lg['h'][-VENTANA:], mode='lines', name=NOMBRES[k],
                                         line=dict(color=COLORES[k], width=3)), row=1, col=1)
        lg = s['traces'].get(esc)
        if lg and lg['t']:
            tt = lg['t'][-VENTANA:]
            if esc in ('2', '4'):
                fig.add_trace(go.Scatter(x=[tt[0], tt[-1]], y=[sp, sp], mode='lines', name='Referencia',
                                         line=dict(color='#ff6b6b', dash='dot', width=2)), row=1, col=1)
            if con_w:
                ww = lg['w'][-VENTANA:]
                fig.add_trace(go.Scatter(x=tt, y=ww, mode='lines', name='w(t)', line=dict(color='#ff9f43', shape='hv'),
                                         fill='tozeroy', fillcolor='rgba(255,159,67,0.35)'), row=2, col=1)
                ini = None
                for ti, wi in zip(tt, ww):
                    if wi != 0 and ini is None:
                        ini = ti
                    elif wi == 0 and ini is not None:
                        fig.add_vrect(x0=ini, x1=ti, fillcolor="orange", opacity=0.15, line_width=0, row=1, col=1)
                        ini = None
                if ini is not None:
                    fig.add_vrect(x0=ini, x1=tt[-1], fillcolor="orange", opacity=0.15, line_width=0, row=1, col=1)
                fig.update_yaxes(title_text="w (m/s)", row=2, col=1)

    fig.update_yaxes(range=[0, 1.1], title_text="Altura (m)", row=1, col=1)
    fig.update_xaxes(title_text="Tiempo (s)", row=2 if con_w else 1, col=1)
    fig.update_xaxes(showgrid=True, gridcolor='#2c3e50')
    fig.update_yaxes(showgrid=True, gridcolor='#2c3e50')
    fig.update_layout(plot_bgcolor='#111111', paper_bgcolor='#111111', font=dict(color='#ecf0f1'),
                      margin=dict(l=55, r=20, t=25, b=40), uirevision='osc',
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

def chip(label, valor, desc=None):
    cuerpo = [
        html.Div(label, className="small fw-bold text-primary"),
        html.Div(valor, className="fw-bold fs-6 text-dark my-1")
    ]
    if desc:
        cuerpo.append(html.Div(desc, className="text-muted", style={"fontSize": "0.70rem", "lineHeight": "1.15"}))
    return dbc.Col(html.Div(cuerpo, className="border rounded p-2 bg-white shadow-sm text-center h-100"), md=4, lg=2, className="mb-2")

def fmt(x, u="", d=2):
    return "—" if x is None else f"{x:.{d}f}{u}"

def construir_metricas(s, sim, esc, sp):
    if esc == 'MC' and s['mc']:
        mc = s['mc']
        return html.Div([
            html.Div(f"Monte Carlo: {mc['n']} corridas · PID + ráfagas · 8 s", className="mb-2 text-primary"),
            dbc.Row([
                chip("P(toca la tapa)", f"{mc['p_tapa']:.0f} %", "Probabilidad de chocar arriba (1.0 m)."),
                chip("P(satura PWM)", f"{mc['p_sat']:.0f} %", "Probabilidad de llegar al tope 0% o 100%."),
                chip("P(|e|>10 cm, t>4 s)", f"{mc['p_fuera']:.0f} %", "Probabilidad de desviarse >10 cm tras estabilizar."),
                chip("IAE medio", f"{mc['iae']:.2f} m·s", "Error acumulado promedio en las corridas."),
                chip("|e| medio (últimos 2 s)", f"{mc['err_fin'] * 100:.1f} cm", "Error promedio en los últimos 2 s.")
            ]),
            html.Div("Cambia parámetros y pulsa Reiniciar para recalcular.", className="small text-muted")])

    est = sim.gen
    if esc in ('3', '4'):
        if sim.vis['activa']:
            msg = html.Span([html.I(className="fa-solid fa-triangle-exclamation fa-fade me-2"), "¡RÁFAGA ACTIVA!"], className="text-danger")
        else:
            msg = html.Span(f"Próxima ráfaga en {sim.rafagas.tiempo_a_proxima(sim.t):.1f} s", className="text-warning")
        cab = html.Div([html.Span(f"t = {sim.t:.1f} s | R = {est.ultimo:.4f} ({est.tipo}) | "), msg], className="mb-2")
    else:
        cab = html.Div(f"t = {sim.t:.1f} s", className="mb-2")

    m = metricas_lazo(sim.log, sp) if esc in ('2', '4') else None
    if m is None:
        return cab
    return html.Div([cab, dbc.Row([
        chip("Sobreimpulso", fmt(m['sobreimpulso'], " %", 1), "Cuánto se pasó la esfera por encima del Set Point."),
        chip("T. subida", fmt(m['t_subida'], " s"), "Tiempo en subir del 10% al 90% de la altura meta."),
        chip("Asentamiento 5 %", fmt(m['t_asent'], " s"), "Tiempo hasta quedarse estable dentro de ±5% del SP."),
        chip("IAE", fmt(m['iae'], " m·s"), "Error absoluto acumulado en el tiempo (menor = mejor)."),
        chip("PWM máx.", fmt(m['u_max'], " %", 1), "Potencia pico máxima que pidió el PID al ventilador."),
        chip("% saturado", fmt(m['sat'], " %", 1), "Tiempo en que el motor tocó su tope físico (0% o 100%).")
    ])])

def construir_panel_matematico(sim, esc):
    if not sim or not hasattr(sim.planta, 'debug_math') or esc not in ('1', '2', '3', '4'):
        return html.Div("Esperando inicialización del motor matemático...", style={'color': '#bdc3c7'})

    p_dbg = sim.planta.debug_math
    c_dbg = sim.pid.debug_math if hasattr(sim.pid, 'debug_math') else {}
    s_dbg = sim.debug_math if hasattr(sim, 'debug_math') else {}

    html_planta = [
        html.Span("--- DOMINIO 1: FÍSICA CINEMÁTICA Y AERODINÁMICA ---", style={'color': '#3498db', 'fontWeight': 'bold'}), html.Br(),
        f"• Constante de Equilibrio (v_eq) = {p_dbg.get('v_eq', 0):.4f} m/s", html.Br(),
        f"• Constante de Equilibrio (u_eq) = {p_dbg.get('u_eq', 0):.4f} % PWM", html.Br(),
        f"• Inercia Motor (dv_a/dt)        = {p_dbg.get('dv_a', 0):+.4f} (Filtro 1er orden)", html.Br(),
        f"• Vel. Relativa Esfera (v_rel)   = {p_dbg.get('v_rel', 0):+.4f} m/s", html.Br(),
        f"• Fuerza de Arrastre (F_d)       = {p_dbg.get('F_d', 0):+.6f} N", html.Br(),
        f"• Aceleración Neta (a)           = {p_dbg.get('a', 0):+.4f} m/s²", html.Br(),
        f"• Euler: Nueva v(t+dt)           = {sim.planta.v:+.4f} m/s", html.Br(),
        f"• Euler: Nueva h(t+dt)           = {sim.planta.h:+.4f} m", html.Br(),
    ]

    if esc in ('2', '4'):
        html_pid = [
            html.Br(), html.Span("--- DOMINIO 2: LEY DE CONTROL PID (Anti-Windup) ---", style={'color': '#2ecc71', 'fontWeight': 'bold'}), html.Br(),
            f"• Error de Posición (e)        = {c_dbg.get('error', 0):+.4f} m", html.Br(),
            f"• Filtro Sensor (alpha)        = {c_dbg.get('alpha', 0):.4f}", html.Br(),
            f"• Derivada filtrada (dh_f/dt)  = {c_dbg.get('dh', 0):+.4f} m/s", html.Br(),
            f"• Componente P (Kp*e)          = {c_dbg.get('p_term', 0):+.4f}", html.Br(),
            f"• Acumulador Int. (∫e)         = {c_dbg.get('integral', 0):+.4f}", html.Br(),
            f"• Componente I (Ki*∫e)         = {c_dbg.get('i_term', 0):+.4f}", html.Br(),
            f"• Componente D (-Kd*de)        = {c_dbg.get('d_term', 0):+.4f}", html.Br(),
            f"• Salida al Actuador u(t)      = {sim.vis['u']:+.4f} %"
        ]
    else:
        html_pid = [html.Br(), html.Span("--- DOMINIO 2: LEY DE CONTROL PID ---", style={'color': '#95a5a6', 'fontWeight': 'bold'}), html.Br(), "Inactivo en Lazo Abierto"]

    html_estocastico = [
        html.Br(), html.Br(), html.Span("--- DOMINIO 3: MODELADO ESTOCÁSTICO ---", style={'color': '#f39c12', 'fontWeight': 'bold'}), html.Br(),
        f"• RNG Uniforme (R)             = {s_dbg.get('R', 0):.6f}", html.Br(),
        f"• Transf. Inversa Poisson (T)  = {s_dbg.get('t_next', 0):.2f} s", html.Br(),
        f"• Ruido Gauss. Sensor (sigma)  = {p_dbg.get('ruido_sensor', 0):+.6f} m", html.Br(),
        f"• Ruido Gauss. Viento          = {p_dbg.get('ruido_viento', 0):+.6f} m/s", html.Br(),
        f"• Señal Ráfaga sen² (w)        = {sim.vis['w']:+.4f} m/s"
    ]
    return html.Div(html_planta + html_pid + html_estocastico)
