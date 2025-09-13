################################
# Libraries
################################
import flask

################################
# Model Loading
################################


################################
# Settings
################################
app = flask.Flask(__name__, template_folder="templates", static_folder="static")


################################
# Routes
################################
@app.route("/", methods=["GET", "POST"])
def index():
    return flask.render_template("index.html")


################################
# Execution
################################
if __name__ == "__main__":
    app.run(debug=True)
