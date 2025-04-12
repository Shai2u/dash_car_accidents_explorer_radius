from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Welcome to my Dash App!'),
    html.Div('This is a simple div element.')
])

if __name__ == '__main__':
    app.run_server(debug=True)
