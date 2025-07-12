import React, { useState } from 'react';
import '../styles/Chat.css';

function Chat({ onClose }) {
  const [messages] = useState([
    { id: 1, text: "hi !!", time: "10:25 AM", sender: "other" },
    { id: 2, text: "you in office ??", time: "10:25 AM", sender: "other" },
    { id: 3, text: "Plz share the images ?", time: "11:40 AM", sender: "other" },
    { id: 4, text: "Sure !", time: "11:40 AM", sender: "me" }
  ]);
  const [newMessage, setNewMessage] = useState('');

  const sendMessage = () => {
    if (!newMessage.trim()) return;
    setNewMessage('');
  };

  return (
    <div className="chat-overlay">
      <div className="chat-window">
        <div className="chat-header">
          <div className="user-info">
            <div className="avatar">😊</div>
            <div className="user-details">
              <h3>BillSkenny</h3>
              <span className="typing-status">Typing...</span>
            </div>
          </div>
          <div className="chat-actions">
            <button className="action-btn">📷</button>
            <button className="action-btn">📎</button>
            <button className="action-btn">🔍</button>
            <button onClick={onClose} className="close-btn">×</button>
          </div>
        </div>
        
        <div className="chat-messages">
          {messages.map((message) => (
            <div key={message.id} className={`message-bubble ${message.sender}`}>
              <div className="message-content">{message.text}</div>
              <div className="message-time">{message.time}</div>
            </div>
          ))}
        </div>
        
        <div className="chat-input-container">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message"
            className="chat-message-input"
          />
          <button onClick={sendMessage} className="send-btn">▶</button>
        </div>
      </div>
    </div>
  );
}

export default Chat;
