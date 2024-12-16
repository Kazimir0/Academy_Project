from dash import dcc, html

def create_navbar():
    return html.Div([
        # Link to Products Page
        dcc.Link("Products", href="/products", className="navbar-button"),

        # Link to Add New Product Page
        dcc.Link("Add New Product", href="/add-new-product", className="navbar-button"),

        # Button to Logout (or Home page)
        html.Button('Logout', id='logout-button', className='logout-button')
    ], className="navbar")
