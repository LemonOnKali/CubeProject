import os
import mariadb
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, validators
from flask_cors import CORS

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3307")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "tjmsa")

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'tjmsa123'  # Change this to a secret key for your application

CREATE_CAPTEUR_TABLE = """
CREATE TABLE IF NOT EXISTS Capteur (
   Id_Capteur INT AUTO_INCREMENT,
   Nom_capteur VARCHAR(255),
   PRIMARY KEY(Id_Capteur)
);
"""

CREATE_DONNEES_TABLE = """
CREATE TABLE IF NOT EXISTS Donnees (
   ID INT AUTO_INCREMENT,
   va_Temperature DECIMAL(5,2),
   va_Humidite DECIMAL(5,2),
   va_Pression INT,
   Date_mesure DATETIME DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY(ID)
);
"""

class DonneesForm(FlaskForm):
    va_Temperature = DecimalField('Température', [validators.DataRequired()])
    va_Humidite = DecimalField('Humidité', [validators.DataRequired()])
    va_Pression = IntegerField('Pression', [validators.DataRequired()])

def initialize_database():
    with app.app_context():
        connection = connect_to_database()
        with connection.cursor() as cursor:
            cursor.execute(CREATE_DONNEES_TABLE)
            cursor.execute(CREATE_CAPTEUR_TABLE)
        connection.close()

def connect_to_database():
    return mariadb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME
    )

@app.before_request
def before_request():
    initialize_database()

@app.route('/info')
def display_page():
    return render_template('donnees.html')

# CRUD: Create (Création) - Ajouter une nouvelle donnée
@app.route('/donnees', methods=['POST'])
def add_data():
    data = request.json
    temperature = data.get('va_Temperature')
    humidite = data.get('va_Humidite')
    pression = data.get('va_Pression')

    with connect_to_database() as connection, connection.cursor() as cursor:
        cursor.execute("INSERT INTO Donnees (va_Temperature, va_Humidite, va_Pression) VALUES (%s, %s, %s);",
                       (temperature, humidite, pression))
        connection.commit()

    return jsonify({"message": "Donnée ajoutée avec succès"}), 201

# CRUD: Read (Lecture) - Récupérer toutes les données
@app.route('/donnees', methods=['GET'])
def get_all_data():
    connection = connect_to_database()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Donnees ORDER BY Date_mesure DESC;")
        all_data = cursor.fetchall()
    connection.close()

    return jsonify(data=all_data)

# CRUD: Read (Lecture) - Récupérer une donnée par ID
@app.route('/donnees/<int:data_id>', methods=['GET'])
def get_data_by_id(data_id):
    with connect_to_database() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Donnees WHERE ID = %s;", (data_id,))
        data = cursor.fetchone()

    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Donnée non trouvée"}), 404

# CRUD: Update (Mise à jour) - Modifier une donnée par ID
@app.route('/donnees/<int:data_id>', methods=['PUT'])
def update_data(data_id):
    data = request.json
    temperature = data.get('va_Temperature')
    humidite = data.get('va_Humidite')
    pression = data.get('va_Pression')

    with connect_to_database() as connection, connection.cursor() as cursor:
        # Vérifier d'abord si la donnée existe
        cursor.execute("SELECT * FROM Donnees WHERE ID = %s;", (data_id,))
        existing_data = cursor.fetchone()

        if not existing_data:
            return jsonify({"error": "Donnée non trouvée"}), 404

        # Mettre à jour la donnée
        cursor.execute("UPDATE Donnees SET va_Temperature=%s, va_Humidite=%s, va_Pression=%s WHERE ID=%s;",
                       (temperature, humidite, pression, data_id))
        connection.commit()

    return jsonify({"message": "Donnée mise à jour avec succès"})

# CRUD: Delete (Suppression) - Supprimer une donnée par ID
@app.route('/donnees/<int:data_id>', methods=['DELETE'])
def delete_data(data_id):
    with connect_to_database() as connection, connection.cursor() as cursor:
        # Vérifier d'abord si la donnée existe
        cursor.execute("SELECT * FROM Donnees WHERE ID = %s;", (data_id,))
        existing_data = cursor.fetchone()

        if not existing_data:
            return jsonify({"error": "Donnée non trouvée"}), 404

        # Supprimer la donnée
        cursor.execute("DELETE FROM Donnees WHERE ID=%s;", (data_id,))
        connection.commit()

    return jsonify({"message": "Donnée supprimée avec succès"})

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, host='0.0.0.0')
