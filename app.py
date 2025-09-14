################################
# Libraries
################################
import flask
import pandas as pd
import joblib


################################
# Model Loading
################################
model = joblib.load("model/diabetes_model.pkl")


################################
# Settings
################################
app = flask.Flask(__name__, template_folder="templates", static_folder="static")


################################
# Routes
################################
@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    probability = None

    if flask.request.method == "POST":
        try:
            gender = flask.request.form["gender"]

            input_data = pd.DataFrame({"gender": [gender]})

            prediction = model.predict(input_data)[0]

        except Exception as e:
            prediction = "Error"
            probability = str(e)

    return flask.render_template("index.html", prediction=prediction, probability=probability)


################################
# Execution
################################
if __name__ == "__main__":
    app.run(debug=True)
