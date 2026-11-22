import plotly.graph_objs as go
from dash import dcc, html
import dash_bootstrap_components as dbc


def construir_diagrama_cuerpo_libre():
    """Diagrama de Cuerpo Libre interactivo (Física de la planta en el tubo)."""
    fig = go.Figure()

    # Fondo suave
    fig.add_shape(type="rect", x0=-0.55, x1=0.88, y0=-0.25, y1=1.28,
                  fillcolor="#f8f9fa", line_width=0, layer="below")

    # Tubo vertical de acrílico
    fig.add_shape(type="rect", x0=-0.12, x1=0.12, y0=0.0, y1=1.0,
                  line=dict(color="#34495e", width=3), fillcolor="rgba(174, 214, 241, 0.22)")

    # Sensor HC-SR04 (arriba)
    fig.add_shape(type="rect", x0=-0.10, x1=0.10, y0=1.02, y1=1.10,
                  fillcolor="#2c3e50", line=dict(color="#1a252f", width=2))
    fig.add_annotation(x=0.14, y=1.06, text="<b>Sensor HC-SR04</b><br>Salida y(t) = h + ruido",
                       showarrow=True, arrowhead=2, ax=0.40, ay=1.06,
                       xanchor="left", font=dict(size=11, color="#2c3e50"), align="left")

    # Ventilador (abajo)
    fig.add_shape(type="rect", x0=-0.14, x1=0.14, y0=-0.12, y1=0.0,
                  fillcolor="#1f618d", line=dict(color="#154360", width=2))
    fig.add_annotation(x=0.14, y=-0.06, text="<b>Ventilador PWM</b><br>Entrada u(t) ∈ [0, 100%]",
                       showarrow=True, arrowhead=2, ax=0.40, ay=-0.06,
                       xanchor="left", font=dict(size=11, color="#1f618d"), align="left")

    # Esfera en equilibrio (centro)
    h_eq = 0.50
    r = 0.085
    fig.add_shape(type="circle", x0=-r, x1=r, y0=h_eq - r, y1=h_eq + r,
                  fillcolor="#3498db", line=dict(color="#1b4f72", width=3))
    fig.add_annotation(x=0, y=h_eq, text="<b>m</b>", showarrow=False,
                       font=dict(size=14, color="white"))

    # Flecha Peso / Gravedad hacia abajo
    fig.add_annotation(x=0, y=h_eq - 0.30, ax=0, ay=h_eq - r,
                       xref="x", yref="y", axref="x", ayref="y",
                       showarrow=True, arrowhead=3, arrowsize=1.3, arrowwidth=3.5, arrowcolor="#e74c3c")
    fig.add_annotation(x=0.16, y=h_eq - 0.24, text="<b>Peso (Gravedad)</b><br>Peso = m · g",
                       showarrow=False, xanchor="left", font=dict(size=11, color="#c0392b"), align="left",
                       bgcolor="rgba(248, 249, 250, 0.85)", borderpad=2)

    # Flecha Fuerza de Arrastre hacia arriba
    fig.add_annotation(x=0, y=h_eq + 0.30, ax=0, ay=h_eq + r,
                       xref="x", yref="y", axref="x", ayref="y",
                       showarrow=True, arrowhead=3, arrowsize=1.3, arrowwidth=3.5, arrowcolor="#27ae60")
    fig.add_annotation(x=0.16, y=h_eq + 0.24, text="<b>Fuerza de Arrastre</b><br>F_d = ½·ρ·C_d·A·v_rel·|v_rel|",
                       showarrow=False, xanchor="left", font=dict(size=11, color="#1e8449"), align="left",
                       bgcolor="rgba(248, 249, 250, 0.85)", borderpad=2)

    # Flecha lateral de Perturbación w(t)
    fig.add_annotation(x=-0.12, y=0.65, ax=-0.38, ay=0.65,
                       xref="x", yref="y", axref="x", ayref="y",
                       showarrow=True, arrowhead=3, arrowwidth=3, arrowcolor="#e67e22")
    fig.add_annotation(x=-0.40, y=0.74, text="<b>Perturbación w(t)</b><br>Ráfaga estocástica",
                       showarrow=False, xanchor="center", font=dict(size=10, color="#d35400"))

    # Cota de Altura H_max = 1.0 m
    fig.add_trace(go.Scatter(x=[-0.26, -0.26], y=[0.0, 1.0], mode="lines",
                             line=dict(color="#7f8c8d", width=2, dash="dash"), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[-0.29, -0.23, None, -0.29, -0.23], y=[0.0, 0.0, None, 1.0, 1.0], mode="lines",
                             line=dict(color="#7f8c8d", width=2), showlegend=False, hoverinfo="skip"))
    fig.add_annotation(x=-0.36, y=0.42, text="<b>Altura h(t)</b><br>[0 a 1.0 m]",
                       showarrow=False, font=dict(size=11, color="#34495e"), textangle=-90)

    # Flujo de aire ascendente
    for x_air in (-0.06, 0.06):
        fig.add_annotation(x=x_air, y=0.22, ax=x_air, ay=0.04,
                           xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=2, arrowwidth=2, arrowcolor="rgba(52,152,219,0.7)")

    fig.update_layout(
        xaxis=dict(range=[-0.55, 0.88], visible=False, constrain="domain"),
        yaxis=dict(range=[-0.20, 1.20], visible=False, scaleanchor="x", scaleratio=1, constrain="domain"),
        margin=dict(l=5, r=5, t=5, b=5),
        plot_bgcolor="#f8f9fa",
        paper_bgcolor="#f8f9fa",
        height=390
    )
    return fig


