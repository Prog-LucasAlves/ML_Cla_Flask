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
    """
    Creates and returns a connection to the PostgreSQL database.

    This function loads environment variables and establishes a database
    connection using psycopg2. The connection parameters are retrieved
    from environment variables for security.

    Environment Variables Used:
        - DB_HOST: Database host name or IP address
        - DB_PORT: Database port number (default PostgreSQL port is 5432)
        - DB_NAME: Name of the database to connect to
        - DB_USER: Database username for authentication
        - DB_PASSWORD: Database password for authentication

    Returns:
        psycopg2.extensions.connection: A PostgreSQL database connection object

    """

    dotenv.load_dotenv()
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

    return conn


def init_db():
    """
    Initializes the database by creating the predictions table if it doesn't exist.

    This function establishes a database connection, creates a table for storing
    diabetes prediction results with appropriate schema, and ensures the changes
    are committed to the database.

    Table Schema:
        - id: Primary key (auto-incrementing integer)
        - date: Timestamp of when the prediction was stored (defaults to current time)
        - gender: Text field for gender information
        - age: Integer field for age
        - hypertension: Integer flag for hypertension (0 or 1)
        - heart_disease: Integer flag for heart disease (0 or 1)
        - smoking_history: Text field for smoking history
        - bmi: Floating point number for Body Mass Index
        - hba1c_level: Floating point number for HbA1c level
        - blood_glucose_level: Floating point number for blood glucose level
        - prediction: Integer field for the prediction result (0 or 1)
        - probability: Floating point number for prediction probability confidence

    Operations:
        - Creates table 'predictions' with specified schema if it doesn't exist
        - Uses IF NOT EXISTS to avoid errors if table already exists
        - Sets default timestamp for the date column
        - Commits changes and closes the database connection
    """

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
    """
    Saves a diabetes prediction result to the database.

    This function takes form data and prediction results, converts them to
    appropriate data types, and inserts them into the predictions table.

    Parameters:
        form_data (dict): A dictionary containing form input data with keys:
            - gender (str): Gender information
            - age (str): Age as string (converted to int)
            - hypertension (str): Hypertension flag as string (converted to int)
            - heart_disease (str): Heart disease flag as string (converted to int)
            - smoking_history (str): Smoking history information
            - bmi (str): Body Mass Index as string (converted to float)
            - hba1c_level (str): HbA1c level as string (converted to float)
            - blood_glucose_level (str): Blood glucose level as string (converted to float)

        prediction (int or compatible): The prediction result (0 or 1)
        probability (float or compatible): The prediction probability confidence

    Operations:
        - Establishes database connection
        - Inserts a new record into the predictions table
        - Converts form string data to appropriate data types
        - Rounds probability to 2 decimal places for storage
        - Commits the transaction and closes the connection
    """
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


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = flask.request.json

        gender = data["gender"]
        age = float(data["age"])
        hypertension = int(data["hypertension"])
        heart_disease = int(data["heart_disease"])
        smoking_history = data["smoking_history"]
        bmi = float(data["bmi"])
        hba1c_level = float(data["hba1c_level"])
        blood_glucose_level = float(data["blood_glucose_level"])

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

        save_preddiction(data, prediction, probability)

        return flask.jsonify(
            {"prediction": int(prediction), "probability": float(probability), "status": "success"},
        )

    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500


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


@app.route("/logout")
def logout():
    flask.session.pop("logged_in", None)
    return flask.redirect(flask.url_for("index"))


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
