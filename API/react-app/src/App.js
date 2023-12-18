import logo from './logo.svg';
import './App.css';
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'; // Remplacez 'Switch' par 'Routes'
import Accueil from './Composants/Accueil';
import Temperature from './Composants/Temperature';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Accueil />} />
        <Route path="/temperature" element={<Temperature />} />
      </Routes>
    </Router>
  );
}

export default App;