def _bloque(titulo, subtitulo, bg, borde, texto="#2c3e50"):
    return html.Div([
        html.Div(titulo, className="fw-bold", style={"fontSize": "0.85rem", "color": texto}),
        html.Div(subtitulo, style={"fontSize": "0.73rem", "color": "#555"})
    ], className="p-2 rounded text-center shadow-sm",
       style={"backgroundColor": bg, "border": f"2px solid {borde}", "minWidth": "115px"})


def _flecha(etiqueta=""):
    return html.Div([
        html.Div(etiqueta, style={"fontSize": "0.68rem", "color": "#555", "marginBottom": "-4px"}),
        html.Span("──▶", className="fw-bold text-secondary")
    ], className="text-center px-1 d-flex flex-column justify-content-center")


def construir_diagrama_bloques():
    """Diagrama de bloques formal del lazo cerrado (Controlador -> Ventilador -> Planta -> Sensor)."""
    return html.Div([
        html.Div([
            _bloque("Perturbación w(t)", "Ráfagas de aire (m/s)", "#fef5e7", "#e67e22", "#d35400"),
            html.Div("⬇", className="fw-bold text-warning text-center", style={"fontSize": "1.1rem"})
        ], className="d-flex flex-column align-items-end pe-4 mb-1"),

        html.Div([
            html.Div([html.B("SP (h*)"), html.Br(), html.Small("Ref.")], className="text-center small text-danger pe-1"),
            _flecha("+"),
            html.Div("Σ", className="rounded-circle border border-dark d-flex align-items-center justify-content-center fw-bold",
                     style={"width": "30px", "height": "30px", "backgroundColor": "white", "fontSize": "0.9rem"}),
            _flecha("e(t)"),
            _bloque("Controlador", "PID + Anti-Windup", "#ebf5fb", "#3498db", "#1b4f72"),
            _flecha("u(t)"),
            _bloque("Ventilador", "Inercia K_f, τ_f", "#e8f8f5", "#1abc9c", "#117864"),
            _flecha("v_a"),
            _bloque("Tubo y Esfera", "Newton + Arrastre", "#eafaf1", "#2ecc71", "#1d8348"),
            _flecha("h(t)"),
        ], className="d-flex align-items-center justify-content-center flex-wrap gap-1"),

        html.Div([
            html.Span("◀────────────── ", className="text-secondary fw-bold"),
            _bloque("Sensor HC-SR04", "y(t) = h + N(0,σ)", "#fdedec", "#e74c3c", "#922b21"),
            html.Span(" ◀──────────────", className="text-secondary fw-bold"),
        ], className="d-flex align-items-center justify-content-center mt-2"),

        html.Div([
            html.Span("Estado S(t) = [h, v, v_a]   |   ", className="fw-bold text-primary"),
            html.Span("Parámetros p = {m, g, ρ, C_d, A, K_f, τ_f, Δt}", className="text-muted")
        ], className="text-center small mt-2 p-2 bg-light rounded border")
    ])


