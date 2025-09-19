################################
# Libraries
################################
import flask
import pandas as pd
import joblib
import numpy as np
import psycopg2
import os
import dotenv
import secrets


################################
# Settings
################################
app = flask.Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


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
# Database Setup
################################
def get_db_connection():
    dotenv.load_dotenv()
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password,
    )

    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP(0),
            gender TEXT,
            age INT,
            hypertension INT,
            heart_disease INT,
            smoking_history TEXT,
            bmi FLOAT,
            hba1c_level FLOAT,
            blood_glucose_level FLOAT,
            prediction INT,
            probability FLOAT
        )
    """,
    )

    conn.commit()
    conn.close()


def save_preddiction(form_data, prediction, probability):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO predictions (
            gender, age, hypertension, heart_disease, smoking_history, bmi, hba1c_level, blood_glucose_level, prediction, probability
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            form_data["gender"],
            int(form_data["age"]),
            int(form_data["hypertension"]),
            int(form_data["heart_disease"]),
            form_data["smoking_history"],
            float(form_data["bmi"]),
            float(form_data["hba1c_level"]),
            float(form_data["blood_glucose_level"]),
            int(prediction),
            round(float(probability), 2),
        ),
    )

    conn.commit()
    conn.close()


################################
# Authentication
################################
def login_required(f):
    def decorated_function(*args, **kwargs):
        if not flask.session.get("logged_in"):
            return flask.redirect(flask.url_for("login", next=flask.request.url))
        return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__

    return decorated_function


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

            save_preddiction(flask.request.form, prediction, probability)

        except Exception as e:
            prediction = "Error"
            probability = str(e)

    return flask.render_template("index.html", prediction=prediction, probability=probability)


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "POST":
        username = flask.request.form["username"]
        password = flask.request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            flask.session["logged_in"] = True
            return flask.redirect(flask.url_for("index"))
        else:
            flask.flash("Invalid credentials. Please try again..")

    return flask.render_template("login.html")


@app.route("/data")
@login_required
def show_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions LIMIT 10")
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        return flask.render_template("data.html", data=data, columns=columns)

    except Exception as e:
        return f"Error accessing database: {str(e)}"


@app.route("/dash")
def dash():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Basic statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total_predictions,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as positive_cases,
                SUM(CASE WHEN prediction = 0 THEN 1 ELSE 0 END) as negative_cases,
                AVG(probability) as avg_probability
            FROM predictions
        """)
        stats = cursor.fetchall()

        # Distribution by age group
        cursor.execute("""
            SELECT
                CASE
                    WHEN age < 30 THEN 'Menos 30'
                    WHEN age BETWEEN 30 AND 45 THEN '30-45'
                    WHEN age BETWEEN 46 AND 60 THEN '46-60'
                    ELSE 'Mais 60'
                END as age_group,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM predictions), 2) as percentage
            FROM predictions
            GROUP BY age_group
        """)
        age_distribution = cursor.fetchall()

        # Distribution by gender
        cursor.execute("""
            SELECT
                gender,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM predictions), 2) as percentage
            FROM predictions
            GROUP BY gender
        """)
        gender_distribution = cursor.fetchall()

        # Top risk factors
        cursor.execute("""
            SELECT
                COALESCE(ROUND(CAST(AVG(age) FILTER (WHERE prediction = 1) AS NUMERIC), 1), 0) as avg_age_positive,
                COALESCE(ROUND(CAST(AVG(age) FILTER (WHERE prediction = 0) AS NUMERIC), 1), 0) as avg_age_negative,
                COALESCE(ROUND(CAST(AVG(bmi) FILTER (WHERE prediction = 1) AS NUMERIC), 2), 0) as avg_bmi_positive,
                COALESCE(ROUND(CAST(AVG(bmi) FILTER (WHERE prediction = 0) AS NUMERIC), 2), 0) as avg_bmi_negative,
                COALESCE(ROUND(CAST(AVG(hba1c_level) FILTER (WHERE prediction = 1) AS NUMERIC), 2), 0) as avg_hba1c_positive,
                COALESCE(ROUND(CAST(AVG(hba1c_level) FILTER (WHERE prediction = 0) AS NUMERIC), 2), 0) as avg_hba1c_negative,
                COALESCE(ROUND(CAST(AVG(blood_glucose_level) FILTER (WHERE prediction = 1) AS NUMERIC), 2), 0) as avg_glucose_positive,
                COALESCE(ROUND(CAST(AVG(blood_glucose_level) FILTER (WHERE prediction = 0) AS NUMERIC), 2), 0) as avg_glucose_negative
            FROM predictions
        """)
        risk_factors = cursor.fetchone()

        # Distribution by smoking history
        cursor.execute("""
            SELECT
                smoking_history,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 /(SELECT COUNT(*) FROM predictions), 2) as percentage,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as positive_cases,
                AVG(probability) as avg_probability
            FROM predictions
            GROUP BY smoking_history
            ORDER BY count DESC
        """)
        smoking_distribution = cursor.fetchall()

        total = stats[0][0] or 1
        positive_rate = round((stats[0][1] / total) * 100, 2) if total > 0 else 0
        negative_rate = round((stats[0][2] / total) * 100, 2) if total > 0 else 0

        # Diabetes rate by hypertension condition
        cursor.execute("""
            SELECT
                hypertension AS com_hipertensao,
                COUNT(*) AS total_patients,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as diabetes_cases,
                ROUND((SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS diabetes_rates_hypertension
            FROM predictions
            GROUP BY hypertension
        """)
        hypertension_distribution = cursor.fetchall()

        # Diabetes rate by heart disease condition
        cursor.execute("""
            SELECT
                heart_disease AS and_heart_disease,
                COUNT(*) AS total_patients,
                SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) AS diabetes_cases,
                ROUND((SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) AS diabetes_rates_heart_disease
            FROM predictions
            GROUP BY heart_disease
        """)
        heart_disease_distribution = cursor.fetchall()

        return flask.render_template(
            "dashboard.html",
            stats=stats,
            age_distribution=age_distribution,
            gender_distribution=gender_distribution,
            risk_factors=risk_factors,
            positive_rate=positive_rate,
            negative_rate=negative_rate,
            smoking_distribution=smoking_distribution,
            hypertension_distribution=hypertension_distribution,
            heart_disease_distribution=heart_disease_distribution,
        )

    except Exception as e:
        return f"Erro ao carregar dashboard: {str(e)}"


################################
# Initialization
################################
init_db()


################################
# Execution
################################
if __name__ == "__main__":
    app.run(debug=True)
