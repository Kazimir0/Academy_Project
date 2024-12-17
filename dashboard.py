import base64
import dash
from dash import dcc, html, Input, Output, State
import requests
import pandas as pd
from dash.dash_table import DataTable  # Import DataTable for displaying table
from navbar import create_navbar

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Product Dashboard"
API_BASE_URL = "http://127.0.0.1:8000"  # FastAPI endpoint

# Layout
app.layout = html.Div([

    # Navbar Section (initially hidden)
    html.Div(create_navbar(), id="navbar", style={"display": "none"}),

    # Header (initially hidden)
    html.H1("Product Management Dashboard", id="dashboard-header", className="header", style={"display": "none"}),

    # Store the authentication status
    dcc.Store(id="auth-store", storage_type="session"),

    # Form Login (visible initially)
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

    # Placeholder for product list (Table of products)
    html.Div(id="product-list", children=[], className="product-list"),

    # Container for success or error messages
    html.Div(id="message-container", children=[], className="message-container"),

    # Interval to hide the message after 3 seconds
    dcc.Interval(id="hide-message", interval=3000, n_intervals=0),
])

# Combined callback for login, product listing, and product addition
@app.callback(
    [
        Output("login-message", "children"),
        Output("product-form-section", "style"),
        Output("login-form", "style"),
        Output("navbar", "style"),
        Output("dashboard-header", "style"),
        Output("auth-store", "data"),
        Output("product-list", "children"),
        Output("product-name", "value"),
        Output("product-description", "value"),
        Output("product-price", "value"),
        Output("product-image", "contents"),
        Output("product-image", "filename"),
        Output("message-container", "children"),
    ],
    [
        Input("login-button", "n_clicks"),
        Input("logout-button", "n_clicks"),
        Input("add-product-button", "n_clicks"),
        Input("hide-message", "n_intervals"),
    ],
    [
        State("login-username", "value"),
        State("login-password", "value"),
        State("auth-store", "data"),
        State("product-name", "value"),
        State("product-description", "value"),
        State("product-price", "value"),
        State("product-image", "contents"),
        State("product-image", "filename"),
        State("message-container", "children"),
    ]
)
def manage_login_logout_and_product_addition(
    login_clicks, logout_clicks, add_product_clicks, hide_message_clicks,
    username, password, auth_data, name, description, price, image_contents, image_filename, current_message
):
    # Ensure clicks are integers (defaulting to 0 if None)
    login_clicks = login_clicks or 0
    logout_clicks = logout_clicks or 0
    add_product_clicks = add_product_clicks or 0
    hide_message_clicks = hide_message_clicks or 0

    triggered_id = dash.callback_context.triggered_id

    # Handle login logic
    if triggered_id == "login-button" and login_clicks > 0:
        if not username or not password:
            return (
                "Please enter both username and password.", {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, None, [], 
                name, description, price, image_contents, image_filename, current_message
            )
        try:
            response = requests.post(f"{API_BASE_URL}/login/", data={"username": username, "password": password})
            if response.status_code == 200:
                # Successful login
                user_data = response.json()
                user_id = user_data.get("user_id")

                # Fetch the product data here
                products_response = requests.get(f"{API_BASE_URL}/products/")
                if products_response.status_code == 200:
                    products = products_response.json()
                    product_table = create_product_table(products)
                else:
                    product_table = html.Div("Error loading product data.", className="error-message")

                return (
                    f"Login successful! User ID: {user_id}", 
                    {'display': 'block'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'},
                    {"user_id": user_id}, product_table,
                    "", "", 0, None, "", []
                )
            else:
                return (
                    "Invalid username or password.", {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, None, [], 
                    name, description, price, image_contents, image_filename, current_message
                )
        except requests.exceptions.RequestException as e:
            return (
                f"Error connecting to server: {str(e)}", {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, None, [], 
                name, description, price, image_contents, image_filename, current_message
            )

    # Handle logout logic
    if triggered_id == "logout-button" and logout_clicks > 0:
        return (
            "You have been logged out.", {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, None, [], 
            name, description, price, image_contents, image_filename, current_message
        )

    # Handle product addition logic
    if triggered_id == "add-product-button" and add_product_clicks > 0:
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

    if hide_message_clicks > 0 and current_message:
        return dash.no_update

    return dash.no_update


# Function to create the product table from fetched data
def create_product_table(products):
    # Convert the product data into a DataFrame
    if not products:
        return html.Div("No products found.", className="error-message")

    df = pd.DataFrame(products)
    return html.Div([
        DataTable(
            id="product-table",
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
        )
    ])

if __name__ == "__main__":
    app.run_server(debug=True)