def construir_anatomia_sistema():
    """Formalización del Sistema (Frontera, Entradas, Perturbaciones, Estados, Parámetros y Salidas)."""
    def caja(titulo, items, bg, borde, color_t):
        return dbc.Col(html.Div([
            html.Div(titulo, className="fw-bold mb-1", style={"fontSize": "0.82rem", "color": color_t}),
            html.Ul([html.Li(it, style={"fontSize": "0.75rem"}) for it in items], className="ps-3 mb-0")
        ], className="p-2 rounded h-100", style={"backgroundColor": bg, "border": f"1.5px solid {borde}"}), md=6, lg=3, className="mb-2")

    return html.Div([
        dbc.Row([
            caja("Entrada u(t)", ["PWM del ventilador (0–100%)", "Señal controlada por el PID o manual"], "#e8f8f5", "#1abc9c", "#117864"),
            caja("Perturbación w(t)", ["Ráfagas de viento (m/s)", "Llegadas Poisson + perfil sin²", "Ruido de proceso"], "#fef5e7", "#f39c12", "#b9770e"),
            caja("Estado S(t)", ["h(t): altura esfera (m)", "v(t): velocidad esfera (m/s)", "v_a(t): velocidad aire (m/s)"], "#f4ecf7", "#8e44ad", "#6c3483"),
            caja("Parámetros p", ["m, D, C_d, ρ (Pasto)", "K_f, τ_f del ventilador", "g = 9.81 m/s², Δt = 0.05 s"], "#f2f3f4", "#7f8c8d", "#2c3e50"),
        ]),
        dbc.Row([
            dbc.Col(html.Div([
                html.B("Mecanismo de Cambio: "), "F_arrastre − Peso = m · a  (integrado con Euler semi-implícito)"
            ], className="p-2 rounded text-center small", style={"backgroundColor": "#fdedec", "border": "1.5px solid #e74c3c", "color": "#922b21"}), width=12, className="mb-2"),
            dbc.Col(html.Div([html.B("Equilibrio: "), "F_d = m·g  ⇒  v_eq, u_eq"],
                             className="p-2 rounded text-center small bg-light border"), width=6),
            dbc.Col(html.Div([html.B("Salida y(t): "), "Altura medida por HC-SR04 (ruido + 3 mm)"],
                             className="p-2 rounded text-center small bg-light border"), width=6),
        ])
    ])


def construir_tabla_parametros():
    """Tabla formal de parámetros físicos, variables y valores del modelo."""
    filas = [
        ("m", "Masa de la esfera", "8.0 g (0.008 kg)", "Ingresada en g, convertida a kg en Newton"),
        ("D", "Diámetro de la esfera", "0.081 m (81 mm)", "Geometría (A = π·(D/2)²)"),
        ("C_d", "Coeficiente de arrastre", "0.47", "Esfera en régimen turbulento"),
        ("ρ", "Densidad del aire", "0.95 kg/m³", "Altitud de San Juan de Pasto"),
        ("g", "Aceleración de la gravedad", "9.81 m/s²", "Constante física"),
        ("K_f", "Ganancia del ventilador", "0.15 (m/s)/%", "Mapeo PWM → velocidad de aire"),
        ("τ_f", "Constante de tiempo motor", "0.30 s", "Inercia de 1.er orden del ventilador"),
        ("H_max", "Altura útil del tubo", "1.00 m", "Fronteras físicas [0, 1] m"),
        ("Δt", "Paso de control (Bucle)", "0.05 s (20 Hz)", "10 subpasos Euler (hs = 0.005 s)"),
        ("Kp, Ki, Kd", "Ganancias del PID", "40.0, 2.0, 30.0", "Sintonización base + Anti-Windup"),
    ]
    return dbc.Table([
        html.Thead(html.Tr([html.Th("Símbolo"), html.Th("Variable / Parámetro"), html.Th("Valor Base"), html.Th("Significado / Origen")])),
        html.Tbody([html.Tr([html.Td(html.B(s), className="text-primary"), html.Td(n), html.Td(html.Code(v)), html.Td(o)]) for s, n, v, o in filas])
    ], bordered=True, striped=True, hover=True, size="sm", className="mb-0 small bg-white")


def _ecuacion(titulo, formula_latex, explicacion, variables, origen):
    """Tarjeta de ecuación con renderizado LaTeX nativo (MathJax) y glosario letra por letra."""
    lista_vars_md = "\n".join([f"- **{simbolo}:** {desc}" for simbolo, desc in variables])
    return html.Div([
        html.Div(titulo, className="fw-bold text-primary mb-2", style={"fontSize": "0.96rem"}),
        html.Div(
            dcc.Markdown(f"$${formula_latex}$$", mathjax=True, className="mb-0"),
            className="px-3 py-2 mb-2 rounded text-center overflow-auto",
            style={
                "backgroundColor": "#eef5fc",
                "borderLeft": "4px solid #2980b9",
                "color": "#1a252f",
                "fontSize": "1.02rem"
            }
        ),
        html.P(explicacion, className="small text-muted mb-2"),
        html.Div([
            html.Div("¿Qué significa cada letra?", className="small fw-bold text-secondary mb-1"),
            dcc.Markdown(lista_vars_md, mathjax=True, className="small mb-0")
        ], className="p-2 mb-2 rounded bg-light border"),
        html.Details([
            html.Summary(
                [html.I(className="fa-solid fa-circle-question me-1"), "¿De dónde sale esta ecuación? (Ver derivación)"],
                className="small fw-bold text-success",
                style={"cursor": "pointer", "userSelect": "none"}
            ),
            html.Div(
                dcc.Markdown(origen, mathjax=True, className="small mb-0"),
                className="mt-2 p-2 rounded",
                style={"backgroundColor": "#eafaf1", "borderLeft": "3px solid #27ae60", "color": "#1d5b34"}
            )
        ], className="mt-1")
    ], className="p-3 mb-3 bg-white border rounded shadow-sm")


