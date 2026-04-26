from dash import Dash
import interface

app = Dash(__name__, assets_folder="../assets/")

interface.register_layout(app)

if __name__ == "__main__":
    app.run(debug=False)
