import base64
import dash
from dash import dcc, html, Input, Output, State
import requests
from navbar import create_navbar  # Importă funcția din navbar.py

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Product Dashboard"
API_BASE_URL = "http://127.0.0.1:8000/products/"  # FastAPI endpoint

# Define default values
DEFAULT_NAME = ""
DEFAULT_DESCRIPTION = ""
DEFAULT_PRICE = 0
DEFAULT_IMAGE_CONTENTS = None
DEFAULT_IMAGE_FILENAME = ""

# Layout
app.layout = html.Div([

    # Navbar Section (importat din navbar.py)
    create_navbar(),  # Adăugăm navbar-ul în layout-ul aplicației

    # Header
    html.H1("Product Management Dashboard", className="header"),

    # Form Section for adding product
    html.Div([
        html.Label("Product Name:", className="form-label"),
        dcc.Input(
            id="product-name",
            type="text",
            value=DEFAULT_NAME,
            className="input-field",
            placeholder="Enter product name"
        ),

        html.Label("Description:", className="form-label"),
        dcc.Input(
            id="product-description",
            type="text",
            value=DEFAULT_DESCRIPTION,
            className="input-field",
            placeholder="Enter product description"
        ),

        html.Label("Price:", className="form-label"),
        dcc.Input(
            id="product-price",
            type="number",
            value=DEFAULT_PRICE,
            className="input-field",
            placeholder="Enter product price"
        ),

        html.Label("Upload Image:", className="form-label"),
        dcc.Upload(
            id="product-image",
            children=html.Button("Upload Image", className="btn"),
            multiple=False
        ),

        html.Button("Add Product", id="add-product-button", n_clicks=0, className="btn"),
    ], className="form-section"),

    # Placeholder for product list
    html.Div(id="product-list", children=[], className="product-list"),

    # Container for success or error messages
    html.Div(id="message-container", children=[], className="message-container"),

    # Interval to hide the message after 3 seconds
    dcc.Interval(
        id="hide-message",
        interval=3000,  # 3 seconds
        n_intervals=0,
    ),
])

# Callback to handle "Add Product" button click and hide message after interval
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
    [Input("add-product-button", "n_clicks"),
     Input("hide-message", "n_intervals")],
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
    # Handle form submission
    if n_clicks > 0:
        # Set default values for fields if they are None or empty
        name = name or DEFAULT_NAME
        description = description or DEFAULT_DESCRIPTION
        price = price or DEFAULT_PRICE
        image_contents = image_contents or DEFAULT_IMAGE_CONTENTS
        image_filename = image_filename or DEFAULT_IMAGE_FILENAME

        # Validate form fields
        if not all([name, description, price, image_contents]):
            return dash.no_update, name, description, price, image_contents, image_filename, html.Div("Please fill in all fields and upload an image.", className="error-message")

        # Process the uploaded image directly
        try:
            # Extract file content (in base64 format)
            header, base64_image = image_contents.split(",")
            image_data = base64.b64decode(base64_image)
        except Exception as e:
            return dash.no_update, name, description, price, image_contents, image_filename, html.Div(f"Error decoding image: {str(e)}", style={"color": "red"})

        # Prepare payload for the backend
        files = {
            "image": (image_filename, image_data),  # Send the file as binary data
        }
        data = {
            "name": name,
            "description": description,
            "price": float(price),
        }

        try:
            # Make a POST request to FastAPI with the file and data
            response = requests.post(API_BASE_URL, data=data, files=files)
            response.raise_for_status()

            # Return success message and clear the fields
            success_message = html.Div("Product added successfully!", className="success-message")
            return dash.no_update, "", "", 0, None, "", success_message
        except requests.exceptions.RequestException as e:
            return dash.no_update, name, description, price, image_contents, image_filename, html.Div(f"Error: {str(e)}", style={"color": "red"})

    # Handle interval (hide message after 3 seconds)
    if n_intervals > 0 and current_message:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, []

    return dash.no_update

if __name__ == "__main__":
    app.run_server(debug=True)