def construir_contenido_ecuaciones(eq):
    """Devuelve las 5 pestañas de ecuaciones en LaTeX con glosario completo letra por letra y valores en vivo."""
    tab_newton = html.Div([
        _ecuacion(
            "1. Fuerza de Arrastre Aerodinámico (Drag) y Área Frontal",
            r"F_d = \frac{1}{2}\,\rho\,C_d\,A\,v_{rel}\,|v_{rel}| \qquad \text{donde} \quad A = \pi\left(\frac{D}{2}\right)^2, \quad v_{rel} = (v_a + w + \text{ruido}) - v",
            "Empuje vertical que ejerce la columna de aire sobre la esfera. Usa v_rel·|v_rel| para preservar el signo físico si el aire frena a la esfera.",
            [
                (r"$F_d$", "Fuerza de arrastre aerodinámico que empuja la esfera hacia arriba (Newtons, N)."),
                (r"$\frac{1}{2}$", r"Factor de presión dinámica de Bernoulli ($q = \frac{1}{2}\rho v^2$, energía cinética del aire por unidad de volumen)."),
                (r"$\rho$", f"Densidad del aire (en vivo: **{eq['rho']:.2f} kg/m³** — Pasto ≈ 0.95 kg/m³)."),
                (r"$C_d$", f"Coeficiente de arrastre aerodinámico (**{eq['C_d']}** para una esfera, adimensional)."),
                (r"$A$", f"Área frontal expuesta al viento = $\\pi(D/2)^2$ (en vivo: **{eq['A']:.6f} m²**)."),
                (r"$D$", f"Diámetro de la esfera (**{eq['D']} m** = 8.1 cm)."),
                (r"$v_{rel}$", "Velocidad relativa entre el aire y la esfera (m/s)."),
                (r"$v_a$", "Velocidad vertical del aire producida por el ventilador (m/s)."),
                (r"$w$", "Perturbación externa por ráfaga de viento (m/s)."),
                (r"$v$", "Velocidad vertical actual de la esfera (m/s).")
            ],
            r"El factor $\frac{1}{2}$ proviene de la energía cinética por unidad de volumen (presión dinámica de Bernoulli: $q = \frac{1}{2}\rho v^2$). Al multiplicar presión por área frontal ($F = q \cdot A$) obtenemos la fuerza teórica ideal; luego se multiplica por $C_d = 0.47$ para ajustar por la forma esférica. Se escribe $v_{rel}|v_{rel}|$ en vez de $v_{rel}^2$ para conservar la dirección física del empuje."
        ),
        _ecuacion(
            "2. Segunda Ley de Newton y Punto de Equilibrio Estático",
            r"a = \frac{F_d}{m} - g \qquad \Big| \qquad v_{eq} = \sqrt{\frac{2\,m\,g}{\rho\,C_d\,A}}, \qquad u_{eq} = \frac{v_{eq}}{K_f}",
            "La aceleración neta resulta de restar el empuje del aire hacia arriba menos el peso hacia abajo. Cuando empatan (a = 0), la esfera flota quieta.",
            [
                (r"$a$", "Aceleración neta vertical de la esfera (m/s²)."),
                (r"$F_d$", "Fuerza de arrastre aerodinámico hacia arriba (N)."),
                (r"$m$", f"Masa de la esfera (en vivo: **{eq['m'] * 1000:.1f} g** = {eq['m']:.4f} kg ⇒ Peso $m\\cdot g$ = **{eq['peso']:.5f} N**)."),
                (r"$g$", f"Aceleración de la gravedad (**{eq['g']} m/s²**)."),
                (r"$v_{eq}$", f"Velocidad exacta del aire para flotar sin acelerar (en vivo: **{eq['v_eq']:.2f} m/s**)."),
                (r"$u_{eq}$", f"Porcentaje de PWM de equilibrio necesario para sostener la esfera (en vivo: **{eq['u_eq']:.1f} %**)."),
                (r"$K_f$", f"Ganancia estática del ventilador (**{eq['K_f']} (m/s)/%**).")
            ],
            r"Sale del balance de fuerzas verticales $\sum F = m \cdot a \Rightarrow F_d - m \cdot g = m \cdot a$; al dividir todo entre $m$ se despeja $a = \frac{F_d}{m} - g$. Para hallar $v_{eq}$ se impone equilibrio estático ($a = 0$), igualando $\frac{1}{2}\rho C_d A v_{eq}^2 = m g$ y despejando $v_{eq}$ (de ahí aparece el $2$ arriba y la raíz cuadrada). Luego $u_{eq} = v_{eq}/K_f$."
        ),
        _ecuacion(
            "3. Dinámica del Ventilador (Sistema de 1.er Orden)",
            r"\frac{dv_a}{dt} = \frac{-v_a + K_f \cdot u}{\tau_f}",
            "Modela la inercia mecánica del motor: el flujo de aire no cambia instantáneamente cuando varía el PWM.",
            [
                (r"$\frac{dv_a}{dt}$", "Tasa de cambio (aceleración) de la velocidad del aire del ventilador (m/s²)."),
                (r"$v_a$", "Velocidad actual del flujo de aire (m/s)."),
                (r"$K_f$", f"Ganancia estática del ventilador: cuántos m/s produce cada 1% de PWM (**{eq['K_f']} (m/s)/%**)."),
                (r"$u$", "Señal de control PWM enviada al ventilador (0% a 100%)."),
                (r"$\tau_f$", f"Constante de tiempo del motor: mide su inercia mecánica (**{eq['tau_f']} s**).")
            ],
            r"Proviene de la ecuación diferencial canónica de un actuador de primer orden con inercia: $\tau_f \frac{dv_a}{dt} + v_a = K_f u$. Al despejar $\frac{dv_a}{dt}$ se obtiene el modelo que suaviza la respuesta del aire ante saltos bruscos de PWM."
        )
    ])

    tab_euler = html.Div([
        _ecuacion(
            "1. Discretización por Euler Semi-Implícito (10 subpasos por ciclo)",
            r"v_a(k+1) = v_a(k) + \frac{-v_a(k) + K_f u}{\tau_f}\,h_s \quad \Big| \quad v(k+1) = v(k) + a(k)\,h_s \quad \Big| \quad h(k+1) = h(k) + v(k+1)\,h_s",
            "Actualiza primero la velocidad y usa ese valor recién calculado v(k+1) para hallar la nueva altura h(k+1), mejorando la estabilidad numérica.",
            [
                (r"$k,\; k+1$", "Instante de tiempo actual ($k$) e instante futuro siguiente ($k+1$)."),
                (r"$h_s$", f"Subpaso interno de integración Euler = $\\Delta t / 10$ (**0.005 s**)."),
                (r"$\Delta t$", f"Paso del bucle de control principal (**{eq['dt']} s** = 20 Hz)."),
                (r"$v_a$", "Velocidad del aire del ventilador (m/s)."),
                (r"$v$", "Velocidad vertical de la esfera (m/s)."),
                (r"$a(k)$", "Aceleración neta de la esfera en el paso $k$ (m/s²)."),
                (r"$h$", "Altura real de la esfera dentro del tubo (acotada a $[0,\; 1.0]$ m).")
            ],
            r"Sale de la definición de derivada en cálculo: $a = \frac{dv}{dt} \approx \frac{v(k+1) - v(k)}{h_s}$ y $v = \frac{dh}{dt} \approx \frac{h(k+1) - h(k)}{h_s}$. Despejando el estado futuro ($k+1$) convertimos ecuaciones diferenciales continuas en ecuaciones en diferencias ejecutables en Python."
        ),
        _ecuacion(
            "2. Modelo del Sensor Ultrasónico HC-SR04 (Ruido y Cuantización)",
            r"y(t) = \operatorname{round}\!\left(\frac{h(t) + \mathcal{N}(0,\sigma)}{0.003}\right) \cdot 0.003",
            "Reproduce el comportamiento real del sensor ultrasónico: añade ruido aleatorio y redondea la lectura a saltos discretos de 3 mm.",
            [
                (r"$y(t)$", "Altura medida por el sensor HC-SR04, también denotada $h_m$ (m)."),
                (r"$h(t)$", "Altura real verdadera de la esfera en el instante $t$ (m)."),
                (r"$\mathcal{N}(0,\sigma)$", "Ruido Gaussiano con media 0 y desviación estándar $\\sigma = 0.003$ m (3 mm)."),
                (r"$0.003$", "Resolución física de cuantización del sensor (3 mm = 0.003 m).")
            ],
            r"Un sensor ultrasónico real nunca entrega la altura exacta: su lectura oscila con ruido térmico/acústico ($\mathcal{N}(0,\sigma)$) y su electrónica reporta distancias en múltiplos de su resolución mínima (3 mm)."
        ),
        html.Div([
            html.Div("3. El Bucle Universal de la Simulación (Paso a Paso cada Δt = 0.05 s)", className="fw-bold text-success mb-2"),
            dbc.ListGroup([
                dbc.ListGroupItem([html.B("Paso 1 — Lectura (Sensor): "), "El HC-SR04 mide y(t) = h(t) + N(0, 0.003 m) cuantizado a 3 mm."]),
                dbc.ListGroupItem([html.B("Paso 2 — Decisión (Control PID): "), "Calcula e(t) = SP − y(t) y determina la potencia u(t) ∈ [0, 100]%."]),
                dbc.ListGroupItem([html.B("Paso 3 — Perturbación (Viento): "), "Evalúa si una ráfaga Poisson w(t) está activa en el instante t."]),
                dbc.ListGroupItem([html.B("Paso 4 — Transición (Newton + Euler): "), "Integra 10 subpasos físicos para obtener los nuevos estados S(t+Δt) = [h, v, v_a]."]),
                dbc.ListGroupItem([html.B("Paso 5 — Avance y Registro: "), "t ← t + Δt, guarda telemetría en memoria y actualiza gráficas."]),
            ], flush=True, className="small")
        ], className="p-3 bg-white border rounded shadow-sm")
    ])

    tab_pid = html.Div([
        _ecuacion(
            "1. Error de Seguimiento y Ley de Control PID con Feedforward",
            r"e(t) = SP - h_m \qquad \Big| \qquad u(t) = u_{eq} + K_p\,e(t) + K_i \int e(\tau)\,d\tau - K_d\,\frac{dh_f}{dt}",
            "Suma el PWM de equilibrio (u_eq) más las tres acciones correctivas (presente, pasado y futuro). Deriva la altura filtrada para evitar picos al mover el Set Point.",
            [
                (r"$e(t)$", "Error de posición: distancia entre la meta y la lectura del sensor (m)."),
                (r"$SP$", "*Set Point* o altura objetivo deseada (0 a 1.0 m)."),
                (r"$h_m$", "Altura medida por el sensor HC-SR04 (m)."),
                (r"$u(t)$", "Potencia PWM calculada para el ventilador (recortada a $[0\%,\; 100\%]$)."),
                (r"$u_{eq}$", f"PWM base de equilibrio (*feedforward*) para compensar la gravedad (en vivo: **{eq['u_eq']:.1f} %**)."),
                (r"$K_p$", "Ganancia **Proporcional** (presente): reacciona inmediatamente al error actual."),
                (r"$K_i$", "Ganancia **Integral** (pasado): elimina el error permanente acumulado."),
                (r"$K_d$", "Ganancia **Derivativa** (futuro/freno): amortigua movimientos bruscos."),
                (r"$\int e(\tau)\,d\tau$", "Suma acumulada del error en el tiempo (m·s); se congela con Anti-Windup si satura."),
                (r"$\frac{dh_f}{dt}$", "Velocidad estimada de la esfera a partir de la altura filtrada (m/s).")
            ],
            r"Nace de la ecuación clásica del PID sumada al término *feedforward* $u_{eq}$ para vencer la gravedad desde $t = 0$. El signo menos en $-K_d\frac{dh_f}{dt}$ sale porque $e = SP - h$; si $SP$ es constante, $\frac{de}{dt} = -\frac{dh}{dt}$. Derivar $h_f$ en lugar de $e$ evita el *derivative kick* cuando mueves el slider."
        ),
        _ecuacion(
            "2. Filtro Derivativo Paso Bajo + Saturación y Anti-Windup",
            r"\alpha = \frac{\Delta t}{\tau_d + \Delta t} \quad \Big| \quad h_f(k) = h_f(k-1) + \alpha\big(h_m - h_f(k-1)\big) \quad \Big| \quad \frac{dh_f}{dt} = \frac{h_f(k) - h_f(k-1)}{\Delta t}",
            "Suaviza el ruido del sensor antes de derivar. Además, el Anti-Windup congela la integral cuando u(t) toca 0% o 100%.",
            [
                (r"$\alpha$", "Factor de suavizado del filtro paso bajo ($\\alpha = 0.5$ cuando $\\tau_d = \\Delta t = 0.05$ s)."),
                (r"$\Delta t$", f"Periodo de muestreo del bucle de control (**{eq['dt']} s**)."),
                (r"$\tau_d$", "Constante de tiempo del filtro derivativo (**0.05 s**)."),
                (r"$h_f(k),\; h_f(k-1)$", "Altura filtrada (suavizada) en el paso actual y en el paso anterior (m)."),
                (r"$h_m$", "Medición cruda del sensor HC-SR04 en el instante actual (m).")
            ],
            r"El filtro sale de discretizar el filtro paso bajo continuo $\tau_d \frac{dh_f}{dt} + h_f = h_m$ usando diferencias hacia atrás: $\tau_d \frac{h_f(k) - h_f(k-1)}{\Delta t} + h_f(k) = h_m$. Al despejar $h_f(k)$ aparece exactamente $\alpha = \frac{\Delta t}{\tau_d + \Delta t}$."
        )
    ])

    tab_estoc = html.Div([
        _ecuacion(
            "1. Generador Pseudoaleatorio (LCG) y Prueba de Uniformidad χ²",
            r"X_{n+1} = (a\,X_n + c) \bmod m \;\Rightarrow\; R = \frac{X_{n+1}}{m} \qquad \Big| \qquad \chi^2 = \sum_{i=1}^{K} \frac{(O_i - E_i)^2}{E_i}",
            "Genera números uniformes reproducibles en (0, 1) y verifica estadísticamente que no se amontonen en pocos intervalos.",
            [
                (r"$X_n,\; X_{n+1}$", "Estado entero actual y siguiente del generador (inicia en la semilla)."),
                (r"$a,\; c,\; m$", "Parámetros del LCG: multiplicador ($1664525$), incremento ($1013904223$) y módulo ($2^{32}$)."),
                (r"$R$", "Número pseudoaleatorio continuo uniforme $U(0, 1)$."),
                (r"$\chi^2$", "Estadístico Chi-cuadrado de Pearson (aprueba uniformidad si $\\chi^2 < 16.919$)."),
                (r"$K$", "Número de intervalos o cajones en que se divide $(0,1)$ ($K = 10$)."),
                (r"$O_i,\; E_i$", "Frecuencia observada ($O_i$) y esperada ($E_i = N/K = 200$) en el cajón $i$.")
            ],
            r"El LCG viene de la aritmética modular (algoritmo de Lehmer): el residuo $\bmod\,m$ produce enteros en $[0, m-1]$ y dividir entre $m$ los normaliza a $(0,1)$. La prueba $\chi^2$ de Pearson mide si las frecuencias observadas $O_i$ se desvían demasiado de una uniforme ideal ($E_i = N/K$)."
        ),
        _ecuacion(
            "2. Transformada Inversa (Tiempos entre Ráfagas — Exponencial)",
            r"T = -\frac{1}{\lambda}\,\ln(R)",
            "Convierte un número uniforme R en un tiempo de espera realista en segundos entre llegadas de ráfagas de viento (proceso de Poisson).",
            [
                (r"$T$", "Tiempo de espera hasta la llegada de la próxima ráfaga (s)."),
                (r"$\lambda$", "Tasa promedio de llegada de ráfagas por segundo (ej. $0.3$ ráfagas/s)."),
                (r"$\ln$", "Logaritmo natural (función inversa de la exponencial)."),
                (r"$R$", "Variable aleatoria uniforme $U(0, 1)$ entregada por el generador RNG.")
            ],
            r"Sale de la función de distribución acumulada (CDF) exponencial: $F(T) = 1 - e^{-\lambda T}$. Igualando $F(T) = U \sim U(0,1)$, obtenemos $e^{-\lambda T} = 1 - U$. Como $1 - U$ también es uniforme en $(0,1)$, se renombra como $R$ y al aplicar $\ln$ a ambos lados se despeja $T = -\frac{1}{\lambda}\ln(R)$."
        ),
        _ecuacion(
            "3. Perfil Suave de Ráfaga de Viento (Ventana de Hann)",
            r"w(t) = A_{raf}\,\sin^2\!\left(\pi\,\frac{t - t_0}{\text{dur}}\right)",
            "Evita escalones irreales: la ráfaga nace suavemente en 0, alcanza su pico máximo en la mitad y decae suavemente a 0.",
            [
                (r"$w(t)$", "Velocidad de la ráfaga de viento en el instante $t$ (m/s)."),
                (r"$A_{raf}$", "Amplitud pico aleatoria de la ráfaga (entre 80% y 120% de la amplitud configurada)."),
                (r"$t$", "Tiempo actual del reloj de simulación (s)."),
                (r"$t_0$", "Instante exacto en que inició la ráfaga actual (s)."),
                (r"$\text{dur}$", "Duración total de la ráfaga (exponencial acotada entre 0.4 s y 3.0 s).")
            ],
            r"Es una ventana de Hann: en $t = t_0$, $\sin(0) = 0$; a la mitad de la ráfaga, $\sin(\pi/2) = 1$ (pico $A_{raf}$); al finalizar, $\sin(\pi) = 0$. Elevar al cuadrado garantiza suavidad en los bordes y signo consistente."
        )
    ])

    tab_mc = html.Div([
        _ecuacion(
            "1. Simulación de Monte Carlo (Análisis de Riesgo y Robustez)",
            r"\text{semilla}_i = \text{seed} + 7919 \cdot i \quad (i = 0,1,\dots,N-1) \;\Rightarrow\; P_5,\; P_{50},\; P_{95}",
            "Ejecuta N corridas paralelas con ráfagas independientes para cuantificar la probabilidad real de falla y los corredores de trayectoria.",
            [
                (r"$\text{semilla}_i$", "Semilla independiente asignada a la corrida número $i$."),
                (r"$\text{seed}$", "Semilla base ingresada por el usuario (ej. 202624)."),
                (r"$7919$", "Número primo grande que evita correlaciones entre corridas consecutivas."),
                (r"$N$", "Total de simulaciones independientes ($N = 40$ corridas de 8 s)."),
                (r"$P_{50}$", "Percentil 50 (mediana): trayectoria típica esperada de la esfera."),
                (r"$P_5,\; P_{95}$", "Percentiles 5 y 95: corredor que contiene a la esfera el 90% del tiempo.")
            ],
            r"Se fundamenta en la Ley de los Grandes Números: al repetir el experimento estocástico $N$ veces con semillas independientes, la frecuencia empírica de eventos críticos (chocar con la tapa, saturar PWM o desviarse $>10\text{ cm}$) converge a su probabilidad real."
        ),
        _ecuacion(
            "2. Métricas de Desempeño de Control (IAE y Sobreimpulso)",
            r"\text{IAE} = \int |h(t) - SP|\,dt \approx \sum |h_k - SP|\,\Delta t \qquad \Big| \qquad \text{Sobreimpulso} = \frac{h_{\max} - SP}{SP} \times 100\%",
            "Cuantifican objetivamente la precisión acumulada y el exceso de altura del controlador PID.",
            [
                (r"$\text{IAE}$", "Error Absoluto Integral acumulado durante la corrida (m·s; menor = mejor control)."),
                (r"$h(t),\; h_k$", "Altura real de la esfera en el tiempo $t$ o paso discreto $k$ (m)."),
                (r"$SP$", "Altura objetivo o *Set Point* (m)."),
                (r"$\Delta t$", f"Paso de muestreo del registro (**{eq['dt']} s**)."),
                (r"$h_{\max}$", "Altura máxima (pico más alto) alcanzada antes de estabilizarse (m).")
            ],
            r"El IAE aproxima la integral definida $\int |e(t)|\,dt$ mediante sumas de Riemann (rectángulos de base $\Delta t$ y altura $|h_k - SP|$). El sobreimpulso expresa porcentualmente cuánto excede el pico máximo $h_{\max}$ a la meta $SP$."
        )
    ])

    return tab_newton, tab_euler, tab_pid, tab_estoc, tab_mc


