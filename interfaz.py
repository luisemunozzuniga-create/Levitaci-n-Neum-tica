import uuid
from dash import dcc, html
import dash_bootstrap_components as dbc
from modulo_matematico import construir_modulo_matematico

def lab(txt, cls="fw-bold text-muted"):
    return html.Label(txt, className=cls)

def serve_layout():
    return dbc.Container([
        html.Div(id="toast-container"),
        dcc.Store(id='sid', data=uuid.uuid4().hex),

        # Encabezado principal
        dbc.Row([dbc.Col(html.Div([
            html.H2([html.I(className="fa-solid fa-microchip me-3"), "Ecosistema de Gemelos Digitales"], className="text-white m-0 fw-bold"),
            html.H5("Planta 1: Levitación Neumática (CB1979) — Simulador y Modelo Matemático", className="text-light m-0 mt-1")
        ], className="bg-primary p-4 rounded-bottom shadow-lg text-center mb-3"), width=12)]),

        # Navegación Principal de Módulos
        dbc.Tabs([
            dbc.Tab(label="1. Simulador y Telemetría en Vivo", tab_id="main-tab-sim",
                    label_style={"fontWeight": "bold", "fontSize": "1.05rem"}),
            dbc.Tab(label="2. Modelo Matemático, Variables y Bucle Universal", tab_id="main-tab-math",
                    label_style={"fontWeight": "bold", "fontSize": "1.05rem"}),
        ], id="main-tabs", active_tab="main-tab-sim", className="mb-3 nav-pills nav-fill bg-white p-2 rounded shadow-sm"),

        # =====================================================================
        # MÓDULO 1: SIMULADOR EN VIVO
        # =====================================================================
        html.Div(id="main-content-sim", children=[
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardHeader(html.H5([html.I(className="fa-solid fa-cube me-2"), "Renderizado Físico 2D"], className="mb-0 text-primary fw-bold")),
                    dbc.CardBody([
                        dcc.Graph(id='grafica-animacion', config={'displayModeBar': False}, style={'height': '600px'}),
                        html.Div(id='indicadores-estado', className="mt-3 text-center fw-bold text-dark fs-6 bg-light p-2 rounded shadow-sm border")
                    ], className="p-2")], className="shadow-lg border-0 h-100"), width=4),

                dbc.Col(dbc.Card([
                    dbc.CardHeader(dbc.Tabs([
                        dbc.Tab(label="Configuración Física", tab_id="tab-fisica", label_style={"fontWeight": "bold"}),
                        dbc.Tab(label="Controlador PID", tab_id="tab-pid", label_style={"fontWeight": "bold"}),
                        dbc.Tab(label="Perturbaciones", tab_id="tab-pert", label_style={"fontWeight": "bold"}),
                        dbc.Tab(label="Prueba RNG", tab_id="tab-rng", label_style={"fontWeight": "bold"}),
                    ], id="tabs", active_tab="tab-pid", className="nav-fill")),
                    dbc.CardBody([
                        # TAB 1: CONFIGURACIÓN FÍSICA (Masa en gramos)
                        html.Div(id="content-fisica", style={'display': 'none'}, children=[dbc.Row([
                            dbc.Col([
                                lab("Masa esfera (g):"),
                                dbc.Input(id="inp-m", type="number", value=8.0, step=0.5, min=0.5),
                                html.Small("Se convierte automáticamente a kg (m / 1000) para Newton.", className="text-muted")
                            ]),
                            dbc.Col([
                                lab("Densidad aire ρ (kg/m³):"),
                                dbc.Input(id="inp-rho", type="number", value=0.95, step=0.05),
                                html.Small("Pasto ≈ 0.95 kg/m³ · Nivel del mar ≈ 1.225.", className="text-muted")
                            ]),
                            dbc.Col([
                                lab("PWM manual (lazo abierto, %):"),
                                dcc.Slider(id="slider-pwm", min=0, max=100, step=0.1, value=55.1,
                                           marks={0: '0%', 55.1: 'Eq', 100: '100%'}, tooltip={"placement": "bottom"})
                            ], width=5),
                            dbc.Col(html.Div(id="info-eq", className="small text-primary fw-bold mt-2"), width=12)
                        ])]),

                        # TAB 2: CONTROLADOR PID (Con significado y efecto de Kp, Ki, Kd)
                        html.Div(id="content-pid", children=[dbc.Row([
                            dbc.Col([
                                lab("Set Point — Altura objetivo (m):", "fw-bold text-primary"),
                                dcc.Slider(id="slider-sp", min=0, max=1.0, step=0.05, value=0.5, marks={0: '0m', 0.5: '0.5m', 1: '1m'})
                            ], width=12, className="mb-3"),
                            dbc.Col([
                                lab("Kp (Proporcional):"),
                                dbc.Input(id="inp-kp", type="number", value=40.0),
                                html.Small([
                                    html.B("Presente: "),
                                    "Reacciona de inmediato al error actual (SP − h). Más Kp = sube más rápido, pero en exceso genera oscilaciones."
                                ], className="text-muted d-block mt-1")
                            ], md=4),
                            dbc.Col([
                                lab("Ki (Integral):"),
                                dbc.Input(id="inp-ki", type="number", value=2.0),
                                html.Small([
                                    html.B("Pasado: "),
                                    "Acumula el error en el tiempo para eliminar desviaciones permanentes. En exceso provoca sobreimpulso."
                                ], className="text-muted d-block mt-1")
                            ], md=4),
                            dbc.Col([
                                lab("Kd (Derivativo):"),
                                dbc.Input(id="inp-kd", type="number", value=30.0),
                                html.Small([
                                    html.B("Futuro (Freno): "),
                                    "Mide qué tan rápido cambia la altura y amortigua el movimiento para evitar que la esfera se pase del Set Point."
                                ], className="text-muted d-block mt-1")
                            ], md=4)
                        ])]),

                        # TAB 3: PERTURBACIONES (Con explicación de variables y comportamiento dinámico del RNG)
                        html.Div(id="content-pert", style={'display': 'none'}, children=[
                            dbc.Row([
                                dbc.Col([
                                    lab("Motor RNG:"),
                                    dbc.Select(id="sel-rng", options=[
                                        {'label': 'LCG Clásico', 'value': 'LCG_CLASICO'},
                                        {'label': 'Von Neumann', 'value': 'VON_NEUMANN'}
                                    ], value='LCG_CLASICO')
                                ], md=4),
                                dbc.Col([
                                    lab("Semilla (Seed):"),
                                    dbc.Input(id="inp-seed", type="number", value=202624),
                                    html.Small("Permite reproducir exactamente las mismas ráfagas.", className="text-muted")
                                ], md=4),
                                dbc.Col([
                                    lab("Amplitud viento (m/s):", "fw-bold text-danger"),
                                    dbc.Input(id="inp-pert-aire", type="number", value=2.5, step=0.5),
                                    html.Small("Fuerza pico de la ráfaga (±20% aleatorio).", className="text-muted")
                                ], md=4),
                            ], className="mb-2"),
                            dbc.Row([
                                dbc.Col([
                                    lab("Tasa λ (ráfagas/s):"),
                                    dbc.Input(id="inp-tasa", type="number", value=0.3, step=0.1),
                                    html.Small("Controla cada cuánto llegan ráfagas: T = −(1/λ)·ln(R).", className="text-muted")
                                ], md=6),
                                dbc.Col([
                                    lab("Duración media (s):"),
                                    dbc.Input(id="inp-dur", type="number", value=1.0, step=0.1),
                                    html.Small("Tiempo promedio que sopla cada ráfaga (perfil sin²).", className="text-muted")
                                ], md=6),
                            ], className="mb-2"),
                            html.Div(id="info-rng-desc", className="mt-2"),
                            html.Div("La semilla y el motor RNG se aplican al pulsar Reiniciar (o al cambiar de escenario).", className="small text-muted mt-1")
                        ]),

                        # TAB 4: PRUEBA RNG
                        html.Div(id="content-rng", style={'display': 'none'}, children=[
                            dbc.Button("Generar y Validar Transformada Inversa", id="btn-rng", color="primary", className="mb-2 w-100"),
                            html.Div(id="txt-rng", className="fw-bold text-center mb-1"),
                            dbc.Row([
                                dbc.Col(dcc.Graph(id="graf-rng", style={'height': '220px'}), width=6),
                                dbc.Col(dcc.Graph(id="graf-exp", style={'height': '220px'}), width=6)
                            ])]),

                        html.Hr(className="my-3"),
                        dbc.Row([
                            dbc.Col(dbc.Select(id='select-escenario', options=[
                                {'label': 'Escenario 1: Lazo Abierto (Sin Control)', 'value': '1'},
                                {'label': 'Escenario 2: Lazo Cerrado (PID)', 'value': '2'},
                                {'label': 'Escenario 3: Lazo Abierto + Viento Estocástico', 'value': '3'},
                                {'label': 'Escenario 4: PID + Viento Estocástico', 'value': '4'},
                                {'label': 'Análisis de Riesgo: Monte Carlo (40 corridas)', 'value': 'MC'}], value='4',
                                className="shadow-sm border-primary fw-bold text-primary"), width=5),
                            dbc.Col(dbc.ButtonGroup([
                                dbc.Button([html.I(className="fa-solid fa-play me-2"), "Iniciar"], id="btn-play", color="success", className="fw-bold"),
                                dbc.Button([html.I(className="fa-solid fa-pause me-2"), "Pausar"], id="btn-pause", color="warning", className="fw-bold"),
                                dbc.Button([html.I(className="fa-solid fa-stop me-2"), "Reiniciar"], id="btn-reset", color="danger", className="fw-bold"),
                                dbc.Button([html.I(className="fa-solid fa-download me-2"), "CSV"], id="btn-csv", color="info", className="fw-bold text-white")
                            ], className="w-100"), width=7)], className="align-items-center mb-3"),
                        dcc.Download(id="download-dataframe-csv"),
                        dbc.Card(dbc.CardBody(dcc.Graph(id='grafica-osciloscopio', style={'height': '380px'}), className="p-1 bg-dark rounded"),
                                 className="shadow-sm border-0 mt-2"),
                        html.Div(id='metricas-panel', className="mt-3 text-primary fs-6"),

                        dbc.Card([
                            dbc.CardHeader(html.H5([html.I(className="fa-solid fa-terminal me-2"), "Monitor Matemático en Tiempo Real (Depuración Académica)"], className="mb-0 text-success fw-bold")),
                            dbc.CardBody(html.Div(id='panel-matematico', className="font-monospace small"), style={'backgroundColor': '#1e272e', 'color': '#2ecc71', 'height': '320px', 'overflowY': 'auto'})
                        ], className="shadow-sm border-0 mt-3"),
                    ])], className="shadow-lg border-0"), width=8)
            ])
        ]),

        # =====================================================================
        # MÓDULO 2: EXPLICACIÓN DEL MODELO MATEMÁTICO Y FORMALIZACIÓN
        # =====================================================================
        html.Div(id="main-content-math", style={'display': 'none'}, children=[
            construir_modulo_matematico()
        ]),

        dcc.Interval(id='sim-interval', interval=350, n_intervals=0, disabled=True)
    ], fluid=True, className="bg-light pb-5")
