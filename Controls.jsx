import React from 'react';
import '../styles/Controls.css';

function Controls() {
  return (
    <div className="Controls">
      <input type="text" placeholder="Search by skill..." />
      <button>Search</button>
    </div>
  );
}

export default Controls;
