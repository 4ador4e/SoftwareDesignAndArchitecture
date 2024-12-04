import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home'; // Home.js
import List from './List'; // List.js
import React, { useState, useEffect } from 'react';

function App() {
  const [state, setState] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8080/api/all')
        .then(response => response.json())
        .then(data => setState(data))
        .catch(error => console.error('Error:', error));
  }, []);

  return (
      <Router>
        <div className="App">
          <h1>Data List</h1>
          <Router>
            <Routes>
              <Route exact path="/" element={<Home />} />
              <Route path="/list" element={<List data={state} />} />
            </Routes>
          </Router>
            <ul>
                {state.length > 0 ? state.map(obj => (
                    <div key={obj.id}>
                        {obj.name} {/* Проверете дали 'name' е вистинскиот атрибут */}
                    </div>
                )) : (
                    <p>Loading data...</p>
                )}
            </ul>
        </div>
      </Router>
  );
}

export default App;
