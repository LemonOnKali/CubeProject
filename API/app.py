import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_cors import CORS

load_dotenv()
url = os.getenv('DATABASE_URL')
connection = psycopg2.connect(url)

CREATE_ROOMS_TABLE = "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT)"
CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL, 
                        date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
GET_ROOM_FROM_ID = "SELECT * FROM rooms WHERE id = (%s);"
DELETE_ROOM_FROM_ID = "DELETE FROM rooms WHERE id = (%s);"

GET_TEMPS_FROM_ROOM_ID = "SELECT * FROM temperatures WHERE room_id = %s;"
GET_TEMP_FROM_ID = "SELECT * FROM temperatures WHERE id = %s;"
DELETE_TEMP_FROM_ID = "DELETE FROM temperatures WHERE id = %s;"
INSERT_TEMP = "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"

app = Flask(__name__)
CORS(app)

def initialize_database():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(CREATE_TEMPS_TABLE)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/temperatures')
def view_temperatures():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM temperatures;")
            temperatures = cursor.fetchall()
    return render_template('temperatures.html', temperatures=temperatures)

# Exemple de même route avec type de requête différente
@app.post("/")
def home2():
    print("toto")
    return "Bonjour les amis! C'est un post"

# Route pour récupérer les données d'un élément avec son ID (READ de CRUD)
@app.get("/api/room/<id>")
def afficher_room_by_id(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_ROOM_FROM_ID, (int(id),))
            room = cursor.fetchall()
    return room


# Créer une route pour supprimer un élément avec son ID (DELETE de CRUD)*
# TODO
@app.delete("/api/room/<id>")
def delete_room(id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_ROOM_FROM_ID, (int(id),))
            # Vous n'avez probablement pas besoin de récupérer les résultats ici
    return "La salle a été supprimée avec succès."

# Idem avec UPDATE pour modifier un élément avec son ID (UPDATE de CRUD)
#TODO
# Route pour mettre à jour un élément avec son ID (UPDATE de CRUD)
@app.put("/api/room/<id>")
def update_room(id):
    # Information à mettre dans le JSON sur Postman : { "name": "Nouveau_nom_de_la_salle" }
    data = request.get_json()

    # Mettez à jour les informations de la salle avec les données fournies
    updated_name = data.get("name")
    if updated_name:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE rooms SET name = %s WHERE id = %s", (updated_name, int(id)))

    # Retournez un message indiquant que la salle a été mise à jour
    return {"message": f"Room {id} updated with name {updated_name}."}



@app.get("/api/room")
def get_all_rooms():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM rooms;")
            rooms = cursor.fetchall()
    return rooms

@app.post("/api/room")
def create_room():
    data = request.get_json()
    name = data["name"]
    print(name)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_ROOM_RETURN_ID, (name,))
            room_id = cursor.fetchone()[0]
    return {"id": room_id, "message": f"Room {name} created."}, 201

@app.get("/api/room/<room_id>/temperatures")
def get_temperatures_by_room_id(room_id):
    try:
        # Créez une nouvelle connexion spécifique pour cette route
        temp_connection = psycopg2.connect(url)
        with temp_connection:
            with temp_connection.cursor() as cursor:
                cursor.execute(GET_TEMPS_FROM_ROOM_ID, (int(room_id),))
                temperatures = cursor.fetchall()

        print(f"Températures pour la salle {room_id} : {temperatures}")

        return jsonify(temperatures)
    except Exception as e:
        print(f"Erreur lors de la récupération des températures : {str(e)}")
        return jsonify({"error": "Erreur lors de la récupération des températures"})
    finally:
        # Assurez-vous de fermer la connexion spécifique
        temp_connection.close()



@app.get("/api/room/<room_id>/temperature/<temp_id>")
def get_temperature_by_id(room_id, temp_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_TEMP_FROM_ID, (int(temp_id),))
            temperature = cursor.fetchall()
    return temperature

@app.post("/api/room/<id>/temperature")
def add_temperature(id):
    # Information à mettre dans le JSON sur Postman : { "temperature": Valeur_de_la_température }
    data = request.get_json()
    temperature = data.get("temperature")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_TEMP, (int(id), temperature))
            temp_id = cursor.fetchone()[0]
    return {"id": temp_id, "message": f"Temperature {temperature} added to room {id}."}, 201

@app.delete("/api/room/<room_id>/temperature/<temp_value>")
def delete_temperature(room_id, temp_value):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM temperatures WHERE room_id = %s AND temperature = %s;", (int(room_id), float(temp_value)))
    return f"Temperature {temp_value} has been deleted from room {room_id}."

if __name__ == '__main__':
    app.run()
    initialize_database()  # Appeler la fonction d'initialisation ici
    app.run(debug=True, host='0.0.0.0')  # Accepter les connexions depuis n'importe quelle adresse IP