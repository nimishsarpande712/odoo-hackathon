import React from 'react';
import '../styles/CardList.css';
import Card from './Card';

function CardList() {
  const sampleData = [
    { id: 1, name: 'John Doe', skill: 'Photoshop' },
    { id: 2, name: 'Jane Smith', skill: 'Excel' },
  ];

  return (
    <div className="CardList">
      {sampleData.map((user) => (
        <Card key={user.id} name={user.name} skill={user.skill} />
      ))}
    </div>
  );
}

export default CardList;
