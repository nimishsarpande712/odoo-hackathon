import React, { useState } from 'react';
import '../styles/ChatSimple.css';

function ChatSimple({ onClose }) {
  const [message, setMessage] = useState('');

  const sendMessage = (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    setMessage('');
  };

  return (
    <div className="chat-wrapper">
      <form className="chat-input-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="message-input"
        />
        <button type="submit" className="send-button">
          <span>▶</span>
        </button>
      </form>
    </div>
  );
}

export default ChatSimple;
