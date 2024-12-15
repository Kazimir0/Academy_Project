import base64
import dash
from dash import dcc, html, Input, Output, State
import requests
from navbar import create_navbar  # Importă funcția din navbar.py

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Product Dashboard"
API_BASE_URL = "http://127.0.0.1:8000"  # FastAPI endpoint

# Layout
app.layout = html.Div([

    # Navbar Section (importat din navbar.py)
    create_navbar(),  # Adăugăm navbar-ul în layout-ul aplicației

    # Header
    html.H1("Product Management Dashboard", className="header"),

    # Form Login
    html.Div([ 
        html.H2("Login", className="section-header"),
        html.Label("Username:", className="form-label"),
        dcc.Input(id="login-username", type="text", className="input-field", placeholder="Enter username", value=""),  # Added value=""
        html.Label("Password:", className="form-label"),
        dcc.Input(id="login-password", type="password", className="input-field", placeholder="Enter password", value=""),  # Added value=""
        html.Button("Login", id="login-button", n_clicks=0, className="btn"),
        html.Div(id="login-message", className="message-container")
    ], className="form-section"),

    # Form Section for adding product (hidden initially)
    html.Div(id="product-form", children=[
        html.Label("Product Name:", className="form-label"),
        dcc.Input(id="product-name", type="text", value="", className="input-field", placeholder="Enter product name"),

        html.Label("Description:", className="form-label"),
        dcc.Input(id="product-description", type="text", value="", className="input-field", placeholder="Enter product description"),

        html.Label("Price:", className="form-label"),
        dcc.Input(id="product-price", type="number", value=0, className="input-field", placeholder="Enter product price"),

        html.Label("Upload Image:", className="form-label"),
        dcc.Upload(id="product-image", children=html.Button("Upload Image", className="btn"), multiple=False),

        html.Button("Add Product", id="add-product-button", n_clicks=0, className="btn"),
    ], className="form-section", style={'display': 'none'}),

    # Placeholder for product list
    html.Div(id="product-list", children=[], className="product-list"),

    # Container for success or error messages
    html.Div(id="message-container", children=[], className="message-container"),

    # Interval to hide the message after 3 seconds
    dcc.Interval(id="hide-message", interval=3000, n_intervals=0),
])

# Callback for login
@app.callback(
    Output("login-message", "children"),
    Output("product-form", "style"),
    Input("login-button", "n_clicks"),
    [State("login-username", "value"), State("login-password", "value")]
)
def login_user(n_clicks, username, password):
    if n_clicks > 0:
        try:
            response = requests.post(f"{API_BASE_URL}/login/", data={"username": username, "password": password})
            if response.status_code == 200:
                # Extract user_id from the response
                user_data = response.json()
                user_id = user_data.get("user_id")  # This is the user_id sent from the backend
                
                # Optionally, you could store the user_id in a session or token
                return html.Div(f"Login successful! User ID: {user_id}", className="success-message"), {'display': 'block'}
            else:
                return html.Div("Invalid username or password.", className="error-message"), {'display': 'none'}
        except requests.exceptions.RequestException as e:
            return html.Div(f"Error connecting to server: {str(e)}", className="error-message"), {'display': 'none'}
    return "", {'display': 'none'}

# Callback for adding product
@app.callback(
    [
        Output("product-list", "children"),
        Output("product-name", "value"),
        Output("product-description", "value"),
        Output("product-price", "value"),
        Output("product-image", "contents"),
        Output("product-image", "filename"),
        Output("message-container", "children"),
    ],
    [Input("add-product-button", "n_clicks"), Input("hide-message", "n_intervals")],
    [
        State("product-name", "value"),
        State("product-description", "value"),
        State("product-price", "value"),
        State("product-image", "contents"),
        State("product-image", "filename"),
        State("message-container", "children"),
    ]
)
def add_product_and_hide_message(n_clicks, n_intervals, name, description, price, image_contents, image_filename, current_message):
    if n_clicks > 0:
        if not all([name, description, price, image_contents]):
            return dash.no_update, name, description, price, image_contents, image_filename, html.Div("Please fill in all fields and upload an image.", className="error-message")

        try:
            header, base64_image = image_contents.split(",")
            image_data = base64.b64decode(base64_image)
        except Exception as e:
            return dash.no_update, name, description, price, image_contents, image_filename, html.Div(f"Error decoding image: {str(e)}", className="error-message")

        files = {"image": (image_filename, image_data)}
        data = {"name": name, "description": description, "price": float(price)}

        try:
            response = requests.post(f"{API_BASE_URL}/products/", data=data, files=files)
            response.raise_for_status()
            success_message = html.Div("Product added successfully!", className="success-message")
            return dash.no_update, "", "", 0, None, "", success_message
        except requests.exceptions.RequestException as e:
            return dash.no_update, name, description, price, image_contents, image_filename, html.Div(f"Error adding product: {str(e)}", className="error-message")

    if n_intervals > 0 and current_message:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, []

    return dash.no_update

if __name__ == "__main__":
    app.run_server(debug=True)
