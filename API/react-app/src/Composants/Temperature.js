import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Temperature() {
  // État pour stocker les données de température
  const [temperatureData, setTemperatureData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/room/1/temperatures');
        
        // Ajoutez ces logs pour déboguer
        console.log('Réponse de l\'API :', response);
        console.log('Données de température récupérées :', response.data);

        // Remplacez le setTemperatureData avec le traitement approprié des données
        const formattedData = response.data.map(entry => ({
          id: entry[0],
          temperature: entry[1],
          date: entry[2],
        }));
        setTemperatureData(formattedData);
      } catch (error) {
        console.error('Erreur lors de la récupération des données de température', error);
      }
    };
  
    // Appel de la fonction asynchrone
    fetchData();
  }, []); // Le tableau vide signifie que cela s'exécute une seule fois après le rendu initial

  // Afficher les données de température dans un tableau
  return (
    <div>
      <h2>Données de température</h2>
      <table>
        <thead>
          <tr>
            <th>Température</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>
          {temperatureData.map((temperature) => (
            <tr key={temperature.id}>
              <td>{temperature.temperature}</td>
              <td>{temperature.date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Temperature;