def construir_modulo_matematico():
    """Layout completo de la pestaña 'Modelo Matemático y Formalización'."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5([
                        html.I(className="fa-solid fa-atom me-2"),
                        "Diagrama de Cuerpo Libre — Planta Neumática"
                    ], className="mb-0 text-primary fw-bold")),
                    dbc.CardBody([
                        dcc.Graph(
                            id="grafica-cuerpo-libre",
                            figure=construir_diagrama_cuerpo_libre(),
                            config={"displayModeBar": False},
                            style={"height": "390px"}
                        )
                    ], className="p-2")
                ], className="shadow-sm border-0 mb-3"),

                dbc.Card([
                    dbc.CardHeader(dbc.Tabs([
                        dbc.Tab(label="Newton y Física", tab_id="math-newton", label_style={"fontWeight": "bold", "fontSize": "0.85rem"}),
                        dbc.Tab(label="Euler y Bucle", tab_id="math-euler", label_style={"fontWeight": "bold", "fontSize": "0.85rem"}),
                        dbc.Tab(label="Control PID", tab_id="math-pid", label_style={"fontWeight": "bold", "fontSize": "0.85rem"}),
                        dbc.Tab(label="Estocástico (RNG)", tab_id="math-estoc", label_style={"fontWeight": "bold", "fontSize": "0.85rem"}),
                        dbc.Tab(label="Monte Carlo", tab_id="math-mc", label_style={"fontWeight": "bold", "fontSize": "0.85rem"}),
                    ], id="math-tabs", active_tab="math-newton")),
                    dbc.CardBody([
                        html.Div(id="math-content-newton"),
                        html.Div(id="math-content-euler", style={"display": "none"}),
                        html.Div(id="math-content-pid", style={"display": "none"}),
                        html.Div(id="math-content-estoc", style={"display": "none"}),
                        html.Div(id="math-content-mc", style={"display": "none"}),
                    ], className="bg-light")
                ], className="shadow-sm border-0")
            ], lg=6, className="mb-3"),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5([
                        html.I(className="fa-solid fa-diagram-project me-2"),
                        "Diagrama de Bloques en Lazo Cerrado"
                    ], className="mb-0 text-primary fw-bold")),
                    dbc.CardBody(construir_diagrama_bloques())
                ], className="shadow-sm border-0 mb-3"),

                dbc.Card([
                    dbc.CardHeader(html.H5([
                        html.I(className="fa-solid fa-sitemap me-2"),
                        "Anatomía Formal del Sistema (Frontera, Estados y Parámetros)"
                    ], className="mb-0 text-primary fw-bold")),
                    dbc.CardBody(construir_anatomia_sistema())
                ], className="shadow-sm border-0 mb-3"),

                dbc.Card([
                    dbc.CardHeader(html.H5([
                        html.I(className="fa-solid fa-table me-2"),
                        "Diccionario de Variables y Parámetros Físicos"
                    ], className="mb-0 text-primary fw-bold")),
                    dbc.CardBody(construir_tabla_parametros(), className="p-2")
                ], className="shadow-sm border-0")
            ], lg=6)
        ])
    ])
