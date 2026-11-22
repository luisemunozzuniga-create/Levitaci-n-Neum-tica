import os
import dash
from interfaz import serve_layout
from controlador import registrar_callbacks
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.LUMEN,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
])
server = app.server
app.title = "Levitación Neumática — Gemelo Digital"

app.layout = serve_layout
registrar_callbacks(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
