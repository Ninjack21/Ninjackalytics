import dash

# TODO: go find an example starter dash app and copy its layout
# TODO: perhaps find some templates that give you a clean look and feel


def create_app():
    app = dash.Dash(__name__)
    app.layout = html.Div("Hello, world!")
    return app
