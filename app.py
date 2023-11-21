import dash
import dash_bootstrap_components as dbc


app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

server = app.server

if __name__ == "__main__":
    app.run_server()
