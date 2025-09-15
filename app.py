################################
# Libraries
################################
import flask
import pandas as pd
import joblib
import numpy as np


################################
# Model Loading
################################
model = joblib.load("model/diabetes_model.pkl")
scaler = joblib.load("model/scaler.pkl")
pca = joblib.load("model/pca.pkl")
gender_encoder = joblib.load("model/gender_encoder.pkl")
smoking_encoder = joblib.load("model/smoking_encoder.pkl")
feature_names = joblib.load("model/feature_names.pkl")


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
            age = float(flask.request.form["age"])
            hypertension = int(flask.request.form["hypertension"])
            heart_disease = int(flask.request.form["heart_disease"])
            smoking_history = flask.request.form["smoking_history"]
            bmi = float(flask.request.form["bmi"])
            hba1c_level = float(flask.request.form["hba1c_level"])
            blood_glucose_level = float(flask.request.form["blood_glucose_level"])

            gender_encoded = gender_encoder.transform([gender])[0]
            smoking_encoded = smoking_encoder.transform([smoking_history])[0]

            """
            input_data = pd.DataFrame(
                {
                    "gender": [gender_encoded],
                    "age": [age],
                    "hypertension": [hypertension],
                    "heart_disease": [heart_disease],
                    "smoking_history": [smoking_encoded],
                    "bmi": [bmi],
                    "HbA1c_level": [hba1c_level],
                    "blood_glucose_level": [blood_glucose_level],
                },
            )
            """
            input_data = np.array(
                [
                    [
                        gender_encoded,
                        age,
                        hypertension,
                        heart_disease,
                        smoking_encoded,
                        bmi,
                        hba1c_level,
                        blood_glucose_level,
                    ],
                ],
            )

            input_df = pd.DataFrame(input_data, columns=feature_names)

            input_scaled = scaler.transform(input_df)

            input_pca = pca.transform(input_scaled)

            prediction = model.predict(input_pca)[0]
            probability = model.predict_proba(input_pca)[0][1]

        except Exception as e:
            prediction = "Error"
            probability = str(e)

    return flask.render_template("index.html", prediction=prediction, probability=probability)


################################
# Execution
################################
if __name__ == "__main__":
    app.run(debug=True)
