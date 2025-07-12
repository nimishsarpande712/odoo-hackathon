import React from 'react';
import './App.css';
import Header from './components/Header';
import Controls from './components/Controls';
import CardList from './components/CardList';

function App() {
  return (
    <div className="App">
      <Header />
      <main>
        <Controls />
        <CardList />
      </main>
    </div>
  );
}

export default App;
