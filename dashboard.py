import base64
import dash
from dash import dcc, html, Input, Output, State
import requests
from navbar import create_navbar

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Product Dashboard"
API_BASE_URL = "http://127.0.0.1:8000"  # FastAPI endpoint

# Layout
app.layout = html.Div([

    # Navbar Section (imported from navbar.py)
    create_navbar(),

    # Header
    html.H1("Product Management Dashboard", className="header"),

    # Store the authentication status
    dcc.Store(id="auth-store", storage_type="session"),

    # Form Login (hidden after login)
    html.Div([ 
        html.H2("Login", className="section-header"),
        html.Label("Username:", className="form-label"),
        dcc.Input(id="login-username", type="text", className="input-field", placeholder="Enter username", value=""),
        html.Label("Password:", className="form-label"),
        dcc.Input(id="login-password", type="password", className="input-field", placeholder="Enter password", value=""),
        html.Button("Login", id="login-button", n_clicks=0, className="btn"),
        html.Div(id="login-message", className="message-container")
    ], id="login-form", className="form-section"),

    # Form Section for adding product (hidden until login is successful)
    html.Div(id="product-form-section", children=[ 
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


# Combined callback for login and logout actions
@app.callback(
    [
        Output("login-message", "children"),
        Output("product-form-section", "style"),
        Output("login-form", "style"),
        Output("auth-store", "data")
    ],
    [
        Input("login-button", "n_clicks"),
        Input("logout-button", "n_clicks"),
    ],
    [
        State("login-username", "value"),
        State("login-password", "value"),
        State("auth-store", "data"),
    ]
)
def manage_login_logout(login_clicks, logout_clicks, username, password, auth_data):
    # Ensure clicks are integers (defaulting to 0 if None)
    login_clicks = login_clicks or 0
    logout_clicks = logout_clicks or 0

    # Check which button was clicked
    triggered_id = dash.callback_context.triggered_id
    
    # Logic for login
    if triggered_id == "login-button" and login_clicks > 0:
        if not username or not password:
            return html.Div("Please enter both username and password.", className="error-message"), {'display': 'none'}, {'display': 'block'}, None
        
        try:
            response = requests.post(f"{API_BASE_URL}/login/", data={"username": username, "password": password})
            if response.status_code == 200:
                # Successful login
                user_data = response.json()
                user_id = user_data.get("user_id")
                return html.Div(f"Login successful! User ID: {user_id}", className="success-message"), {'display': 'block'}, {'display': 'none'}, {"user_id": user_id}
            else:
                return html.Div("Invalid username or password.", className="error-message"), {'display': 'none'}, {'display': 'block'}, None
        except requests.exceptions.RequestException as e:
            return html.Div(f"Error connecting to server: {str(e)}", className="error-message"), {'display': 'none'}, {'display': 'block'}, None
    
    # Logic for logout
    if triggered_id == "logout-button" and logout_clicks > 0:
        return html.Div("You have been logged out.", className="success-message"), {'display': 'none'}, {'display': 'block'}, None
    
    # Handle case where the user is already logged in
    if auth_data and "user_id" in auth_data:
        return "", {'display': 'block'}, {'display': 'none'}, auth_data
    
    # If no action is triggered, show login form
    return "", {'display': 'none'}, {'display': 'block'}, None


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
