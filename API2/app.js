const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.send('Bienvenue sur votre API !');
});

app.listen(port, () => {
  console.log(`Le serveur écoute sur le port ${port}`);
});