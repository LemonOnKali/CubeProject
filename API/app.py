import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()
url = os.getenv('DATABASE_URL')
connection = psycopg2.connect(url)

CREATE_ROOMS_TABLE = "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT)"
CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL, 
                        date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
GET_ROOM_FROM_ID = "SELECT * FROM rooms WHERE id = (%s);"
DELETE_ROOM_FROM_ID = "DELETE FROM rooms WHERE id = (%s);"
INSERT_TEMP = "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"

app = Flask(__name__)

def initialize_database():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(CREATE_TEMPS_TABLE)


@app.get("/test")
def test():
    return "Ceci est un test."


@app.get("/")
def home():
    print("toto")
    return "Bonjour les amis!"

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
            cursor.execute(DELETE_ROOM_FROM_ID, (int(id),))
            room = cursor.fetchall()
    return room


# Créer une route pour supprimer un élément avec son ID (DELETE de CRUD)*
# TODO
@app.delete("/api/room/<id>")
def delete_all_rooms():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_ROOM_FROM_ID, (int(id),))
            room = cursor.fetchall()
    return room

# Idem avec UPDATE pour modifier un élément avec son ID (UPDATE de CRUD)
#TODO




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


if __name__ == '__main__':
    app.run()
    initialize_database()  # Appeler la fonction d'initialisation ici
    app.run(debug=True, host='0.0.0.0')  # Accepter les connexions depuis n'importe quelle adresse IP