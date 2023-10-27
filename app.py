import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)

if __name__ == "__main__":
    app.run(debug=True)
