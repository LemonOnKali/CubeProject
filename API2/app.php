<?php
// Inclure les dépendances nécessaires
require_once('vendor/autoload.php');
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;

// Charger les variables d'environnement depuis le fichier .env
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

// Configuration de la base de données
$DB_HOST = $_ENV['DB_HOST'] ?? 'localhost';
$DB_PORT = $_ENV['DB_PORT'] ?? '3307';
$DB_USER = $_ENV['DB_USER'] ?? 'root';
$DB_PASSWORD = $_ENV['DB_PASSWORD'] ?? '';
$DB_NAME = $_ENV['DB_NAME'] ?? 'tjmsa';

// Créer une connexion à la base de données
$connection = new mysqli($DB_HOST, $DB_USER, $DB_PASSWORD, $DB_NAME, $DB_PORT);

// Vérifier la connexion
if ($connection->connect_error) {
    die("Échec de la connexion : " . $connection->connect_error);
}

// Créer la table Donnees si elle n'existe pas
$CREATE_DONNEES_TABLE = "
CREATE TABLE IF NOT EXISTS Donnees (
   ID INT AUTO_INCREMENT,
   va_Temperature DECIMAL(5,2),
   va_Humidite DECIMAL(5,2),
   va_Pression INT,
   Date_mesure DATETIME DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY(ID)
);
";
$connection->query($CREATE_DONNEES_TABLE);

// Gérer CORS
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE");
header("Content-Type: application/json");

// Gérer les requêtes entrantes
$request = Request::createFromGlobals();
$path = $request->getPathInfo();

switch ($request->getMethod()) {
    case 'GET':
        // Récupérer toutes les données
        $result = $connection->query("SELECT * FROM Donnees ORDER BY Date_mesure DESC;");
        $all_data = [];
        while ($row = $result->fetch_assoc()) {
            $all_data[] = $row;
        }
        $response = new JsonResponse(['data' => $all_data]);
        break;

    case 'POST':
        // Ajouter des données
        $data = json_decode($request->getContent(), true);
        $temperature = $data['va_Temperature'];
        $humidite = $data['va_Humidite'];
        $pression = $data['va_Pression'];

        $insert_query = "INSERT INTO Donnees (va_Temperature, va_Humidite, va_Pression) VALUES ('$temperature', '$humidite', '$pression')";
        $connection->query($insert_query);

        $response = new JsonResponse(['message' => 'Donnée ajoutée avec succès'], 201);
        break;

    // Gérer les autres méthodes HTTP (PUT, DELETE) de manière similaire

    default:
        $response = new JsonResponse(['error' => 'Méthode non autorisée'], 405);
        break;
}

// Fermer la connexion à la base de données
$connection->close();

// Envoyer la réponse
$response->send();
